"""Team Workspaces & RBAC API router (F-54)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.workspace_service import (
    get_all_workspaces,
    get_workspace,
    create_workspace,
    update_workspace,
    delete_workspace,
    get_members,
    add_member,
    update_member_role,
    remove_member,
    get_user_workspaces,
    migrate_memories_to_default,
)

router = APIRouter()


# ─── Workspace CRUD ────────────────────────────────────────────────────────────

@router.get("")
def list_workspaces():
    """Get all workspaces."""
    return {"workspaces": get_all_workspaces(), "total": len(get_all_workspaces())}


@router.get("/{workspace_id}")
def get_one(workspace_id: str):
    """Get a specific workspace."""
    ws = get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")
    return {"workspace": ws}


class CreateWorkspaceReq(BaseModel):
    name: str
    description: str = ""
    created_by: str = "system"


@router.post("")
def create(req: CreateWorkspaceReq):
    """Create a new workspace."""
    ws = create_workspace(req.name, req.description, req.created_by)
    return {"success": True, "workspace": ws}


class UpdateWorkspaceReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.put("/{workspace_id}")
def update(workspace_id: str, req: UpdateWorkspaceReq):
    """Update a workspace."""
    ws = update_workspace(workspace_id, req.name, req.description)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")
    return {"success": True, "workspace": ws}


@router.delete("/{workspace_id}")
def delete(workspace_id: str):
    """Delete a workspace."""
    if not delete_workspace(workspace_id):
        raise HTTPException(status_code=400, detail="Cannot delete default workspace or workspace not found")
    return {"success": True}


# ─── Member Management ────────────────────────────────────────────────────────

@router.get("/{workspace_id}/members")
def list_members(workspace_id: str):
    """Get all members of a workspace."""
    ws = get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Workspace {workspace_id} not found")
    return {"members": get_members(workspace_id), "total": len(get_members(workspace_id))}


class AddMemberReq(BaseModel):
    user_id: str
    role: str = "viewer"


@router.post("/{workspace_id}/members")
def add(req: AddMemberReq, workspace_id: str):
    """Add a member to a workspace."""
    try:
        member = add_member(workspace_id, req.user_id, req.role)
        return {"success": True, "member": member}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class UpdateMemberReq(BaseModel):
    role: str


@router.put("/{workspace_id}/members/{user_id}")
def update_member(workspace_id: str, user_id: str, req: UpdateMemberReq):
    """Update a member's role."""
    result = update_member_role(workspace_id, user_id, req.role)
    if not result:
        raise HTTPException(status_code=404, detail=f"Member {user_id} not found in workspace {workspace_id}")
    return {"success": True, "member": result}


@router.delete("/{workspace_id}/members/{user_id}")
def remove(workspace_id: str, user_id: str):
    """Remove a member from a workspace."""
    if not remove_member(workspace_id, user_id):
        raise HTTPException(status_code=404, detail=f"Member {user_id} not found")
    return {"success": True}


@router.get("/user/{user_id}")
def user_workspaces(user_id: str):
    """Get all workspaces for a user."""
    return {"workspaces": get_user_workspaces(user_id)}


@router.post("/migrate")
def migrate():
    """Migrate existing memories to default workspace."""
    return migrate_memories_to_default()
