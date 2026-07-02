"""Provider-neutral memory graph service.

Nodes are unified memory items. Edges are lightweight semantic relations built
from provider-neutral signals: concepts, tags, and extracted keywords.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from app.core.memory_schema import MemoryItem
from app.services.intelligence import load_unified_memories

_ALLOWED_TYPES = {"pattern", "fact", "preference", "bug", "workflow", "architecture"}
_STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "but",
    "for",
    "from",
    "has",
    "have",
    "into",
    "not",
    "that",
    "the",
    "this",
    "with",
    "you",
    "your",
}


def _raw(item: MemoryItem) -> dict[str, Any]:
    return item.metadata.raw if isinstance(item.metadata.raw, dict) else {}


def _title(item: MemoryItem) -> str:
    raw = _raw(item)
    title = raw.get("title")
    if title:
        return str(title)
    content = re.sub(r"\s+", " ", item.content).strip()
    return content[:80] or item.id


def _memory_type(item: MemoryItem) -> str:
    value = str(_raw(item).get("type", "")).lower()
    return value if value in _ALLOWED_TYPES else item.metadata.source


def _strength(item: MemoryItem) -> int:
    try:
        value = int(float(_raw(item).get("strength", 5)))
    except (TypeError, ValueError):
        value = 5
    return max(1, min(10, value))


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
        if token not in _STOPWORDS
    ]


def _concepts(item: MemoryItem) -> list[str]:
    raw_concepts = _raw(item).get("concepts", [])
    if not isinstance(raw_concepts, list):
        return []
    return [str(concept).strip().lower() for concept in raw_concepts if str(concept).strip()]


def _signals(item: MemoryItem) -> set[str]:
    concepts = set(_concepts(item))
    tags = {str(tag).strip().lower() for tag in item.metadata.tags if str(tag).strip()}
    text_terms = set(_tokenize(f"{_title(item)} {item.content}"))
    return concepts.union(tags).union(text_terms)


def build_graph_from_items(items: list[MemoryItem]) -> dict[str, Any]:
    """Build a graph response from unified memory items."""
    active_items = [item for item in items if not bool(_raw(item).get("archived", False))]

    # Detect duplicate titles and disambiguate with content prefix
    title_counts: dict[str, int] = {}
    for item in active_items:
        t = _title(item)
        title_counts[t] = title_counts.get(t, 0) + 1

    def _unique_label(item: MemoryItem) -> str:
        t = _title(item)
        if title_counts.get(t, 0) <= 1:
            return t
        # Disambiguate: use first meaningful line of content
        lines = [l.strip() for l in item.content.split('\n') if l.strip() and not l.strip().startswith('§')]
        snippet = lines[0][:40] if lines else item.id
        return f"{t[:20]}… {snippet}" if len(t) > 20 else f"{t} · {snippet}"

    nodes = [
        {
            "id": item.id,
            "label": _unique_label(item),
            "type": _memory_type(item),
            "strength": _strength(item),
            "size": max(8, _strength(item) * 3),
            "provider": item.metadata.source,
            "sessionId": item.metadata.session_id,
            "tags": item.metadata.tags,
            "contentSnippet": re.sub(r"\s+", " ", item.content).strip()[:180],
        }
        for item in active_items
    ]

    signal_index: dict[str, list[int]] = defaultdict(list)
    for index, item in enumerate(active_items):
        for signal in _signals(item):
            signal_index[signal].append(index)

    edge_map: dict[tuple[int, int], set[str]] = defaultdict(set)
    for signal, indices in signal_index.items():
        unique_indices = sorted(set(indices))
        for left_pos, left_idx in enumerate(unique_indices):
            for right_idx in unique_indices[left_pos + 1 :]:
                edge_map[(left_idx, right_idx)].add(signal)

    edges = []
    max_weight = 0
    for (left_idx, right_idx), shared in sorted(edge_map.items()):
        shared_terms = sorted(shared)
        weight = len(shared_terms)
        max_weight = max(max_weight, weight)
        edges.append(
            {
                "source": active_items[left_idx].id,
                "target": active_items[right_idx].id,
                "weight": weight,
                "shared_concepts": shared_terms[:8],
                "relation_type": "semantic",
            }
        )

    providers = sorted({item.metadata.source for item in active_items})
    return {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "max_weight": max_weight,
            "providers": providers,
        },
    }


async def build_graph(provider: str = "", session_id: str = "", limit: int = 200) -> dict[str, Any]:
    """Load unified memories and build a provider-neutral relation graph."""
    items = await load_unified_memories(provider=provider, session_id=session_id, limit=limit)
    return build_graph_from_items(items)
