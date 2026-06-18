"""Unified memory CRUD API backed by MemoryProvider."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.adapters.registry import get_registry
from app.core.errors import MemoryNotFoundError, MemoryProviderError, UnsupportedCapabilityError
from app.core.memory_schema import MemoryInput, MemoryQuery

router = APIRouter()


class UnifiedMemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[list[float]] = None
    provider: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    concepts: Optional[list[str]] = None
    strength: Optional[int] = Field(default=None, ge=0, le=10)
    tags: Optional[list[str]] = None
    agentId: Optional[str] = None
    sessionId: Optional[str] = None


class UnifiedMemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    provider: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    concepts: Optional[list[str]] = None
    strength: Optional[int] = Field(default=None, ge=0, le=10)
    tags: Optional[list[str]] = None
    agentId: Optional[str] = None
    sessionId: Optional[str] = None


def _factory():
    return get_registry().provider_factory


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    if isinstance(exc, MemoryNotFoundError):
        status_code = 404
    elif isinstance(exc, UnsupportedCapabilityError):
        status_code = 400
    elif exc.code == "provider_config_error":
        status_code = 404
    else:
        status_code = 502 if exc.retryable else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


def _merged_metadata(req: UnifiedMemoryCreateRequest | UnifiedMemoryUpdateRequest) -> dict[str, Any]:
    metadata = dict(req.metadata or {})
    aliases = {
        "title": req.title,
        "type": req.type,
        "concepts": req.concepts,
        "strength": req.strength,
        "tags": req.tags,
        "agentId": req.agentId,
        "sessionId": req.sessionId,
    }
    for key, value in aliases.items():
        if value is not None:
            metadata[key] = value
    return metadata


@router.get("")
async def list_memories(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    provider: str = Query(default="", description="Provider name; empty means all providers"),
    include_raw: bool = Query(default=False),
):
    """List memories through the unified provider layer."""
    reg = get_registry()
    query = MemoryQuery(query="", mode="keyword", limit=limit + offset, include_raw=include_raw)
    try:
        if provider:
            result = await reg.query_provider_memory(provider, query)
        else:
            result = await reg.query_all_memory(query)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc

    items = result.items[offset : offset + limit]
    return {
        "items": [item.to_dict() for item in items],
        "total": len(result.items),
        "limit": limit,
        "offset": offset,
        "provider": result.provider,
    }


@router.post("")
async def create_memory(req: UnifiedMemoryCreateRequest):
    """Create a memory through the active or selected provider."""
    memory_input = MemoryInput(
        content=req.content,
        metadata=_merged_metadata(req),
        embedding=req.embedding,
    )
    try:
        item = await _factory().store_memory(memory_input, provider_name=req.provider)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"memory": item.to_dict()}


@router.get("/{memory_id}")
async def get_memory(memory_id: str, provider: str = Query(default="")):
    """Get one memory through the active or selected provider."""
    try:
        item = await _factory().get_memory_by_id(memory_id, provider_name=provider or None)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"memory": item.to_dict()}


@router.put("/{memory_id}")
async def update_memory(memory_id: str, req: UnifiedMemoryUpdateRequest):
    """Update one memory through the active or selected provider."""
    patch: dict[str, Any] = {"metadata": _merged_metadata(req)}
    if req.content is not None:
        patch["content"] = req.content
    if req.title is not None:
        patch["title"] = req.title
    if req.concepts is not None:
        patch["concepts"] = req.concepts
    if req.strength is not None:
        patch["strength"] = req.strength
    if req.tags is not None:
        patch["tags"] = req.tags

    try:
        await _factory().update_memory(memory_id, patch, provider_name=req.provider)
        item = await _factory().get_memory_by_id(memory_id, provider_name=req.provider)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"success": True, "memory": item.to_dict()}


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, provider: str = Query(default="")):
    """Delete one memory through the active or selected provider."""
    try:
        await _factory().delete_memory(memory_id, provider_name=provider or None)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"success": True, "deleted_id": memory_id}
