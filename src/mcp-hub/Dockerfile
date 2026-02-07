# Build stage
FROM node:20-slim AS build-stage
WORKDIR /hub-build
# Copy the hub sources specifically for building
COPY src/mcp-hub ./
RUN npm install
RUN npm run build

# Production stage
FROM python:3.12-slim AS production-stage
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir . fastapi uvicorn

COPY src/mcp-hub ./src/mcp-hub
COPY src/mcp_telemetry.py ./src/mcp_telemetry.py
# Copy all other MCP servers for discovery
COPY src/mcp-trader ./src/mcp-trader
COPY src/mcp-web ./src/mcp-web
COPY src/mcp-azure-sre ./src/mcp-azure-sre
COPY src/mcp-rag-secure ./src/mcp-rag-secure
COPY src/mcp-trading-research ./src/mcp-trading-research
COPY src/mcp-github ./src/mcp-github
COPY src/mcp-seo ./src/mcp-seo
COPY src/mcp-weather ./src/mcp-weather

COPY --from=build-stage /hub-build/dist ./src/mcp-hub/dist

ENV PYTHONPATH=/app/src
ENV PORT=7860

EXPOSE 7860

CMD ["python", "src/mcp-hub/api.py"]
