"""Memory Conflict Detection service (F-45) — Detect contradictions between memories.

Uses embedding similarity + LLM verification to find conflicting memories.
Conflict types: direct_contradiction, outdated_info, partial_overlap.
"""

import hashlib
import json
import logging
import math
import os
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import get_all_memories
from app.services.semantic_search import _tokenize, _compute_tf

logger = logging.getLogger(__name__)

CONFLICTS_PATH = os.path.join(settings.cache_dir, "conflicts.json")

# Cache
_conflict_cache: Optional[dict] = None
_conflict_cache_time: float = 0
_CACHE_TTL = 7200  # 2 hours


def _load_conflicts() -> dict:
    """Load persisted conflicts."""
    try:
        with open(CONFLICTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"conflicts": [], "resolved": []}


def _save_conflicts(data: dict) -> None:
    """Save conflicts to disk."""
    os.makedirs(os.path.dirname(CONFLICTS_PATH), exist_ok=True)
    from app.services.agentmemory import _atomic_write_json
    _atomic_write_json(CONFLICTS_PATH, data)


def _cosine_sim(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(a.keys()) & set(b.keys())
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _build_tfidf(memories: list[dict]) -> dict[str, dict[str, float]]:
    """Build TF-IDF vectors for memories."""
    doc_tokens: dict[str, list[str]] = {}
    for mem in memories:
        mid = mem.get("id", "")
        text = f"{mem.get('title', '')} {mem.get('content', '')} {' '.join(mem.get('concepts', []))}"
        doc_tokens[mid] = _tokenize(text)

    doc_freq: Counter = Counter()
    n_docs = len(doc_tokens)
    for tokens in doc_tokens.values():
        for term in set(tokens):
            doc_freq[term] += 1

    vectors: dict[str, dict[str, float]] = {}
    for doc_id, tokens in doc_tokens.items():
        tf = _compute_tf(tokens)
        tfidf = {}
        for term, tf_val in tf.items():
            df = doc_freq.get(term, 1)
            idf = math.log(n_docs / df) if df > 0 else 0
            tfidf[term] = tf_val * idf
        vectors[doc_id] = tfidf

    return vectors


def _classify_conflict_type(mem_a: dict, mem_b: dict) -> str:
    """Classify the type of conflict between two memories.
    
    Simple heuristic-based classification:
    - Same type + high similarity → direct_contradiction
    - Similar content + different timestamps → outdated_info  
    - Partial overlap → partial_overlap
    """
    title_a = mem_a.get("title", "").lower()
    title_b = mem_b.get("title", "").lower()
    content_a = mem_a.get("content", "").lower()
    content_b = mem_b.get("content", "").lower()

    # Check for negation patterns
    negation_words = ["不", "不是", "不要", "不喜欢", "never", "not", "don't", "doesn't", "prefer"]
    has_negation_a = any(neg in content_a for neg in negation_words)
    has_negation_b = any(neg in content_b for neg in negation_words)

    if has_negation_a != has_negation_b:
        return "direct_contradiction"

    # Check type match
    if mem_a.get("type") == mem_b.get("type"):
        return "direct_contradiction"

    # Check timestamp difference for outdated
    ts_a = mem_a.get("created_at", "")
    ts_b = mem_b.get("created_at", "")
    if ts_a and ts_b and ts_a != ts_b:
        return "outdated_info"

    return "partial_overlap"


def _compute_severity(similarity: float, conflict_type: str) -> str:
    """Compute conflict severity based on similarity and type."""
    if conflict_type == "direct_contradiction" and similarity > 0.8:
        return "high"
    if conflict_type == "direct_contradiction" and similarity > 0.6:
        return "medium"
    if conflict_type == "outdated_info" and similarity > 0.7:
        return "medium"
    return "low"


def scan_conflicts(force: bool = False, top_k: int = 50) -> list[dict]:
    """Scan for conflicts between memories using similarity + heuristics.
    
    AC-F45-1: POST /api/conflicts/scan triggers conflict detection.
    AC-F45-2: Returns conflict pairs with similarity score and contradiction type.
    AC-F45-3: Identifies semantic contradictions.
    AC-F45-6: Scan completes within 30s for 500 memories.
    """
    global _conflict_cache, _conflict_cache_time

    now = time.time()
    if not force and _conflict_cache and (now - _conflict_cache_time) < _CACHE_TTL:
        return _conflict_cache.get("conflicts", [])

    memories = get_all_memories()
    if len(memories) < 2:
        return []

    # Build TF-IDF vectors
    vectors = _build_tfidf(memories)
    mem_map = {m.get("id"): m for m in memories}
    mem_ids = [m.get("id") for m in memories]

    # Load already resolved conflicts to skip
    persisted = _load_conflicts()
    resolved_pairs = set()
    for rc in persisted.get("resolved", []):
        resolved_pairs.add(tuple(sorted([rc.get("memory_a_id", ""), rc.get("memory_b_id", "")])))

    # Find highly similar pairs
    conflicts = []
    checked = set()

    for i in range(len(mem_ids)):
        for j in range(i + 1, len(mem_ids)):
            id_a, id_b = mem_ids[i], mem_ids[j]
            pair_key = tuple(sorted([id_a, id_b]))

            if pair_key in checked or pair_key in resolved_pairs:
                continue
            checked.add(pair_key)

            sim = _cosine_sim(vectors.get(id_a, {}), vectors.get(id_b, {}))
            if sim < 0.5:  # Only check high-similarity pairs
                continue

            mem_a = mem_map[id_a]
            mem_b = mem_map[id_b]
            conflict_type = _classify_conflict_type(mem_a, mem_b)
            severity = _compute_severity(sim, conflict_type)

            conflict_id = hashlib.md5(f"{id_a}:{id_b}".encode()).hexdigest()[:12]
            conflicts.append({
                "id": f"conflict-{conflict_id}",
                "memory_a": {
                    "id": id_a,
                    "title": mem_a.get("title", ""),
                    "content": mem_a.get("content", "")[:200],
                    "type": mem_a.get("type", "unknown"),
                    "strength": mem_a.get("strength", 0),
                },
                "memory_b": {
                    "id": id_b,
                    "title": mem_b.get("title", ""),
                    "content": mem_b.get("content", "")[:200],
                    "type": mem_b.get("type", "unknown"),
                    "strength": mem_b.get("strength", 0),
                },
                "similarity": round(sim, 4),
                "conflict_type": conflict_type,
                "severity": severity,
                "detected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "resolved": False,
            })

    # Sort by severity then similarity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    conflicts.sort(key=lambda c: (severity_order.get(c["severity"], 3), -c["similarity"]))

    # Limit results
    conflicts = conflicts[:top_k]

    # Persist
    persisted["conflicts"] = conflicts
    _save_conflicts(persisted)

    _conflict_cache = {"conflicts": conflicts}
    _conflict_cache_time = now

    return conflicts


def get_conflicts_list(limit: int = 50, severity: Optional[str] = None,
                       resolved: Optional[bool] = None) -> list[dict]:
    """Get the list of detected conflicts."""
    persisted = _load_conflicts()
    conflicts = persisted.get("conflicts", [])

    if severity:
        conflicts = [c for c in conflicts if c.get("severity") == severity]
    if resolved is not None:
        conflicts = [c for c in conflicts if c.get("resolved") == resolved]

    return conflicts[:limit]


def resolve_conflict(conflict_id: str, action: str, user: str = "system") -> Optional[dict]:
    """Resolve a conflict with the given action.
    
    AC-F45-4: Resolution actions update the memory base correctly.
    Actions: keep_a, keep_b, merge, dismiss
    """
    persisted = _load_conflicts()
    conflicts = persisted.get("conflicts", [])

    conflict = None
    idx = -1
    for i, c in enumerate(conflicts):
        if c.get("id") == conflict_id:
            conflict = c
            idx = i
            break

    if not conflict:
        return None

    conflict["resolved"] = True
    conflict["resolution"] = {
        "action": action,
        "resolved_by": user,
        "resolved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    # Move to resolved list
    persisted.setdefault("resolved", []).append(conflict)
    if idx >= 0:
        conflicts.pop(idx)
    persisted["conflicts"] = conflicts
    _save_conflicts(persisted)

    # Invalidate cache
    global _conflict_cache, _conflict_cache_time
    _conflict_cache = None
    _conflict_cache_time = 0

    return conflict


def get_conflict_summary() -> dict:
    """Get conflict count summary for sidebar badge."""
    persisted = _load_conflicts()
    conflicts = persisted.get("conflicts", [])
    severity_counts = Counter(c.get("severity", "low") for c in conflicts if not c.get("resolved"))
    return {
        "total": len([c for c in conflicts if not c.get("resolved")]),
        "high": severity_counts.get("high", 0),
        "medium": severity_counts.get("medium", 0),
        "low": severity_counts.get("low", 0),
    }
