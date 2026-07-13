"""Provider-agnostic memory intelligence built on the unified schema."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from app.adapters.registry import get_registry
from app.core.memory_schema import MemoryItem, MemoryQuery

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

_NEGATIONS = {"not", "never", "no", "without", "avoid", "dislike", "don't", "doesn't", "isn't"}


async def load_unified_memories(
    *,
    provider: str = "",
    session_id: str = "",
    limit: int = 200,
) -> list[MemoryItem]:
    """Load memories from the unified provider layer and optional session filter."""
    registry = get_registry()
    query = MemoryQuery(query="", mode="keyword", limit=limit, include_raw=True)
    if provider:
        result = await registry.query_provider_memory(provider, query)
    else:
        result = await registry.query_all_memory(query)

    items = result.items
    if session_id:
        items = [item for item in items if item.metadata.session_id == session_id]
    return items[:limit]


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
        if token not in _STOPWORDS
    ]


def _raw(item: MemoryItem) -> dict[str, Any]:
    return item.metadata.raw if isinstance(item.metadata.raw, dict) else {}


def _title(item: MemoryItem) -> str:
    raw = _raw(item)
    title = raw.get("title")
    return str(title) if title else item.content[:80]


def _item_terms(item: MemoryItem) -> list[str]:
    raw = _raw(item)
    concepts = raw.get("concepts", [])
    concept_text = " ".join(str(concept) for concept in concepts) if isinstance(concepts, list) else ""
    tag_text = " ".join(item.metadata.tags)
    return _tokens(f"{_title(item)} {item.content} {concept_text} {tag_text}")


def _has_negation(text: str) -> bool:
    words = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_'’-]*", text.lower()))
    return bool(words.intersection(_NEGATIONS))


def _top_terms(items: list[MemoryItem], limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for item in items:
        counter.update(_item_terms(item))
    return [term for term, _ in counter.most_common(limit)]


def summarize_memories(items: list[MemoryItem]) -> dict[str, Any]:
    """Summarize a memory slice without provider-specific assumptions."""
    providers = sorted({item.metadata.source for item in items})
    sessions = sorted({item.metadata.session_id for item in items if item.metadata.session_id})
    tags = sorted({tag for item in items for tag in item.metadata.tags})
    keywords = _top_terms(items)
    leading = [item.content.strip().replace("\n", " ") for item in items[:3] if item.content.strip()]
    summary = " ".join(text[:180] for text in leading)
    if len(summary) > 420:
        summary = f"{summary[:417]}..."

    return {
        "summary": summary or "No memories available.",
        "memoryCount": len(items),
        "providers": providers,
        "sessionIds": sessions,
        "topTags": tags[:10],
        "keywords": keywords,
    }


def compress_memories(items: list[MemoryItem], max_chars: int = 800) -> dict[str, Any]:
    """Compress memories into a deduplicated text block."""
    seen: set[str] = set()
    chunks: list[str] = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item.content).strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        chunks.append(normalized)

    compressed = " ".join(chunks)
    if len(compressed) > max_chars:
        compressed = f"{compressed[: max_chars - 3].rstrip()}..."
    return {
        "compressed": compressed,
        "originalCount": len(items),
        "compressedCount": len(chunks),
        "maxChars": max_chars,
        "keywords": _top_terms(items),
    }


def cluster_memories(items: list[MemoryItem]) -> dict[str, Any]:
    """Group memories by their strongest provider-neutral topic signal."""
    grouped: dict[str, list[MemoryItem]] = defaultdict(list)
    for item in items:
        terms = _item_terms(item)
        key = item.metadata.tags[0] if item.metadata.tags else (terms[0] if terms else item.metadata.source)
        grouped[key].append(item)

    clusters = []
    for index, (key, members) in enumerate(sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0]))):
        cluster_members = [
            {
                "id": member.id,
                "provider": member.metadata.source,
                "title": _title(member),
                "content": member.content[:220],
            }
            for member in members
        ]
        clusters.append(
            {
                "id": f"cluster-{index}",
                "name": key.title(),
                "count": len(members),
                "memoryIds": [member.id for member in members],
                "members": cluster_members,
                "providers": sorted({member.metadata.source for member in members}),
                "keywords": _top_terms(members, limit=5),
            }
        )
    return {"clusters": clusters, "total": len(clusters), "memoryCount": len(items)}


def detect_contradictions(items: list[MemoryItem], limit: int = 20) -> dict[str, Any]:
    """Find simple contradiction candidates from unified memory content."""
    candidates = []
    term_sets = [set(_item_terms(item)) for item in items]
    negated = [_has_negation(item.content) for item in items]

    for left_idx, left in enumerate(items):
        for right_idx in range(left_idx + 1, len(items)):
            shared = term_sets[left_idx].intersection(term_sets[right_idx])
            if len(shared) < 2 or negated[left_idx] == negated[right_idx]:
                continue
            right = items[right_idx]
            candidates.append(
                {
                    "id": f"contradiction-{left.id}-{right.id}",
                    "memoryA": {
                        "id": left.id,
                        "title": _title(left),
                        "content": left.content[:220],
                        "provider": left.metadata.source,
                    },
                    "memoryB": {
                        "id": right.id,
                        "title": _title(right),
                        "content": right.content[:220],
                        "provider": right.metadata.source,
                    },
                    "sharedTerms": sorted(shared)[:8],
                    "severity": "medium" if len(shared) >= 4 else "low",
                }
            )
            if len(candidates) >= limit:
                return {"contradictions": candidates, "total": len(candidates)}

    return {"contradictions": candidates, "total": len(candidates)}
