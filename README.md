# Agentic AI Projects Monorepo

A comprehensive collection of AI-powered agentic applications built with modern LLM frameworks, featuring multi-agent systems, RAG implementations, and real-time data integration. All projects share a common virtual environment and reusable components.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync --prerelease=allow

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run a specific project
python run.py <project-name>
# Example: python run.py chatbot
```

## 📁 Monorepo Structure

```
agenticaiprojects/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── pyproject.toml              # Shared dependencies and project metadata
├── uv.lock                     # Locked dependency versions
├── run.py                      # Universal launcher for all projects
├── .env                        # Environment variables (gitignored)
├── .env.name                   # Environment variable template
├── .gitignore                  # Git ignore rules
├── pytest.ini                  # Pytest configuration
│
├── .github/                    # CI/CD Workflows
│   └── workflows/              # GitHub Actions for HuggingFace deployment
│       ├── chatbot-app-hf.yml
│       ├── deep-research-app-hf.yml
│       ├── healthcare-assistant-app-hf.yml
│       ├── travel-agent-app-hf.yml
│       ├── trip-planner-api-hf.yml
│       ├── trip-planner-app-hf.yml
│       └── hf-keep-live.yml
│
├── common/                     # Shared libraries and utilities
│   ├── aagents/               # Reusable AI agents
│   │   ├── google_agent.py    # Google search agent
│   │   ├── healthcare_agent.py # Healthcare RAG agent
│   │   ├── news_agent.py      # News retrieval agent
│   │   ├── weather_agent.py   # Weather information agent
│   │   ├── web_agent.py       # General web agent
│   │   ├── web_research_agent.py # Deep research agent
│   │   └── yf_agent.py        # Yahoo Finance agent
│   ├── mcp/                   # Model Context Protocol utilities
│   │   ├── mcp_server.py      # MCP server implementation
│   │   └── tools/             # MCP tools
│   │       ├── google_tools.py
│   │       ├── news_tools.py
│   │       ├── rag_tool.py
│   │       ├── search_tools.py
│   │       ├── time_tools.py
│   │       ├── weather_tools.py
│   │       └── yf_tools.py
│   ├── rag/                   # RAG utilities
│   │   └── chroma_rag.py      # ChromaDB RAG implementation
│   └── utility/               # Common utilities
│       ├── llm_factory.py     # LLM provider factory
│       ├── logger.py          # Centralized logging
│       └── ...
│
├── data/                      # Data files
│   ├── healthcare/           # Healthcare documents for RAG
│   │   ├── ICD10.pdf
│   │   ├── PRIMARYCARE1.pdf
│   │   └── PRIMARYCARE2.pdf
│   ├── audio/                # Audio files
│   ├── rag_learning/         # RAG learning datasets
│   └── ...                   # Other datasets
│
├── db/                       # Database files
│   ├── chroma_db/           # ChromaDB vector store
│   ├── healthcare_db/       # Healthcare-specific vector DB
│   └── sessions/            # Session storage
│
├── notebooks/               # Jupyter notebooks for learning
│   ├── autogen_basics.ipynb
│   ├── langchain_basics.ipynb
│   ├── langchain_classification.ipynb
│   ├── langchain_rag_with_memory.ipynb
│   ├── langchain_translator.ipynb
│   ├── langchain_youtube_summerizer.ipynb
│   ├── mcpserver_basics.ipynb
│   ├── openai_agent.ipynb
│   ├── openai_basics.ipynb
│   └── ...
│
├── src/                     # Application projects
│   ├── accessibility/       # Accessibility tools (In Progress)
│   ├── chatbot/            # Multi-agent chatbot with real-time data
│   ├── deep-research/      # AI-powered deep research tool
│   ├── healthcare-assistant/ # Healthcare RAG chatbot
│   ├── mcp-servers/        # MCP server implementations
│   ├── stock-advisor/      # Stock market analysis (In Development)
│   ├── travel-agent/       # Travel planning agent
│   └── trip-planner/       # AI trip planner with itinerary
│
└── tests/                  # Test files
    ├── test_healthcare_agent.py
    └── ...
```

## 🎯 Projects

### 1. **Chatbot** 🤖
Multi-agent chatbot with real-time financial data, news, and web search capabilities.

- **Tech Stack**: OpenAI Agents, Streamlit
- **Features**: Financial analysis, news summarization, web search, predefined prompts
- **Agents**: Orchestrator, Financial, News, Search, Input Validation
- **Live Demo**: [https://mishrabp-chatbot-app.hf.space](https://mishrabp-chatbot-app.hf.space)
- **Status**: ✅ Deployed

### 2. **Deep Research** 🔍
AI-powered deep research tool that generates comprehensive reports from web searches.

- **Tech Stack**: OpenAI Agents, Streamlit, Serper API
- **Features**: Multi-agent research pipeline, parallel web searches, PDF/Markdown export
- **Agents**: Planner, Guardrail, Search, Writer, Email (not functional)
- **Live Demo**: [https://mishrabp-deep-research.hf.space](https://mishrabp-deep-research.hf.space)
- **Status**: ✅ Deployed

### 3. **Healthcare Assistant** 🏥
Healthcare chatbot using RAG with medical knowledge base and web search fallback.

- **Tech Stack**: Gemini 2.0 Flash, LangChain, ChromaDB, Streamlit
- **Features**: RAG search, DuckDuckGo fallback, conversation memory, source citations
- **Knowledge Base**: ICD10, Primary Care medical documents
- **Live Demo**: [https://huggingface.co/spaces/{username}/healthcare-assistant](https://huggingface.co/spaces/{username}/healthcare-assistant)
- **Status**: 🚀 Ready for Deployment

### 4. **Trip Planner** 🌍
AI-powered trip planning with real-time weather, attractions, and cost estimation.

- **Tech Stack**: FastAPI, Streamlit, OpenAI
- **Features**: Weather info, attractions, hotel costs, currency conversion, itinerary planning
- **Live Demo**: [https://mishrabp-trip-advisor-app.hf.space](https://mishrabp-trip-advisor-app.hf.space)
- **Status**: ✅ Deployed

### 5. **Travel Agent** ✈️
Intelligent travel agent for booking and travel assistance.

- **Tech Stack**: OpenAI Agents, Streamlit
- **Features**: Travel recommendations, booking assistance, itinerary management
- **Status**: ✅ Deployed

### 6. **Stock Advisor** 📈
Stock market analysis and trading recommendations.

- **Tech Stack**: Yahoo Finance, LangChain, Streamlit
- **Features**: Real-time stock data, sentiment analysis, trade recommendations
- **Status**: 🔨 In Development

### 7. **Accessibility Tools** ♿
Accessibility enhancement tools.

- **Status**: 🔨 In Progress

### 8. **MCP Servers** 🔌
Model Context Protocol server implementations for tool integration.

- **Features**: Custom MCP servers for various integrations
- **Status**: ✅ Active

## 🛠️ Technology Stack

### LLM Providers
- **OpenAI** (GPT-4, GPT-3.5)
- **Google Gemini** (Gemini 2.0 Flash)
- **Anthropic Claude**
- **Groq**
- **Ollama** (Local models)

### Frameworks
- **LangChain** - LLM application framework
- **LangGraph** - Multi-agent orchestration
- **OpenAI Agents** - Agent framework
- **Autogen** - Multi-agent conversations

### Vector Databases
- **ChromaDB** - Vector storage for RAG
- **FAISS** - Facebook AI Similarity Search

### Web Frameworks
- **Streamlit** - Interactive web UIs
- **FastAPI** - REST APIs

### Tools & Integrations
- **Serper API** - Web search
- **DuckDuckGo** - Web search (no API key)
- **Yahoo Finance** - Financial data
- **News API** - News articles
- **Playwright** - Web scraping
- **MCP** - Model Context Protocol

## 📦 Installation

### Prerequisites
- **Python 3.12**
- **uv** package manager ([Install uv](https://github.com/astral-sh/uv))

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd agenticaiprojects

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Copy environment template
cp .env.name .env

# Configure API keys in .env
# Add your API keys for:
# - OPENAI_API_KEY
# - GOOGLE_API_KEY
# - SERPER_API_KEY
# - NEWS_API_KEY
# - etc.
```

## 🚀 Running Projects

### Using the Universal Launcher

```bash
python run.py <project-name>
```

Available projects:
- `chatbot`
- `deep-research`
- `healthcare-assistant`
- `trip-planner`
- `travel-agent`
- `stock-advisor`
- `accessibility`

### Running Directly

```bash
# Navigate to project folder
cd src/<project-name>

# Run Streamlit app
streamlit run app.py
# or
streamlit run ui/app.py

# Run FastAPI app (for API projects)
uvicorn main:app --reload
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_healthcare_agent.py

# Run with verbose output
pytest -v
```

## 📚 Learning Resources

The `notebooks/` folder contains Jupyter notebooks covering:
- **Autogen basics** - Multi-agent conversations
- **LangChain basics** - LLM application development
- **LangChain RAG** - Retrieval-Augmented Generation with memory
- **LangChain classification** - Text classification
- **OpenAI agents** - Agent framework basics
- **MCP server basics** - Model Context Protocol

## 🌐 Deployment

All projects are configured for automatic deployment to **Hugging Face Spaces** via GitHub Actions.

### Deployment Workflow
1. Push changes to `main` branch
2. GitHub Actions triggers deployment workflow
3. Project is built as Docker container
4. Deployed to Hugging Face Spaces

### Required Secrets
Configure in GitHub repository settings:
- `HF_TOKEN` - Hugging Face API token
- `HF_USERNAME` - Hugging Face username

## 🤝 Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests: `pytest`
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Live Demos

| Project | URL | Status |
|---------|-----|--------|
| Chatbot | [mishrabp-chatbot-app.hf.space](https://mishrabp-chatbot-app.hf.space) | ✅ Live |
| Deep Research | [mishrabp-deep-research.hf.space](https://mishrabp-deep-research.hf.space) | ✅ Live |
| Healthcare Assistant | TBD | 🚀 Ready |
| Trip Planner | [mishrabp-trip-advisor-app.hf.space](https://mishrabp-trip-advisor-app.hf.space) | ✅ Live |
| Travel Agent | TBD | ✅ Deployed |
| Stock Advisor | TBD | 🔨 In Dev |
| Accessibility | TBD | 🔨 In Progress |

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using modern AI frameworks and best practices**
