"""Unified API endpoints for memory sources (P15)."""

from __future__ import annotations

import asyncio
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


def _get_registry():
    from app.adapters.registry import get_registry
    return get_registry()


@router.get("/sources")
async def list_sources():
    """List all registered memory sources with health and count info."""
    reg = _get_registry()
    if reg is None:
        return {"sources": []}

    health = await reg.health_check()
    sources = []
    for info_name, info in health.items():
        sources.append({
            "name": info_name,
            "type": info["type"],
            "enabled": info["enabled"],
            "healthy": info["healthy"],
            "count": info["count"],
        })
    return {"sources": sources}


@router.get("/memories/unified")
async def unified_memories(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    source: str = Query(default="", description="Filter by source name"),
):
    """Aggregate memories from all sources (or a specific one)."""
    reg = _get_registry()
    if reg is None:
        return {"memories": [], "total": 0, "offset": offset, "limit": limit}

    # Efficient pagination: fetch only what's needed from each source
    if source:
        adapter = reg.get(source)
        if adapter is None:
            return {"memories": [], "total": 0, "offset": offset, "limit": limit}
        # Fetch offset+limit, then slice to offset:offset+limit
        items = await adapter.list(limit=limit + offset)
        items = items[offset : offset + limit]
        # Get total count for pagination metadata
        total = len(items) + offset  # approximate without full count
    else:
        # Parallel fetch from all sources with pagination hints
        async def fetch_source(s_name: str, s_adapter, s_limit: int) -> tuple:
            try:
                items = await s_adapter.list(limit=s_limit)
                return (s_name, items, None)
            except Exception as e:
                return (s_name, [], str(e))
        tasks = [fetch_source(s.name, s, limit + offset) for s in reg._sources.values() if s.enabled]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items: list = []
        for r in results:
            if isinstance(r, tuple):
                _, items, _ = r
                all_items.extend(items)
            elif isinstance(r, list):
                all_items.extend(r)

        # Sort and paginate
        all_items.sort(key=lambda m: m.updated_at or m.created_at or "", reverse=True)
        total = len(all_items)
        items = all_items[offset : offset + limit]

    return {
        "memories": [m.to_dict() for m in items],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/memories/unified/detail")
async def unified_memory_detail(
    source: str = Query(..., min_length=1, description="Registered source name"),
    id: str = Query(..., min_length=1, description="Provider-scoped memory ID"),
):
    """Return one provider-scoped memory in the normalized display schema."""
    reg = _get_registry()
    adapter = reg.get(source) if reg is not None else None
    if adapter is None or not adapter.enabled:
        raise HTTPException(status_code=404, detail=f"Memory source not found: {source}")

    item = await adapter.get(id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Memory not found in {source}: {id}")
    return {"memory": item.to_dict()}


@router.get("/memories/unified/search")
async def unified_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100),
    source: str = Query(default="", description="Filter by source name"),
):
    """Search across all memory sources (or a specific one)."""
    reg = _get_registry()
    if reg is None:
        return {"memories": [], "total": 0}

    if source:
        adapter = reg.get(source)
        if adapter is None:
            return {"memories": [], "total": 0}
        items = await adapter.search(q, limit=limit)
    else:
        items = await reg.search_all(q, limit=limit)

    return {
        "memories": [m.to_dict() for m in items],
        "total": len(items),
        "query": q,
    }
