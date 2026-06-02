"""Hermes Memory API router."""

from fastapi import APIRouter

from app.services import hermes_memory as service

router = APIRouter()


@router.get("")
def get_hermes_memory():
    """Read hermes built-in memory files (global + per-profile)."""
    return service.get_hermes_memory()
