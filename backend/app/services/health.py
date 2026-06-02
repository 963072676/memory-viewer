"""Memory health scoring service (F-20).

Scoring formula (each dimension 0-100):
  - strength_score (40%): strength / 10 * 100
  - age_score (30%): max(0, 100 - days_since_created / 30 * 100)
  - concepts_score (15%): min(len(concepts) / 5, 1) * 100
  - recommendation_score (15%): min(recommendation_count / 3, 1) * 100

Color: green (>70), yellow (40-70), red (<40)
"""

from datetime import datetime, timezone
from typing import Optional

from app.services.agentmemory import get_all_memories


def _days_since(date_str: str) -> int:
    """Parse ISO date and return days since then."""
    if not date_str:
        return 0
    try:
        dt_str = date_str.replace("Z", "+00:00")
        created = datetime.fromisoformat(dt_str)
        now = datetime.now(timezone.utc)
        return max(0, (now - created).days)
    except (ValueError, TypeError):
        return 0


def _count_recommendations(memory_id: str) -> int:
    """Count how many other memories share concepts with this one.

    This is a lightweight proxy for 'how often this memory would be recommended'.
    """
    from app.services.recommendation import compute_recommendations
    recs = compute_recommendations(memory_id, limit=100)
    return len(recs.get("recommendations", []))


def compute_health(memory: dict, recommendation_count: Optional[int] = None) -> dict:
    """Compute health score for a memory.

    Args:
        memory: memory dict
        recommendation_count: pre-computed count (avoids recomputation)
    """
    strength = memory.get("strength", 5)
    concepts = memory.get("concepts", [])
    created_at = memory.get("createdAt") or memory.get("updatedAt") or ""
    days = _days_since(created_at)

    # Dimension scores (0-100)
    strength_score = min(100, max(0, (strength / 10) * 100))
    age_score = max(0, 100 - (days / 30) * 100)
    concepts_score = min(100, (len(concepts) / 5) * 100)

    if recommendation_count is None:
        rec_count = _count_recommendations(memory.get("id", ""))
    else:
        rec_count = recommendation_count
    recommendation_score = min(100, (rec_count / 3) * 100)

    # Weighted total
    total = (
        strength_score * 0.40
        + age_score * 0.30
        + concepts_score * 0.15
        + recommendation_score * 0.15
    )

    # Color
    if total > 70:
        color = "green"
    elif total >= 40:
        color = "yellow"
    else:
        color = "red"

    # Decay linkage (days until strength zero)
    decay_rate = strength / 90.0 if strength > 0 else 0
    current_strength = max(0, strength - decay_rate * days)
    days_until_zero = int(current_strength / decay_rate) if decay_rate > 0 else None

    return {
        "memory_id": memory.get("id", ""),
        "health_score": round(total),
        "color": color,
        "breakdown": {
            "strength_score": round(strength_score),
            "age_score": round(age_score),
            "concepts_score": round(concepts_score),
            "recommendation_score": round(recommendation_score),
        },
        "days_since_created": days,
        "days_until_strength_zero": days_until_zero,
    }
