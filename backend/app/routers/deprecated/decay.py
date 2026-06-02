"""Decay API router (F-22)."""

from fastapi import APIRouter, HTTPException

from app.services.agentmemory import get_memory_by_id
from app.services.decay import compute_decay
from app.models.decay import DecayResponse

router = APIRouter()


@router.get("/{memory_id}/decay", response_model=DecayResponse)
def get_decay(memory_id: str):
    """Get decay curve and prediction for a memory."""
    memory = get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    return compute_decay(memory)
