# Agent Framework

## What “Agentic” Means Here
An agent is a bounded workflow orchestrator that:
- Maintains state
- Selects and invokes tools
- Evaluates structured outputs
- Routes execution paths
- Stops at human approval gates

It is not a free-form chatbot.

## Lifecycle
1. Initialize state
2. Extract structured fields
3. Validate deterministically
4. Evaluate risk / choose path
5. Generate operational artifacts
6. Halt for human decision (when required)

## MCP-Style Tool Routing
We implement “MCP-style” routing as:
- A registry of tools
- Tool invocation by name + structured inputs
- Structured outputs validated by schema
- Clear logs of tool calls and results
