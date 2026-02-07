
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# git is often needed for pip installing from git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir .

# Copy the specific server source code
COPY src/mcp-trader ./src/mcp-trader

# Set PYTHONPATH to include src so imports work
ENV PYTHONPATH=/app/src

# Expose the port that Hugging Face Spaces expects (7860)
EXPOSE 7860

# Run the server
# FastMCP supports --transport sse --port 7860 args by default if mcp[cli] is installed
CMD ["python", "src/mcp-trader/server.py", "--transport", "sse", "--port", "7860", "--host", "0.0.0.0"]
