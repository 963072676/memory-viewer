"""API Usage Analytics router (F-49)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query

from app.middleware.usage_tracker import usage_tracker

router = APIRouter()


@router.get("/usage")
def usage_summary(period: str = Query(default="24h", pattern="^(1h|24h|7d|30d)$")):
    """Get usage summary for a time period.
    
    AC-F49-1: All API requests tracked without impacting performance.
    AC-F49-2: Usage dashboard shows request volume, latency, error rate.
    AC-F49-4: Time range filtering works (24h, 7d, 30d).
    """
    return usage_tracker.get_usage_summary(period)


@router.get("/endpoints")
def endpoint_breakdown(period: str = Query(default="24h", pattern="^(1h|24h|7d|30d)$")):
    """Get per-endpoint usage breakdown.
    
    AC-F49-2: Usage dashboard shows top endpoints.
    """
    return {
        "endpoints": usage_tracker.get_endpoint_breakdown(period),
        "period": period,
    }


@router.get("/costs")
def cost_breakdown():
    """Get LLM token usage and estimated cost.
    
    AC-F49-3: LLM token usage broken down by feature.
    AC-F49-6: Cost estimation configurable (per-token pricing).
    """
    return usage_tracker.get_cost_breakdown()


@router.get("/trends")
def trends(
    period: str = Query(default="24h", pattern="^(1h|24h|7d|30d)$"),
    granularity: str = Query(default="hourly", pattern="^(hourly|daily)$"),
):
    """Get time-series data for charts.
    
    AC-F49-4: Time range filtering works.
    """
    return {
        "trends": usage_tracker.get_trends(period, granularity),
        "period": period,
        "granularity": granularity,
    }


class CostConfigReq(BaseModel):
    input_cost_per_1k: float = 0.0015
    output_cost_per_1k: float = 0.002


@router.put("/costs/config")
def update_cost_config(req: CostConfigReq):
    """Update LLM cost configuration.
    
    AC-F49-6: Cost estimation configurable.
    """
    usage_tracker.set_cost_config(req.input_cost_per_1k, req.output_cost_per_1k)
    return {"success": True, "input_cost": req.input_cost_per_1k, "output_cost": req.output_cost_per_1k}
