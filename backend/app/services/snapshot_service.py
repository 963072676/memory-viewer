"""Disaster Recovery & Snapshot Management service (F-59).

Snapshot creation, listing, restoration, integrity verification.
Storage: backend/snapshots/ directory with rolling retention.
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

SNAPSHOTS_DIR = os.path.join(settings.cache_dir, "snapshots")
SNAPSHOT_CONFIG_PATH = os.path.join(settings.cache_dir, "snapshot_config.json")

DEFAULT_CONFIG = {
    "schedule_enabled": True,
    "interval_hours": 24,
    "retention_hourly": 24,
    "retention_daily": 7,
    "retention_weekly": 4,
    "max_snapshots": 50,
}


def _ensure_dir():
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)


def _load_config() -> dict:
    try:
        with open(SNAPSHOT_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)


def _save_config(config: dict) -> None:
    os.makedirs(os.path.dirname(SNAPSHOT_CONFIG_PATH), exist_ok=True)
    _atomic_write_json(SNAPSHOT_CONFIG_PATH, config)


def _compute_checksum(data: bytes) -> str:
    """Compute SHA-256 checksum."""
    return hashlib.sha256(data).hexdigest()


def _load_memories() -> list[dict]:
    """Load all memories for snapshot."""
    try:
        cache_path = settings.AGENTMEMORY_CACHE
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("memories", data.get("agentmemory", []))
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ─── Snapshot Operations ─────────────────────────────────────────────────────

def create_snapshot(description: str = "", snapshot_type: str = "manual", triggered_by: str = "user:admin") -> dict:
    """Create a new snapshot."""
    _ensure_dir()

    memories = _load_memories()
    snapshot_id = f"snap_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    # Build snapshot data
    snapshot_data = {
        "id": snapshot_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "type": snapshot_type,
        "description": description,
        "memory_count": len(memories),
        "triggered_by": triggered_by,
        "memories": memories,
    }

    # Serialize and compress
    raw = json.dumps(snapshot_data, ensure_ascii=False).encode("utf-8")
    checksum = _compute_checksum(raw)

    # Write compressed snapshot
    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json.gz")
    with gzip.open(snapshot_file, "wb") as f:
        f.write(raw)

    # Write metadata
    metadata = {
        "id": snapshot_id,
        "created_at": snapshot_data["created_at"],
        "type": snapshot_type,
        "description": description,
        "memory_count": len(memories),
        "checksum_sha256": checksum,
        "size_bytes": os.path.getsize(snapshot_file),
        "triggered_by": triggered_by,
        "file": snapshot_file,
    }

    meta_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.meta.json")
    _atomic_write_json(meta_file, metadata)

    logger.info(f"Created snapshot {snapshot_id}: {len(memories)} memories, {metadata['size_bytes']} bytes")

    # Enforce retention policy
    _enforce_retention()

    return metadata


def list_snapshots() -> list[dict]:
    """List all snapshots sorted by date (newest first)."""
    _ensure_dir()
    snapshots = []

    for fname in os.listdir(SNAPSHOTS_DIR):
        if fname.endswith(".meta.json"):
            try:
                meta_path = os.path.join(SNAPSHOTS_DIR, fname)
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    # Remove internal file path
                    meta.pop("file", None)
                    snapshots.append(meta)
            except (json.JSONDecodeError, IOError):
                continue

    snapshots.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return snapshots


def get_snapshot(snapshot_id: str) -> Optional[dict]:
    """Get snapshot metadata."""
    meta_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.meta.json")
    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            meta.pop("file", None)
            return meta
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_snapshot_data(snapshot_id: str) -> Optional[dict]:
    """Load full snapshot data (with memories)."""
    meta_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.meta.json")
    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    snapshot_file = meta.get("file", os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json.gz"))
    try:
        with gzip.open(snapshot_file, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
            return data
    except Exception as e:
        logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
        return None


def verify_snapshot(snapshot_id: str) -> dict:
    """Verify snapshot integrity by checking SHA-256 checksum."""
    meta_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.meta.json")
    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"valid": False, "error": "Snapshot not found"}

    expected_checksum = meta.get("checksum_sha256", "")
    snapshot_file = meta.get("file", os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json.gz"))

    try:
        with gzip.open(snapshot_file, "rb") as f:
            raw = f.read()
        actual_checksum = _compute_checksum(raw)

        return {
            "valid": actual_checksum == expected_checksum,
            "expected_checksum": expected_checksum,
            "actual_checksum": actual_checksum,
            "snapshot_id": snapshot_id,
            "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def restore_snapshot(snapshot_id: str) -> dict:
    """Restore from a snapshot.

    1. Create pre-restore snapshot of current state
    2. Validate target snapshot integrity
    3. Replace current cache with snapshot data
    4. Log restore event
    """
    # Verify target snapshot
    verification = verify_snapshot(snapshot_id)
    if not verification.get("valid"):
        return {"success": False, "error": f"Snapshot integrity check failed: {verification.get('error', 'checksum mismatch')}"}

    # Create pre-restore snapshot
    try:
        pre_restore = create_snapshot(
            description=f"Pre-restore backup before restoring {snapshot_id}",
            snapshot_type="pre-restore",
            triggered_by="system",
        )
        logger.info(f"Created pre-restore snapshot: {pre_restore['id']}")
    except Exception as e:
        logger.warning(f"Failed to create pre-restore snapshot: {e}")

    # Load snapshot data
    snapshot_data = get_snapshot_data(snapshot_id)
    if not snapshot_data:
        return {"success": False, "error": "Failed to load snapshot data"}

    # Restore memories
    try:
        cache_path = settings.AGENTMEMORY_CACHE
        memories = snapshot_data.get("memories", [])
        restore_data = {"agentmemory": memories, "memories": memories}
        _atomic_write_json(cache_path, restore_data)

        logger.info(f"Restored {len(memories)} memories from snapshot {snapshot_id}")

        return {
            "success": True,
            "snapshot_id": snapshot_id,
            "memories_restored": len(memories),
            "restored_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return {"success": False, "error": f"Restore failed: {str(e)}"}


def delete_snapshot(snapshot_id: str) -> bool:
    """Delete a snapshot."""
    _ensure_dir()
    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json.gz")
    meta_file = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.meta.json")

    deleted = False
    if os.path.exists(snapshot_file):
        os.remove(snapshot_file)
        deleted = True
    if os.path.exists(meta_file):
        os.remove(meta_file)
        deleted = True

    return deleted


def verify_all_snapshots() -> list[dict]:
    """Verify integrity of all snapshots."""
    results = []
    for snap in list_snapshots():
        result = verify_snapshot(snap["id"])
        results.append(result)
    return results


def _enforce_retention() -> None:
    """Enforce retention policy by removing old snapshots."""
    config = _load_config()
    max_snapshots = config.get("max_snapshots", 50)

    snapshots = list_snapshots()
    if len(snapshots) > max_snapshots:
        # Remove oldest snapshots beyond max
        to_remove = snapshots[max_snapshots:]
        for snap in to_remove:
            delete_snapshot(snap["id"])
            logger.info(f"Retention: removed old snapshot {snap['id']}")


# ─── Configuration ───────────────────────────────────────────────────────────

def get_config() -> dict:
    """Get snapshot scheduling configuration."""
    return _load_config()


def update_config(updates: dict) -> dict:
    """Update snapshot scheduling configuration."""
    config = _load_config()
    config.update(updates)
    _save_config(config)
    return config
