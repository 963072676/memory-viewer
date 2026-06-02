"""Dedup API router (F-21)."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.dedup import find_duplicates, merge_memories

router = APIRouter()


class MergeRequest(BaseModel):
    keep_id: str
    merge_id: str


@router.get("/duplicates")
def get_duplicates(threshold: float = Query(default=0.7, ge=0.0, le=1.0)):
    """Find duplicate memory pairs above similarity threshold."""
    return find_duplicates(threshold=threshold)


@router.post("/merge")
def merge(req: MergeRequest):
    """Merge two duplicate memories."""
    if req.keep_id == req.merge_id:
        raise HTTPException(status_code=400, detail="Cannot merge a memory with itself")
    result = merge_memories(keep_id=req.keep_id, merge_id=req.merge_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Merge failed"))
    return result
