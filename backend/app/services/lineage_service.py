"""Memory Lineage & Provenance service (F-48) — Track origin, transformations, and derivation chain.

Each memory gets a lineage field: {source, parent_ids, created_at, transformations}.
Source types: manual, import, agent, merge, derived, legacy.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import get_all_memories, _read_json_cache, _atomic_write_json

logger = logging.getLogger(__name__)

LINEAGE_CACHE = os.path.join(settings.cache_dir, "lineage.json")

SOURCE_ICONS = {
    "manual": "✍️",
    "import": "📥",
    "agent": "🤖",
    "merge": "🔀",
    "derived": "🔗",
    "legacy": "📦",
}


def _load_lineage() -> dict:
    """Load lineage data from cache file."""
    try:
        with open(LINEAGE_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"lineages": {}}


def _save_lineage(data: dict) -> None:
    """Save lineage data to cache file."""
    os.makedirs(os.path.dirname(LINEAGE_CACHE), exist_ok=True)
    _atomic_write_json(LINEAGE_CACHE, data)


def get_lineage(memory_id: str) -> Optional[dict]:
    """Get the full provenance chain for a memory.
    
    AC-F48-1: New memories automatically get lineage metadata.
    AC-F48-6: Backfilled legacy memories show "legacy" source.
    """
    data = _load_lineage()
    lineage = data.get("lineages", {}).get(memory_id)
    if not lineage:
        # Try to find the memory and create legacy lineage
        memories = get_all_memories()
        mem = next((m for m in memories if m.get("id") == memory_id), None)
        if not mem:
            return None
        lineage = _backfill_lineage(memory_id)
    return lineage


def _backfill_lineage(memory_id: str) -> dict:
    """Create legacy lineage for a memory that doesn't have one."""
    lineage = {
        "memory_id": memory_id,
        "source": "legacy",
        "parent_ids": [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "transformations": [],
        "icon": SOURCE_ICONS["legacy"],
    }
    data = _load_lineage()
    data.setdefault("lineages", {})[memory_id] = lineage
    _save_lineage(data)
    return lineage


def record_creation(memory_id: str, source: str = "manual", parent_ids: list[str] = None) -> dict:
    """Record the creation of a new memory with lineage metadata.
    
    AC-F48-1: New memories automatically get lineage metadata.
    """
    lineage = {
        "memory_id": memory_id,
        "source": source,
        "parent_ids": parent_ids or [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "transformations": [],
        "icon": SOURCE_ICONS.get(source, "📦"),
    }
    data = _load_lineage()
    data.setdefault("lineages", {})[memory_id] = lineage
    _save_lineage(data)
    return lineage


def record_transformation(memory_id: str, transform_type: str, detail: str = "") -> Optional[dict]:
    """Record a transformation event on a memory.
    
    AC-F48-2: Edited memories record transformation history.
    """
    data = _load_lineage()
    lineage = data.get("lineages", {}).get(memory_id)
    if not lineage:
        lineage = _backfill_lineage(memory_id)
        data = _load_lineage()  # Reload after backfill

    transformation = {
        "type": transform_type,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "detail": detail,
    }
    lineage.setdefault("transformations", []).append(transformation)
    data["lineages"][memory_id] = lineage
    _save_lineage(data)
    return lineage


def record_merge(merged_id: str, parent_ids: list[str]) -> dict:
    """Record a merge operation linking to both parents.
    
    AC-F48-3: Merged memories link to both parents.
    """
    lineage = {
        "memory_id": merged_id,
        "source": "merge",
        "parent_ids": parent_ids,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "transformations": [{
            "type": "merge",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "detail": f"Merged from {len(parent_ids)} memories: {', '.join(parent_ids)}",
        }],
        "icon": SOURCE_ICONS["merge"],
    }
    data = _load_lineage()
    data.setdefault("lineages", {})[merged_id] = lineage
    _save_lineage(data)
    return lineage


def get_lineage_graph() -> dict:
    """Get DAG visualization data of all memory derivations.
    
    AC-F48-4: Lineage graph renders correctly.
    AC-F48-5: Source type displayed with appropriate icon.
    """
    data = _load_lineage()
    lineages = data.get("lineages", {})
    memories = get_all_memories()
    mem_map = {m.get("id"): m for m in memories}

    nodes = []
    links = []

    for mid, lineage in lineages.items():
        mem = mem_map.get(mid, {})
        source = lineage.get("source", "legacy")
        nodes.append({
            "id": mid,
            "label": mem.get("title", mid[:20]),
            "source": source,
            "icon": SOURCE_ICONS.get(source, "📦"),
            "type": mem.get("type", "unknown"),
        })
        for parent_id in lineage.get("parent_ids", []):
            links.append({
                "source": parent_id,
                "target": mid,
                "type": "derivation",
            })

    # Add any memories not yet in lineage as legacy nodes
    for mem in memories:
        mid = mem.get("id", "")
        if mid not in lineages:
            nodes.append({
                "id": mid,
                "label": mem.get("title", mid[:20]),
                "source": "legacy",
                "icon": SOURCE_ICONS["legacy"],
                "type": mem.get("type", "unknown"),
            })

    return {
        "nodes": nodes,
        "links": links,
        "total": len(nodes),
    }


def backfill_all() -> dict:
    """Backfill lineage for all memories that don't have one.
    
    AC-F48-6: Backfilled legacy memories show "legacy" source.
    """
    data = _load_lineage()
    memories = get_all_memories()
    count = 0
    for mem in memories:
        mid = mem.get("id", "")
        if mid and mid not in data.get("lineages", {}):
            data.setdefault("lineages", {})[mid] = {
                "memory_id": mid,
                "source": "legacy",
                "parent_ids": [],
                "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "transformations": [],
                "icon": SOURCE_ICONS["legacy"],
            }
            count += 1
    _save_lineage(data)
    return {"backfilled": count, "total": len(memories)}
