"""Recommendation API router (F-19)."""

from fastapi import APIRouter, HTTPException, Query

from app.services.agentmemory import get_memory_by_id
from app.services.recommendation import compute_recommendations

router = APIRouter()


@router.get("/{memory_id}/recommendations")
def get_recommendations(memory_id: str, limit: int = Query(default=5, ge=1, le=50)):
    """Get top-N recommended memories for a given memory."""
    memory = get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    return compute_recommendations(memory_id, limit=limit)
