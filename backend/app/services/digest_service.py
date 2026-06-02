"""AI Memory Digest service (F-51) — Generate AI-powered summaries of memory changes.

Digest types: daily, weekly, custom range.
Sections: New Memories, Top Changes, Emerging Themes, Health Alerts.
Cached as JSON in backend/cache/digests/.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import get_all_memories, _atomic_write_json

logger = logging.getLogger(__name__)

DIGESTS_DIR = os.path.join(settings.cache_dir, "digests")
DIGEST_INDEX_PATH = os.path.join(DIGESTS_DIR, "index.json")


def _ensure_dir():
    os.makedirs(DIGESTS_DIR, exist_ok=True)


def _load_index() -> dict:
    """Load digest index from disk."""
    try:
        with open(DIGEST_INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"digests": []}


def _save_index(data: dict) -> None:
    """Save digest index to disk."""
    _ensure_dir()
    _atomic_write_json(DIGEST_INDEX_PATH, data)


def _generate_id() -> str:
    """Generate a unique digest ID."""
    ts = str(time.time()).encode()
    return f"digest-{hashlib.md5(ts).hexdigest()[:12]}"


def _get_time_window(digest_type: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> tuple[str, str]:
    """Calculate time window based on digest type."""
    now = datetime.now(timezone.utc)
    if digest_type == "daily":
        start = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        end = now.isoformat().replace("+00:00", "Z")
    elif digest_type == "weekly":
        start = (now - timedelta(days=7)).isoformat().replace("+00:00", "Z")
        end = now.isoformat().replace("+00:00", "Z")
    elif digest_type == "custom" and start_date and end_date:
        start = start_date
        end = end_date
    else:
        start = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        end = now.isoformat().replace("+00:00", "Z")
    return start, end


def _parse_dt(dt_str: str) -> datetime:
    """Parse ISO datetime string."""
    try:
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def _collect_memories_in_window(start: str, end: str) -> list[dict]:
    """Collect memories created or updated within the time window."""
    memories = get_all_memories()
    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)
    result = []
    for m in memories:
        created = m.get("createdAt", "")
        updated = m.get("updatedAt", "")
        dt = _parse_dt(updated or created)
        if start_dt <= dt <= end_dt:
            result.append(m)
    return result


def _group_by_tag(memories: list[dict]) -> dict[str, list[dict]]:
    """Group memories by their tags."""
    groups: dict[str, list[dict]] = {}
    for m in memories:
        tags = m.get("tags", []) or m.get("concepts", [])
        if not tags:
            groups.setdefault("untagged", []).append(m)
        else:
            for tag in tags:
                groups.setdefault(tag, []).append(m)
    return groups


def _analyze_health(memories: list[dict]) -> list[dict]:
    """Identify memories with low health scores."""
    alerts = []
    for m in memories:
        score = m.get("health_score", 100)
        if score < 40:
            alerts.append({
                "id": m.get("id"),
                "title": m.get("title", ""),
                "health_score": score,
                "alert": "critical" if score < 20 else "warning",
            })
    return alerts


def _detect_themes(memories: list[dict]) -> list[dict]:
    """Detect emerging themes from memory tags/concepts."""
    tag_counts: dict[str, int] = {}
    for m in memories:
        for tag in (m.get("tags", []) or []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        for concept in (m.get("concepts", []) or []):
            tag_counts[concept] = tag_counts.get(concept, 0) + 1
    sorted_themes = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"theme": t, "count": c} for t, c in sorted_themes[:10]]


def _build_llm_summary(memories: list[dict], digest_type: str) -> str:
    """Build a summary string. In production this would call an LLM;
    for now we generate a structured text summary."""
    if not memories:
        return "No memories found in the selected time window."

    types_count: dict[str, int] = {}
    for m in memories:
        t = m.get("type", "unknown")
        types_count[t] = types_count.get(t, 0) + 1

    parts = [f"During this {digest_type} period, {len(memories)} memories were active."]
    if types_count:
        type_desc = ", ".join(f"{c} {t}" for t, c in types_count.items())
        parts.append(f"Breakdown by type: {type_desc}.")

    top_titles = [m.get("title", "Untitled") for m in memories[:5]]
    if top_titles:
        parts.append(f"Notable memories: {'; '.join(top_titles)}.")

    return " ".join(parts)


def generate_digest(digest_type: str = "daily",
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> dict:
    """Generate a new memory digest.

    AC-F51-1: Digest generation collects memories in time window.
    AC-F51-2: Groups by cluster/tag and produces sections.
    """
    digest_id = _generate_id()
    start, end = _get_time_window(digest_type, start_date, end_date)
    memories = _collect_memories_in_window(start, end)
    grouped = _group_by_tag(memories)
    health_alerts = _analyze_health(memories)
    themes = _detect_themes(memories)
    summary = _build_llm_summary(memories, digest_type)

    # Build new memories section
    new_memories = [{"id": m.get("id"), "title": m.get("title", ""), "type": m.get("type", ""), "tags": m.get("tags", [])}
                    for m in memories[:20]]

    # Top changes: recently updated
    updated = sorted(memories, key=lambda m: m.get("updatedAt", m.get("createdAt", "")), reverse=True)
    top_changes = [{"id": m.get("id"), "title": m.get("title", ""), "type": m.get("type", "")}
                   for m in updated[:10]]

    digest = {
        "id": digest_id,
        "type": digest_type,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "period": {"start": start, "end": end},
        "summary": summary,
        "sections": {
            "new_memories": new_memories,
            "top_changes": top_changes,
            "emerging_themes": themes,
            "health_alerts": health_alerts,
        },
        "stats": {
            "total_memories": len(memories),
            "unique_tags": len(grouped),
            "health_alerts_count": len(health_alerts),
        },
    }

    # Cache digest
    _ensure_dir()
    digest_path = os.path.join(DIGESTS_DIR, f"{digest_id}.json")
    _atomic_write_json(digest_path, digest)

    # Update index
    index = _load_index()
    index.setdefault("digests", []).append({
        "id": digest_id,
        "type": digest_type,
        "generated_at": digest["generated_at"],
        "period": digest["period"],
        "total_memories": len(memories),
    })
    _save_index(index)

    return digest


def get_digest(digest_id: str) -> Optional[dict]:
    """Get a specific digest by ID."""
    digest_path = os.path.join(DIGESTS_DIR, f"{digest_id}.json")
    try:
        with open(digest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_latest_digest() -> Optional[dict]:
    """Get the most recently generated digest."""
    index = _load_index()
    digests = index.get("digests", [])
    if not digests:
        return None
    latest = digests[-1]
    return get_digest(latest["id"])


def get_digest_history() -> list[dict]:
    """Get all digest metadata."""
    index = _load_index()
    return index.get("digests", [])
