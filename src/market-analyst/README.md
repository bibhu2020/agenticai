---
app_port: 7860
colorFrom: blue
colorTo: gray
emoji: 📈
license: mit
pinned: false
sdk: docker
short_description: Multi-agent AI Market Analyst
title: AI Market Analyst v2
---

# 📈 AI Market Analyst --- Upgraded Architecture

This application has been upgraded to a decoupled architecture with a **FastAPI backend** and a **Vue.js frontend**. The multi-agent swarm now communicates via Server-Sent Events (SSE) for real-time analysis streaming.

## 🏗️ New Architecture

### 📂 `backend/`
- **FastAPI**: Exposes an SSE endpoint for real-time agent streams.
- **Agents**: Same powerful multi-agent team (Market, Sentiment, Strategy, Risk).
- **Tools**: Technical analysis, DuckDuckGo news scraping, and FinBERT sentiment analysis.

### 📂 `frontend/`
- **Vue.js 3 + Vite**: A modern, glassy UI built for performance and intuition.
- **Glassmorphism Design**: High-end visuals with backdrop blurs and neon accents.
- **Real-time Streaming**: Watch agents "think" and communicate as it happens.

---

## 🚀 Getting Started

### 1. Run the Backend
```bash
cd src/market-analyst/backend
# Install dependencies (if not already in root env)
pip install -r requirements.txt
# Launch FastAPI
uvicorn main:app --reload --port 8000
```
Backend API will be at `http://localhost:8000`

### 2. Run the Frontend
```bash
cd src/market-analyst/frontend
# Install dependencies
npm install
# Launch Vite
npm run dev
```
Frontend UI will be at `http://localhost:5173`

---

## ✨ Features
- **SSE Streaming**: Agents stream results character-by-character for a more interactive experience.
- **Glassy Dashboard**: A premium, dark-mode adaptive UI.
- **Multi-Agent Coordination**: MarketAnalyst (Technicals), SentimentAnalyst (News), StrategyAdvisor (Logic), RiskManager (Validation).
- **FinBERT Integration**: Real-time financial sentiment analysis on full article text.

---

## ⚠️ Financial Disclaimer
**Educational use only.** This tool is not a financial advisor. Do not use for real-money trading without consulting a certified professional.
