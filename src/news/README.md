---
title: News
emoji: 📰
colorFrom: yellow
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Daily News Digest — AI Summerized
---

# Daily News Digest

A PWA showing the top 5 most-talked-about stories in 10 categories — World, USA, India, Odisha, Sports, Cricket, USA Stock, AI, Quantum, and Trump — each with a ~100-word neutral summary, a thumbnail, a link to the original source, and a text-to-speech audio version you can listen to per article, per tab, or across all tabs back-to-back.

## How it works

A **LangGraph agent** runs daily via GitHub Actions (06:00 UTC):
1. Gathers candidate articles per category from free RSS feeds (Reuters, BBC, NPR, ESPN Cricinfo, MarketWatch, Ars Technica, etc.) plus a DuckDuckGo News fallback search
2. Uses **Claude Haiku 4.5** (via OpenRouter) to pick the 5 most significant, distinct stories per category and write a neutral ~100-word summary for each
3. Resolves a thumbnail per article (RSS media tag, or an Open Graph image scrape fallback)
4. Narrates each article with **Kokoro-82M** (local, open-weight TTS — no API key), pushing the MP3 to the shared `bibhu2020/media` repo to keep large binary churn out of this repo's history
5. Commits the resulting text + audio-URL data to `src/news/data/news.json` in this repo

The **FastAPI** backend fetches that JSON straight from GitHub (5-minute cache) and serves it to the **Vue.js PWA** frontend — so a daily data update never requires rebuilding the Space.

A persistent mini-player lets you listen to any article, an entire tab, or every story across every tab in sequence.

An admin screen (`/admin`, passphrase-gated) can force-trigger the GitHub Action on demand and shows the status of the last run.

## Stack

Vue.js 3 + Vite PWA · FastAPI · LangGraph · Claude Haiku 4.5 (OpenRouter) · Kokoro-82M (local TTS) · RSS (feedparser) · DuckDuckGo · GitHub Actions
