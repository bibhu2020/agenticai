
---
title: MCP GitHub
emoji: 🐙
colorFrom: gray
colorTo: yellow
sdk: docker
pinned: false
---

# MCP GitHub Server

This is a Model Context Protocol (MCP) server for GitHub repository management and automation.

## Tools
- `list_issues`: List repository issues.
- `create_issue`: Create a new issue.
- `get_issue`: Get detailed issue info.
- `create_pull_request`: Create a new PR.
- `list_security_alerts`: Check for security alerts.

## Configuration
Requires `GITHUB_TOKEN` secret in Hugging Face Space settings.

## Running Locally
```bash
python src/mcp-github/server.py
```
