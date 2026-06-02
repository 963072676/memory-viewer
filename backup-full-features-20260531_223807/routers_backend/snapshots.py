"""Disaster Recovery & Snapshot Management router (F-59)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.services.snapshot_service import (
    create_snapshot,
    list_snapshots,
    get_snapshot,
    get_snapshot_data,
    verify_snapshot,
    restore_snapshot,
    delete_snapshot,
    verify_all_snapshots,
    get_config,
    update_config,
)

router = APIRouter()


@router.get("")
def list_all():
    """List all snapshots sorted by date."""
    snapshots = list_snapshots()
    return {"snapshots": snapshots, "total": len(snapshots)}


class CreateSnapshotReq(BaseModel):
    description: str = ""
    tags: list[str] = []


@router.post("")
def create(req: CreateSnapshotReq):
    """Create a manual snapshot."""
    snapshot = create_snapshot(
        description=req.description,
        snapshot_type="manual",
        triggered_by="user:admin",
    )
    return {"success": True, "snapshot": snapshot}


@router.get("/{snapshot_id}")
def get_one(snapshot_id: str):
    """Get snapshot details."""
    snapshot = get_snapshot(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    return {"snapshot": snapshot}


@router.get("/{snapshot_id}/download")
def download(snapshot_id: str):
    """Download snapshot data."""
    data = get_snapshot_data(snapshot_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found or corrupted")
    return JSONResponse(content=data)


@router.post("/{snapshot_id}/restore")
def restore(snapshot_id: str):
    """Restore from a snapshot."""
    result = restore_snapshot(snapshot_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
    return result


@router.delete("/{snapshot_id}")
def delete(snapshot_id: str):
    """Delete a snapshot."""
    if not delete_snapshot(snapshot_id):
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    return {"success": True}


@router.post("/verify")
def verify_all():
    """Verify integrity of all snapshots."""
    results = verify_all_snapshots()
    total = len(results)
    valid = sum(1 for r in results if r.get("valid"))
    return {"results": results, "total": total, "valid": valid, "invalid": total - valid}


@router.get("/{snapshot_id}/verify")
def verify_one(snapshot_id: str):
    """Verify integrity of a specific snapshot."""
    result = verify_snapshot(snapshot_id)
    return result


# ─── Configuration ───────────────────────────────────────────────────────────

@router.get("/config/schedule")
def get_schedule_config():
    """Get snapshot scheduling configuration."""
    return get_config()


class UpdateConfigReq(BaseModel):
    schedule_enabled: Optional[bool] = None
    interval_hours: Optional[int] = None
    retention_hourly: Optional[int] = None
    retention_daily: Optional[int] = None
    retention_weekly: Optional[int] = None
    max_snapshots: Optional[int] = None


@router.put("/config/schedule")
def update_schedule_config(req: UpdateConfigReq):
    """Update snapshot scheduling configuration."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    config = update_config(updates)
    return {"success": True, "config": config}
