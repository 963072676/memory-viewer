"""Provider-agnostic Memory Intelligence API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.errors import MemoryProviderError
from app.services.intelligence import (
    cluster_memories,
    compress_memories,
    detect_contradictions,
    load_unified_memories,
    summarize_memories,
)

router = APIRouter()


class CompressionRequest(BaseModel):
    provider: str = ""
    sessionId: str = ""
    limit: int = Field(default=200, ge=1, le=500)
    maxChars: int = Field(default=800, ge=120, le=4000)


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    status_code = 404 if exc.code == "provider_config_error" else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


@router.get("/summary")
async def get_memory_summary(
    provider: str = Query(default=""),
    session_id: str = Query(default="", alias="sessionId"),
    limit: int = Query(default=200, ge=1, le=500),
):
    """Summarize memories through the unified provider layer."""
    try:
        items = await load_unified_memories(provider=provider, session_id=session_id, limit=limit)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return summarize_memories(items)


@router.post("/compress")
async def compress_memory(req: CompressionRequest):
    """Compress a provider-neutral memory slice."""
    try:
        items = await load_unified_memories(provider=req.provider, session_id=req.sessionId, limit=req.limit)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return compress_memories(items, max_chars=req.maxChars)


@router.get("/clusters")
async def get_memory_clusters(
    provider: str = Query(default=""),
    session_id: str = Query(default="", alias="sessionId"),
    limit: int = Query(default=200, ge=1, le=500),
):
    """Cluster memories from unified schema fields."""
    try:
        items = await load_unified_memories(provider=provider, session_id=session_id, limit=limit)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return cluster_memories(items)


@router.get("/contradictions")
async def get_memory_contradictions(
    provider: str = Query(default=""),
    session_id: str = Query(default="", alias="sessionId"),
    limit: int = Query(default=200, ge=1, le=500),
):
    """Detect contradiction candidates from provider-neutral memory content."""
    try:
        items = await load_unified_memories(provider=provider, session_id=session_id, limit=limit)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return detect_contradictions(items)
