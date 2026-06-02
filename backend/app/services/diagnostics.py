"""Memory system diagnostics service (F-28)."""

from collections import Counter
from typing import Optional

from app.services.agentmemory import get_all_memories


def _jaccard(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def run_diagnostics() -> dict:
    """
    Run full memory system diagnostics.
    Returns:
        {
            "total_memories": int,
            "duplicates": [...],         # pairs with Jaccard(concepts) > 0.6
            "orphaned_concepts": [...],   # concepts appearing < 2 times
            "strength_anomalies": [...],  # memories with strength < 1 or > 9
        }
    """
    memories = get_all_memories()
    total = len(memories)

    # --- Duplicate detection (Jaccard > 0.6 on concepts) ---
    duplicates = []
    for i in range(len(memories)):
        concepts_i = set(memories[i].get("concepts", []))
        if not concepts_i:
            continue
        for j in range(i + 1, len(memories)):
            concepts_j = set(memories[j].get("concepts", []))
            if not concepts_j:
                continue
            sim = _jaccard(concepts_i, concepts_j)
            if sim > 0.6:
                duplicates.append({
                    "memory_a_id": memories[i].get("id", ""),
                    "memory_a_title": memories[i].get("title", ""),
                    "memory_b_id": memories[j].get("id", ""),
                    "memory_b_title": memories[j].get("title", ""),
                    "jaccard_similarity": round(sim, 3),
                })

    # --- Orphaned concepts (appearing < 2 times) ---
    concept_counts: Counter = Counter()
    for m in memories:
        for c in m.get("concepts", []):
            concept_counts[c] += 1
    orphaned_concepts = [
        {"concept": c, "count": count}
        for c, count in concept_counts.items()
        if count < 2
    ]

    # --- Strength anomalies (< 1 or > 9) ---
    strength_anomalies = []
    for m in memories:
        s = m.get("strength", 5)
        if s < 1 or s > 9:
            strength_anomalies.append({
                "id": m.get("id", ""),
                "title": m.get("title", ""),
                "strength": s,
            })

    return {
        "total_memories": total,
        "duplicates": duplicates,
        "orphaned_concepts": orphaned_concepts,
        "strength_anomalies": strength_anomalies,
    }
