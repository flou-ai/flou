# Setting up a local dev environment

To start contributing to flou create a local python & node environment and
install all the dependencies by following these steps.

1. Clone this repo:

        % git clone https://github.com/flou-ai/flou-private/ flou
        % cd flou

1. Create a python virtual environment:

        % python -m venv venv
        % source venv/bin/activate

    > Whenever you start a new terminal start the virtualenv with `source
    > venv/bin/activate`.

1. Install the python dev dependencies:

        (venv) % cd flou
        (venv) % pip install -r requirements-dev.txt
        (venv) % cd ..

1. Install a local javascript node env and install the js dependencies.

        (venv) % nodeenv -p
        (venv) % source venv/bin/activate
        (venv) % cd studio
        (venv) % npm install
        (venv) % cd ..

    > Note that the `venv` needs to be re-activated just after installing >
    > `nodeenv` in order to activate it this first time.

1. Install the docs requirements

        (venv) % cd ../docs
        (venv) % pip install -r requirements.txt
        (venv) % cd ..

## Running Flou for contributing

We need to run each part of Flou in it's own terminal.

1. You will need a local redis and postgresql instance. If you don't want to
install them locally you can run them [via docker](docker-registry.md).

        % docker compose up db cache

1. To run the api and engine you will need to create a [sample Flou
project](../../getting-started/index.md).
       - Run the Flou Api and visit <http://localhost:8000/docs> :

            % cd my_flou_project
            % source venv/bin/activate
            (venv) % flou run api

       - Run the Flou Engine:

            % cd my_flou_project
            % source venv/bin/activate
            (venv) % flou run engine

1. For the Studio and Docs go to the flou repo:
       - Run the Flou Studio and visit <http://localhost:8001> :

            % source venv/bin/activate
            (venv) % cd flou/studio
            (venv) % npm run dev -- --port 8001

       - Run the Flou Docs and visit <http://localhost:8002> :

            % source venv/bin/activate
            (venv) % cd flou/docs
            (venv) % mkdocs serve -a 0.0.0.0:8002
