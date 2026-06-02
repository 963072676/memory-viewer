"""Workspace context middleware (F-54) — Extract workspace context from requests."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class WorkspaceContextMiddleware(BaseHTTPMiddleware):
    """Extract workspace ID from request headers or query params."""

    async def dispatch(self, request: Request, call_next):
        workspace_id = request.headers.get("X-Workspace-Id") or request.query_params.get("workspace_id", "default")
        request.state.workspace_id = workspace_id
        user_id = request.headers.get("X-User-Id", "anonymous")
        request.state.user_id = user_id
        response = await call_next(request)
        return response
