"""CLI Manifest API router (F-56) — Endpoint for CLI tool discovery."""

from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/manifest")
def cli_manifest():
    """Get CLI manifest with available endpoints and configuration.

    AC-F56-8: Backend manifest endpoint for CLI tool.
    """
    return {
        "version": "2.2.0",
        "name": "Memory Viewer CLI",
        "base_url": f"http://{settings.MEMORY_VIEWER_HOST}:{settings.MEMORY_VIEWER_PORT}",
        "endpoints": {
            "memories": {
                "list": "GET /api/agentmemory",
                "create": "POST /api/agentmemory",
                "get": "GET /api/agentmemory/{id}",
                "update": "PUT /api/agentmemory/{id}",
                "delete": "DELETE /api/agentmemory/{id}",
                "export": "GET /api/agentmemory/export",
                "import": "POST /api/agentmemory/import",
            },
            "search": {
                "keyword": "GET /api/search",
                "semantic": "GET /api/search/semantic",
                "rag": "POST /api/search/rag",
            },
            "tags": {
                "list": "GET /api/memories/tags",
                "auto_tag": "POST /api/memories/bulk-auto-tag",
            },
            "digest": {
                "generate": "POST /api/digest/generate",
                "latest": "GET /api/digest/latest",
                "history": "GET /api/digest/history",
            },
            "stats": "GET /api/stats",
            "health": "GET /api/health",
            "workspaces": "GET /api/workspaces",
        },
        "auth": {
            "type": "header",
            "header_name": "X-Api-Key",
            "required": False,
        },
    }
