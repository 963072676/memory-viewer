"""Memory activity heatmap API router (F-37)."""

from fastapi import APIRouter, Query

from app.services.heatmap import get_heatmap_data, get_heatmap_summary

router = APIRouter()


@router.get("")
def heatmap(
    metric: str = Query(default="created", pattern="^(created|accessed|modified)$"),
    days: int = Query(default=365, ge=7, le=730),
):
    """Get memory activity heatmap data.

    Returns daily counts for the specified metric over the given time period.
    Metric options: created, accessed, modified.
    """
    return get_heatmap_data(metric=metric, days=days)


@router.get("/summary")
def heatmap_summary(
    metric: str = Query(default="created", pattern="^(created|accessed|modified)$"),
    days: int = Query(default=365, ge=7, le=730),
):
    """Get heatmap data with summary statistics."""
    return get_heatmap_summary(metric=metric, days=days)
