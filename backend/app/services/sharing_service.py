"""Memory Sharing service (F-42) — Generate shareable links with access control.

Share links use UUIDs, support access levels, expiration, and optional password protection.
Auto-applies PII masking on share (depends on F-41).
"""

import json
import os
import time
import uuid
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.services.redaction_service import detect_pii, mask_text

logger = logging.getLogger(__name__)

_SHARES_PATH = os.path.join(settings.cache_dir, "shares.json")


@dataclass
class ShareLink:
    """A share link record."""
    share_id: str
    memory_id: str
    memory_title: str
    access_level: str           # "view" | "comment" | "edit"
    created_at: str             # ISO timestamp
    expires_at: Optional[str]   # ISO timestamp or None for never
    password_hash: Optional[str]  # hashed password or None
    shared_by: str = "user"
    access_count: int = 0
    last_accessed: Optional[str] = None
    pii_masked: bool = True
    batch_ids: list[str] = field(default_factory=list)


def _load_shares() -> dict[str, dict]:
    """Load shares from JSON file."""
    try:
        with open(_SHARES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_shares(shares: dict[str, dict]) -> None:
    """Save shares to JSON file atomically."""
    os.makedirs(os.path.dirname(_SHARES_PATH), exist_ok=True)
    fd, tmp_path = tempfile_mkstemp(_SHARES_PATH)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(shares, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, _SHARES_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def tempfile_mkstemp(path: str):
    """Create a temp file next to path."""
    import tempfile
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    return tempfile.mkstemp(dir=dir_name, suffix=".tmp")


def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


EXPIRY_OPTIONS = {
    "1h": 3600,
    "1d": 86400,
    "7d": 604800,
    "30d": 2592000,
    "never": None,
}


def create_share(
    memory_id: str,
    memory_title: str,
    memory_content: str,
    access_level: str = "view",
    expires_in: str = "7d",
    password: Optional[str] = None,
    batch_ids: Optional[list[str]] = None,
) -> dict:
    """Create a share link for a memory.
    
    Args:
        memory_id: ID of the memory to share
        memory_title: Title of the memory
        memory_content: Content of the memory (for PII masking)
        access_level: "view" | "comment" | "edit"
        expires_in: "1h" | "1d" | "7d" | "30d" | "never"
        password: Optional password protection
        batch_ids: Optional list of memory IDs for batch sharing
    
    Returns:
        Share link info dict
    """
    share_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Calculate expiration
    expires_at = None
    if expires_in != "never":
        seconds = EXPIRY_OPTIONS.get(expires_in, 604800)
        expires_at = now.timestamp() + seconds

    # Hash password if provided
    pw_hash = _hash_password(password) if password else None

    # Auto-apply PII masking flag
    content_text = f"{memory_title} {memory_content}"
    pii_detected = len(detect_pii(content_text)) > 0

    share_data = {
        "share_id": share_id,
        "memory_id": memory_id,
        "memory_title": memory_title,
        "access_level": access_level,
        "created_at": now.isoformat(),
        "expires_at": datetime.fromtimestamp(expires_at, timezone.utc).isoformat() if expires_at else None,
        "password_hash": pw_hash,
        "shared_by": "user",
        "access_count": 0,
        "last_accessed": None,
        "pii_masked": pii_detected,
        "batch_ids": batch_ids or [],
    }

    shares = _load_shares()
    shares[share_id] = share_data
    _save_shares(shares)

    logger.info(f"Share created: {share_id} for memory {memory_id}")

    return {
        "share_id": share_id,
        "share_url": f"/shared/{share_id}",
        "access_level": access_level,
        "expires_at": share_data["expires_at"],
        "password_protected": bool(password),
        "pii_masked": pii_detected,
    }


def get_share(share_id: str, password: Optional[str] = None) -> Optional[dict]:
    """Retrieve a share link. Returns None if expired or not found.
    
    Validates password if share is password-protected.
    """
    shares = _load_shares()
    share = shares.get(share_id)

    if not share:
        return None

    # Check expiration
    if share.get("expires_at"):
        expires = datetime.fromisoformat(share["expires_at"])
        if datetime.now(timezone.utc) > expires:
            return None  # Expired

    # Check password
    if share.get("password_hash"):
        if not password:
            return {"password_required": True}
        if _hash_password(password) != share["password_hash"]:
            return {"invalid_password": True}

    # Update access count
    share["access_count"] = share.get("access_count", 0) + 1
    share["last_accessed"] = datetime.now(timezone.utc).isoformat()
    shares[share_id] = share
    _save_shares(shares)

    return share


def list_shares(memory_id: Optional[str] = None) -> list[dict]:
    """List all active (non-expired) share links."""
    shares = _load_shares()
    now = datetime.now(timezone.utc)
    result = []

    for sid, share in shares.items():
        # Filter expired
        if share.get("expires_at"):
            expires = datetime.fromisoformat(share["expires_at"])
            if now > expires:
                continue

        # Filter by memory_id
        if memory_id and share.get("memory_id") != memory_id:
            continue

        result.append(share)

    # Sort by creation time descending
    result.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return result


def delete_share(share_id: str) -> bool:
    """Revoke/delete a share link. Returns True if found and deleted."""
    shares = _load_shares()
    if share_id not in shares:
        return False

    del shares[share_id]
    _save_shares(shares)
    logger.info(f"Share revoked: {share_id}")
    return True


def apply_pii_masking(memory: dict) -> dict:
    """Apply PII masking to a memory before sharing.
    
    AC-F42-6: Auto-applies PII masking on share.
    """
    content = memory.get("content", "")
    title = memory.get("title", "")
    text = f"{title}\n{content}"
    matches = detect_pii(text)

    if matches:
        masked_text = mask_text(text, matches)
        parts = masked_text.split("\n", 1)
        masked_title = parts[0] if parts else title
        masked_content = parts[1] if len(parts) > 1 else content

        return {
            **memory,
            "title": masked_title,
            "content": masked_content,
            "pii_masked": True,
            "pii_count": len(matches),
        }

    return memory
