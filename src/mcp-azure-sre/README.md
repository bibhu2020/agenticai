
---
title: MCP Azure SRE
emoji: ☁️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# MCP Azure SRE Server

This is a Model Context Protocol (MCP) server for Azure Infrastructure management and monitoring.

## Tools
- `list_resources`: List Azure resources.
- `restart_vm`: Restart Virtual Machines.
- `get_metrics`: Get Azure Monitor metrics.
- `analyze_logs`: Query Log Analytics.

## Configuration
Requires Azure credentials (set as Secrets in Hugging Face Space settings):
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

## Running Locally
```bash
python src/mcp-azure-sre/server.py
```
