# Agents Network

The Network of Agents is Flou's main abstraction and data model. They are an
orchestration layer to coordinate LLM prompts, tools and arbitrary code
containing the logic and structure that LLM-powered apps need to focus on and
iterate in order to achieve good production performance.

They were designed to be able to express any kind of workflow from a simple
unique prompt to complex workflows in a declarative way with clean, elegant and
spaghetti free code.

The Networks of Agents follows a code-first approach but in order to extract the
best value it's recommended to use them with the visual representation and tools
found in [Flou Studio](../studio/index.md).

In this section of the documentation you will learn:

1. How to represent and implement your workflow in a [State
Machine](states-machines.md)
1. [Nesting](nesting.md) Agents Networks for working with complex workflows
1. Creating [concurrent](concurrency.md) Agents Networks
