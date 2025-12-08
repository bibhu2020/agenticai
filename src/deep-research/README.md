---
title: AI Deep Researcher        # Give your app a title
emoji: 🤖                       # Pick an emoji
colorFrom: indigo               # Theme start color
colorTo: blue                   # Theme end color
sdk: docker                     # SDK type
sdk_version: "4.39.0"           # Example Gradio version
app_file: ui/app.py             # <-- points to your app.py inside ui/
pinned: false
---

# AI Deep Researcher

**AI Deep Researcher** is a generative AI learning project built using the OpenAI Agentic Framework. This app performs deep-level web research based on user queries and generates a well-structured, consolidated report.

To achieve this, the project integrates the following technologies and AI features:
- **OpenAI SDK**
- **OpenAI Agents**
- **OpenAI WebSearch Tool**
- **Serper API** - a free alternative to OpenAI WebSearch Tool (https://serper.dev/api-keys)
- **News API** (https://newsapi.org/v2/everything)
- **SendGrid** (for emailing report)
- **LLMs** - (OpenAI, Geminia, Groq)

## How it works?
The system is a multi-agent solution, where each agent has a specific responsibility:

1. **Planner Agent**
    - Receives the user query and builds a structured query plan.

2. **Guardrail Agent**
    - Validates user input and ensures compliance.
    - Stops the workflow if the input contains inappropriate or unparliamentary words.

3. **Search Agent**
    - Executes the query plan.
    - Runs multiple web searches in parallel to gather data.

4. **Writer Agent**
    - Reads results from all search agents.
    - Generates a well-formatted, consolidated report.

5. **Email Agent (not functional at present)**
    - Responsible for sending the report via email using SendGrid.

6. **Orchestrator**
    - The entry point of the system.
    - Facilitates communication and workflow between all agents.

## Project Folder Structure

```
deep-research/
├── ui/
│   ├── app.py                    # Main Streamlit application entry point
│   └── __pycache__/              # Python bytecode cache
├── appagents/
│   ├── __init__.py               # Package initialization
│   ├── orchestrator.py           # Orchestrator agent - coordinates all agents
│   ├── planner_agent.py          # Planner agent - builds structured query plans
│   ├── guardrail_agent.py        # Guardrail agent - validates user input
│   ├── search_agent.py           # Search agent - performs web searches
│   ├── writer_agent.py           # Writer agent - generates consolidated reports
│   ├── email_agent.py            # Email agent - sends reports via email (not functional)
│   └── __pycache__/              # Python bytecode cache
├── core/
│   ├── __init__.py               # Package initialization
│   ├── logger.py                 # Centralized logging configuration
│   └── __pycache__/              # Python bytecode cache
├── tools/
│   ├── __init__.py               # Package initialization
│   ├── google_tools.py           # Google search utilities
│   ├── time_tools.py             # Time-related utility functions
│   └── __pycache__/              # Python bytecode cache
├── prompts/
│   ├── __init__.py               # Package initialization (if present)
│   ├── planner_prompt.txt        # Prompt for planner agent (if present)
│   ├── guardrail_prompt.txt      # Prompt for guardrail agent (if present)
│   ├── search_prompt.txt         # Prompt for search agent (if present)
│   └── writer_prompt.txt         # Prompt for writer agent (if present)
├── Dockerfile                     # Docker configuration for container deployment
├── pyproject.toml                 # Project metadata and dependencies (copied from root)
├── uv.lock                        # Locked dependency versions (copied from root)
├── README.md                      # Project documentation
└── run.py                         # Script to run the application locally (if present)
```

## File Descriptions

### UI Layer (`ui/`)
- **app.py** - Main Streamlit web application that provides the user interface. Handles:
  - Text input for research queries
  - Run/Download buttons (PDF, Markdown)
  - Real-time streaming of results
  - Display of final research reports
  - Session state management
  - Button enable/disable during streaming

### Agents (`appagents/`)
- **orchestrator.py** - Central coordinator that:
  - Manages the multi-agent workflow
  - Handles communication between all agents
  - Streams results back to the UI
  - Implements the research pipeline

- **planner_agent.py** - Creates a structured plan for the query:
  - Breaks down user query into actionable research steps
  - Defines search queries and research angles

- **guardrail_agent.py** - Validates user input:
  - Checks for inappropriate content
  - Ensures compliance with policies
  - Stops workflow if violations detected

- **search_agent.py** - Executes web searches:
  - Performs parallel web searches
  - Integrates with Google Search / Serper API
  - Gathers raw research data

- **writer_agent.py** - Generates final report:
  - Consolidates search results
  - Formats findings into structured markdown
  - Creates well-organized research summaries

- **email_agent.py** - Email delivery (not functional):
  - Intended to send reports via SendGrid
  - Currently not integrated in the workflow

### Core Utilities (`core/`)
- **logger.py** - Centralized logging configuration:
  - Provides consistent logging across agents
  - Handles log levels and formatting

### Tools (`tools/`)
- **google_tools.py** - Google/Serper API wrapper:
  - Executes web searches
  - Handles API authentication and response parsing

- **time_tools.py** - Utility functions:
  - Time-related operations
  - Timestamp management

### Configuration Files
- **Dockerfile** - Container deployment:
  - Builds Docker image with Python 3.12
  - Installs dependencies using `uv`
  - Sets up Streamlit server on port 7860
  - Configures PYTHONPATH for module imports

- **pyproject.toml** - Project metadata:
  - Package name: "agents"
  - Python version requirement: 3.12
  - Lists all dependencies (OpenAI, LangChain, Streamlit, etc.)

- **uv.lock** - Dependency lock file:
  - Ensures reproducible builds
  - Pins exact versions of all dependencies

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Framework | OpenAI Agents | Multi-agent orchestration |
| Web Search | Serper API / Google Search | Research data gathering |
| Web UI | Streamlit | User interface and interaction |
| Document Export | ReportLab | PDF generation from markdown |
| Async Operations | AsyncIO | Parallel agent execution |
| Dependencies | UV | Fast Python package management |
| Containerization | Docker | Cloud deployment |

## Running Locally

```bash
# Install dependencies
uv sync

# Set environment variables defined in .env.name file
export OPENAI_API_KEY="your-key"
export SERPER_API_KEY="your-key"

# Run the Streamlit app
python run.py
```

## Deployment

The project is deployed on Hugging Face Spaces as a Docker container:
- **Space**: https://huggingface.co/spaces/mishrabp/deep-research
- **URL**: https://huggingface.co/spaces/mishrabp/deep-research
- **Trigger**: Automatic deployment on push to `main` branch
- **Configuration**: `.github/workflows/deep-research-app-hf.yml`
