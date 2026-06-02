"""Memory Links service (F-65).

Manual memory-to-memory links with typed relations.
Storage: backend/cache/memory_links.json
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

LINKS_PATH = os.path.join(settings.cache_dir, "memory_links.json")

VALID_RELATION_TYPES = {"caused_by", "depends_on", "related_to", "supersedes", "contradicts"}


def _load_links() -> list[dict]:
    """Load links from cache file."""
    try:
        with open(LINKS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "links" in data:
                return data["links"]
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_links(links: list[dict]) -> None:
    """Save links to cache file atomically."""
    os.makedirs(os.path.dirname(LINKS_PATH), exist_ok=True)
    _atomic_write_json(LINKS_PATH, {"links": links})


def _load_memories() -> list[dict]:
    """Load all memories for graph building."""
    try:
        cache_path = settings.AGENTMEMORY_CACHE
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("memories", data.get("agentmemory", []))
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_links(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relation_type: Optional[str] = None,
) -> list[dict]:
    """Get links with optional filters."""
    links = _load_links()

    if source_id:
        links = [l for l in links if l.get("source_id") == source_id]
    if target_id:
        links = [l for l in links if l.get("target_id") == target_id]
    if relation_type:
        links = [l for l in links if l.get("relation_type") == relation_type]

    return links


def create_link(data: dict) -> dict:
    """Create a new memory link."""
    relation_type = data.get("relation_type", "related_to")
    if relation_type not in VALID_RELATION_TYPES:
        raise ValueError(f"Invalid relation_type: {relation_type}. Must be one of: {VALID_RELATION_TYPES}")

    links = _load_links()

    link = {
        "id": str(uuid.uuid4()),
        "source_id": data["source_id"],
        "target_id": data["target_id"],
        "relation_type": relation_type,
        "label": data.get("label", ""),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    links.append(link)
    _save_links(links)
    logger.info(f"Created link {link['id']}: {link['source_id']} -> {link['target_id']} ({relation_type})")
    return link


def delete_link(link_id: str) -> bool:
    """Delete a link."""
    links = _load_links()
    original_len = len(links)
    links = [l for l in links if l["id"] != link_id]

    if len(links) < original_len:
        _save_links(links)
        logger.info(f"Deleted link {link_id}")
        return True
    return False


def get_link(link_id: str) -> Optional[dict]:
    """Get a single link by ID."""
    links = _load_links()
    for l in links:
        if l["id"] == link_id:
            return l
    return None


def get_graph() -> dict:
    """Build a graph structure for visualization.

    Returns:
        {nodes: [{id, title, type}], edges: [{source, target, type, label}]}
    """
    links = _load_links()
    memories = _load_memories()
    memories_by_id = {m.get("id", ""): m for m in memories}

    # Collect all node IDs referenced in links
    node_ids = set()
    for link in links:
        node_ids.add(link["source_id"])
        node_ids.add(link["target_id"])

    # Build nodes
    nodes = []
    for nid in node_ids:
        mem = memories_by_id.get(nid, {})
        nodes.append({
            "id": nid,
            "title": mem.get("title", nid),
            "type": mem.get("type", "unknown"),
        })

    # Build edges
    edges = []
    for link in links:
        edges.append({
            "source": link["source_id"],
            "target": link["target_id"],
            "type": link["relation_type"],
            "label": link.get("label", ""),
        })

    return {"nodes": nodes, "edges": edges}
