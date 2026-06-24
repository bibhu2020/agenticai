---
title: Athena
emoji: 🦉
colorFrom: indigo
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
license: mit
short_description: Plans, searches, and synthesises deep research
---

# Athena

Athena is a deep research AI named after the goddess of wisdom. Given a question, she formulates a research plan, dispatches targeted web searches, reads the source material, and writes a structured, cited report — all autonomously.

## What it does

- **Plan** — breaks the question into a multi-step research strategy
- **Search** — queries DuckDuckGo via the Scout MCP server for each step
- **Synthesise** — reads page content and weaves findings into a coherent report
- **Report** — delivers a markdown document with inline citations and a source list

## Stack

Streamlit · OpenAI Agents SDK · MCP (stdio) · SQLite session memory · Google Gemini / GPT-4o
