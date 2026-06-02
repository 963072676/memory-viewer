#!/bin/bash
# Memory Viewer v2 — Production start script
set -e
cd "$(dirname "$0")/backend"

# Copy agentmemory cache if not present
if [ ! -f cache/agentmemory.json ]; then
    mkdir -p cache
    if [ -f /opt/data/memory-viewer/cache/agentmemory.json ]; then
        cp /opt/data/memory-viewer/cache/agentmemory.json cache/
    fi
fi

exec /home/.hermes/hermes-agent/venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8501 --log-level info
