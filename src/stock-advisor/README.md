
# 🧠 Multi-Agent Stock Analysis & Advisory Chatbot

## 📘 Overview
A modular multi-agent chatbot that performs real-time stock analysis, fundamental and technical evaluation, sentiment analysis, and generates trading/investment recommendations. Powered by **OpenAI SDK** and **Gradio UI**.

---

## 🧩 System Architecture

### Core Modules

| Module | Description |
|--------|--------------|
| UI Layer (Gradio) | Interactive chat, stock input, and visualization |
| Agent Orchestrator | Routes user queries to specialized agents |
| Data Agent | Fetches market data and financials |
| Technical Analysis Agent | Computes indicators (RSI, MACD, etc.) |
| Fundamental Analysis Agent | Evaluates company financial metrics |
| Sentiment Analysis Agent | Analyzes news and market sentiment |
| Strategy & Advisory Agent | Generates trade recommendations |
| Portfolio & Risk Agent | Performs portfolio optimization and risk checks |

---

## 🧱 Folder Structure

```
stockbot/
│
├── agents/
│   ├── __init__.py
│   ├── data_agent.py
|   |__ news_agent.py 
│   ├── technical_agent.py
│   ├── fundamental_agent.py
│   ├── sentiment_agent.py
│   ├── strategy_agent.py
│   └── portfolio_agent.py
│
├── core/
│   ├── __init__.py
│   ├── orchestrator.py
│   └── memory_manager.py
│
├── ui/
│   ├── __init__.py
│   └── app.py               # Gradio interface
│
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── visualization.py
│   └── helpers.py
│
├── requirements.txt
├── config.py
├── README.md
└── run.py                   # Entry point
```

---

## ⚙️ Sample Components

### **Orchestrator**
```python
from openai import OpenAI

client = OpenAI()

def orchestrator(user_query):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a multi-agent stock advisor."},
            {"role": "user", "content": user_query}
        ]
    )
    return response.choices[0].message.content
```

### **UI (Gradio)**
```python
import gradio as gr
from core.orchestrator import orchestrator

def chat_with_bot(message, history):
    reply = orchestrator(message)
    return reply

gr.ChatInterface(
    fn=chat_with_bot,
    title="StockAdvisor.AI",
    description="Your multi-agent stock analysis companion"
).launch()
```

---

## 🧮 Tech Stack

| Layer | Tools |
|--------|--------|
| LLM | OpenAI SDK (GPT-4.1, function calling) |
| Data | yfinance, polygon.io, financialmodelingprep |
| Computation | pandas, numpy, ta |
| UI | Gradio |
| Visualization | plotly, matplotlib |
| Orchestration | Python (custom multi-agent) |
| Memory (optional) | SQLite / ChromaDB |

---

## 🚀 Getting Started

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Run the App
```bash
python run.py
```

---

## 📈 Future Enhancements
- Integration with LangGraph or LlamaIndex
- Portfolio simulation and backtesting
- Voice interaction
- Compliance-safe advice generation
- Fine-tuned financial LLM model

---

© 2025 — StockAdvisor.AI | Built with ❤️ using OpenAI + Gradio
