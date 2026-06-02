#!/bin/bash
set -e

# Optionally run fetch_agentmemory to refresh cache
if [ "${SKIP_FETCH:-0}" != "1" ]; then
    echo "[start.sh] Running fetch_agentmemory..."
    python3 /app/fetch_agentmemory.py || echo "[start.sh] fetch_agentmemory failed, continuing with existing cache"
fi

# Start the FastAPI server
exec python3 -m uvicorn app.main:app \
    --host "${MEMORY_VIEWER_HOST:-0.0.0.0}" \
    --port "${MEMORY_VIEWER_PORT:-8000}" \
    --workers 1
