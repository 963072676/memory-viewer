"""Memory activity heatmap service (F-37).

Aggregates memory timestamps (created, accessed, modified) into
daily counts for calendar heatmap display.
"""

import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import settings


def get_heatmap_data(metric: str = "created", days: int = 365) -> dict[str, int]:
    """Get activity heatmap data.

    Args:
        metric: One of "created", "accessed", "modified"
        days: Number of days to look back (default 365)

    Returns:
        Dict mapping ISO date strings to counts, e.g. {"2026-01-15": 5, ...}
    """
    from app.services.agentmemory import get_all_memories

    memories = get_all_memories()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    date_counts: Counter = Counter()

    for m in memories:
        if metric == "created":
            ts = m.get("createdAt", "")
        elif metric == "modified":
            ts = m.get("updatedAt", "")
        else:  # accessed — approximate from updatedAt
            ts = m.get("updatedAt", "")

        if not ts:
            continue

        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt >= cutoff:
                date_str = dt.strftime("%Y-%m-%d")
                date_counts[date_str] += 1
        except (ValueError, TypeError):
            continue

    # Also aggregate from audit log for accessed events
    if metric == "accessed":
        _aggregate_audit_access(date_counts, cutoff)

    return dict(date_counts)


def _aggregate_audit_access(date_counts: Counter, cutoff: datetime) -> None:
    """Aggregate access events from audit log."""
    audit_json_path = settings.AUDIT_LOG
    audit_jsonl_path = os.path.join(os.path.dirname(audit_json_path), "audit.jsonl")

    for log_path in [audit_jsonl_path]:
        if not os.path.exists(log_path):
            continue
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        ts = entry.get("timestamp", "")
                        if not ts:
                            continue
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if dt >= cutoff:
                            # Count GET requests on memory endpoints as access
                            method = entry.get("method", "")
                            path = entry.get("path", "")
                            if method == "GET" and "/agentmemory/" in path:
                                date_str = dt.strftime("%Y-%m-%d")
                                date_counts[date_str] += 1
                    except (json.JSONDecodeError, ValueError, TypeError):
                        continue
        except (OSError, IOError):
            continue


def get_heatmap_summary(metric: str = "created", days: int = 365) -> dict:
    """Get heatmap data with summary statistics."""
    data = get_heatmap_data(metric, days)
    values = list(data.values())

    return {
        "data": data,
        "metric": metric,
        "days": days,
        "total_events": sum(values),
        "max_day_count": max(values) if values else 0,
        "active_days": len(values),
        "total_days": days,
    }
