# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY src/agora/frontend/package*.json ./
RUN npm install
COPY src/agora/frontend/ ./
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app:$PYTHONPATH

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
COPY common/ ./common/
COPY src/agora/backend/ ./src/agora/backend/

# Copy built frontend from Stage 1 to the location FastAPI expects
COPY --from=frontend-builder /app/frontend/dist ./src/agora/frontend/dist

# Install dependencies
RUN uv sync --frozen --no-dev --prerelease=allow

ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user for HF Spaces security compliance
RUN useradd -m -u 1000 user

# Set env vars for cache (must be writable by user)
ENV HF_HOME=/app/hf_cache \
    TRANSFORMERS_CACHE=/app/hf_cache \
    NUMBA_CACHE_DIR=/app/numba_cache

# Create cache directories and ownership
RUN mkdir -p /app/hf_cache /app/numba_cache && \
    chown -R user:user /app

# Switch to non-root user
USER user

# Preload FinBERT model (as user, to ensure cache writes to correct location)
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='ProsusAI/finbert', device=-1)"

# HF Spaces default port is 7860
EXPOSE 7860

# Run uvicorn on port 7860
CMD ["uvicorn", "src.agora.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
