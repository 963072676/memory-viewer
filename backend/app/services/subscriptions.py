"""API Webhook subscriptions service (F-26)."""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

SUBSCRIPTIONS_FILE = os.path.join(settings.cache_dir, "subscriptions.json")


def _ensure_dir():
    os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)


def _read_subscriptions() -> list[dict]:
    try:
        with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "subscriptions" in data:
            return data["subscriptions"]
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _write_subscriptions(subscriptions: list[dict]) -> None:
    _ensure_dir()
    dir_name = os.path.dirname(SUBSCRIPTIONS_FILE)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"subscriptions": subscriptions}, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, SUBSCRIPTIONS_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def create_subscription(url: str, events: Optional[list[str]] = None, description: str = "") -> dict:
    """Register a new webhook subscription."""
    subscriptions = _read_subscriptions()

    sub_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    subscription = {
        "id": sub_id,
        "url": url,
        "events": events or ["create", "update", "delete"],
        "description": description,
        "enabled": True,
        "created_at": now,
    }

    subscriptions.append(subscription)
    _write_subscriptions(subscriptions)
    return subscription


def delete_subscription(sub_id: str) -> bool:
    """Delete a webhook subscription by ID."""
    subscriptions = _read_subscriptions()
    original_len = len(subscriptions)
    subscriptions = [s for s in subscriptions if s.get("id") != sub_id]
    if len(subscriptions) == original_len:
        return False
    _write_subscriptions(subscriptions)
    return True


def get_subscriptions() -> list[dict]:
    """Get all webhook subscriptions."""
    return _read_subscriptions()


def notify_subscribers(operation: str, title: str, memory_id: str) -> None:
    """Push notifications to all matching webhook subscribers."""
    subscriptions = _read_subscriptions()
    for sub in subscriptions:
        if not sub.get("enabled", True):
            continue
        if operation not in sub.get("events", []):
            continue
        url = sub.get("url", "")
        if not url:
            continue
        payload = {
            "event": operation,
            "memory_id": memory_id,
            "title": title,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        try:
            with httpx.Client(timeout=5) as client:
                client.post(url, json=payload)
        except Exception:
            pass  # Don't let subscriber failures break main flow
