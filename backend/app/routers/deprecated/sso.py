"""SSO / OIDC Integration router (F-57)."""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.services.sso_service import (
    is_oidc_enabled,
    generate_login_url,
    handle_callback,
    get_current_user,
    invalidate_session,
    get_all_users,
    get_providers,
)

router = APIRouter()


@router.get("/sso/login")
def sso_login():
    """Initiate SSO login. Returns OIDC authorization URL or redirect."""
    if not is_oidc_enabled():
        return {"enabled": False, "message": "SSO/OIDC not configured. Set OIDC_ISSUER_URL and OIDC_CLIENT_ID environment variables."}

    result = generate_login_url()
    return result


@router.get("/sso/callback")
def sso_callback(code: str = Query(...), state: str = Query(...)):
    """Handle OIDC callback after authentication."""
    if not is_oidc_enabled():
        raise HTTPException(status_code=400, detail="OIDC not configured")

    result = handle_callback(code, state)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Authentication failed"))

    return result


@router.get("/sso/providers")
def sso_providers():
    """List configured authentication providers."""
    return {"providers": get_providers(), "oidc_enabled": is_oidc_enabled()}


@router.get("/sso/me")
def sso_me(session_token: str = Query("")):
    """Get current user info from session."""
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token required")

    user = get_current_user(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"user": user}


@router.post("/sso/logout")
def sso_logout(session_token: str = Query("")):
    """Invalidate session (logout)."""
    if session_token:
        invalidate_session(session_token)
    return {"success": True, "message": "Logged out"}


@router.get("/sso/users")
def sso_users():
    """List all provisioned SSO users."""
    return {"users": get_all_users(), "total": len(get_all_users())}
