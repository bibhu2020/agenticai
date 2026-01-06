---
app_file: app.py
colorFrom: green
colorTo: indigo
emoji: 🩺
license: mit
pinned: false
sdk: docker
sdk_version: 0.0.1
short_description: Ask healthcare questions and get source-cited answers
  from medical documents and trusted web search
title: Ask Medical Questions with Verified Sources
---

# 🩺 Ask Medical Questions --- Get Cited Answers

Ask healthcare-related questions and receive **clear, source-backed
answers** retrieved from: - 📚 Curated medical knowledge bases\
- 🌐 Trusted web sources (only when needed)

This assistant is designed to **reduce hallucinations** by **never
answering without sources**.

## 👉 Try asking (click an example or type your own)

-   "What are the symptoms of diabetes?"
-   "How is hypertension diagnosed?"
-   "Difference between Type 1 and Type 2 diabetes?"
-   "What is HL7 in healthcare?"

⬆️ Start with a simple question and ask follow-ups naturally.

## ✨ Why this is different

Most healthcare chatbots rely on hidden model knowledge.\
This one **does not**.

✔️ Answers only from retrieved sources\
✔️ Shows where the information comes from\
✔️ Falls back to web search when documents are insufficient\
✔️ Designed for transparency and auditability

## 🚀 Features

-   🩺 Source-cited answers\
-   📚 Retrieval-Augmented Generation (RAG)\
-   🌐 Automatic web search fallback\
-   🧠 Conversation memory\
-   📥 Export conversations\
-   🎨 Clean Streamlit UI

## ⚠️ Important Notice

This assistant provides **educational information only**.\
It does **not** provide medical advice, diagnosis, or treatment.

## 🔍 How it works

1. **User asks a question** → Sent to healthcare agent
2. **Agent calls `rag_search`** → Searches medical knowledge base
3. **If RAG has info** → Returns with "Knowledge Base" citation
4. **If RAG fails** → Agent automatically calls `duckduckgo_search`
5. **If web search succeeds** → Returns with "Web Search" citation
6. **If both fail** → Returns "no information available" message

## 🔧 Under the hood

    src/healthcare-rag-chatbot/
    ├── app.py
    ├── chat.py
    └── README.md

## ⚙️ Configuration

-   Model: Gemini 2.0 Flash
-   UI: Streamlit
-   Web Search: DuckDuckGo

## ▶️ Running the Application locally

### Prerequisites

- Python 3.12
- Virtual environment activated
- Required dependencies installed (see `pyproject.toml`)

### Start the App

```bash
# From project root
cd src/healthcare-rag-chatbot
streamlit run app.py
```

## 💡 Feedback

⭐ Like the Space · 🔁 Duplicate · 💬 Share feedback
