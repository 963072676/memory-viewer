"""Recommendation service (F-19): Jaccard similarity + strength weighted scoring.

score = jaccard * 0.7 + (strength / 10) * 0.3
Filters: exclude self, exclude archived, exclude empty-concepts.
"""

from typing import Optional

from app.services.agentmemory import get_all_memories


def _jaccard(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def compute_recommendations(memory_id: str, limit: int = 5) -> dict:
    """Compute top-N recommended memories for the given memory."""
    all_memories = get_all_memories()

    # Find the target memory
    target = None
    for m in all_memories:
        if m.get("id") == memory_id:
            target = m
            break

    if not target:
        return {"memory_id": memory_id, "recommendations": []}

    target_concepts = set(target.get("concepts", []))

    # If target has no concepts, return empty
    if not target_concepts:
        return {"memory_id": memory_id, "recommendations": []}

    scored = []
    for m in all_memories:
        mid = m.get("id", "")
        # Skip self
        if mid == memory_id:
            continue
        # Skip archived
        if m.get("archived", False):
            continue
        # Skip empty concepts
        m_concepts = set(m.get("concepts", []))
        if not m_concepts:
            continue

        jaccard = _jaccard(target_concepts, m_concepts)
        strength = m.get("strength", 5)
        score = jaccard * 0.7 + (strength / 10) * 0.3

        shared = list(target_concepts & m_concepts)

        scored.append({
            "memory": m,
            "score": round(score, 4),
            "shared_concepts": sorted(shared),
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "memory_id": memory_id,
        "recommendations": scored[:limit],
    }
