
---
title: MCP Secure RAG
emoji: 🔒
colorFrom: pink
colorTo: red
sdk: docker
pinned: false
---

# MCP Secure Multi-Tenant RAG Server

This is a Model Context Protocol (MCP) server for secure, tenant-isolated Retrieval-Augmented Generation.

## Tools
- `ingest_document`: Add documents with strict tenant ID metadata.
- `query_knowledge_base`: Query documents filtered by tenant ID.
- `delete_tenant_data`: Wipe data for a specific tenant.

## Security
- Uses ChromaDB for vector storage.
- All operations require a `tenant_id` to ensure data isolation.

## Running Locally
```bash
python src/mcp-rag-secure/server.py
```
