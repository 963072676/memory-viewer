"""Backup and restore service (F-30)."""

import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings

BACKUP_DIR = settings.BACKUP_DIR


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup() -> dict:
    """
    Create a backup of agentmemory.json + hermes memories + webhook config.
    Stores in BACKUP_DIR/{timestamp}/.
    """
    _ensure_backup_dir()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = os.path.join(BACKUP_DIR, ts)
    os.makedirs(backup_path, exist_ok=True)

    files_copied = []

    # 1. agentmemory.json
    am_cache = settings.AGENTMEMORY_CACHE
    if os.path.exists(am_cache):
        dest = os.path.join(backup_path, "agentmemory.json")
        shutil.copy2(am_cache, dest)
        files_copied.append("agentmemory.json")

    # 2. hermes memories directory
    memories_dir = settings.HERMES_MEMORIES_DIR
    if os.path.isdir(memories_dir):
        dest = os.path.join(backup_path, "memories")
        shutil.copytree(memories_dir, dest, dirs_exist_ok=True)
        files_copied.append("memories/")

    # 3. webhook/subscriptions config
    webhook_path = os.path.join(settings.cache_dir, "subscriptions.json")
    if os.path.exists(webhook_path):
        dest = os.path.join(backup_path, "subscriptions.json")
        shutil.copy2(webhook_path, dest)
        files_copied.append("subscriptions.json")

    # Write manifest
    manifest = {
        "timestamp": ts,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "files": files_copied,
    }
    with open(os.path.join(backup_path, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "backup_id": ts,
        "path": backup_path,
        "files": files_copied,
    }


def list_backups() -> list[dict]:
    """List all available backups."""
    _ensure_backup_dir()
    backups = []
    for entry in sorted(os.listdir(BACKUP_DIR), reverse=True):
        bp = os.path.join(BACKUP_DIR, entry)
        if not os.path.isdir(bp):
            continue
        manifest_path = os.path.join(bp, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            backups.append(manifest)
        else:
            backups.append({"backup_id": entry, "timestamp": entry, "files": []})
    return backups


def restore_backup(backup_id: str) -> dict:
    """Restore from a specific backup."""
    backup_path = os.path.join(BACKUP_DIR, backup_id)
    if not os.path.isdir(backup_path):
        return {"success": False, "error": f"Backup not found: {backup_id}"}

    restored = []

    # 1. agentmemory.json
    am_src = os.path.join(backup_path, "agentmemory.json")
    if os.path.exists(am_src):
        shutil.copy2(am_src, settings.AGENTMEMORY_CACHE)
        restored.append("agentmemory.json")

    # 2. hermes memories
    mem_src = os.path.join(backup_path, "memories")
    if os.path.isdir(mem_src):
        dest = settings.HERMES_MEMORIES_DIR
        os.makedirs(dest, exist_ok=True)
        shutil.copytree(mem_src, dest, dirs_exist_ok=True)
        restored.append("memories/")

    # 3. webhook config
    wh_src = os.path.join(backup_path, "subscriptions.json")
    if os.path.exists(wh_src):
        dest = os.path.join(settings.cache_dir, "subscriptions.json")
        shutil.copy2(wh_src, dest)
        restored.append("subscriptions.json")

    return {
        "success": True,
        "backup_id": backup_id,
        "restored_files": restored,
    }
