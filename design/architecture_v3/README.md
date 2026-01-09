# Architecture V3: LangGraph Implementation

This version replicates the Agentic Architecture using **LangGraph**, a library for building stateful, multi-actor applications with LLMs.

## Philosophy
In this version, the "Anatomy of an Agent" is mapped to Graph Nodes and State:
- **Perception**: Input filtering and state updates (Graph Nodes).
- **Cognition**: The `ChatModel` (LLM) determining the next step (Conditional Edges).
- **Action**: Tool execution nodes.
- **Memory**: The shared `State` (messages list).
- **Security**: Pre/Post-processing nodes (Guardrails).

## Structure
- `layers/`: functional components defining nodes and tools.
- `patterns/`: The Graph definition (StateGraph).
- `app.py`: Streamlit interface.
- `main.py`: CLI entry point.
