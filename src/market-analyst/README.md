---
app_port: 7860
colorFrom: blue
colorTo: gray
emoji: 📈
license: mit
pinned: false
sdk: docker
short_description: Multi-agent AI that recommends stock option spreads
title: AI Market Analyst --- Real-Time Stock & Options Insights
---

# 📈 AI Market Analyst --- From Ticker to Strategy

Enter a stock ticker and get **real-time technical analysis, news
sentiment, and AI-generated option strategies** --- all powered by a
coordinated **multi-agent system**.

Designed for **learning, demos, and research** in agentic finance
workflows.

------------------------------------------------------------------------

## 👉 Try it with these tickers

-   `AAPL` --- Large-cap, steady trend
-   `TSLA` --- High volatility, news-driven
-   `NVDA` --- Momentum + sentiment play
-   `SPY` --- Market-wide signal

⬆️ Start with one ticker and explore how different agents reason
together.

------------------------------------------------------------------------

## ✨ Why this Space is different

Most market tools show charts.\
This one **explains the reasoning** behind a strategy.

✔️ Multiple specialized AI agents (not one monolithic model)\
✔️ Combines **technicals + sentiment + volatility**\
✔️ Generates **structured option strategies**, not vague advice\
✔️ Built with strong guardrails to avoid misleading outputs

This Space is a **reference implementation** for agentic AI in finance.

------------------------------------------------------------------------

## 🚀 Features

### 🧠 Multi-Agent Swarm

Each agent has a single responsibility:

-   **Market Analyst Agent**
    -   Computes SMA (20 / 50 / 200), RSI (14)
    -   Detects trend, momentum, and regime
-   **Sentiment Analyst Agent**
    -   Scrapes full news articles (not just headlines)
    -   Uses **FinBERT** to classify sentiment as Bullish / Bearish /
        Neutral
-   **Strategy Advisor Agent**
    -   Proposes **option spreads** (Iron Condors, Vertical Spreads)
    -   Includes concrete legs: strikes, expiry, and structure
-   **Risk Manager Agent**
    -   Validates strategies against:
        -   Confidence score (\>70% required)
        -   Market volatility (VIX regime)
        -   Data completeness

------------------------------------------------------------------------

### 🕵️ Deep Sentiment Engine

-   Fetches **full article text** using `requests` + `BeautifulSoup`
-   Runs transformer-based sentiment analysis (FinBERT)
-   Aggregates sentiment across multiple sources

------------------------------------------------------------------------

### 🛡️ Built-in Guardrails

-   ⏰ **Market Hours Aware**\
    Runs only during US market hours (09:30--16:00 ET)

-   🧾 **Type Safety**\
    End-to-end Pydantic validation

-   🧯 **Robust by Design**\
    Handles missing data, low-liquidity tickers, and new IPOs gracefully

------------------------------------------------------------------------

## 🔍 How it works (high level)

1.  You enter a stock ticker
2.  Market data is fetched and technical indicators are computed
3.  News articles are scraped and sentiment-scored
4.  Strategy Advisor proposes an option structure
5.  Risk Manager validates or rejects the strategy
6.  Final output includes **analysis + rationale**

------------------------------------------------------------------------

## 🧪 Example use cases

-   Learning **options strategy design**
-   Demonstrating **multi-agent coordination**
-   Building agentic finance prototypes
-   Educational demos (no real-money trading)

------------------------------------------------------------------------

## 🔧 Under the hood (for developers)

    src/market-analyst/
    ├── app.py                  # Streamlit UI (Agent Orchestrator)
    ├── aagents/                # Agent definitions
    │   ├── market_analyst.py   # Technical indicators & trends
    │   ├── sentiment_analyst.py# FinBERT sentiment engine
    │   ├── strategy_advisor.py # Options strategist
    │   └── risk_manager.py     # Trade validator
    ├── tools/                  # Capability layer
    │   ├── market_data.py      # yfinance, pandas-ta, options chains
    │   └── news_data.py        # DDGS, requests, FinBERT, Pydantic
    └── Dockerfile              # HF Spaces deployment

------------------------------------------------------------------------

## ▶️ Run locally

### Prerequisites

-   Python 3.12+
-   Virtual environment recommended

### Install & run

``` bash
pip install -e .
streamlit run src/market-analyst/app.py
```

App runs at: `http://localhost:8501`

------------------------------------------------------------------------

## 🐳 Docker / Hugging Face Spaces

``` bash
docker build -t market-analyst -f src/market-analyst/Dockerfile .
docker run -p 7860:7860 market-analyst
```

------------------------------------------------------------------------

## ⚠️ Financial Disclaimer

**Educational use only.**\
This tool is **not** a financial advisor and does **not** provide
investment advice.\
Do **not** use for real-money trading.

------------------------------------------------------------------------

💡 Like this Space?\
⭐ Give it a like · 🔁 Duplicate it · 💬 Share feedback
