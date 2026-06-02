"""Favorites service (F-63).

Manages user favorites for memory items.
Storage: backend/cache/favorites.json
"""

import json
import os
import logging
from datetime import datetime, timezone

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

FAVORITES_PATH = os.path.join(settings.cache_dir, "favorites.json")


def _load_favorites() -> dict:
    """Load favorites from cache file."""
    try:
        with open(FAVORITES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_favorites(data: dict) -> None:
    """Save favorites to cache file atomically."""
    os.makedirs(os.path.dirname(FAVORITES_PATH), exist_ok=True)
    _atomic_write_json(FAVORITES_PATH, data)


def toggle_favorite(memory_id: str) -> bool:
    """Toggle favorite status for a memory.

    Returns:
        True if now favorited, False if unfavorited.
    """
    favorites = _load_favorites()

    if memory_id in favorites and favorites[memory_id].get("favorited"):
        # Unfavorite
        favorites[memory_id] = {
            "favorited": False,
            "favorited_at": None,
        }
        _save_favorites(favorites)
        logger.info(f"Unfavorited memory {memory_id}")
        return False
    else:
        # Favorite
        favorites[memory_id] = {
            "favorited": True,
            "favorited_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        _save_favorites(favorites)
        logger.info(f"Favorited memory {memory_id}")
        return True


def get_favorites() -> list[str]:
    """Get list of favorited memory IDs."""
    favorites = _load_favorites()
    return [mid for mid, info in favorites.items() if info.get("favorited")]


def is_favorited(memory_id: str) -> bool:
    """Check if a specific memory is favorited."""
    favorites = _load_favorites()
    entry = favorites.get(memory_id, {})
    return entry.get("favorited", False)


def get_all_favorite_details() -> dict:
    """Get full favorites dict with details."""
    return _load_favorites()
