"""Cross-Agent Knowledge Insights router (F-62)."""

from fastapi import APIRouter, HTTPException, Query

from app.services.cross_agent_service import (
    compute_overlap,
    compute_gaps,
    compute_themes,
    compute_specialization,
    refresh_all,
    invalidate_cache,
)

router = APIRouter()


@router.get("/overlap")
def overlap(threshold: float = Query(0.85, ge=0.0, le=1.0)):
    """Get cross-agent knowledge overlap report."""
    return compute_overlap(threshold=threshold)


@router.get("/gaps")
def gaps():
    """Get per-profile knowledge gap analysis."""
    return compute_gaps()


@router.get("/themes")
def themes():
    """Get collective themes across all profiles."""
    return compute_themes()


@router.get("/specialization")
def specialization():
    """Get profile specialization scores."""
    return compute_specialization()


@router.post("/refresh")
def refresh():
    """Force recalculation of all insights."""
    return refresh_all()


@router.post("/invalidate")
def invalidate():
    """Invalidate the insights cache."""
    invalidate_cache()
    return {"success": True, "message": "Cache invalidated"}
