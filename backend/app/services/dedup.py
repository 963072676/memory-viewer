"""Dedup service (F-21): Jaccard (concepts) + Levenshtein (title) similarity.

Combined similarity = concepts_jaccard * 0.6 + title_similarity * 0.4
Threshold default: 0.7
"""

from typing import Optional

from app.services.agentmemory import get_all_memories, _read_json_cache, _atomic_write_json, _audit_log
from app.config import settings


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _levenshtein(s: str, t: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if s == t:
        return 0
    if not s:
        return len(t)
    if not t:
        return len(s)

    # Optimize: use two rows instead of full matrix
    prev = list(range(len(t) + 1))
    curr = [0] * (len(t) + 1)

    for i in range(1, len(s) + 1):
        curr[0] = i
        for j in range(1, len(t) + 1):
            cost = 0 if s[i - 1] == t[j - 1] else 1
            curr[j] = min(
                curr[j - 1] + 1,      # insertion
                prev[j] + 1,           # deletion
                prev[j - 1] + cost,    # substitution
            )
        prev, curr = curr, prev

    return prev[len(t)]


def _title_similarity(a: str, b: str) -> float:
    """1 - edit_distance / max(len(a), len(b))."""
    if not a and not b:
        return 1.0
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    dist = _levenshtein(a.lower(), b.lower())
    return 1.0 - dist / max_len


def find_duplicates(threshold: float = 0.7) -> dict:
    """Find duplicate memory pairs.

    Returns pairs with combined similarity > threshold.
    """
    memories = get_all_memories()
    # Only non-archived
    active = [m for m in memories if not m.get("archived", False)]

    pairs = []
    n = len(active)
    for i in range(n):
        for j in range(i + 1, n):
            a = active[i]
            b = active[j]

            concepts_a = set(a.get("concepts", []))
            concepts_b = set(b.get("concepts", []))
            c_sim = _jaccard(concepts_a, concepts_b)

            t_sim = _title_similarity(a.get("title", ""), b.get("title", ""))

            combined = c_sim * 0.6 + t_sim * 0.4

            if combined >= threshold:
                shared = sorted(concepts_a & concepts_b)
                pairs.append({
                    "memory_a": a,
                    "memory_b": b,
                    "similarity": round(combined, 4),
                    "concepts_similarity": round(c_sim, 4),
                    "title_similarity": round(t_sim, 4),
                    "shared_concepts": shared,
                })

    # Sort by similarity descending
    pairs.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "pairs": pairs,
        "total_pairs": len(pairs),
    }


def merge_memories(keep_id: str, merge_id: str) -> dict:
    """Merge two memories: keep the one with higher strength, merge concepts.

    The kept memory gets merged concepts (deduped) and combined content note.
    The merged memory is deleted.
    """
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])

    keep_mem = None
    merge_mem = None
    for m in memories:
        if m.get("id") == keep_id:
            keep_mem = m
        if m.get("id") == merge_id:
            merge_mem = m

    if not keep_mem or not merge_mem:
        return {"success": False, "error": "One or both memories not found"}

    # Determine which to keep (higher strength)
    if merge_mem.get("strength", 0) > keep_mem.get("strength", 0):
        keep_mem, merge_mem = merge_mem, keep_mem
        keep_id, merge_id = merge_id, keep_id

    # Merge concepts (deduplicate)
    existing_concepts = set(keep_mem.get("concepts", []))
    new_concepts = set(merge_mem.get("concepts", []))
    merged_concepts = sorted(existing_concepts | new_concepts)
    keep_mem["concepts"] = merged_concepts

    # Append merged content
    merge_content = merge_mem.get("content", "")
    if merge_content and merge_content not in keep_mem.get("content", ""):
        keep_mem["content"] = keep_mem.get("content", "") + "\n\n[Merged]\n" + merge_content

    # Remove merged memory
    data["memories"] = [m for m in memories if m.get("id") != merge_id]

    # Update keep memory in data
    for m in data["memories"]:
        if m.get("id") == keep_id:
            m.update(keep_mem)
            break

    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)
    _audit_log("merge", keep_id, details={"merged_id": merge_id})

    return {"success": True, "merged_memory": keep_mem}
