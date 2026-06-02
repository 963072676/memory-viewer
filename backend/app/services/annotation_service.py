"""Collaborative Annotations service (F-46) — Team-based comments and annotations on memories.

Data model: annotations stored per memory_id with {author, content, timestamp, parent_id, type}.
Annotation types: comment, flag_for_review, suggest_edit, tag_suggestion.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

ANNOTATIONS_PATH = os.path.join(settings.cache_dir, "annotations.json")


def _load_annotations() -> dict:
    """Load annotations from disk."""
    try:
        with open(ANNOTATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"annotations": {}}


def _save_annotations(data: dict) -> None:
    """Save annotations to disk."""
    os.makedirs(os.path.dirname(ANNOTATIONS_PATH), exist_ok=True)
    from app.services.agentmemory import _atomic_write_json
    _atomic_write_json(ANNOTATIONS_PATH, data)


def get_annotations(memory_id: str) -> list[dict]:
    """Get all annotations for a memory.
    
    AC-F46-1: Can add comment to any memory.
    """
    data = _load_annotations()
    annotations = data.get("annotations", {}).get(memory_id, [])
    return annotations


def add_annotation(memory_id: str, author: str, content: str,
                   annotation_type: str = "comment", parent_id: Optional[str] = None) -> dict:
    """Add an annotation to a memory.
    
    AC-F46-1: Can add comment to any memory.
    AC-F46-2: Comments support threading (reply to comment).
    AC-F46-3: Flag for review shows badge on memory card.
    """
    annotation_id = f"ann-{hashlib.md5(f'{memory_id}:{author}:{time.time()}'.encode()).hexdigest()[:10]}"

    annotation = {
        "id": annotation_id,
        "memory_id": memory_id,
        "author": author,
        "content": content,
        "type": annotation_type,
        "parent_id": parent_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": None,
        "resolved": False,
    }

    data = _load_annotations()
    data.setdefault("annotations", {}).setdefault(memory_id, []).append(annotation)
    _save_annotations(data)
    return annotation


def update_annotation(annotation_id: str, content: str = None, author: str = None) -> Optional[dict]:
    """Update an annotation."""
    data = _load_annotations()
    for memory_id, annotations in data.get("annotations", {}).items():
        for i, ann in enumerate(annotations):
            if ann.get("id") == annotation_id:
                if content is not None:
                    ann["content"] = content
                if author is not None:
                    ann["author"] = author
                ann["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                annotations[i] = ann
                data["annotations"][memory_id] = annotations
                _save_annotations(data)
                return ann
    return None


def delete_annotation(annotation_id: str) -> bool:
    """Delete an annotation."""
    data = _load_annotations()
    for memory_id, annotations in data.get("annotations", {}).items():
        original_len = len(annotations)
        data["annotations"][memory_id] = [a for a in annotations if a.get("id") != annotation_id]
        if len(data["annotations"][memory_id]) < original_len:
            _save_annotations(data)
            return True
    return False


def resolve_annotation(annotation_id: str, resolved_by: str = "system") -> Optional[dict]:
    """Resolve a flag or suggestion annotation.
    
    AC-F46-3: Flag for review shows badge on memory card.
    """
    data = _load_annotations()
    for memory_id, annotations in data.get("annotations", {}).items():
        for i, ann in enumerate(annotations):
            if ann.get("id") == annotation_id:
                ann["resolved"] = True
                ann["resolved_by"] = resolved_by
                ann["resolved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                annotations[i] = ann
                data["annotations"][memory_id] = annotations
                _save_annotations(data)
                return ann
    return None


def get_annotation_stats(memory_id: str) -> dict:
    """Get annotation statistics for a memory card.
    
    AC-F46-6: Annotation count visible on collapsed memory cards.
    """
    annotations = get_annotations(memory_id)
    active = [a for a in annotations if not a.get("resolved")]
    flags = [a for a in active if a.get("type") in ("flag_for_review", "suggest_edit")]
    return {
        "total": len(annotations),
        "active": len(active),
        "flags": len(flags),
        "has_flags": len(flags) > 0,
        "has_suggestions": any(a.get("type") == "suggest_edit" and not a.get("resolved") for a in annotations),
    }


def get_all_annotation_stats() -> dict:
    """Get annotation stats for all memories."""
    data = _load_annotations()
    stats = {}
    for memory_id, annotations in data.get("annotations", {}).items():
        active = [a for a in annotations if not a.get("resolved")]
        flags = [a for a in active if a.get("type") in ("flag_for_review", "suggest_edit")]
        stats[memory_id] = {
            "total": len(annotations),
            "active": len(active),
            "flags": len(flags),
            "has_flags": len(flags) > 0,
        }
    return stats


def get_flagged_memories() -> list[dict]:
    """Get all memories with unresolved flags.
    
    AC-F46-5: Can filter memories by "has flags" or "has suggestions".
    """
    data = _load_annotations()
    flagged = []
    for memory_id, annotations in data.get("annotations", {}).items():
        flags = [a for a in annotations if not a.get("resolved") and a.get("type") in ("flag_for_review", "suggest_edit")]
        if flags:
            flagged.append({
                "memory_id": memory_id,
                "flag_count": len(flags),
                "flags": flags,
            })
    return flagged
