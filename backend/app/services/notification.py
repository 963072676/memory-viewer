"""Notification service for sending Feishu webhook notifications (F-17)."""

import asyncio
import hashlib
import hmac
import base64
import json
import logging
import time
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "webhook_config.json"


def load_webhook_config() -> dict:
    """Load webhook configuration from JSON file."""
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"enabled": False, "webhook_url": "", "secret": "", "events": {"create": True, "update": True, "delete": True}}


def save_webhook_config(config: dict) -> None:
    """Save webhook configuration to JSON file."""
    import tempfile, os
    dir_name = os.path.dirname(str(_CONFIG_PATH))
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, str(_CONFIG_PATH))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _gen_sign(secret: str, timestamp: int) -> str:
    """Generate Feishu webhook signature."""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def _build_card(operation: str, title: str, memory_id: str, details: str = "") -> dict:
    """Build a Feishu interactive message card."""
    icon_map = {
        "create": "🆕",
        "update": "✏️",
        "delete": "🗑️",
        "archive": "📦",
        "unarchive": "📤",
    }
    op_label_map = {
        "create": "新增记忆",
        "update": "更新记忆",
        "delete": "删除记忆",
        "archive": "归档记忆",
        "unarchive": "取消归档",
    }

    icon = icon_map.get(operation, "📝")
    op_label = op_label_map.get(operation, operation)

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**操作类型**: {icon} {op_label}\n**记忆标题**: {title}\n**记忆 ID**: `{memory_id}`"
            }
        },
        {
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"Memory Viewer v2.1.0 · {time.strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        }
    ]

    if details:
        elements.insert(1, {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**详情**: {details}"
            }
        })

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{icon} Memory Viewer — {op_label}"
                },
                "template": "blue" if operation in ("create", "unarchive") else ("orange" if operation == "update" else "red")
            },
            "elements": elements
        }
    }


async def send_notification(operation: str, title: str, memory_id: str, details: str = "") -> None:
    """Send a notification via Feishu webhook. Non-blocking, logs errors."""
    config = load_webhook_config()

    if not config.get("enabled", False):
        return

    if not config.get("events", {}).get(operation, True):
        return

    webhook_url = config.get("webhook_url", "")
    if not webhook_url:
        logger.warning("Webhook URL not configured, skipping notification")
        return

    payload = _build_card(operation, title, memory_id, details)

    secret = config.get("secret", "")
    if secret:
        timestamp = int(time.time())
        sign = _gen_sign(secret, timestamp)
        payload["timestamp"] = str(timestamp)
        payload["sign"] = sign

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Webhook send failed: HTTP {resp.status_code} - {resp.text}")
            else:
                logger.info(f"Webhook notification sent: {operation} - {title}")
    except Exception as e:
        logger.error(f"Webhook send error: {e}")


def send_notification_sync(operation: str, title: str, memory_id: str, details: str = "") -> None:
    """Synchronous notification sender using httpx.Client (thread-safe)."""
    config = load_webhook_config()

    if not config.get("enabled", False):
        return

    if not config.get("events", {}).get(operation, True):
        return

    webhook_url = config.get("webhook_url", "")
    if not webhook_url:
        logger.warning("Webhook URL not configured, skipping notification")
        return

    payload = _build_card(operation, title, memory_id, details)

    secret = config.get("secret", "")
    if secret:
        timestamp = int(time.time())
        sign = _gen_sign(secret, timestamp)
        payload["timestamp"] = str(timestamp)
        payload["sign"] = sign

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(webhook_url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Webhook send failed: HTTP {resp.status_code} - {resp.text}")
            else:
                logger.info(f"Webhook notification sent: {operation} - {title}")
    except Exception as e:
        logger.error(f"Webhook send error: {e}")
