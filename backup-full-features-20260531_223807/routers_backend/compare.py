"""Compare API router — multi-agent memory comparison (P31-T1)."""

from fastapi import APIRouter, Query

from app.services.compare_service import compare_two_profiles, list_compare_profiles

router = APIRouter()


@router.get("/profiles")
def compare_profiles_endpoint(
    left: str = Query(..., description="Left profile name"),
    right: str = Query(..., description="Right profile name"),
):
    """
    Compare memories between two profiles (P31-T1).

    Returns diff report: items unique to left, unique to right, common,
    and a similarity score between 0 and 1.
    """
    return compare_two_profiles(left, right)


@router.get("/profiles/list")
def list_compare_profiles_endpoint():
    """List available profiles for comparison."""
    profiles = list_compare_profiles()
    return {"profiles": profiles}