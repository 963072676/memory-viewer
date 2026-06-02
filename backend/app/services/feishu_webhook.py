"""Feishu webhook notification service (F-17)."""

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _build_card(title: str, body: str, msg_type: str = "info") -> dict:
    """Build a Feishu interactive message card."""
    color_map = {
        "info": "blue",
        "success": "green",
        "warning": "orange",
        "danger": "red",
    }
    template = color_map.get(msg_type, "blue")

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title,
                },
                "template": template,
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": body,
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "Memory Viewer v2",
                        }
                    ]
                }
            ],
        }
    }


def send_notification(title: str, body: str, msg_type: str = "info") -> None:
    """Send a Feishu webhook notification (fire-and-forget).

    Args:
        title: Card title text.
        body: Card body content (markdown supported).
        msg_type: One of "info", "success", "warning", "danger".
    """
    webhook_url = getattr(settings, "FEISHU_WEBHOOK_URL", None)
    if not webhook_url:
        logger.debug("FEISHU_WEBHOOK_URL not configured, skipping notification")
        return

    payload = _build_card(title, body, msg_type)

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(webhook_url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Feishu webhook failed: HTTP {resp.status_code} - {resp.text[:200]}")
            else:
                logger.info(f"Feishu notification sent: {title}")
    except Exception as e:
        logger.error(f"Feishu webhook error: {e}")