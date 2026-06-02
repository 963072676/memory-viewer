"""Profiles API router."""

from fastapi import APIRouter

from app.services import hermes_memory as service

router = APIRouter()


@router.get("")
def get_profiles():
    """Return list of known profile names."""
    return service.get_profiles()
