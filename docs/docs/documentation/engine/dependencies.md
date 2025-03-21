# Dependencies and configuration

Most Flou projects will need to install 3rd party Python packages to use in
their Networks of Agents. As the orchestration engine runs inside Docker, Flou
automatically handles the installation of the dependencies.

## Adding dependencies to a Flou project

1. Create a `requirements.txt` file in the same folder as your `app.py`
1. Add any package you wish to install
1. Restart the Flou Engine `flou compose restart engine`
1. Upon initialization the engine installs any new dependencies present in
`requirements.txt`

## Using environment variables

For different environments, project settings and 3rd party packages
configuration you might need to set environment variables.

1. Create a `.env` file in the same folder as your `app.py`
1. Add pairs of `KEY=value` defining your environment variables, one per line.
Variable names must be written in caps.  For example in the case of OpenAI API
you can set:

    ```ini
    OPENAI_API_KEY=sk-pro...
    ```

1. Inside your python scripts you can:

    ```python
    import os
    os.environ['OPENAI_API_KEY']
    ```

## Modifying Flou's settings

Flou's own settings can be overridden by `.env` files. For example you can set
`APP_NAME` to modify the project's name that will appear in the Studio.

You can see all the available settings in
[flou/conf.py](https://github.com/flou-ai/flou/blob/main/flou/flou/conf.py).

For nested configs use `__` (double underscore), for example `DATABASE__NAME`.

<!-- 
## Using the engine Python environment in VSCode

In order to develop a Flou project in VSCode and use the Python environment with
the installed packages dependencies follow these steps:

1. Install the [Dev
Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
VSCode extension
1. Press ++command+shift+p++ and select "Dev Containers: Attach to Running Container..."
1. Select the docker container that ends in `...-engine-1`
1. A new VSCode window will appear using the engine Python environment -->

### Engine settings

#### Max retries

- **Type**: Int
- **Default**: 1
- **Description**: You can set the maximum amount of retries for a certain
execution by setting `ENGINE__MAX_RETRIES`. Each retry will be done with a
jittery exponential backoff. For more information see [Celery's
documentation](https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.retry_backoff).
