---
title: News
emoji: 📰
colorFrom: yellow
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Daily news digest — top 5 stories across 10 categories, AI-summarized
---

# Daily News Digest

A PWA showing the top 5 most-talked-about stories in 10 categories — World, USA, India, Odisha, Sports, Cricket, USA Stock, AI, Quantum, and Trump — each with a ~100-word neutral summary, a thumbnail, and a link to the original source.

## How it works

A **LangGraph agent** runs daily via GitHub Actions (06:00 UTC):
1. Gathers candidate articles per category from free RSS feeds (Reuters, BBC, NPR, ESPN Cricinfo, MarketWatch, Ars Technica, etc.) plus a DuckDuckGo News fallback search
2. Uses **Claude Haiku 4.5** (via OpenRouter) to pick the 5 most significant, distinct stories per category and write a neutral ~100-word summary for each
3. Resolves a thumbnail per article (RSS media tag, or an Open Graph image scrape fallback)
4. Commits the result to `src/news/data/news.json` in this repo

The **FastAPI** backend fetches that JSON straight from GitHub (5-minute cache) and serves it to the **Vue.js PWA** frontend — so a daily data update never requires rebuilding the Space.

An admin screen (`/admin`, passphrase-gated) can force-trigger the GitHub Action on demand and shows the status of the last run.

## Stack

Vue.js 3 + Vite PWA · FastAPI · LangGraph · Claude Haiku 4.5 (OpenRouter) · RSS (feedparser) · DuckDuckGo · GitHub Actions
