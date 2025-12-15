---
title: Market Analyst
emoji: 📈
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Multi-Agent AI for Real-Time Stock Analysis & Strategy
---

# 📈 AI Market Analyst

A sophisticated **Multi-Agent System** that performs real-time technical and sentimental analysis on stock tickers to generate actionable option trading strategies with high confidence.

## 🚀 Features

- **🧠 Multi-Agent Swarm**:
  - **Market Analyst**: Calculates technicals (SMA 20/50/200, RSI 14) and analyzes trend/momentum.
  - **Sentiment Analyst**: Scrapes full news articles and uses **FinBERT** to score sentiment (Bullish/Bearish).
  - **Strategy Advisor**: Recommends complex option spreads (Iron Condors, Vertical Spreads) with *specific* legs (Strikes/Expiry).
  - **Risk Manager**: Validates trades against a confidence rubric (>70% required) and volatility regime (VIX).
- **🕵️ Deep Sentiment Engine**: Goes beyond headlines by fetching and analyzing the full text of news articles using `BeautifulSoup` and `Transformers` (FinBERT).
- **⚡ High Performance**: Parallelized news fetching for rapid analysis.
- **🛡️ Guardrails**:
  - **Market Hours**: Only operates during US Market Open (09:30-16:00 ET) to prevent stale data usage.
  - **Type Safety**: Pydantic validation for all data pipelines.
  - **Robustness**: Gracefully handles new IPOs or missing data.

## 🛠️ Architecture

```
src/market-analyst/
├── app.py                  # Streamlit UI (Orchestrator)
├── agents/                 # Agent Definitions
│   ├── market_analyst.py   # Technical Analysis Agent
│   ├── sentiment_analyst.py# FinBERT Agent
│   ├── strategy_advisor.py # Option Strategist
│   └── risk_manager.py     # Validator
├── tools/                  # Capability Layer
│   ├── market_data.py      # yfinance, pandas-ta logic (SMA, RSI, Options)
│   └── news_data.py        # DDGS, Requests, FinBERT, Pydantic
└── Dockerfile              # Deployment Configuration
```

## 📦 Startup

### Prerequisites
- Python 3.12+
- `uv` package manager (optional but recommended)

### Local Run

1. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

2. **Run Application**:
   ```bash
   streamlit run src/market-analyst/app.py
   ```
   The app will open at `http://localhost:8501`.

## 🐳 Docker / Deployment

The project is packaged for **Hugging Face Spaces** (Docker SDK).

```bash
# Build
docker build -t market-analyst -f src/market-analyst/Dockerfile .

# Run
docker run -p 7860:7860 market-analyst
```

## ⚠️ Disclaimer

**Educational Use Only**. This tool uses AI to analyze financial data. It is not a certified financial advisor. Do not use for real-money trading.