# Orchestration Engine

The Flou Engine abstracts all the infrastructure needed for orchestrating Flou's
Networks of Agents. It provides state management, efficient concurrency, error
handling, retries, a time machine (an execution history with replay and rewind)
and data storage out-of-the-box.

It provides several APIs best suited for different use cases:

* A [REST API](api-cli.md) similar to that of LLM providers
* [CLI](api-cli.md) for development UX, scripts and easy CI/DC integration
* [Websockets](websockets.md) for realtime updates

You can create many instances of a Network of Agents. An instance is the fixed
structure defined in your code plus a status for each LTM (State Machine /
State) and a store. You interact with the Network of Agents by performing
labelled transitions and waiting for other transitions to run.

Every time a transition is performed or a state get's executed a snapshot is
taken so it's possible to inspect and trace the whole execution history at any
point in time. It also allows for rollbacks to a previous snapshot and replays.
