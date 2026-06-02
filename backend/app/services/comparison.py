"""Multi-agent memory comparison service (F-23)."""

import json
from pathlib import Path
from typing import Optional

from app.config import settings


def _load_hermes_memories(profile: str) -> dict:
    """Load hermes memories for a given profile."""
    memories_dir = Path(settings.HERMES_MEMORIES_DIR) / profile
    result = {"user": [], "memory": []}

    for category in ("user", "memory"):
        fpath = memories_dir / f"{category}.json"
        if fpath.exists():
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    result[category] = data
                elif isinstance(data, dict):
                    result[category] = data.get("memories", data.get("entries", []))
                    if not isinstance(result[category], list):
                        result[category] = []
            except (json.JSONDecodeError, OSError):
                pass
    return result


def _extract_title(entry: dict) -> str:
    """Extract title from a memory entry."""
    return entry.get("title", entry.get("key", entry.get("content", "")[:60]))


def _extract_concepts(entry: dict) -> list[str]:
    """Extract concepts from a memory entry."""
    return entry.get("concepts", [])


def compare_profiles(profile_a: str, profile_b: str) -> dict:
    """Compare memories between two profiles."""
    mem_a = _load_hermes_memories(profile_a)
    mem_b = _load_hermes_memories(profile_b)

    all_a = mem_a.get("user", []) + mem_a.get("memory", [])
    all_b = mem_b.get("user", []) + mem_b.get("memory", [])

    titles_a = {}
    for entry in all_a:
        t = _extract_title(entry)
        if t:
            titles_a[t] = entry

    titles_b = {}
    for entry in all_b:
        t = _extract_title(entry)
        if t:
            titles_b[t] = entry

    set_a = set(titles_a.keys())
    set_b = set(titles_b.keys())

    only_in_a = [{"title": t, "entry": titles_a[t]} for t in sorted(set_a - set_b)]
    only_in_b = [{"title": t, "entry": titles_b[t]} for t in sorted(set_b - set_a)]
    shared = []

    for t in sorted(set_a & set_b):
        ea = titles_a[t]
        eb = titles_b[t]
        concepts_a = set(_extract_concepts(ea))
        concepts_b = set(_extract_concepts(eb))
        shared.append({
            "title": t,
            "concepts_a": sorted(concepts_a),
            "concepts_b": sorted(concepts_b),
            "concepts_only_a": sorted(concepts_a - concepts_b),
            "concepts_only_b": sorted(concepts_b - concepts_a),
            "content_a": ea.get("content", ""),
            "content_b": eb.get("content", ""),
            "content_match": ea.get("content", "") == eb.get("content", ""),
        })

    return {
        "profile_a": profile_a,
        "profile_b": profile_b,
        "count_a": len(all_a),
        "count_b": len(all_b),
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "shared": shared,
        "summary": {
            "only_a_count": len(only_in_a),
            "only_b_count": len(only_in_b),
            "shared_count": len(shared),
        },
    }


def list_profiles() -> list[str]:
    """List available profile directories."""
    profiles_dir = Path(settings.HERMES_PROFILES_DIR)
    if not profiles_dir.exists():
        return []
    return sorted([d.name for d in profiles_dir.iterdir() if d.is_dir()])
