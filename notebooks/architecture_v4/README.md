# Architecture V4: Microsoft AutoGen Implementation

This version replicates the Agentic Architecture using **AutoGen**, a framework that enables the development of LLM applications using multiple agents that can converse with each other to solve tasks.

## Philosophy
In this version, we map the "Anatomy of an Agent" to AutoGen constructs:
- **Agents**: `AssistantAgent` (LLM-backed) and `UserProxyAgent` (Tool-executor/Human-proxy).
- **Communication**: `GroupChat` and `GroupChatManager` handling the routing (Swarm pattern).
- **Security**: Can be implemented via `check_termination` or custom reply checks.

## Structure
- `layers/`: Configuration and Tool definitions.
- `patterns/`: The `GroupChat` definition.
- `app.py`: Streamlit interface.
- `main.py`: CLI entry point.

## Key Features
- **Auto-Routing**: The `GroupChatManager` automatically selects the next speaker based on conversation history.
- **Code Execution**: Handled by `UserProxyAgent` (simulated here for tools).
