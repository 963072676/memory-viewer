"""Backup & restore API router (F-30)."""

from fastapi import APIRouter, HTTPException

from app.services.backup import create_backup, list_backups, restore_backup

router = APIRouter()


@router.post("/create")
def api_create_backup():
    """Create a new backup."""
    return create_backup()


@router.get("/list")
def api_list_backups():
    """List all available backups."""
    return {"backups": list_backups()}


@router.post("/restore")
def api_restore_backup(backup_id: str):
    """Restore from a specific backup."""
    result = restore_backup(backup_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Backup not found"))
    return result
