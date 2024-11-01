# Release procedure

This document specifies how to create a new release of Flou.

A release is compose of these steps:

1. Check and update the Changelog
1. Update the version for releasing
1. Publish the new docker images
1. Publish the [python package](https://pypi.org/project/flou) to PyPI
1. Advance the release version

## Updating the version

Flou follows [Semantic Versioning](https://semver.org/) (SemVer) versioning.

!!! warning "Flou is in early development, expect the Public API to evolve"
    While in rapid development Flou will stay in 0 major version indicating that
    its public API may be subject to changes while we experiment and release new
    features. Expect the API to break.

You can find the current version in the `pyproject.toml` file.

Flou will be released in `stable` and `dev`. Every release with a `-dev.X`
suffix means it's in active development and should not be used except to try
experimental features. Before releasing a `stable` release, remove the `dev`
suffix, publish the changes and then advance the minor or patch version and add
the `dev` suffix again.

## Updating the docker images

        % export FLOU_VERSION=0.1.0-dev.1
        % docker compose -f compose.yml -f compose.dev.yml build

        % docker tag flou-engine:latest flouai/flou:latest
        % docker tag flou-studio:latest flouai/studio:latest
        % docker tag flou-docs:latest flouai/docs:latest
        % docker tag flou-engine:latest flouai/flou:$FLOU_VERSION
        % docker tag flou-studio:latest flouai/studio:$FLOU_VERSION
        % docker tag flou-docs:latest flouai/docs:$FLOU_VERSION

        % docker push flouai/flou:latest
        % docker push flouai/studio:latest
        % docker push flouai/docs:latest
        % docker push flouai/flou:$FLOU_VERSION
        % docker push flouai/studio:$FLOU_VERSION
        % docker push flouai/docs:$FLOU_VERSION

## Updating the python package in PyPI

Make sure you have your PyPI credentials set in `~/.pypirc`.

1. Build the package:

        python3 -m build

1. Upload it to PyPI:

        python3 -m twine upload dist/*

1. Check that the [python package](https://pypi.org/project/flou) has been
uploaded correctly.
