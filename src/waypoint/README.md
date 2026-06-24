---
title: Waypoint
emoji: 📍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: LangGraph-powered trip itinerary planning REST API
---

# Waypoint

Waypoint is the REST API backend for trip itinerary planning, powered by a LangGraph agentic workflow. It exposes a simple query endpoint that accepts a travel request and streams back a fully structured itinerary.

## What it does

- **Agentic workflow** — LangGraph graph with specialised nodes for weather, attractions, hotels, currency, and summarisation
- **REST API** — FastAPI endpoints for trip planning queries and health checks
- **Streaming** — itinerary chunks are streamed back as they are generated
- **Real-time data** — live weather, attraction listings, hotel costs, and currency conversion

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health and agent readiness |
| `POST` | `/query` | Submit a trip planning request |

## Stack

FastAPI · LangGraph · OpenAI / Google Gemini · Real-time data tools
