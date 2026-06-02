"""API Webhook subscriptions router (F-26)."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.subscriptions import (
    create_subscription,
    delete_subscription,
    get_subscriptions,
)

router = APIRouter()


class SubscriptionCreateRequest(BaseModel):
    url: str
    events: Optional[list[str]] = None
    description: str = ""


@router.get("/subscriptions")
def api_get_subscriptions():
    """Get all webhook subscriptions."""
    subs = get_subscriptions()
    return {"subscriptions": subs, "total": len(subs)}


@router.post("/subscriptions")
def api_create_subscription(req: SubscriptionCreateRequest):
    """Register a new webhook subscription."""
    if not req.url:
        raise HTTPException(status_code=400, detail="URL is required")
    sub = create_subscription(url=req.url, events=req.events, description=req.description)
    return {"success": True, "subscription": sub}


@router.delete("/subscriptions/{sub_id}")
def api_delete_subscription(sub_id: str):
    """Delete a webhook subscription."""
    deleted = delete_subscription(sub_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Subscription not found: {sub_id}")
    return {"success": True, "deleted_id": sub_id}
