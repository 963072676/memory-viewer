"""
Webhook configuration endpoint.

P38: 之前在 deprecated/webhook.py,被排除。
前端 SettingsView 拉不到数据 → 404 + 红条 "Not Found"。
现在实现:
  - GET /webhook/config  → 读 ~/.hermes/memory-viewer/webhook.json
  - PUT /webhook/config  → 写回

持久化到 /opt/data/.config/memory-viewer/webhook.json(用户级)。
"""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

CONFIG_DIR = Path(os.environ.get("MEMORY_VIEWER_CONFIG_DIR", "/opt/data/.config/memory-viewer"))
CONFIG_PATH = CONFIG_DIR / "webhook.json"
FEISHU_CONFIG_PATH = CONFIG_DIR / "feishu_notifications.json"

DEFAULT_CONFIG = {
    "enabled": False,
    "webhook_url": "",
    "has_secret": False,
    "events": {"create": True, "update": True, "delete": True},
}


def _load_config(path: Path) -> dict:
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()


def _save_config(path: Path, data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


@router.get("/webhook/config")
def get_webhook_config():
    """Read global webhook config."""
    return _load_config(CONFIG_PATH)


class WebhookConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[dict] = None


@router.put("/webhook/config")
def update_webhook_config(body: WebhookConfigUpdate):
    """Update global webhook config."""
    cfg = _load_config(CONFIG_PATH)
    if body.enabled is not None:
        cfg["enabled"] = body.enabled
    if body.webhook_url is not None:
        cfg["webhook_url"] = body.webhook_url
    if body.events is not None:
        cfg["events"] = {**cfg.get("events", {}), **body.events}
    if body.secret:
        cfg["has_secret"] = True
        # 不把明文 secret 写盘,只标记 has_secret
    _save_config(CONFIG_PATH, cfg)
    return cfg


@router.get("/notifications/feishu/config")
def get_feishu_config():
    """Read Feishu notification config."""
    return _load_config(FEISHU_CONFIG_PATH)


@router.put("/notifications/feishu/config")
def update_feishu_config(body: WebhookConfigUpdate):
    """Update Feishu notification config."""
    cfg = _load_config(FEISHU_CONFIG_PATH)
    if body.enabled is not None:
        cfg["enabled"] = body.enabled
    if body.webhook_url is not None:
        cfg["webhook_url"] = body.webhook_url
    if body.events is not None:
        cfg["events"] = {**cfg.get("events", {}), **body.events}
    if body.secret:
        cfg["has_secret"] = True
    _save_config(FEISHU_CONFIG_PATH, cfg)
    return cfg
