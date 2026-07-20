#!/bin/bash
# Options Paper Trader — Ubuntu/Linux launcher

set -e
cd "$(dirname "$0")"

echo "======================================"
echo "  Options Paper Trader"
echo "======================================"

# Check uv
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "uv: $(uv --version)"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
uv sync --quiet

# Create logs dir if missing
mkdir -p logs

echo ""
echo "Starting server..."
echo "Dashboard → http://localhost:5050"
echo "Press Ctrl+C to stop."
echo ""

uv run main.py
