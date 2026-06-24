FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app:/app/common:$PYTHONPATH

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

# Copy required folders
COPY common/ ./common/
COPY src/nexus/ ./src/nexus/

# Install dependencies using uv, then export and install with pip to system
RUN uv sync --frozen --no-dev --prerelease=allow && \
    uv pip install -e . --system

# Copy entry point
COPY run.py .

EXPOSE 7860

CMD ["python", "run.py", "nexus", "--port", "7860"]
