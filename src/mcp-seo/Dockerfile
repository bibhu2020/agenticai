
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/mcp-seo ./src/mcp-seo
COPY src/mcp_telemetry.py ./src/mcp_telemetry.py

ENV PYTHONPATH=/app/src

EXPOSE 7860

CMD ["mcp", "run", "src/mcp-seo/server.py", "--transport", "sse"]
