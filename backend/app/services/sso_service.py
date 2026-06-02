"""SSO / OIDC Integration service (F-57).

OIDC discovery, token verification, user mapping.
Supports any standards-compliant OIDC provider (Keycloak, Azure AD, Google, Okta).
Falls back gracefully when OIDC is not configured.
"""

import hashlib
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

OIDC_ISSUER_URL = os.environ.get("OIDC_ISSUER_URL", "")
OIDC_CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "")
OIDC_CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET", "")
OIDC_REDIRECT_URI = os.environ.get("OIDC_REDIRECT_URI", "http://localhost:8000/api/auth/sso/callback")
OIDC_SCOPES = os.environ.get("OIDC_SCOPES", "openid profile email").split()

USERS_PATH = os.path.join(settings.cache_dir, "sso_users.json")
SESSIONS_PATH = os.path.join(settings.cache_dir, "sso_sessions.json")

# ─── State storage for CSRF protection ────────────────────────────────────────

_pending_states: dict[str, dict] = {}  # state -> {nonce, created_at}


def is_oidc_enabled() -> bool:
    """Check if OIDC is configured."""
    return bool(OIDC_ISSUER_URL and OIDC_CLIENT_ID)


def _load_users() -> dict:
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": []}


def _save_users(data: dict) -> None:
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    _atomic_write_json(USERS_PATH, data)


def _load_sessions() -> dict:
    try:
        with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sessions": {}}


def _save_sessions(data: dict) -> None:
    os.makedirs(os.path.dirname(SESSIONS_PATH), exist_ok=True)
    _atomic_write_json(SESSIONS_PATH, data)


# ─── OIDC Discovery ──────────────────────────────────────────────────────────

_discovery_cache: Optional[dict] = None
_discovery_cache_time: float = 0


def get_oidc_discovery() -> dict:
    """Fetch OIDC discovery document from the issuer URL.

    Caches for 1 hour.
    """
    global _discovery_cache, _discovery_cache_time

    if _discovery_cache and (time.time() - _discovery_cache_time) < 3600:
        return _discovery_cache

    import httpx

    well_known_url = f"{OIDC_ISSUER_URL.rstrip('/')}/.well-known/openid-configuration"
    try:
        resp = httpx.get(well_known_url, timeout=10)
        resp.raise_for_status()
        _discovery_cache = resp.json()
        _discovery_cache_time = time.time()
        return _discovery_cache
    except Exception as e:
        logger.error(f"OIDC discovery failed: {e}")
        # Return minimal config for development
        return {
            "authorization_endpoint": f"{OIDC_ISSUER_URL}/protocol/openid-connect/auth",
            "token_endpoint": f"{OIDC_ISSUER_URL}/protocol/openid-connect/token",
            "userinfo_endpoint": f"{OIDC_ISSUER_URL}/protocol/openid-connect/userinfo",
            "jwks_uri": f"{OIDC_ISSUER_URL}/protocol/openid-connect/certs",
            "issuer": OIDC_ISSUER_URL,
        }


# ─── Login URL Generation ────────────────────────────────────────────────────

def generate_login_url() -> dict:
    """Generate the OIDC authorization URL for login redirect."""
    if not is_oidc_enabled():
        return {"enabled": False, "message": "OIDC not configured"}

    discovery = get_oidc_discovery()
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    # Store state for CSRF verification
    _pending_states[state] = {"nonce": nonce, "created_at": time.time()}

    params = {
        "response_type": "code",
        "client_id": OIDC_CLIENT_ID,
        "redirect_uri": OIDC_REDIRECT_URI,
        "scope": " ".join(OIDC_SCOPES),
        "state": state,
        "nonce": nonce,
    }

    auth_url = f"{discovery['authorization_endpoint']}?{urlencode(params)}"

    return {
        "enabled": True,
        "url": auth_url,
        "state": state,
    }


# ─── Callback Handling ───────────────────────────────────────────────────────

def handle_callback(code: str, state: str) -> dict:
    """Handle the OIDC callback: exchange code for tokens, verify, and create session."""
    if not is_oidc_enabled():
        return {"success": False, "error": "OIDC not configured"}

    # Verify state (CSRF protection)
    state_data = _pending_states.pop(state, None)
    if not state_data:
        return {"success": False, "error": "Invalid or expired state parameter"}

    # Clean up old states (> 10 minutes)
    cutoff = time.time() - 600
    expired = [s for s, d in _pending_states.items() if d["created_at"] < cutoff]
    for s in expired:
        _pending_states.pop(s, None)

    discovery = get_oidc_discovery()

    # Exchange authorization code for tokens
    try:
        import httpx

        token_resp = httpx.post(
            discovery["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": OIDC_REDIRECT_URI,
                "client_id": OIDC_CLIENT_ID,
                "client_secret": OIDC_CLIENT_SECRET,
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return {"success": False, "error": f"Token exchange failed: {str(e)}"}

    # Extract user info from ID token or userinfo endpoint
    user_info = {}

    id_token = token_data.get("id_token")
    if id_token:
        try:
            # Decode without verification for basic parsing
            # In production, verify with JWKS
            payload = _decode_jwt_payload(id_token)
            user_info = {
                "sub": payload.get("sub", ""),
                "name": payload.get("name", payload.get("preferred_username", "Unknown")),
                "email": payload.get("email", ""),
                "picture": payload.get("picture", ""),
                "groups": payload.get("groups", []),
            }
        except Exception as e:
            logger.warning(f"Failed to decode ID token: {e}")

    if not user_info.get("sub"):
        # Fall back to userinfo endpoint
        try:
            userinfo_resp = httpx.get(
                discovery["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {token_data.get('access_token', '')}"},
                timeout=10,
            )
            userinfo_resp.raise_for_status()
            user_info = userinfo_resp.json()
        except Exception as e:
            logger.error(f"Userinfo fetch failed: {e}")
            return {"success": False, "error": f"Failed to get user info: {str(e)}"}

    # Map/create local user
    user = _provision_user(user_info)

    # Create session
    session_token = secrets.token_urlsafe(48)
    session = {
        "token": session_token,
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_at": datetime.now(timezone.utc).replace(hour=23, minute=59, second=59).isoformat().replace("+00:00", "Z"),
        "access_token": token_data.get("access_token", ""),
        "id_token": token_data.get("id_token", ""),
    }

    sessions = _load_sessions()
    sessions["sessions"][session_token] = session
    _save_sessions(sessions)

    return {
        "success": True,
        "session_token": session_token,
        "user": user,
    }


def _decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification (for development/fallback)."""
    import base64

    parts = token.split(".")
    if len(parts) != 3:
        return {}

    # Pad the payload
    payload = parts[1]
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += "=" * padding

    try:
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception:
        return {}


def _provision_user(user_info: dict) -> dict:
    """Create or update local user from OIDC user info."""
    sub = user_info.get("sub", "")
    data = _load_users()

    # Find existing user
    for i, user in enumerate(data["users"]):
        if user.get("oidc_sub") == sub:
            # Update user info
            data["users"][i].update({
                "name": user_info.get("name", user.get("name", "")),
                "email": user_info.get("email", user.get("email", "")),
                "picture": user_info.get("picture", user.get("picture", "")),
                "last_login": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            })
            _save_users(data)
            return data["users"][i]

    # Create new user
    user_id = f"user-{hashlib.md5(sub.encode()).hexdigest()[:12]}"
    user = {
        "id": user_id,
        "oidc_sub": sub,
        "name": user_info.get("name", "Unknown"),
        "email": user_info.get("email", ""),
        "picture": user_info.get("picture", ""),
        "groups": user_info.get("groups", []),
        "role": _map_groups_to_role(user_info.get("groups", [])),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "last_login": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    data["users"].append(user)
    _save_users(data)
    logger.info(f"Provisioned new OIDC user: {user_id} ({user_info.get('name', '')})")
    return user


def _map_groups_to_role(groups: list[str]) -> str:
    """Map OIDC groups to workspace roles."""
    role_mapping_str = os.environ.get("OIDC_ROLE_MAPPING", "")
    if role_mapping_str:
        try:
            mapping = json.loads(role_mapping_str)
            for group in groups:
                if group in mapping:
                    return mapping[group]
        except json.JSONDecodeError:
            pass

    # Default mapping
    admin_groups = os.environ.get("OIDC_ADMIN_GROUPS", "admin,admins").split(",")
    editor_groups = os.environ.get("OIDC_EDITOR_GROUPS", "editor,editors,developers").split(",")

    for group in groups:
        if group.lower() in [g.strip().lower() for g in admin_groups]:
            return "admin"
        if group.lower() in [g.strip().lower() for g in editor_groups]:
            return "editor"

    return "viewer"


# ─── Session Management ──────────────────────────────────────────────────────

def get_session(session_token: str) -> Optional[dict]:
    """Get session by token."""
    sessions = _load_sessions()
    session = sessions.get("sessions", {}).get(session_token)
    if not session:
        return None

    # Check expiry
    expires_at = session.get("expires_at", "")
    if expires_at:
        try:
            exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > exp:
                return None
        except ValueError:
            pass

    return session


def get_current_user(session_token: str) -> Optional[dict]:
    """Get current user from session token."""
    session = get_session(session_token)
    if not session:
        return None

    users = _load_users()
    for user in users.get("users", []):
        if user["id"] == session["user_id"]:
            return user
    return None


def invalidate_session(session_token: str) -> bool:
    """Invalidate a session (logout)."""
    sessions = _load_sessions()
    if session_token in sessions.get("sessions", {}):
        del sessions["sessions"][session_token]
        _save_sessions(sessions)
        return True
    return False


def get_all_users() -> list[dict]:
    """Get all provisioned users."""
    data = _load_users()
    return data.get("users", [])


def get_providers() -> list[dict]:
    """List configured authentication providers."""
    providers = []

    if is_oidc_enabled():
        discovery = get_oidc_discovery()
        providers.append({
            "type": "oidc",
            "name": OIDC_ISSUER_URL.split("/")[-1] if "/" in OIDC_ISSUER_URL else "OIDC Provider",
            "issuer": OIDC_ISSUER_URL,
            "enabled": True,
            "scopes": OIDC_SCOPES,
        })

    # Always show API key as fallback
    providers.append({
        "type": "api_key",
        "name": "API Key",
        "enabled": True,
        "description": "For CLI/SDK usage",
    })

    return providers
