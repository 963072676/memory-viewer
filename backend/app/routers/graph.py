"""Provider-neutral Memory Graph API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.errors import MemoryProviderError
from app.services.graph import build_graph

router = APIRouter()


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    status_code = 404 if exc.code == "provider_config_error" else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


@router.get("")
async def get_graph(
    provider: str = Query(default="", description="Provider name; empty means all providers"),
    session_id: str = Query(default="", alias="sessionId"),
    limit: int = Query(default=200, ge=1, le=500),
):
    """Build memory graph nodes and semantic edges from unified memories."""
    try:
        return await build_graph(provider=provider, session_id=session_id, limit=limit)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
