---
title: Remedy
emoji: 💊
colorFrom: green
colorTo: teal
sdk: docker
app_file: app.py
pinned: false
license: mit
short_description: RAG-powered medical knowledge base with live web fallback
---

# Remedy

Remedy is a healthcare information assistant that combines a private document knowledge base (RAG) with live DuckDuckGo web search. It always searches your knowledge base first; if the result isn't useful, it automatically falls back to the web.

## What it does

- **RAG search** — retrieves answers from uploaded medical PDFs using FAISS vector search
- **Web fallback** — automatically calls DuckDuckGo when the knowledge base lacks relevant content
- **Source transparency** — every response cites whether it came from the knowledge base or the web
- **Conversation memory** — maintains context across the session with export to JSON, Markdown, or plain text

## Stack

Streamlit · OpenAI Agents SDK · FAISS · LangChain · HuggingFace Embeddings · mcp-web-search

> **Disclaimer:** For educational purposes only. Always consult a qualified healthcare professional for medical advice.
