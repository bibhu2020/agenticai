
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/mcp-rag-secure ./src/mcp-rag-secure

ENV PYTHONPATH=/app/src

# Create directory for ChromaDB
RUN mkdir -p src/mcp-rag-secure/chroma_db && chmod 777 src/mcp-rag-secure/chroma_db

EXPOSE 7860

CMD ["python", "src/mcp-rag-secure/server.py", "--transport", "sse", "--port", "7860", "--host", "0.0.0.0"]
