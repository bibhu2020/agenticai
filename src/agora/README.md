---
title: Agora
emoji: 🏛️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Real-time streaming multi-agent market intelligence
---

# Agora

Agora — named after the ancient Greek marketplace — is a real-time multi-agent market intelligence platform. A swarm of four specialist agents analyses a stock simultaneously and streams their findings character-by-character to a modern Vue.js dashboard.

## What it does

- **Market Analyst** — technical indicators: SMA, RSI, MACD, Bollinger Bands
- **Sentiment Analyst** — FinBERT sentiment scoring on live news articles
- **Strategy Advisor** — synthesises technicals and sentiment into actionable strategy
- **Risk Manager** — validates the strategy against volatility and risk thresholds

## Stack

Vue.js 3 + Vite · FastAPI · Server-Sent Events (SSE) · OpenAI Agents SDK · FinBERT · DuckDuckGo

> **Disclaimer:** For informational purposes only. Not financial advice.
