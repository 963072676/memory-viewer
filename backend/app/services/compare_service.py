"""Compare service — multi-agent memory comparison (P31-T1)."""

import hashlib
import math
import os
from collections import Counter

from app.config import settings
from app.services.agentmemory import _read_json_cache


def _load_hermes_memories() -> dict:
    """Load hermes memory data (global + profiles)."""
    from app.services.hermes_memory import get_hermes_memory
    return get_hermes_memory()


def _get_profile_memory_items(profile: str) -> set[str]:
    """Get all memory item identifiers for a given profile."""
    hermes = _load_hermes_memories()
    items = set()

    # Check profiles section
    if profile in hermes.get("profiles", {}):
        profile_data = hermes["profiles"][profile]
        for entry in profile_data.get("memory", []):
            items.add(_normalize_item(entry))
        for entry in profile_data.get("user", []):
            items.add(_normalize_item(entry))

    return items


def _normalize_item(text: str) -> str:
    """Normalize a memory item for comparison (lowercase, strip)."""
    return text.strip().lower()


def _compute_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return round(intersection / union, 4) if union > 0 else 0.0


def compare_two_profiles(left: str, right: str) -> dict:
    """
    Compare two profiles' memories and return diff report.

    Returns:
        {
            left_only: [items only in left profile],
            right_only: [items only in right profile],
            common: [items in both profiles],
            similarity_score: float (0-1)
        }
    """
    left_items = _get_profile_memory_items(left)
    right_items = _get_profile_memory_items(right)

    common = sorted(left_items & right_items)
    left_only = sorted(left_items - right_items)
    right_only = sorted(right_items - left_items)

    similarity = _compute_similarity(left_items, right_items)

    return {
        "left": left,
        "right": right,
        "left_only": left_only,
        "right_only": right_only,
        "common": common,
        "similarity_score": similarity,
    }


def list_compare_profiles() -> list[str]:
    """List available profile names for comparison."""
    from app.services.hermes_memory import get_profiles
    return get_profiles()