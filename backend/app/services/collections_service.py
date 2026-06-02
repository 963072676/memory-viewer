"""Smart Collections service (F-64).

Collections with query-based filtering against memories.
Storage: backend/cache/collections.json
"""

import json
import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

COLLECTIONS_PATH = os.path.join(settings.cache_dir, "collections.json")


def _load_collections() -> list[dict]:
    """Load collections from cache file."""
    try:
        with open(COLLECTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "collections" in data:
                return data["collections"]
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_collections(collections: list[dict]) -> None:
    """Save collections to cache file atomically."""
    os.makedirs(os.path.dirname(COLLECTIONS_PATH), exist_ok=True)
    _atomic_write_json(COLLECTIONS_PATH, {"collections": collections})


def _load_memories() -> list[dict]:
    """Load all memories for query evaluation."""
    try:
        cache_path = settings.AGENTMEMORY_CACHE
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("memories", data.get("agentmemory", []))
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_all_collections() -> list[dict]:
    """Get all collections."""
    return _load_collections()


def get_collection(collection_id: str) -> Optional[dict]:
    """Get a single collection by ID."""
    collections = _load_collections()
    for c in collections:
        if c["id"] == collection_id:
            return c
    return None


def create_collection(data: dict) -> dict:
    """Create a new collection."""
    collections = _load_collections()

    collection = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Untitled"),
        "description": data.get("description", ""),
        "query": data.get("query", {}),
        "icon": data.get("icon", "📁"),
        "color": data.get("color", "#6366f1"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    collections.append(collection)
    _save_collections(collections)
    logger.info(f"Created collection {collection['id']}: {collection['name']}")
    return collection


def update_collection(collection_id: str, data: dict) -> Optional[dict]:
    """Update an existing collection."""
    collections = _load_collections()

    for i, c in enumerate(collections):
        if c["id"] == collection_id:
            # Update allowed fields
            for key in ("name", "description", "query", "icon", "color"):
                if key in data:
                    collections[i][key] = data[key]
            _save_collections(collections)
            logger.info(f"Updated collection {collection_id}")
            return collections[i]

    return None


def delete_collection(collection_id: str) -> bool:
    """Delete a collection."""
    collections = _load_collections()
    original_len = len(collections)
    collections = [c for c in collections if c["id"] != collection_id]

    if len(collections) < original_len:
        _save_collections(collections)
        logger.info(f"Deleted collection {collection_id}")
        return True
    return False


def evaluate_collection(collection_id: str) -> list[dict]:
    """Evaluate a collection's query against all memories.

    Query fields:
      - type: filter by memory type
      - date_range: {start?, end?} ISO date strings
      - strength_min: minimum strength value
      - text: text search in title/content
    """
    collection = get_collection(collection_id)
    if not collection:
        return []

    query = collection.get("query", {})
    memories = _load_memories()
    results = []

    for mem in memories:
        if _matches_query(mem, query):
            results.append(mem)

    return results


def _matches_query(memory: dict, query: dict) -> bool:
    """Check if a memory matches a collection query."""
    # Filter by type
    if "type" in query and query["type"]:
        mem_type = memory.get("type", "")
        if query["type"].lower() not in mem_type.lower():
            return False

    # Filter by date range
    date_range = query.get("date_range", {})
    if date_range:
        mem_date = memory.get("created_at", memory.get("timestamp", ""))
        if date_range.get("start") and mem_date < date_range["start"]:
            return False
        if date_range.get("end") and mem_date > date_range["end"]:
            return False

    # Filter by minimum strength
    if "strength_min" in query:
        mem_strength = memory.get("strength", 0)
        if isinstance(mem_strength, (int, float)) and mem_strength < query["strength_min"]:
            return False

    # Filter by text search
    if "text" in query and query["text"]:
        search_text = query["text"].lower()
        title = memory.get("title", "").lower()
        content = memory.get("content", "").lower()
        if search_text not in title and search_text not in content:
            return False

    return True
