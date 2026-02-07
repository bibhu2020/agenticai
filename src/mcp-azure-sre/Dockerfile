
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/mcp-azure-sre ./src/mcp-azure-sre
COPY src/core ./src/core

ENV PYTHONPATH=/app/src

EXPOSE 7860

ENV MCP_TRANSPORT=sse

CMD ["python", "src/mcp-azure-sre/server.py"]
