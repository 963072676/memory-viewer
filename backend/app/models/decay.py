"""Pydantic models for decay (F-22)."""

from typing import Optional
from pydantic import BaseModel, Field


class DecayPoint(BaseModel):
    """A single point on the decay curve."""
    day: int
    strength: float


class DecayResponse(BaseModel):
    """Response for GET /api/agentmemory/{id}/decay."""
    memory_id: str
    current_strength: float
    initial_strength: int
    decay_rate: float
    days_since_created: int
    predicted_zero_date: Optional[str] = None
    decay_curve: list[DecayPoint] = Field(default_factory=list)
