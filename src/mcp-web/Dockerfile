
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir .

# Install Playwright browsers (Chromium only to save space)
RUN playwright install --with-deps chromium

# Copy the specific server source code
COPY src/mcp-web ./src/mcp-web
COPY src/core ./src/core

# Set PYTHONPATH to include src so imports work
ENV PYTHONPATH=/app/src

# Expose the port that Hugging Face Spaces expects (7860)
EXPOSE 7860

ENV MCP_TRANSPORT=sse

# Run the server
CMD ["python", "src/mcp-web/server.py"]
