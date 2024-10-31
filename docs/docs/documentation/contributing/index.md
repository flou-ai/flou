# Contributing

The contributing docs contains documentation on internals and processes used by
the dev team.

## Bugs, feature requests, help and chat

For bug reporting and feature requests please use the [github
issues](https://github.com/flou-ai/flou/issues). Before creating a new
issue please be sure to search among existing issues.

For questions and help please use the [github
discussions](https://github.com/flou-ai/flou/discussions).

For a quick chat, join us on our [discord
server](https://discord.gg/STB6RRraVr).

## Architecture

Flou is structured as a monorepo, containing all the core components that make
up the system:

- Flou Engine: a Python project that runs a task queue (celery) for running
  concurrent tasks.
- Flou Api: a FastAPI Python project that share's code with the Engine.
- Flou Studio: a SvelteKit project
- Flou Docs: a MKDocs project

Each runs it's own process detailed in [setting up a development
environment](dev-environment.md).
