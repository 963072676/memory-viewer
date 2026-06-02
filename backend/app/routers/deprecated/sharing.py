"""Memory Sharing API router (F-42)."""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from app.services.sharing_service import (
    create_share,
    get_share,
    list_shares,
    delete_share,
    apply_pii_masking,
)
from app.services.agentmemory import get_memory_by_id, get_all_memories

router = APIRouter()


class ShareRequest(BaseModel):
    access_level: str = Field(default="view", pattern="^(view|comment|edit)$")
    expires_in: str = Field(default="7d", pattern="^(1h|1d|7d|30d|never)$")
    password: Optional[str] = None
    batch_ids: Optional[list[str]] = None


class ShareResponse(BaseModel):
    share_id: str
    share_url: str
    access_level: str
    expires_at: Optional[str]
    password_protected: bool
    pii_masked: bool


@router.post("/memories/{memory_id}/share", response_model=ShareResponse)
def share_memory(memory_id: str, req: ShareRequest):
    """Create a share link for a memory.
    
    AC-F42-1: Generate share link for single memory.
    AC-F42-6: Auto-applies PII masking on share.
    """
    mem = get_memory_by_id(memory_id)
    if not mem:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")

    # If batch IDs provided, validate them
    batch_ids = req.batch_ids or []
    if batch_ids:
        all_mems = {m.get("id"): m for m in get_all_memories()}
        invalid = [bid for bid in batch_ids if bid not in all_mems]
        if invalid:
            raise HTTPException(
                status_code=404,
                detail=f"Memories not found: {', '.join(invalid[:5])}",
            )

    result = create_share(
        memory_id=memory_id,
        memory_title=mem.get("title", ""),
        memory_content=mem.get("content", ""),
        access_level=req.access_level,
        expires_in=req.expires_in,
        password=req.password,
        batch_ids=batch_ids,
    )

    return ShareResponse(**result)


@router.get("/shared/{share_id}")
def get_shared_memory(share_id: str, password: Optional[str] = Query(default=None)):
    """Access a shared memory via share link. No auth required.
    
    AC-F42-1: Unauthenticated user can view.
    AC-F42-2: Share link becomes inaccessible after expiration.
    """
    result = get_share(share_id, password=password)
    if result is None:
        raise HTTPException(status_code=404, detail="Share link not found or expired")

    if result.get("password_required"):
        return {"password_required": True, "message": "This share link requires a password"}

    if result.get("invalid_password"):
        raise HTTPException(status_code=403, detail="Invalid password")

    # Fetch the actual memory
    memory_id = result.get("memory_id")
    mem = get_memory_by_id(memory_id)
    if not mem:
        raise HTTPException(status_code=404, detail="Shared memory no longer exists")

    # Apply PII masking if configured
    if result.get("pii_masked"):
        mem = apply_pii_masking(mem)

    # Handle batch sharing
    batch_memories = []
    if result.get("batch_ids"):
        all_mems = {m.get("id"): m for m in get_all_memories()}
        for bid in result["batch_ids"]:
            batch_mem = all_mems.get(bid)
            if batch_mem:
                if result.get("pii_masked"):
                    batch_mem = apply_pii_masking(batch_mem)
                batch_memories.append(batch_mem)

    return {
        "share_id": share_id,
        "access_level": result.get("access_level", "view"),
        "memory": mem,
        "batch_memories": batch_memories if batch_memories else None,
        "created_at": result.get("created_at"),
        "expires_at": result.get("expires_at"),
        "access_count": result.get("access_count", 0),
    }


@router.get("/shares")
def get_shares(memory_id: Optional[str] = Query(default=None)):
    """List all active share links.
    
    AC-F42-4: Share links can be revoked (listed for management).
    """
    shares = list_shares(memory_id=memory_id)
    return {"shares": shares, "total": len(shares)}


@router.delete("/shares/{share_id}")
def revoke_share(share_id: str):
    """Revoke a share link.
    
    AC-F42-4: Share links can be revoked.
    """
    success = delete_share(share_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Share {share_id} not found")
    return {"success": True, "deleted": share_id}
