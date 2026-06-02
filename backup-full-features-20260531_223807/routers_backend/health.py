"""Health check API router."""

import time

from fastapi import APIRouter, Request

from app.services.agentmemory import get_all_memories, get_cache_age
from app.services.hermes_memory import get_hermes_memory_count
from app.scheduler import get_scheduler_status

router = APIRouter()


@router.get("/health")
def health_check(request: Request):
    """Service health check endpoint."""
    uptime = time.time() - request.app.state.start_time
    scheduler_info = get_scheduler_status()
    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": int(uptime),
        "cache_age_seconds": int(get_cache_age()),
        "agentmemory_count": len(get_all_memories()),
        "hermes_memory_count": get_hermes_memory_count(),
        "scheduler": {
            "running": scheduler_info.get("running", False),
            "last_refresh_at": scheduler_info.get("last_refresh_at"),
            "next_refresh_at": scheduler_info.get("next_refresh_at"),
            "last_refresh_success": scheduler_info.get("last_refresh_success"),
            "last_refresh_error": scheduler_info.get("last_refresh_error"),
        },
    }
