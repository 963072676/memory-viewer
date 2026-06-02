"""Multi-agent memory comparison API router (F-23)."""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.comparison import compare_profiles, list_profiles

router = APIRouter()


@router.get("/compare")
def api_compare_memories(
    profile_a: str = Query(..., description="First profile name"),
    profile_b: str = Query(..., description="Second profile name"),
):
    """Compare memories between two profiles."""
    return compare_profiles(profile_a, profile_b)


@router.get("/compare/profiles")
def api_list_profiles():
    """List available profiles for comparison."""
    profiles = list_profiles()
    return {"profiles": profiles}
