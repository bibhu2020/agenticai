# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (Python 3.12 required)
uv sync --prerelease=allow

# Activate virtual environment
source .venv/bin/activate

# Run any project via the universal launcher
python run.py <app-name>
python run.py --list                      # show all registered apps

# Run a project directly
streamlit run src/<project>/app.py        # Streamlit apps
uvicorn main:app --reload                 # FastAPI apps (trip-planner)

# Run tests
pytest
pytest tests/test_healthcare_agent.py     # single file
pytest -v                                 # verbose
```

## Architecture

### Monorepo layout

- **`common/`** — shared libraries imported by all `src/` projects
  - `utility/` — model factories (`openai_model_factory.py`, `langchain_model_factory.py`, `autogen_model_factory.py`, `logger.py`)
  - `aagents/` — reusable agent wrappers (weather, news, finance, web search, RAG)
  - `rag/rag.py` — ChromaDB RAG utilities
  - `mcp/` — MCP server base and reusable tools
- **`src/`** — individual application projects (each is independently runnable)
- **`tests/`** — pytest tests; `src` and `common` are on `pythonpath` (no package prefix needed)
- **`notebooks/`** — Jupyter learning notebooks, not production code

### Model factory pattern

All apps obtain LLM clients through factories in `common/utility/` rather than constructing them directly:

- `OpenAIModelFactory.get_model(provider, model_name)` — returns `OpenAIChatCompletionsModel` (OpenAI Agents SDK); supports providers: `openai`, `azure`, `google`, `groq`, `ollama`
- `LangchainModelFactory` — returns LangChain-compatible chat models for the same providers
- `AutogenModelFactory` — returns AutoGen model configs

### Layered agent architecture (chatbot_v2)

`src/chatbot_v2` implements a ReAct-style layered architecture:
- **Perception layer** (`layers/perception.py`) — input parsing
- **Cognition layer** (`layers/cognition.py`) — reasoning, tool selection (GPT-4o)
- **Memory layer** (`layers/memory.py`) — session/conversation state
- **Action layer** (`layers/action.py`) — tool execution
- **Orchestrator** (`patterns/orchestrator.py`) — ties all layers together

### MCP servers

Projects under `src/mcp-*/` each expose a `server.py` implementing a standalone MCP server. They share tool patterns from `common/mcp/tools/`.

### Deployment

GitHub Actions workflows in `.github/workflows/` deploy to Hugging Face Spaces on pushes to `main`. Each workflow builds a Docker container from the project's `Dockerfile` and uploads via the HF API. Required GitHub secrets: `HF_TOKEN`, `HF_USERNAME`.

## Environment variables

Copy `.env.name` to `.env` and fill in keys. Key variables:

| Variable | Used by |
|---|---|
| `OPENAI_API_KEY` | Most projects |
| `GOOGLE_API_KEY` | Gemini / Google Search |
| `SERPER_API_KEY` | Deep Research web search |
| `NEWS_API_KEY` | News agent |
| `AZURE_OPENAI_API_URI` / `AZURE_OPENAI_API_VERSION` | Azure provider in factories |
| `LANGSMITH_API_KEY` / `LANGSMITH_TRACING` | LangSmith tracing (optional) |
| `HF_TOKEN` | Hugging Face model downloads |
