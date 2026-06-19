"""Search API router."""

from typing import Optional

from fastapi import APIRouter, Query

from app.models.agentmemory import QuickSearchResponse
from app.core.memory_schema import QueryMode
from app.services import search as service
from app.services.agentmemory import quick_search

router = APIRouter()


@router.get("/quick", response_model=QuickSearchResponse)
def search_quick(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(default=10, ge=1, le=20, description="Max results to return"),
):
    """Quick search across memory titles and content (F47).

    Returns minimal fields (id, title, type, snippet, tags) sorted by relevance.
    """
    results = quick_search(query=q, limit=limit)
    return {"results": results, "total": len(results)}


@router.get("")
async def search(
    q: str = Query(default="", description="Search query (empty for pure filter mode)"),
    mode: QueryMode = Query(default="keyword", description="keyword, semantic, or hybrid"),
    source: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    types: Optional[str] = Query(default=None, description="Comma-separated type filters"),
    profile: Optional[str] = Query(default=None),
    strength_min: Optional[int] = Query(default=None, ge=0, le=10),
    strength_max: Optional[int] = Query(default=None, ge=0, le=10),
    date_from: Optional[str] = Query(default=None, description="ISO date string, e.g. 2026-01-01"),
    date_to: Optional[str] = Query(default=None, description="ISO date string, e.g. 2026-12-31"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Search across all memory sources. Supports empty query for pure filter mode (F-07)."""
    # Parse comma-separated types
    type_list = None
    if types:
        type_list = [t.strip() for t in types.split(",") if t.strip()]
    elif type:
        type_list = [type]

    return await service.search_memories_async(
        query=q,
        mode=mode,
        source=source,
        type_filter=type_list,
        profile_filter=profile,
        strength_min=strength_min,
        strength_max=strength_max,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
