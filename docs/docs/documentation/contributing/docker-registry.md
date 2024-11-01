# Docker registry

Flou uses docker and it's hub as the preferred way to develop and deploy Flou
apps. Here are the process and options to build, test and deploy Flou's docker
images.

## Running the images from the local Flou repo

You need to override the default `compose.yml` so that it builds the
images from the local source code instead of pulling them from the registry:

``` zsh
% docker compose -f compose.yml -f compose.dev.yml up
```

## Building and deploying the images

To build, tag and push the images use:

``` zsh
% docker compose -f compose.yml -f compose.dev.yml build

% docker tag flou-engine:latest flouai/flou:latest
% docker tag flou-studio:latest flouai/studio:latest
% docker tag flou-docs:latest flouai/docs:latest

% docker push flouai/flou:latest
% docker push flouai/studio:latest
% docker push flouai/docs:latest
```

## Creating a local docker registry for testing

Creating a local docker registry can be useful for testing release procedures.

We will be following [this
guide](https://www.docker.com/blog/how-to-use-your-own-registry-2/) to set up
the local registry using docker.

### Set up your local docker registry

First start your docker daemon and then run:

``` zsh
% docker run -d -p 5001:5000 --name registry registry:2.7
```

If you need to see the logs:

``` zsh
% docker logs -f registry
```

If you want a nice UI to see the registry instead run the `compose.yml`
defined in [this image](https://hub.docker.com/r/joxit/docker-registry-ui)
adding to `registry-server`:

``` yaml
    ports:
      - 5001:5000
```

### Using the local registry

After building the docker image use the following instructions to tag, push and
pull from the local repository.

``` zsh
% docker compose -f compose.yml -f compose.dev.yml build
% docker tag flou-engine:latest localhost:5001/flouai/flou:latest
% docker push localhost:5001/flouai/flou:latest
% docker pull localhost:5001/flouai/flou
```

The same can be done for the studio changing `engine` for `studio` or `docs`.

``` zsh
% docker tag flou-engine:latest localhost:5001/flouai/flou:latest
% docker tag flou-studio:latest localhost:5001/flouai/studio:latest
% docker tag flou-docs:latest localhost:5001/flouai/docs:latest
% docker push localhost:5001/flouai/flou:latest
% docker push localhost:5001/flouai/studio:latest
% docker push localhost:5001/flouai/docs:latest
```

To the use this images in `flou compose` add the `REGISTRY` envvar to point to
the local registry:

``` zsh
% REGISTRY=localhost:5001/ flou compose up
```

> This overrides the default `compose.yml` file by changing the `build`
> property to an `image` pointing to the local registry and adding local volumes
> for developing.
