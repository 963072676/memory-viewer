"""LLM Usage & Cost Dashboard router (F-61)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.llm_usage_service import (
    record_usage,
    get_summary,
    get_timeline,
    get_recent,
    get_config,
    update_config,
)

router = APIRouter()


@router.get("/summary")
def summary(days: int = Query(30, ge=1, le=365)):
    """Get LLM usage summary for the specified period."""
    return get_summary(days=days)


@router.get("/timeline")
def timeline(days: int = Query(30, ge=1, le=365)):
    """Get daily cost timeline for charting."""
    return get_timeline(days=days)


@router.get("/recent")
def recent(page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=200)):
    """Get recent usage records (paginated)."""
    return get_recent(page=page, per_page=per_page)


@router.get("/config")
def config():
    """Get pricing and alert configuration."""
    return get_config()


class UpdateConfigReq(BaseModel):
    pricing: Optional[dict] = None
    alerts: Optional[dict] = None


@router.put("/config")
def update(req: UpdateConfigReq):
    """Update pricing and alert configuration."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    config = update_config(updates)
    return {"success": True, "config": config}


class RecordUsageReq(BaseModel):
    feature: str
    provider: str = "openai"
    model: str = "gpt-4o"
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    memory_id: str = ""
    user_id: str = ""


@router.post("/record")
def record(req: RecordUsageReq):
    """Manually record an LLM usage event (for testing/integration)."""
    result = record_usage(
        feature=req.feature,
        provider=req.provider,
        model=req.model,
        input_tokens=req.input_tokens,
        output_tokens=req.output_tokens,
        latency_ms=req.latency_ms,
        memory_id=req.memory_id,
        user_id=req.user_id,
    )
    return {"success": True, "record": result}
