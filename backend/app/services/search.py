"""Service layer for cross-source search."""

import re
from typing import Optional

from app.services.agentmemory import get_all_memories
from app.services.hermes_memory import get_hermes_memory


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

    # Highlight matches
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    snippet = pattern.sub(lambda m: f"<em>{m.group()}</em>", snippet)

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet


def search_memories(
    query: str = "",
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
    """Search across all memory sources. Supports empty query for pure filter mode (F-07)."""
    results = []
    query_lower = query.lower() if query else ""
    pure_filter_mode = not query_lower  # No keyword, just filters

    # Search agentmemory
    if source in (None, "all", "agentmemory"):
        memories = get_all_memories()
        for m in memories:
            # Type filter (supports multiple types)
            if type_filter and m.get("type") not in type_filter:
                continue
            if strength_min is not None and m.get("strength", 0) < strength_min:
                continue
            if strength_max is not None and m.get("strength", 0) > strength_max:
                continue
            if date_from and m.get("updatedAt", "")[:10] < date_from:
                continue
            if date_to and m.get("updatedAt", "")[:10] > date_to:
                continue

            if pure_filter_mode:
                # Pure filter mode: include all that pass filters
                results.append({
                    "source": "agentmemory",
                    "id": m.get("id"),
                    "type": m.get("type"),
                    "title": m.get("title"),
                    "content": m.get("content"),
                    "concepts": m.get("concepts", []),
                    "strength": m.get("strength"),
                    "updatedAt": m.get("updatedAt"),
                    "matchField": "filter",
                    "matchSnippet": m.get("content", "")[:100],
                })
            else:
                # Keyword search mode
                title_match = query_lower in m.get("title", "").lower()
                content_match = query_lower in m.get("content", "").lower()
                concepts_match = any(query_lower in c.lower() for c in m.get("concepts", []))

                if title_match or content_match or concepts_match:
                    match_field = "title" if title_match else ("concepts" if concepts_match else "content")
                    match_text = m.get(match_field, m.get("content", ""))
                    if match_field == "concepts":
                        match_text = ", ".join(m.get("concepts", []))
                    results.append({
                        "source": "agentmemory",
                        "id": m.get("id"),
                        "type": m.get("type"),
                        "title": m.get("title"),
                        "content": m.get("content"),
                        "concepts": m.get("concepts", []),
                        "strength": m.get("strength"),
                        "updatedAt": m.get("updatedAt"),
                        "matchField": match_field,
                        "matchSnippet": _highlight_text(match_text, query),
                    })

    # Search hermes memory
    if source in (None, "all", "hermes"):
        hermes = get_hermes_memory()

        def search_entries(entries: list[str], profile: str, file_name: str):
            for i, entry in enumerate(entries):
                if pure_filter_mode:
                    results.append({
                        "source": "hermes",
                        "profile": profile,
                        "file": file_name,
                        "index": i,
                        "content": entry,
                        "matchField": "filter",
                        "matchSnippet": entry[:100],
                    })
                elif query_lower in entry.lower():
                    results.append({
                        "source": "hermes",
                        "profile": profile,
                        "file": file_name,
                        "index": i,
                        "content": entry,
                        "matchField": "content",
                        "matchSnippet": _highlight_text(entry, query),
                    })

        if not profile_filter or profile_filter == "global":
            search_entries(hermes["global"]["memory"], "global", "MEMORY.md")
            search_entries(hermes["global"]["user"], "global", "USER.md")

        for profile_name, profile_data in hermes.get("profiles", {}).items():
            if profile_filter and profile_filter != "global" and profile_filter != profile_name:
                continue
            search_entries(profile_data.get("memory", []), profile_name, "MEMORY.md")
            search_entries(profile_data.get("user", []), profile_name, "USER.md")

    total = len(results)
    paginated = results[offset : offset + limit]
    return {"query": query, "total": total, "limit": limit, "offset": offset, "results": paginated}
