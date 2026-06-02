"""Memory Conflict Detection API router (F-45)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.conflict_service import (
    scan_conflicts,
    get_conflicts_list,
    resolve_conflict,
    get_conflict_summary,
)

router = APIRouter()


@router.get("")
def list_conflicts(
    limit: int = Query(default=50, ge=1, le=200),
    severity: Optional[str] = Query(default=None, pattern="^(high|medium|low)$"),
    resolved: Optional[bool] = Query(default=None),
):
    """Get list of detected conflicts.
    
    AC-F45-2: Returns conflict pairs with similarity score and contradiction type.
    """
    conflicts = get_conflicts_list(limit=limit, severity=severity, resolved=resolved)
    return {"conflicts": conflicts, "total": len(conflicts)}


@router.get("/summary")
def conflict_summary():
    """Get conflict count summary for sidebar badge.
    
    AC-F45-5: Conflict count shown in sidebar with severity color.
    """
    return get_conflict_summary()


@router.post("/scan")
def trigger_scan(force: bool = Query(default=True)):
    """Trigger conflict detection scan.
    
    AC-F45-1: POST /api/conflicts/scan triggers conflict detection.
    AC-F45-6: Scan completes within 30s for 500 memories.
    """
    conflicts = scan_conflicts(force=force)
    return {
        "success": True,
        "conflicts_found": len(conflicts),
        "conflicts": conflicts,
    }


class ResolveRequest(BaseModel):
    action: str  # keep_a, keep_b, merge, dismiss
    user: str = "system"


@router.post("/{conflict_id}/resolve")
def resolve(conflict_id: str, req: ResolveRequest):
    """Resolve a conflict with the given action.
    
    AC-F45-4: Resolution actions update the memory base correctly.
    """
    if req.action not in ("keep_a", "keep_b", "merge", "dismiss"):
        raise HTTPException(status_code=400, detail=f"Invalid action: {req.action}. Use keep_a, keep_b, merge, or dismiss.")

    result = resolve_conflict(conflict_id, req.action, req.user)
    if not result:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
    return {"success": True, "conflict": result}
