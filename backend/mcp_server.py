#!/usr/bin/env python3
"""MCP Server entry script for Memory Viewer.

Supports two modes:
  - stdio mode (default): python mcp_server.py
  - HTTP mode: python mcp_server.py --port 8501

Usage:
    # Start as stdio MCP Server (for MCP clients like Claude Desktop)
    python mcp_server.py

    # Start as HTTP MCP Server (for web clients)
    python mcp_server.py --port 8501

    # With API key
    MCP_API_KEY=secret python mcp_server.py
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Memory Viewer MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Start HTTP server on specified port (default: stdio mode)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind for HTTP mode (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    if args.port:
        # HTTP mode — run as FastAPI/Uvicorn server
        os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.dirname(__file__)))
        from app.main import app
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    else:
        # stdio mode
        os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.dirname(__file__)))
        from app.mcp_server import run_stdio_server
        run_stdio_server()


if __name__ == "__main__":
    main()