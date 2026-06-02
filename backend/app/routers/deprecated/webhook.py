"""Webhook configuration API router — F-17."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.notification import load_webhook_config, save_webhook_config
from app.services.feishu_webhook import send_notification as feishu_send

router = APIRouter()


class WebhookConfigResponse(BaseModel):
    """Response for GET /api/webhook/config."""
    enabled: bool
    webhook_url: str
    has_secret: bool
    events: dict


class WebhookConfigUpdate(BaseModel):
    """Request body for PUT /api/webhook/config."""
    enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[dict] = None


@router.get("/config", response_model=WebhookConfigResponse)
def get_webhook_config():
    """Get webhook configuration (secret is masked)."""
    config = load_webhook_config()
    return {
        "enabled": config.get("enabled", False),
        "webhook_url": config.get("webhook_url", ""),
        "has_secret": bool(config.get("secret", "")),
        "events": config.get("events", {"create": True, "update": True, "delete": True}),
    }


@router.put("/config", response_model=WebhookConfigResponse)
def update_webhook_config(req: WebhookConfigUpdate):
    """Update webhook configuration."""
    config = load_webhook_config()

    if req.enabled is not None:
        config["enabled"] = req.enabled
    if req.webhook_url is not None:
        config["webhook_url"] = req.webhook_url
    if req.secret is not None:
        config["secret"] = req.secret
    if req.events is not None:
        config["events"] = req.events

    save_webhook_config(config)

    return {
        "enabled": config.get("enabled", False),
        "webhook_url": config.get("webhook_url", ""),
        "has_secret": bool(config.get("secret", "")),
        "events": config.get("events", {"create": True, "update": True, "delete": True}),
    }


@router.post("/feishu/test")
def test_feishu_webhook():
    """Send a test Feishu message card to verify webhook configuration."""
    feishu_send(
        "🧪 Test Notification",
        "This is a test message from **Memory Viewer v2**.\n\nIf you see this, the Feishu webhook is configured correctly!",
        msg_type="info",
    )
    return {"success": True, "message": "Test notification sent"}
