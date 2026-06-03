"""
Metrics / heatmap summary endpoint.

P38: 之前在 deprecated/metrics.py,被 main.py 的 deprecated 列表排除,
前端 dashboard ActivityHeatmap 拉不到数据 → 404。
现在注册为活动 router,返回空数据 + 0 计数,前端可以正常渲染空热图。
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/metrics/heatmap/summary")
def heatmap_summary(
    metric: str = Query("created", description="created | updated | accessed"),
    days: int = Query(365, ge=1, le=730, description="time window in days"),
):
    """
    Return daily activity counts for the heatmap.

    当下没有真实事件源 → 返回全 0 列表,前端 ActivityHeatmap 会显示空白网格(无报错)。
    后续接入事件总线后,这里替换成真实聚合即可。
    """
    today = datetime.now().date()
    data = []
    for i in range(days):
        d = today - timedelta(days=days - 1 - i)
        data.append({"date": d.isoformat(), "count": 0})

    return {
        "metric": metric,
        "days": days,
        "total_events": 0,
        "max_day_count": 0,
        "active_days": 0,
        "total_days": days,
        "data": data,
    }
