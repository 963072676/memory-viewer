"""AI Memory Digest API router (F-51)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.digest_service import generate_digest, get_digest, get_latest_digest, get_digest_history

router = APIRouter()


class GenerateDigestReq(BaseModel):
    type: str = "daily"  # daily, weekly, custom
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/generate")
def generate(req: GenerateDigestReq):
    """Generate a new memory digest.

    AC-F51-1: Digest generation with time window.
    AC-F51-2: Groups by cluster/tag with sections.
    """
    if req.type not in ("daily", "weekly", "custom"):
        raise HTTPException(status_code=400, detail=f"Invalid digest type: {req.type}")
    if req.type == "custom" and (not req.start_date or not req.end_date):
        raise HTTPException(status_code=400, detail="Custom digest requires start_date and end_date")
    digest = generate_digest(req.type, req.start_date, req.end_date)
    return {"success": True, "digest": digest}


@router.get("/latest")
def latest():
    """Get the most recent digest.

    AC-F51-4: Latest digest accessible via endpoint.
    """
    digest = get_latest_digest()
    if not digest:
        return {"digest": None, "message": "No digests generated yet"}
    return {"digest": digest}


@router.get("/history")
def history():
    """Get digest generation history."""
    return {"digests": get_digest_history()}


@router.get("/{digest_id}")
def get_by_id(digest_id: str):
    """Get a specific digest by ID."""
    digest = get_digest(digest_id)
    if not digest:
        raise HTTPException(status_code=404, detail=f"Digest {digest_id} not found")
    return {"digest": digest}
