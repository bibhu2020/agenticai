# Stage 1: Build Vue.js PWA
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY src/fifa/frontend/package*.json ./
RUN npm install
COPY src/fifa/frontend/ ./
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app:/app/src/fifa/backend:$PYTHONPATH

# System deps
RUN apt-get update && apt-get install -y \
    git build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project metadata
COPY pyproject.toml .
COPY uv.lock .

# Copy application code
COPY src/fifa/backend/ ./src/fifa/backend/

# Copy built frontend from Stage 1 to the location FastAPI expects
COPY --from=frontend-builder /app/frontend/dist ./src/fifa/frontend/dist

# Install dependencies
RUN uv sync --frozen --no-dev --prerelease=allow

ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user for HF Spaces security compliance
RUN useradd -m -u 1000 user

ENV HF_HOME=/app/hf_cache
RUN mkdir -p /app/hf_cache && chown -R user:user /app

USER user

EXPOSE 7860

CMD ["uvicorn", "src.fifa.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
