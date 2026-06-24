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
COPY src/waypoint/ ./src/waypoint/

# Install monorepo dependencies via uv
RUN uv sync --frozen --no-dev --prerelease=allow

ENV PATH="/app/.venv/bin:$PATH"

# Install waypoint-specific packages that conflict with monorepo lockfile
RUN pip install --no-cache-dir \
    "langchain-google-community[places]" \
    "langchain-tavily"

# Copy entry point
COPY run.py .

EXPOSE 7860

CMD ["python", "run.py", "waypoint", "--port", "7860"]
