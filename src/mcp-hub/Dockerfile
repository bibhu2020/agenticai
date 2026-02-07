# Build stage
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
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
COPY --from=build-stage /app/dist ./src/mcp-hub/dist
COPY src/mcp_telemetry.py ./src/mcp_telemetry.py

ENV PYTHONPATH=/app/src
ENV PORT=7860

EXPOSE 7860

CMD ["python", "src/mcp-hub/api.py"]
