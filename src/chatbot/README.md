---
title: AI Chatbot
emoji: 🤖
colorFrom: pink
colorTo: yellow
sdk: docker
sdk_version: "0.0.1"
app_file: app.py
pinned: false
license: mit
short_description: An Experimental Agentic Chatbot (uses OpenAI Agent SDK)
---

# AI Chatbot

This is an experimental chatbot for chatting with AI. It is equipped with agents & tools to give you realtime data from the web. It uses **OpenAI - SDK** and **OpenAI - Agents**.

## Features
- Predefined prompts for quick analysis
- Chat interface with AI responses
- Enter key support and responsive design
- Latest messages appear on top

## Usage
1. Type a message or select a predefined prompt
2. Press **Enter** or click **Send**
3. AI responses appear instantly in the chat interface

## Supported APIs
- OpenAI
- Google
- GROQ
- SERPER
- News API

## Notes
- Make sure your API keys are configured in the Space secrets
- Built using Streamlit and deployed as a Docker Space

## References

https://openai.github.io/openai-agents-python/

https://github.com/openai/openai-agents-python/tree/main/examples/mcp

## Project Folder Structure

```
chatbot/
├── app.py                    # Main Streamlit chatbot interface
├── appagents/
│   ├── __init__.py               # Package initialization
│   ├── OrchestratorAgent.py      # Main orchestrator - coordinates all agents
│   ├── FinancialAgent.py         # Financial data and analysis agent
│   ├── NewsAgent.py              # News retrieval and summarization agent
│   ├── SearchAgent.py            # General web search agent
│   └── InputValidationAgent.py   # Input validation and sanitization agent
├── core/
│   ├── __init__.py               # Package initialization
│   └── logger.py                 # Centralized logging configuration
├── tools/
│   ├── __init__.py               # Package initialization
│   ├── google_tools.py           # Google search API wrapper
│   ├── yahoo_tools.py            # Yahoo Finance API wrapper
│   ├── news_tools.py             # News API wrapper
│   └── time_tools.py             # Time-related utility functions
├── prompts/
│   ├── economic_news.txt         # Prompt for economic news analysis
│   ├── market_sentiment.txt      # Prompt for market sentiment analysis
│   ├── news_headlines.txt        # Prompt for news headline summarization
│   ├── trade_recommendation.txt  # Prompt for trade recommendations
│   └── upcoming_earnings.txt     # Prompt for upcoming earnings alerts
├── Dockerfile                     # Docker configuration for container deployment
├── pyproject.toml                 # Project metadata and dependencies (copied from root)
├── uv.lock                        # Locked dependency versions (copied from root)
├── README.md                      # Project documentation
└── run.py                         # Script to run the application locally
```

## File Descriptions

### UI Layer
- **app.py** - Main Streamlit chatbot interface that provides:
  - Chat message display with user and AI messages
  - Text input for user queries
  - Predefined prompt buttons for quick analysis
  - Real-time AI responses
  - Support for Enter key submission
  - Responsive design with latest messages appearing first

### Agents (`appagents/`)
- **OrchestratorAgent.py** - Main orchestrator that:
  - Coordinates communication between all specialized agents
  - Routes user queries to appropriate agents
  - Manages conversation flow and context
  - Integrates tool responses

- **FinancialAgent.py** - Financial data and analysis:
  - Retrieves stock prices and financial metrics
  - Performs financial analysis using Yahoo Finance API
  - Provides market insights and recommendations
  - Integrates with yahoo_tools for data fetching

- **NewsAgent.py** - News retrieval and summarization:
  - Fetches latest news articles
  - Summarizes news content
  - Integrates with News API for real-time updates
  - Provides news-based market insights

- **SearchAgent.py** - General web search:
  - Performs web searches for general queries
  - Integrates with Google Search / Serper API
  - Returns relevant search results
  - Supports multi-source data gathering

- **InputValidationAgent.py** - Input validation:
  - Sanitizes user input
  - Validates query format and content
  - Prevents malicious inputs
  - Ensures appropriate content

### Core Utilities (`core/`)
- **logger.py** - Centralized logging configuration:
  - Provides consistent logging across agents
  - Handles different log levels
  - Formats log messages for clarity

### Tools (`tools/`)
- **google_tools.py** - Google Search API wrapper:
  - Executes web searches via Google Search / Serper API
  - Parses and returns search results
  - Handles API authentication

- **yahoo_tools.py** - Yahoo Finance API integration:
  - Retrieves stock price data
  - Fetches financial metrics and indicators
  - Provides historical price data
  - Returns earnings information

- **news_tools.py** - News API integration:
  - Fetches latest news articles
  - Filters news by category and keywords
  - Returns news headlines and summaries
  - Provides market-related news feeds

- **time_tools.py** - Time utility functions:
  - Provides current time information
  - Formats timestamps
  - Handles timezone conversions

### Prompts (`prompts/`)
Predefined prompts for specialized analysis:
- **economic_news.txt** - Analyzes economic news and implications
- **market_sentiment.txt** - Analyzes market sentiment trends
- **news_headlines.txt** - Summarizes and explains news headlines
- **trade_recommendation.txt** - Provides trading recommendations
- **upcoming_earnings.txt** - Alerts about upcoming earnings reports

### Configuration Files
- **Dockerfile** - Container deployment:
  - Builds Docker image with Python 3.12
  - Installs dependencies using `uv`
  - Sets up Streamlit server on port 8501
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
| Chat Interface | Streamlit | User interaction and display |
| Web Search | Google Search / Serper API | Web search results |
| Financial Data | Yahoo Finance API | Stock prices and metrics |
| News Data | News API | Latest news articles |
| Async Operations | AsyncIO | Parallel agent execution |
| Dependencies | UV | Fast Python package management |
| Containerization | Docker | Cloud deployment |

## Predefined Prompts

The chatbot includes quick-access buttons for common analysis:

1. **Economic News** - Analyzes current economic trends and news
2. **Market Sentiment** - Provides market sentiment analysis
3. **News Headlines** - Summarizes latest news headlines
4. **Trade Recommendation** - Suggests trading strategies
5. **Upcoming Earnings** - Lists upcoming company earnings

## Running Locally

```bash
# Install dependencies
uv sync

# Set environment variables defined in .env.name file
export OPENAI_API_KEY="your-key"
export SERPER_API_KEY="your-key"
export NEWS_API_KEY="your-key"

# Run the Streamlit app (from the root)
python run.py chatbot
```

## Deployment

The project is deployed on Hugging Face Spaces as a Docker container:
- **Space**: https://huggingface.co/spaces/mishrabp/chatbot-app
- **URL**: https://mishrabp-chatbot-app.hf.space
- **Trigger**: Automatic deployment on push to `main` branch
- **Configuration**: `.github/workflows/chatbot-app-hf.yml`
