"""Provider-neutral session inventory API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.adapters.registry import get_registry
from app.core.errors import MemoryProviderError

router = APIRouter()


def _factory():
    return get_registry().provider_factory


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    status_code = 404 if exc.code == "provider_config_error" else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


@router.get("")
async def list_sessions(provider: str = Query(default="")):
    """List sessions from one provider or all providers."""
    factory = _factory()
    try:
        sessions = await factory.list_sessions(provider_name=provider or None)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc

    items = []
    providers: set[str] = set()
    for session in sorted(sessions, key=lambda item: (str(item.metadata.get("source", "")), item.id)):
        source = str(session.metadata.get("source", ""))
        if source:
            providers.add(source)
        items.append(
            {
                "id": session.id,
                "agentId": session.agent_id,
                "provider": source,
                "metadata": session.metadata,
            }
        )

    return {
        "sessions": items,
        "total": len(items),
        "providers": sorted(providers),
        "activeProvider": factory.strategy.active_provider,
    }
