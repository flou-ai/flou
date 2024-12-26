from enum import Enum
import json
import os
import pathlib
import subprocess
import sys
import re
from dotenv import dotenv_values
from importlib import resources
from typing import List
from typing_extensions import Annotated

import typer
from typer import Argument
from rich import print
from rich.table import Table

# add your path to the sys path so we can `import_module` from the path celery is being called
sys.path.append(os.getcwd())

import flou


def get_version_from_pyproject():
    """Read version from pyproject.toml"""
    import tomli

    pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
    return pyproject["project"]["version"]


app = typer.Typer()


def run_docker(command: List[str]):
    # Initialize the docker compose command
    cmd = ["docker", "compose"]

    # Use the cwd as project directoty
    cmd.extend(["--project-directory", os.getcwd()])

    # Get the path to compose.yml included in the package
    resources_dir = resources.files("docker")
    compose_file = resources_dir / "compose.yml"

    # Add the -f flag with the flou's default compose.yml
    cmd.extend(["-f", str(compose_file)])

    # Check for local compose.override.yml and add it if present
    override_file = pathlib.Path("compose.override.yml")
    if override_file.exists():
        cmd.extend(["-f", str(override_file)])

    # Run command
    cmd.extend(command)

    env = os.environ.copy()
    env["RESOURCES_DIR"] = resources_dir

    version = flou.__version__
    docker_tag = version.replace("+", "-")  # docker doesn't support + in tags
    env['REGISTRY_TAG'] = docker_tag  # use this tag for compose

    # Execute the docker compose command
    subprocess.run(cmd, env=env)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def compose(ctx: typer.Context):
    """
    Main command to start flou using docker.

    Run `flou compose up` to start flou where your `app.py` is located.

    This is a thin wrapper for `docker compose`, adding the flou default `compose.yml`.
    Run `docker compose --help` to see the wrapper command help.
    """

    # Append any additional arguments passed to flou compose
    run_docker(ctx.args)


@app.command()
def shell(ctx: typer.Context):
    """
    Start a shell inside the Engine container
    """
    run_docker(["exec", "-it", "engine", "bash"])


@app.command()
def registry():
    """
    List all registered LTMs
    """
    # clashes with the function name
    import app as project_app  # noqa: used to fill the registry
    from flou.registry import registry as flou_registry
    table = Table()
    ltms = flou_registry.get_ltms()
    table.add_column("name")
    table.add_column("fqn")
    for ltm in ltms:
        table.add_row(
            ltm.name,
            ltm.get_class_fqn(),
        )
    print(table)


@app.command()
def list():
    """
    List all LTMs
    """
    from flou.database import get_db
    db = get_db()
    table = Table()
    ltms = db.list_ltms()
    table.add_column("id")
    table.add_column("name")
    table.add_column("fqn")
    table.add_column("#snapshots")
    table.add_column("created_at")
    table.add_column("updated_at")
    for ltm in ltms:
        table.add_row(
            str(ltm["id"]),
            ltm["name"],
            ltm["fqn"],
            str(ltm["snapshots_count"]),
            str(ltm["created_at"]),
            str(ltm["updated_at"]),
        )
    print(table)


@app.command()
def get(ltm_id: int):
    """
    Get LTM instance
    """
    from flou.database import get_db
    db = get_db()
    table = Table()
    ltm = db.load_ltm(ltm_id)
    table.add_column("name")
    table.add_column("fqn")
    table.add_column("state")
    table.add_column("params")
    table.add_column("structure")
    table.add_column("concurrent_instances")
    table.add_column("created_at")
    table.add_column("uploaded_at")
    table.add_row(
        str(ltm.name),
        ltm.get_class_fqn(),
        json.dumps(ltm._state, indent=4),
        str(ltm.params),
        str(ltm.as_json(structure=True)),
        json.dumps(ltm.concurrent_instances_as_json(), indent=4),
        str(ltm.created_at),
        str(ltm.updated_at),
    )
    print(table)


@app.command()
async def transition(
    ltm_id: int,
    label: str,
    namespace: str,
    params_json: str = Argument(
        None, help="optional JSON string with the params for parameterized transitions"
    ),
    payload_json: str = Argument(None, help="optional JSON string with payload"),
):
    """
    Transition `ltm_id` LTM by `label` transition and payload (as JSON string)
    """
    from flou.database import get_db
    from flou.engine import get_engine
    engine = get_engine()
    db = get_db()
    ltm = db.load_ltm(ltm_id)

    if params_json:
        params = json.loads(params_json)
    else:
        params = None

    if payload_json:
        payload = json.loads(payload_json)
    else:
        payload = None

    engine.transition(ltm, label, params=params, namespace=namespace, payload=payload)

    print(
        f"Launched transition [bold]{label}[/bold] for LTM {ltm.name}, id: {ltm.id} with params: {params}, payload: {payload}"
    )


@app.command()
def create(fqn: str, kwargs_json: str = Argument(None, help="JSON string with kwargs")):
    """
    Create LTM with `fqn` and `kwargs` as a JSON string
    """
    from flou.database import get_db
    db = get_db()
    if kwargs_json:
        kwargs = json.loads(kwargs_json)
    else:
        kwargs = {}
    ltm = db.get_ltm_class(fqn)(**kwargs)
    id = ltm.start()
    print(f"Created LTM {ltm.name}, id: {ltm.id}, kwargs: {kwargs}")


@app.command()
def rollback(
    ltm_id: int,
    snapshot_index: Annotated[int, Argument(help="zero index snapshot to rollback to")],
):
    """
    Rollback `ltm_id` LTM to a previous state`snapshot_index`
    """
    from flou.database import get_db
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True, rollbacks=True)
    db.rollback(ltm, snapshot_index)
    print(f"Rollbacked LTM {ltm.name}, id: {ltm.id} to snapshot {snapshot_index}")


run_services = {
    "api": {
        "command": [
            "uvicorn",
            "flou.api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
            "--timeout-graceful-shutdown=0",
            "--reload-dir",
            flou.__path__[0],
        ],
    },
    "engine": {
        "command": [
            "watchmedo",
            "auto-restart",
            "--directory=.",
            f"--directory={flou.__path__[0]}",
            "--pattern=*.py",
            "--recursive",
            "--",
            "celery",
            "-A",
            "flou.engine.celery.app",
            "worker",
            "--loglevel",
            "info",
        ],
    },
}


class Services(str, Enum):
    api = "api"
    engine = "engine"


services_type = Enum("Services", {name: name for name in run_services.keys()})


@app.command()
def run(
    service: Services = Argument(help="Run the specified service"),
    extra_args: List[str] = typer.Argument(
        None, help="Extra arguments to pass to the command"
    ),
):
    """
    Run a service with optional extra arguments.
    """

    # Find the command for the specified service
    run_services[service]

    # Build the command
    command = run_services[service]["command"].copy()
    if extra_args:
        command += extra_args

    env = os.environ.copy()
    env.update(dotenv_values(".env"))

    # Execute the docker compose command
    typer.echo(f"Running command: {' '.join(command)}")
    subprocess.run(command, env=env)


@app.command()
def release(
    push: bool = typer.Option(False, "--push", help="Push images to registry"),
    tag: str = typer.Option(None, "--tag", help="Override the version tag (default: from pyproject.toml)"),
    pypi: bool = typer.Option(False, "--pypi", help="Also release to PyPI"),
):
    """
    Build and optionally push Docker images for Flou.
    Uses the version from pyproject.toml for tagging unless overridden with --tag.
    If --pypi is specified, also builds and uploads the package to PyPI.
    """
    # Get version from pyproject.toml or override
    version = tag if tag else get_version_from_pyproject()
    tags = [version.replace("+", "-")]

    # Build the images
    print(f"Building Docker images for version {tags[0]}...")
    run_docker(["-f", "compose.dev.yml", "build"])

    # Check for any letter or + in the version
    if not re.search(r'[a-zA-Z+]', tags[0]):
        tags.append("latest")

    commands = [
        ["tag", "flou-engine:latest", "flouai/flou:{version}"],
        ["tag", "flou-studio:latest", "flouai/studio:{version}"],
        ["tag", "flou-docs:latest", "flouai/docs:{version}"],
    ]

    for tag in tags:
        for cmd in commands:
            # add the tag to the version
            with_version = cmd.copy()
            with_version[2] = with_version[2].format(version=tag)
            subprocess.run(["docker"] + with_version, check=True)
            print(f"Tagged {with_version[1]} as {with_version[2]}")

    if push:
        print("\nPushing images to registry...")
        push_commands = [
            ["push", "flouai/flou:{version}"],
            ["push", "flouai/studio:{version}"],
            ["push", "flouai/docs:{version}"],
        ]

        for tag in tags:
            for cmd in push_commands:
                with_version = cmd.copy()
                with_version[1] = with_version[1].format(version=tag)
                subprocess.run(["docker"] + with_version, check=True)
                print(f"Pushed {with_version[1]}")

    if pypi:
        print("\nBuilding and releasing to PyPI...")
        # Clean previous builds
        subprocess.run(["rm", "-rf", "dist/", "build/"], check=True)
        # Build the package
        subprocess.run(["python3", "-m", "build"], check=True)
        # Upload to PyPI
        subprocess.run(["python3", "-m", "twine", "upload", "dist/*"], check=True)
        print("PyPI release completed!")

    print(f"\nRelease {tags[0]} completed successfully!")

    if not push:
        print("\nNote: Images were built and tagged but not pushed. Use --push to push to registry.")
    if not pypi:
        print("Note: Package was not released to PyPI. Use --pypi to release to PyPI.")

