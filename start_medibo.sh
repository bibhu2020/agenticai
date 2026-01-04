
#!/bin/bash

# Force Bash
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# Define Paths
BACKEND_DIR="src/medibo/backend"
FRONTEND_DIR="src/medibo/frontend"

# Cleanup Helper
cleanup() {
    echo "Stopping MediBo services..."
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
    exit
}

# Trap Signals (INT for Ctrl+C, TERM for kill)
trap cleanup INT TERM

# Ensure cleanup of previous runs
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "node app.js" 2>/dev/null

# Load NVM if present
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

echo "Starting Backend..."
# Use dot (.) for sourcing checks, more portable
if [ -f ".venv/bin/activate" ]; then
    . .venv/bin/activate
elif [ -f "../../.venv/bin/activate" ]; then
    . ../../.venv/bin/activate
fi

cd "$BACKEND_DIR" || { echo "Failed to find backend directory"; exit 1; }

# Verify Environment
if ! command -v uvicorn &> /dev/null; then
    echo "Error: 'uvicorn' not found. It seems the virtual environment isn't activated or dependencies are missing."
    echo "Please ensure you have run 'pip install uvicorn fastapi openai-agents' in your environment."
    exit 1
fi

python3 -m uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
cd - > /dev/null

echo "Starting Frontend..."
cd "$FRONTEND_DIR" || { echo "Failed to find frontend directory"; exit 1; }
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"
cd - > /dev/null

echo "=================================================="
echo "MediBo Application Running"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000/docs"
echo "Logs:     $BACKEND_DIR/backend.log"
echo "          $FRONTEND_DIR/frontend.log"
echo "=================================================="
echo "Press CTRL+C to stop all services."

# Wait for background processes
wait
