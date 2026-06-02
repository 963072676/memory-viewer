"""Version history API router (F-24)."""

from fastapi import APIRouter, HTTPException, Query

from app.services.versioning import diff_versions, get_version_detail, get_versions, rollback_to_version

router = APIRouter()


@router.get("/{memory_id}/versions")
def api_get_versions(memory_id: str):
    """Get all version snapshots for a memory."""
    versions = get_versions(memory_id)
    return {"memory_id": memory_id, "versions": versions, "total": len(versions)}


@router.get("/{memory_id}/versions/{version}")
def api_get_version_detail(memory_id: str, version: int):
    """Get a single version snapshot detail."""
    detail = get_version_detail(memory_id, version)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    return detail


@router.get("/{memory_id}/versions/diff")
def api_diff_versions(memory_id: str, from_: int = Query(alias="from"), to: int = Query()):
    """Return diff between two versions."""
    result = diff_versions(memory_id, from_, to)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.post("/{memory_id}/versions/{version}/rollback")
def api_rollback_version(memory_id: str, version: int):
    """Rollback a memory to a specific version."""
    result = rollback_to_version(memory_id, version)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    return result
