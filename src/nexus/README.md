---
title: Nexus
emoji: 🔮
colorFrom: pink
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
license: mit
short_description: Multi-specialist AI orchestrator for web research
---

# Nexus

Nexus is a multi-specialist AI research orchestrator. It fans out every query to three dedicated agents — a Financial Markets Analyst, a News Intelligence Specialist, and a Web Research Specialist — then synthesises their reports into a single, coherent answer.

## What it does

- **Finance** — stock prices, market sentiment, analyst ratings, earnings, IV analysis, sector screening
- **News** — breaking headlines, topic-specific articles, category filtering
- **Web Research** — deep-dive fact-finding with cited sources
- **Orchestration** — parallel specialist calls, automatic web fallback on failure, content guardrails

## Stack

Streamlit · OpenAI Agents SDK · MCP (stdio) · Google Gemini / GPT-4o
