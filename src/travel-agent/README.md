---
title: AI Travel Agent
emoji: 🤖
colorFrom: purple
colorTo: pink
sdk: docker
sdk_version: "0.0.1"
app_file: ui/app.py
pinned: false
---

# AI Travel Agent

This is an experimental chatbot for chatting with AI. It is equipped with agents & tools to give you realtime data from the web. It uses **OpenAI - SDK** and **OpenAI - Agents**.

# Travel Planner (Travel Agent)

This repository contains the Travel Planner agent app — a Streamlit-based chat UI that uses modular agents and tools to provide travel plans, flight recommendations, and hotel suggestions.

The app is implemented with the OpenAI Agents SDK patterns used across this workspace and is packaged to run locally or inside Docker.

## Quick Summary
- UI: `ui/app.py` (Streamlit)
- Local runner: `run.py` (invokes `streamlit run ui/app.py` using the current Python interpreter)
- Agents: `aagents/` (agent definitions and orchestrator)
- Contexts: `contexts/` (user context, configuration)
- Tools: `tools/` (helpers and external API wrappers)
- Output models: `output_types/` (Pydantic models for structured outputs)

## Important note about a common error

If you see an error like:

```
AttributeError: partially initialized module 'streamlit' has no attribute 'set_page_config' (most likely due to a circular import)
```

That usually means there is a local file named `streamlit.py` (or `streamlit.pyc`) in the project root or working directory that shadows the real `streamlit` package. Rename any such file (for example, to `app.py`) and re-run. This project provides `run.py` which correctly runs Streamlit as a module and avoids that issue:

```bash
# Recommended: run the helper which calls the streamlit module with the same interpreter
python run.py

# Or run directly with the Streamlit CLI
streamlit run ui/app.py
```

## Setup (local development)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

2. Install dependencies

This project uses `uv` in the Dockerfile. Locally you can either use `uv` (if installed) or pip.

Using `uv` (if you have `uv` available):

```bash
# sync dependencies from pyproject/uv.lock (if available)
uv sync
```

Fallback with pip (if `requirements.txt` is provided or `pyproject.toml`):

```bash
# If a requirements file exists
python -m pip install -r requirements.txt

# Or install the project in editable mode (if pyproject is configured)
python -m pip install -e .
```

3. Environment variables

Copy `.env.name` to `.env` and add API keys and credentials required by the tools and agents (OpenAI key, any search/news API keys, etc.):

```bash
cp .env.name .env
# Edit .env and set keys like OPENAI_API_KEY, SERPER_API_KEY, NEWS_API_KEY, etc.
```

4. Run the app

```bash
# Preferred (ensures same interpreter / environment as dependencies):
python run.py

# Or directly using the Streamlit CLI
streamlit run ui/app.py
```

The helper `run.py` uses `sys.executable -m streamlit run ui/app.py` which is reliable when using virtual environments.

## Project structure (high level)

```
travel-agent/
├── .env.name                 # Example environment variables template
├── Dockerfile                # Docker image for containerized deployment
├── run.py                    # Local runner: executes Streamlit with the current Python interpreter
├── aagents/                  # Agent definitions and orchestrator (travel logic)
├── contexts/                 # User context models and helpers
├── output_types/             # Pydantic models for structured agent outputs
├── tools/                    # API wrappers (flights, hotels, search, news)
├── ui/
│   ├── __init__.py
│   ├── app.py                # Streamlit UI (main entrypoint for the app)
│   └── console.py            # Optional console/debug view
└── README.md                 # This document
```

### Notable files

- `ui/app.py` — Main Streamlit UI (chat interface, input handling, rendering of TravelPlan/Recommendation outputs).
- `run.py` — Small launcher which calls `streamlit run ui/app.py` using `sys.executable`.
- `Dockerfile` — Builds a Docker container; installs dependencies via `uv` and runs Streamlit on port `7860`.

## Configuration & integrations

- Configure API keys and secrets in `.env` (not committed):
  - `OPENAI_API_KEY` — OpenAI API key
  - `SERPER_API_KEY` — (if using Serper/Google search)
  - `NEWS_API_KEY` — News API key

- Optional tracing: `logfire` instrumentation is present in `ui/app.py`. If you do not want tracing, remove or comment out `logfire.configure(...)` and `logfire.instrument_openai_agents()`.

## Docker (build & run)

Build and run the container (example):

```bash
docker build -t travel-agent:latest .
docker run -p 7860:7860 --env-file .env travel-agent:latest
```

The Dockerfile sets `PYTHONPATH=/app` and runs `streamlit run ui/app.py --server.port=7860`.

## Troubleshooting

- If Streamlit fails with an attribute/circular import error, check for files named `streamlit.py` in the same directory — rename them.
- If modules cannot be imported (ModuleNotFoundError), ensure `PYTHONPATH` includes the project root or install the package into the environment (`pip install -e .`). The Dockerfile already sets `PYTHONPATH=/app`.
- For permission or networking issues when running Docker, verify ports and firewall rules.

## Development notes

- The UI expects structured outputs (Pydantic models) from the agents — see `output_types/` for model definitions.
- The agents run asynchronously using `asyncio` to allow parallel tool calls.
- Use `run.py` during development so that the Streamlit process uses the same Python interpreter and virtual environment.

---

If you want, I can also add a short `requirements.txt` snippet or a minimal `dev` section in `pyproject.toml` to simplify local setup. Would you like that?
