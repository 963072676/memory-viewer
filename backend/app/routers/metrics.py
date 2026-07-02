"""
Metrics / heatmap summary endpoint.

P38: 之前在 deprecated/metrics.py,被 main.py 的 deprecated 列表排除,
前端 dashboard ActivityHeatmap 拉不到数据 → 404。
现在注册为活动 router,调用真实 heatmap 服务聚合实际数据。
"""
from fastapi import APIRouter, Query

from app.services.heatmap import get_heatmap_summary

router = APIRouter()


@router.get("/metrics/heatmap/summary")
def heatmap_summary(
    metric: str = Query("created", description="created | updated | accessed"),
    days: int = Query(365, ge=1, le=730, description="time window in days"),
):
    """Return daily activity counts for the heatmap from real memory data."""
    return get_heatmap_summary(metric, days)
