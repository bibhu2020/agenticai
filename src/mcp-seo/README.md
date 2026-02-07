
---
title: MCP SEO & ADA
emoji: 🔍
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# MCP SEO & ADA Audit Server

This is a Model Context Protocol (MCP) server for website auditing, focusing on SEO and ADA/WCAG compliance.

## Tools
- `analyze_seo`: Basic SEO audit (Title, Meta, H1, Alt tags).
- `analyze_ada`: Accessibility compliance check (ARIA, lang, contrast proxies).
- `generate_sitemap`: Crawl and generate a list of internal links.

## Running Locally
```bash
python src/mcp-seo/server.py
```
