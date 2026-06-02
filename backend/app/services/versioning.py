"""Version history service (F-24). Stores snapshots of memory edits."""

import difflib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.services import agentmemory as am_service

VERSIONS_DIR = settings.VERSIONS_DIR


def _ensure_dir():
    os.makedirs(VERSIONS_DIR, exist_ok=True)


def _version_file(memory_id: str) -> str:
    return os.path.join(VERSIONS_DIR, f"{memory_id}.json")


def _read_versions(memory_id: str) -> list[dict]:
    path = _version_file(memory_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "versions" in data:
                return data["versions"]
            if isinstance(data, list):
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _write_versions(memory_id: str, versions: list[dict]) -> None:
    _ensure_dir()
    path = _version_file(memory_id)
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"versions": versions}, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def save_snapshot(memory: dict) -> dict:
    """Save a snapshot of the current memory state before an edit."""
    versions = _read_versions(memory["id"])
    version_num = len(versions) + 1
    snapshot = {
        "version": version_num,
        "snapshot": {
            "title": memory.get("title", ""),
            "content": memory.get("content", ""),
            "concepts": memory.get("concepts", []),
            "strength": memory.get("strength", 5),
            "type": memory.get("type", "pattern"),
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    versions.append(snapshot)
    _write_versions(memory["id"], versions)
    return snapshot


def get_versions(memory_id: str) -> list[dict]:
    """Get all version snapshots for a memory."""
    return _read_versions(memory_id)


def get_version_detail(memory_id: str, version: int) -> dict | None:
    """Get a single version snapshot detail for a memory."""
    versions = _read_versions(memory_id)
    for v in versions:
        if v.get("version") == version:
            return v
    return None


def diff_versions(memory_id: str, from_version: int, to_version: int) -> dict:
    """Return diff between two versions of a memory."""
    versions = _read_versions(memory_id)
    from_ver, to_ver = None, None
    for v in versions:
        if v.get("version") == from_version:
            from_ver = v
        if v.get("version") == to_version:
            to_ver = v

    if not from_ver:
        return {"success": False, "error": f"From version {from_version} not found"}
    if not to_ver:
        return {"success": False, "error": f"To version {to_version} not found"}

    from_text = from_ver["snapshot"].get("content", "")
    to_text = to_ver["snapshot"].get("content", "")

    from_lines = from_text.splitlines(keepends=True)
    to_lines = to_text.splitlines(keepends=True)

    diff = list(difflib.unified_diff(from_lines, to_lines, fromfile=f"v{from_version}", tofile=f"v{to_version}"))

    return {
        "success": True,
        "from_version": from_version,
        "to_version": to_version,
        "diff": diff,
    }


def rollback_to_version(memory_id: str, version: int) -> dict:
    """Rollback a memory to a specific version."""
    versions = _read_versions(memory_id)
    target = None
    for v in versions:
        if v.get("version") == version:
            target = v
            break

    if not target:
        return {"success": False, "error": f"Version {version} not found"}

    # Save current state as a new version before rollback
    current = am_service.get_memory_by_id(memory_id)
    if not current:
        return {"success": False, "error": f"Memory {memory_id} not found"}

    save_snapshot(current)

    # Apply the snapshot
    snapshot = target["snapshot"]
    updated = am_service.update_memory(
        memory_id=memory_id,
        content=snapshot.get("content"),
        concepts=snapshot.get("concepts"),
        strength=snapshot.get("strength"),
    )

    if not updated:
        return {"success": False, "error": "Failed to update memory"}

    return {"success": True, "memory": updated, "rolled_back_to_version": version}
