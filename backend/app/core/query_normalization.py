"""Provider-aware query normalization for the memory core layer."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, cast

from app.core.memory_schema import MemoryQuery, QueryMode

_QUERY_MODES: tuple[QueryMode, ...] = ("hybrid", "semantic", "keyword")

_CAPABILITIES_BY_MODE: dict[QueryMode, set[str]] = {
    "keyword": {"keyword", "keyword_search", "keyword_query"},
    "semantic": {"semantic", "semantic_search", "vector_search", "embedding_search"},
    "hybrid": {"hybrid", "hybrid_search", "hybrid_query"},
}

_MODE_FALLBACKS: dict[QueryMode, tuple[QueryMode, ...]] = {
    "hybrid": ("hybrid", "semantic", "keyword"),
    "semantic": ("semantic", "hybrid", "keyword"),
    "keyword": ("keyword", "hybrid", "semantic"),
}


def _normalized_capabilities(provider: Any) -> set[str]:
    raw_capabilities = getattr(provider, "capabilities", set()) or set()
    return {
        str(capability).strip().lower().replace("-", "_")
        for capability in raw_capabilities
        if str(capability).strip()
    }


def provider_query_modes(provider: Any) -> set[QueryMode]:
    """Return query modes a provider can handle, inferred from capabilities."""
    capabilities = _normalized_capabilities(provider)
    modes: set[QueryMode] = set()

    if capabilities.intersection({"query", "search"}):
        modes.add("keyword")

    for mode, mode_capabilities in _CAPABILITIES_BY_MODE.items():
        if capabilities.intersection(mode_capabilities):
            modes.add(mode)

    return modes or {"keyword"}


def resolve_query_mode(requested_mode: QueryMode, supported_modes: set[QueryMode]) -> QueryMode:
    """Resolve a requested query mode to the best supported provider mode."""
    requested = requested_mode if requested_mode in _QUERY_MODES else "hybrid"
    for mode in _MODE_FALLBACKS[requested]:
        if mode in supported_modes:
            return mode
    return "keyword"


def normalize_query_for_provider(query: MemoryQuery, provider: Any) -> MemoryQuery:
    """Adapt a provider-neutral query to the provider's query capabilities."""
    supported_modes = provider_query_modes(provider)
    effective_mode = resolve_query_mode(cast(QueryMode, query.mode), supported_modes)
    if effective_mode == query.mode:
        return query
    return replace(query, mode=effective_mode)


def query_capability_summary(provider: Any) -> dict[str, Any]:
    """Return a stable capability summary for API and diagnostics surfaces."""
    modes = provider_query_modes(provider)
    capabilities = _normalized_capabilities(provider)
    return {
        "modes": sorted(modes),
        "capabilities": sorted(capabilities),
    }
