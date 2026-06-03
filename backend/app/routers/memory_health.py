"""Memory health scoring router (F-20)."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.agentmemory import get_memory_by_id, get_all_memories
from app.services.health import compute_health

router = APIRouter()


@router.get("/{memory_id}/health")
def get_memory_health(memory_id: str):
    """Get health score for a single memory."""
    memory = get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    return compute_health(memory)
