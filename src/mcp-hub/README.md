
---
title: MCP HUB
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: true
---

# MCP HUB Portal

A centralized discovery and monitoring dashboard for all available Model Context Protocol (MCP) servers.

## Telemetry & Metrics

The Hub acts as a centralized observability server for all MCP agents.

### Architecture
1. **Data Ingestion**:
   - **Local Hub**: Writes directly to a lightweight SQLite database (`/app/data/logs.db`).
   - **Remote Agents**: Send log events via HTTP POST to the Hub's `/api/telemetry` endpoint.
2. **Storage**: Data is stored in a relational `logs` table containing timestamp, server ID, and tool name.
3. **Visualization**: The dashboard polls the SQLite DB to render real-time "Usage Trends" charts.

### Future Proofing (Production Migration)
To scale beyond this monolithic architecture, the system is designed to be swappable with industry-standard tools:
1. **OpenTelemetry (OTel)**: Replace `src/core/mcp_telemetry.py` with the OTel Python SDK to export traces to Jaeger/Tempo.
2. **Prometheus**: Expose a `/metrics` endpoint (scraping `get_metrics()`) for Prometheus to ingest time-series data.
3. **Grafana**: Replace the built-in Vue.js charts with a hosted Grafana dashboard connected to the above data sources.

## Features
- **Server Discovery**: List of all 7 production-ready MCP servers.
- **Real-time Analytics**: Tracks hourly, weekly, and monthly usage trends.
- **Team Adoption**: Visual metrics to see how the team is utilizing different tools.

## Tech Stack
- **Frontend**: Vue.js 3 + Vite
- **Charts**: Plotly.js
- **Styling**: Vanilla CSS
- **Hosting**: Docker + Nginx
