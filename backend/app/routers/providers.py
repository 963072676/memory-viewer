"""Provider management API for the memory abstraction layer."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters.registry import get_registry
from app.core.errors import MemoryProviderError

router = APIRouter()


class ProviderStrategyUpdate(BaseModel):
    activeProvider: Optional[str] = None
    fallbackProviders: Optional[list[str]] = None
    parallelQuery: Optional[bool] = None
    timeoutSeconds: Optional[float] = Field(default=None, gt=0)
    retryAttempts: Optional[int] = Field(default=None, ge=1)
    retryBackoffSeconds: Optional[float] = Field(default=None, ge=0)
    debugRawResponse: Optional[bool] = None


class ProviderSwitchRequest(BaseModel):
    activeProvider: str


def _factory():
    return get_registry().provider_factory


def _provider_summary() -> list[dict]:
    reg = get_registry()
    strategy = reg.provider_factory.strategy
    return [
        {
            "name": source.name,
            "type": source.source_type,
            "enabled": source.enabled,
            "active": source.name == strategy.active_provider,
            "fallback": source.name in strategy.fallback_providers,
            "capabilities": sorted(getattr(source, "capabilities", set())),
        }
        for source in reg._sources.values()
    ]


def _strategy_response() -> dict:
    return _factory().get_strategy_config()


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    status_code = 404 if exc.code == "provider_config_error" else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


@router.get("")
async def get_providers():
    """Return provider inventory, active strategy, and health."""
    reg = get_registry()
    return {
        "providers": _provider_summary(),
        "strategy": _strategy_response(),
        "health": await reg.provider_factory.health_check(),
    }


@router.get("/strategy")
def get_provider_strategy():
    """Return the current runtime provider strategy."""
    return {"strategy": _strategy_response()}


@router.patch("/strategy")
def update_provider_strategy(req: ProviderStrategyUpdate):
    """Update runtime provider strategy without editing config files."""
    try:
        _factory().update_strategy(
            active_provider=req.activeProvider,
            fallback_providers=req.fallbackProviders,
            parallel_query=req.parallelQuery,
            timeout_seconds=req.timeoutSeconds,
            retry_attempts=req.retryAttempts,
            retry_backoff_seconds=req.retryBackoffSeconds,
            debug_raw_response=req.debugRawResponse,
        )
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"strategy": _strategy_response()}


@router.post("/switch")
def switch_provider(req: ProviderSwitchRequest):
    """Switch the active provider at runtime."""
    try:
        _factory().update_strategy(active_provider=req.activeProvider)
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
    return {"strategy": _strategy_response()}


@router.get("/health")
async def get_provider_health():
    """Return normalized provider health state."""
    return {"health": await _factory().health_check()}
