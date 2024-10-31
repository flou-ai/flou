# Welcome to Flou

Flou is the framework for building **LLM-powered apps**. It enables you to
prototype, iterate and optimize your app efficiently to achieve the **best
performance**.

Flou introduces a structured development approach through three main components:

* **[Network of Agents](documentation/network/index.md)**: A formal data model
based on declarative state machines designed to represent any complex (or PoC)
workflow while maintaining clean code and enabling easy experimentation.(1)
{ .annotate }

    1.  

        * decouples your LLM-related code from the rest of your application
        * concurrency and nesting out-of-the-box
        * code-first approach accompanied by a visual representation

* **[Orchestration Engine](documentation/engine/index.md)**: Abstracts
infrastructure and orchestration logic providing an API to execute your Network
of Agents similar to how you interact with plain LLMs. Supports state
management, storage and traceability.(1)
{ .annotate }

    1.  

        * provides a Time Machine that saves a snapshot for every state
        execution and transition, allowing inspection, replay and rewind
        * efficient execution with out-of-the-box error management and retries
        * communicate via websockets, REST API, python code or CLI
        * easily integrates with your CI/CD

* **[Studio](documentation/studio/index.md)**: An IDE designed around the
development UX and best practices for developing with LLMs. It supports
observability, experimentation, performance evaluation, testing and monitoring,
creating a streamlined development cycle from prototyping to production.(1)
{ .annotate }

    1.  

        * visual representation of Network of Agents and execution history
        * production inspection and monitoring
        * playground for manual interactions
        * dataset, annotations and evaluators management
        * experiments tracking

## Why Flou?

Flou was designed after building production LLM powered apps, learning best
practices, reading academia research and extracting internal tools.

### Deterministic coding ⟶ Prompt engineering

Developing on top of LLMs introduced a new paradigm that shifts the old
deterministic substrate into a stochastic one without established best
practices. This results in developers blindly iterating via trial and error.

Flou provides a systematic and rigorous approach to effectively guide and tackle
performance challenges via its experiment tracking.

### Software design ⟶ Network of Agents

Most LLM-powered apps embark on solving a narrow/specific problem which
traditional software design cannot handle and neither naive usage of LLMs.
Taking SotA LLMs to the limits of their capabilities to solve more difficult
problems means continuously and aggressively experimenting your Network of
Agents.

Flou provides the best orchestration foundational layer to iterate over any
network structure applying new techniques and patterns from the simplest ones to
the most complex workflows. Flou's Network of Agents allows you to express ideas
in an elegant way reducing spaghetti code and accelerating iteration.

### Established frameworks ⟶ Fragmented ecosystem

The AI ecosystem is completely fragmented full of niche and narrow tools. To
develop a project you need to analyze, test and choose a set of tools that don't
play nicely with one another. You often end up a prisoner of locked proprietary
platforms and reinventing the wheel with in-house solutions.

Flou is an open-source opinionated unified framework that helps you develop
throughout the whole development cycle from a PoC to a production grade
performance app to maintenance. It's philosophy is modular so you can choose how
much or how little of Flou you want to use.

You can start your project from scratch in Flou or migrate just a small critical
piece of your exiting app that needs performance improvements.

### Sporadic disruptive updates ⟶ Frequent disruptive changes

In the current AI boom new models, checkpoints and academic techniques are
rapidly released in an unprecedented fashion. To avoid becoming obsolete you
need to stay ahead of the curve.

Flou allows you to capitalize on these frequent disruptions by making it's
evaluation platform a core component and providing functional E2E tests and
performance monitoring.
