FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app/src/market-analyst:$PYTHONPATH

WORKDIR /app

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
COPY src/market-analyst/ ./src/market-analyst/

# Install dependencies using uv, then export and install with pip to system
# We use --no-dev to exclude dev dependencies if any
RUN uv sync --frozen --no-dev && \
    uv pip install -e . --system

# Preload FinBERT model into standard cache directory
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='ProsusAI/finbert')"

# Copy entry point
COPY run.py .

EXPOSE 7860

CMD ["python", "run.py", "market-analyst", "--port", "7860"]
