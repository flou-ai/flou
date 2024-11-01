# Creating a Flou project

1. [Install `docker engine`](https://docs.docker.com/engine/install/) if not
already present.

1. Create a new folder for your Flou project:

        % mkdir my-project
        % cd my-project

1. Start a Python virtual environment and install Flou:

        % python3 -m venv venv
        % source venv/bin/activate
        (venv) % pip install flou

1. Create an `app.py` file, the entrypoint for your Flou project and a
`requirements.txt` file for your project dependencies:

        (venv) % touch app.py
        (venv) % touch requirements.txt

1. Start Flou:

        (venv) % flou compose up

    !!! note "Flou uses docker under the hood"

        Flou uses `docker compose` to easily manage all the needed processes
        with a friendly wrapper via `flou compose`.

    !!! warning "Flou is currently private"

        To run Flou you will need to run it in [development
        mode](../documentation/contributing/dev-environment.md) or run a [local
        docker registry](../documentation/contributing/docker-registry.md).

1. Open the Flou Studio by visiting
[http://localhost:8001](http://localhost:8001) .

1. You can find the Flou Api documentation in
[http://localhost:8000/docs](http://localhost:8000/docs) .
