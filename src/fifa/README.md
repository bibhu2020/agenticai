---
title: FIFA
emoji: ⚽
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: FIFA World Cup 2026 live scores, schedule & news dashboard
---

# FIFA World Cup 2026 Dashboard

A real-time PWA dashboard for FIFA World Cup 2026 — live scores, upcoming schedule in CDT, and AI-summarised news.

## What it does

- **Today's Scores** — live match results with country flags, scores, status badges, and venue details. Filter by Live / Final / Upcoming.
- **Upcoming Schedule** — next 7 days of matches in Central Daylight Time (CDT) with stadium and city information.
- **News** — latest FIFA World Cup news with thumbnails and Gemini-generated summaries.

## How it works

A **LangGraph agent** runs daily via GitHub Actions (8 AM UTC):
1. Fetches live scores and schedule from ESPN
2. Fetches news articles (ESPN + DuckDuckGo fallback)
3. Summarises articles using **Gemini 2.5 Flash**
4. Saves everything to an Excel file (`fifa/fifa_data.xlsx`) in a GitHub media repo

The **FastAPI** backend downloads the Excel on demand (5-minute cache) and serves JSON to the **Vue.js PWA** frontend.

## Stack

Vue.js 3 + Vite PWA · FastAPI · LangGraph · Gemini 2.5 Flash · ESPN API · DuckDuckGo · openpyxl · GitHub API
