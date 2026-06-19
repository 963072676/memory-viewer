"""Service layer for provider-neutral cross-source search."""

from __future__ import annotations

import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from app.adapters.registry import get_registry
from app.core.memory_schema import MemoryItem, MemoryQuery, QueryMode


def _highlight_text(text: str, query: str, context_len: int = 100) -> str:
    """Create a snippet with <em> tags around matched query terms."""
    if not query:
        return text[:context_len] + ("..." if len(text) > context_len else "")

    lower_text = text.lower()
    lower_query = query.lower()
    idx = lower_text.find(lower_query)
    if idx == -1:
        return text[:context_len] + ("..." if len(text) > context_len else "")

    start = max(0, idx - context_len // 2)
    end = min(len(text), idx + len(query) + context_len // 2)
    snippet = text[start:end]

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    snippet = pattern.sub(lambda m: f"<em>{m.group()}</em>", snippet)

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet


def _raw_item(item: MemoryItem) -> dict:
    raw = item.metadata.raw
    return raw if isinstance(raw, dict) else {}


def _raw_metadata(item: MemoryItem) -> dict:
    raw = _raw_item(item)
    metadata = raw.get("metadata", {})
    return metadata if isinstance(metadata, dict) else {}


def _result_type(item: MemoryItem) -> str | None:
    raw = _raw_item(item)
    value = raw.get("type")
    return str(value) if value is not None else None


def _result_strength(item: MemoryItem) -> float | None:
    raw = _raw_item(item)
    value = raw.get("strength")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _result_updated_at(item: MemoryItem) -> str:
    raw = _raw_item(item)
    updated_at = raw.get("updatedAt") or raw.get("updated_at")
    return str(updated_at) if updated_at is not None else ""


def _result_concepts(item: MemoryItem) -> list[str]:
    raw = _raw_item(item)
    concepts = raw.get("concepts", [])
    return concepts if isinstance(concepts, list) else []


def _matches_filters(
    item: MemoryItem,
    *,
    type_filter: Optional[list[str]],
    profile_filter: Optional[str],
    strength_min: Optional[int],
    strength_max: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str],
) -> bool:
    metadata = _raw_metadata(item)

    if type_filter:
        item_type = _result_type(item)
        if item_type is not None and item_type not in type_filter:
            return False

    if profile_filter:
        profile = metadata.get("profile")
        if profile is not None and profile != profile_filter:
            return False
        if profile is None and item.metadata.source == "hermes":
            return False

    strength = _result_strength(item)
    if strength_min is not None and strength is not None and strength < strength_min:
        return False
    if strength_max is not None and strength is not None and strength > strength_max:
        return False

    updated_at = _result_updated_at(item)
    if date_from and updated_at and updated_at[:10] < date_from:
        return False
    if date_to and updated_at and updated_at[:10] > date_to:
        return False

    return True


def _match_field(item: MemoryItem, query: str, pure_filter_mode: bool) -> tuple[str, str]:
    raw = _raw_item(item)
    if pure_filter_mode:
        return "filter", item.content

    query_lower = query.lower()
    title = str(raw.get("title", ""))
    concepts = _result_concepts(item)

    if title and query_lower in title.lower():
        return "title", title
    if any(query_lower in str(concept).lower() for concept in concepts):
        return "concepts", ", ".join(str(concept) for concept in concepts)
    return "content", item.content


def _to_legacy_search_result(item: MemoryItem, query: str, pure_filter_mode: bool) -> dict:
    raw = _raw_item(item)
    metadata = _raw_metadata(item)
    match_field, match_text = _match_field(item, query, pure_filter_mode)

    result = {
        "source": item.metadata.source,
        "id": item.id,
        "content": item.content,
        "matchField": match_field,
        "matchSnippet": match_text[:100] if pure_filter_mode else _highlight_text(match_text, query),
    }

    for key in ("type", "title", "strength"):
        if key in raw:
            result[key] = raw[key]

    concepts = _result_concepts(item)
    if concepts:
        result["concepts"] = concepts

    updated_at = _result_updated_at(item)
    if updated_at:
        result["updatedAt"] = updated_at

    for key in ("profile", "file", "index"):
        if key in metadata:
            result[key] = metadata[key]

    return result


async def search_memories_async(
    query: str = "",
    mode: QueryMode = "keyword",
    source: Optional[str] = None,
    type_filter: Optional[list[str]] = None,
    profile_filter: Optional[str] = None,
    strength_min: Optional[int] = None,
    strength_max: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Search memories through the unified provider query layer."""
    reg = get_registry()
    query_limit = max(limit + offset, 1000)
    memory_query = MemoryQuery(query=query, mode=mode, limit=query_limit, include_raw=True)

    if source and source != "all":
        if reg.get(source) is None:
            return {"query": query, "total": 0, "limit": limit, "offset": offset, "results": []}
        result = await reg.query_provider_memory(source, memory_query)
    else:
        result = await reg.query_all_memory(memory_query)

    pure_filter_mode = not query
    filtered = [
        item
        for item in result.items
        if _matches_filters(
            item,
            type_filter=type_filter,
            profile_filter=profile_filter,
            strength_min=strength_min,
            strength_max=strength_max,
            date_from=date_from,
            date_to=date_to,
        )
    ]

    legacy_results = [
        _to_legacy_search_result(item, query, pure_filter_mode)
        for item in filtered
    ]

    total = len(legacy_results)
    paginated = legacy_results[offset : offset + limit]
    return {
        "query": query,
        "mode": mode,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": paginated,
    }


def search_memories(
    query: str = "",
    mode: QueryMode = "keyword",
    source: Optional[str] = None,
    type_filter: Optional[list[str]] = None,
    profile_filter: Optional[str] = None,
    strength_min: Optional[int] = None,
    strength_max: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Synchronous compatibility wrapper for MCP and legacy routers."""
    coroutine_kwargs = {
        "query": query,
        "mode": mode,
        "source": source,
        "type_filter": type_filter,
        "profile_filter": profile_filter,
        "strength_min": strength_min,
        "strength_max": strength_max,
        "date_from": date_from,
        "date_to": date_to,
        "limit": limit,
        "offset": offset,
    }

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(search_memories_async(**coroutine_kwargs))

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(
            lambda: asyncio.run(search_memories_async(**coroutine_kwargs))
        ).result()
