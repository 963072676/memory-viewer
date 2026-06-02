"""Decay service (F-22): linear strength decay model."""

from datetime import datetime, timezone, timedelta
from typing import Optional


def compute_decay(memory: dict) -> dict:
    """Compute decay info for a single memory.

    Linear decay model: strength decreases by decay_rate per day.
    decay_rate = initial_strength / 90 (90 days to decay to 0).
    """
    initial_strength = memory.get("strength", 5)
    created_at_str = memory.get("createdAt") or memory.get("updatedAt") or ""

    # Parse created date
    days_since_created = 0
    if created_at_str:
        try:
            # Handle ISO format with Z suffix
            dt_str = created_at_str.replace("Z", "+00:00")
            created_at = datetime.fromisoformat(dt_str)
            now = datetime.now(timezone.utc)
            days_since_created = max(0, (now - created_at).days)
        except (ValueError, TypeError):
            days_since_created = 0

    # Linear decay: assume 90 days to reach 0
    if initial_strength <= 0:
        decay_rate = 0.0
        current_strength = 0.0
        days_until_zero = 0
    else:
        decay_rate = initial_strength / 90.0
        current_strength = max(0.0, initial_strength - decay_rate * days_since_created)
        if decay_rate > 0:
            days_until_zero = max(0, int(current_strength / decay_rate))
        else:
            days_until_zero = 0

    # Predicted zero date
    now = datetime.now(timezone.utc)
    predicted_zero_date = None
    if days_until_zero > 0:
        predicted_zero_date = (now + timedelta(days=days_until_zero)).strftime("%Y-%m-%d")
    elif initial_strength > 0 and current_strength <= 0:
        predicted_zero_date = now.strftime("%Y-%m-%d")

    # Generate decay curve data points (up to 365 points max)
    total_days = days_since_created + days_until_zero
    num_points = min(max(total_days + 1, 2), 365)

    # If total_days is very large, sample evenly
    if total_days > 365:
        step = total_days / 364
        days_list = [int(i * step) for i in range(365)]
    else:
        days_list = list(range(num_points))

    decay_curve = []
    for day in days_list:
        s = max(0.0, initial_strength - decay_rate * day)
        decay_curve.append({"day": day, "strength": round(s, 2)})

    return {
        "memory_id": memory.get("id", ""),
        "current_strength": round(current_strength, 2),
        "initial_strength": initial_strength,
        "decay_rate": round(decay_rate, 4),
        "days_since_created": days_since_created,
        "predicted_zero_date": predicted_zero_date,
        "decay_curve": decay_curve,
    }
