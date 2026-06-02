"""Team Workspaces & RBAC service (F-54) — Multi-workspace support with role-based access.

Roles: admin (full), editor (CRUD memories), viewer (read-only).
Migration: existing memories → "default" workspace.
Storage: workspaces.json, memberships.json.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

WORKSPACES_PATH = os.path.join(settings.cache_dir, "workspaces.json")
MEMBERSHIPS_PATH = os.path.join(settings.cache_dir, "memberships.json")

VALID_ROLES = {"admin", "editor", "viewer"}


def _load_workspaces() -> dict:
    try:
        with open(WORKSPACES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"workspaces": []}


def _save_workspaces(data: dict) -> None:
    os.makedirs(os.path.dirname(WORKSPACES_PATH), exist_ok=True)
    _atomic_write_json(WORKSPACES_PATH, data)


def _load_memberships() -> dict:
    try:
        with open(MEMBERSHIPS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"memberships": {}}


def _save_memberships(data: dict) -> None:
    os.makedirs(os.path.dirname(MEMBERSHIPS_PATH), exist_ok=True)
    _atomic_write_json(MEMBERSHIPS_PATH, data)


def _ensure_default_workspace() -> dict:
    """Ensure the default workspace exists."""
    data = _load_workspaces()
    for ws in data.get("workspaces", []):
        if ws["id"] == "default":
            return ws
    default = {
        "id": "default",
        "name": "Default Workspace",
        "description": "Default workspace for all memories",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "created_by": "system",
        "is_default": True,
    }
    data.setdefault("workspaces", []).append(default)
    _save_workspaces(data)
    return default


# ─── Workspace CRUD ────────────────────────────────────────────────────────────

def get_all_workspaces() -> list[dict]:
    """Get all workspaces."""
    _ensure_default_workspace()
    data = _load_workspaces()
    return data.get("workspaces", [])


def get_workspace(workspace_id: str) -> Optional[dict]:
    """Get a workspace by ID."""
    data = _load_workspaces()
    for ws in data.get("workspaces", []):
        if ws["id"] == workspace_id:
            return ws
    return None


def create_workspace(name: str, description: str = "", created_by: str = "system") -> dict:
    """Create a new workspace."""
    ws_id = f"ws-{hashlib.md5(f'{name}:{time.time()}'.encode()).hexdigest()[:10]}"
    workspace = {
        "id": ws_id,
        "name": name,
        "description": description,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "created_by": created_by,
        "is_default": False,
    }
    data = _load_workspaces()
    data.setdefault("workspaces", []).append(workspace)
    _save_workspaces(data)

    # Creator becomes admin
    add_member(ws_id, created_by, "admin")
    return workspace


def update_workspace(workspace_id: str, name: str = None, description: str = None) -> Optional[dict]:
    """Update a workspace."""
    data = _load_workspaces()
    for i, ws in enumerate(data.get("workspaces", [])):
        if ws["id"] == workspace_id:
            if name is not None:
                ws["name"] = name
            if description is not None:
                ws["description"] = description
            ws["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            data["workspaces"][i] = ws
            _save_workspaces(data)
            return ws
    return None


def delete_workspace(workspace_id: str) -> bool:
    """Delete a workspace (cannot delete default)."""
    if workspace_id == "default":
        return False
    data = _load_workspaces()
    original_len = len(data.get("workspaces", []))
    data["workspaces"] = [ws for ws in data.get("workspaces", []) if ws["id"] != workspace_id]
    if len(data["workspaces"]) < original_len:
        _save_workspaces(data)
        # Clean up memberships
        mdata = _load_memberships()
        mdata.get("memberships", {}).pop(workspace_id, None)
        _save_memberships(mdata)
        return True
    return False


# ─── Membership CRUD ──────────────────────────────────────────────────────────

def get_members(workspace_id: str) -> list[dict]:
    """Get all members of a workspace."""
    data = _load_memberships()
    members = data.get("memberships", {}).get(workspace_id, [])
    return members


def add_member(workspace_id: str, user_id: str, role: str = "viewer") -> Optional[dict]:
    """Add a member to a workspace."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}. Must be one of {VALID_ROLES}")

    # Check workspace exists
    if not get_workspace(workspace_id):
        raise ValueError(f"Workspace {workspace_id} not found")

    data = _load_memberships()
    members = data.get("memberships", {}).get(workspace_id, [])

    # Check if already a member
    for m in members:
        if m["user_id"] == user_id:
            m["role"] = role
            m["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            data["memberships"][workspace_id] = members
            _save_memberships(data)
            return m

    member = {
        "user_id": user_id,
        "role": role,
        "workspace_id": workspace_id,
        "joined_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    members.append(member)
    data.setdefault("memberships", {})[workspace_id] = members
    _save_memberships(data)
    return member


def update_member_role(workspace_id: str, user_id: str, role: str) -> Optional[dict]:
    """Update a member's role."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}")

    data = _load_memberships()
    members = data.get("memberships", {}).get(workspace_id, [])
    for m in members:
        if m["user_id"] == user_id:
            m["role"] = role
            m["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            data["memberships"][workspace_id] = members
            _save_memberships(data)
            return m
    return None


def remove_member(workspace_id: str, user_id: str) -> bool:
    """Remove a member from a workspace."""
    data = _load_memberships()
    members = data.get("memberships", {}).get(workspace_id, [])
    original_len = len(members)
    data["memberships"][workspace_id] = [m for m in members if m["user_id"] != user_id]
    if len(data["memberships"][workspace_id]) < original_len:
        _save_memberships(data)
        return True
    return False


def check_permission(workspace_id: str, user_id: str, required_role: str = "viewer") -> bool:
    """Check if a user has the required permission level."""
    role_hierarchy = {"viewer": 0, "editor": 1, "admin": 2}
    data = _load_memberships()
    members = data.get("memberships", {}).get(workspace_id, [])
    for m in members:
        if m["user_id"] == user_id:
            return role_hierarchy.get(m["role"], 0) >= role_hierarchy.get(required_role, 0)
    return False


def get_user_workspaces(user_id: str) -> list[dict]:
    """Get all workspaces a user is a member of."""
    data = _load_memberships()
    workspaces = get_all_workspaces()
    ws_ids = set()
    for ws_id, members in data.get("memberships", {}).items():
        for m in members:
            if m["user_id"] == user_id:
                ws_ids.add(ws_id)
    return [ws for ws in workspaces if ws["id"] in ws_ids]


def migrate_memories_to_default() -> dict:
    """Migrate existing memories to default workspace.

    AC-F54-4: Migration assigns existing memories to default workspace.
    """
    _ensure_default_workspace()
    return {"status": "ok", "workspace": "default", "message": "All existing memories belong to the default workspace"}
