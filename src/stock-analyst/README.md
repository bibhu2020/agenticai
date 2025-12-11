---
title: Stock Analyst
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "0.0.1"
app_file: app.py
pinned: false
license: mit
short_description: Multi-Agent Stock Analysis Team (uses AutoGen)
---

# Stock Analyst

This is an experimental multi-agent system for comprehensive stock market analysis. It uses **Microsoft AutoGen** to orchestrate a team of specialized agents that collaborate to provide deep insights and investment decisions.

## Features
- **Team of Agents**: Collaborative analysis from Trends, News, Sentiment, and Decision agents.
- **Round-Robin Orchestration**: Agents take turns sharing insights in a structured conversation.
- **Real-time Data**: Fetches live stock history and financial data via `yfinance`.
- **News Integration**: Searches DuckDuckGo for the latest market news.
- **Streamlit UI**: Clean, interactive interface with agent avatars and real-time streaming.

## Usage
1. Enter a valid stock ticker (e.g., TSLA, NVDA, AAPL).
2. Click **Analyze Stock**.
3. Watch the agents collaborate in real-time to analyze trends, news, and sentiment alongside the "Decision Agent" making the final call.

## Supported Tools
- **Yahoo Finance**: Historical prices, analyst recommendations, market sentiment.
- **DuckDuckGo**: Live news search.
- **Web Scraping**: Fetching and summarizing full article content.

## Project Folder Structure

```
stock-analyst/
├── app.py                    # Main Streamlit UI
├── aagents/
│   ├── agents.py             # Agent definitions (Trends, News, Sentiment, Decision) and factories
├── teams/
│   ├── team.py               # RoundRobinGroupChat orchestration logic
├── tools/
│   ├── yf_tools.py           # Yahoo Finance tool wrappers
│   ├── search_tools.py       # DuckDuckGo and web scraping tools
├── Dockerfile                # Deployment configuration
└── README.md                 # Project documentation
```

## Agents (`aagents/agents.py`)

- **Stock Trends Agent** (📈):
  - Fetches historical price data.
  - Analyzes price movements and volume trends.
  - Outputs structured `StockTrend` data for UI visualization.

- **News Agent** (📰):
  - Searches for top recent news stories.
  - Fetches and reads full article content.
  - Summarizes key events impacting the stock.

- **Sentiment Agent** (💡):
  - Check general market sentiment.
  - Reviews analyst recommendations.
  - Aggregates expert opinions.

- **Decision Agent** (⚖️):
  - Synthesizes all gathered information.
  - Provides a final "Invest" or "Not Invest" decision.
  - Summarizes the rationale.

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Framework | Microsoft AutoGen | Multi-agent orchestration |
| LLM | GPT-4o / Gemini | Intelligence engine for agents |
| UI Framework | Streamlit | User interface |
| Data Source | yfinance | Stock market data |
| Search | DuckDuckGo | Real-time news |

## Running Locally

```bash
# Install dependencies
uv sync

# Set environment variables in .env or shell
export GOOGLE_API_KEY="your-gemini-key" # or OPENAI_API_KEY if using OpenAI

# Run the Streamlit app (from the root)
streamlit run src/stock-analyst/app.py
```
