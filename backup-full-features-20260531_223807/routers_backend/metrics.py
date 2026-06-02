"""Performance metrics API router (F-32)."""

from fastapi import APIRouter

from app.middleware.metrics import metrics_collector

router = APIRouter()


@router.get("")
def get_metrics():
    """Return aggregated performance metrics."""
    return metrics_collector.get_metrics()
