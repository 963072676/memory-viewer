"""Audit log API router (F-29)."""

import json
import os
from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()


def _get_log_path() -> str:
    from app.config import settings
    base_dir = os.path.dirname(settings.AUDIT_LOG)
    return os.path.join(base_dir, "audit.jsonl")


@router.get("")
def get_audit_log(
    limit: int = Query(default=50, ge=1, le=500),
    method: Optional[str] = Query(default=None),
    path: Optional[str] = Query(default=None),
    status: Optional[int] = Query(default=None),
):
    """Read audit log entries from audit.jsonl with optional filters."""
    log_path = _get_log_path()
    entries = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

    # Apply filters
    if method:
        entries = [e for e in entries if e.get("method", "").upper() == method.upper()]
    if path:
        entries = [e for e in entries if path in e.get("path", "")]
    if status is not None:
        entries = [e for e in entries if e.get("status") == status]

    # Reverse to get most recent first
    entries = entries[::-1][:limit]

    return {"total": len(entries), "entries": entries}
