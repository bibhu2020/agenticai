
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .
# Download TextBlob corpora if needed (basic polarity usually doesn't need it, but good practice)
RUN python -m textblob.download_corpora

COPY src/mcp-trading-research ./src/mcp-trading-research
COPY src/mcp_telemetry.py ./src/mcp_telemetry.py

ENV PYTHONPATH=/app/src

EXPOSE 7860

ENV MCP_TRANSPORT=sse

CMD ["python", "src/mcp-trading-research/server.py"]
