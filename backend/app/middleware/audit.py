"""Audit middleware (F-29) — logs every API request to audit.jsonl."""

import json
import os
import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse


class AuditMiddleware(BaseHTTPMiddleware):
    """Records method, path, body, status, and time for every API request."""

    def __init__(self, app, log_path: str = None):
        super().__init__(app)
        if log_path is None:
            from app.config import settings
            # Use JSONL format alongside existing audit.json
            base_dir = os.path.dirname(settings.AUDIT_LOG)
            log_path = os.path.join(base_dir, "audit.jsonl")
        self.log_path = log_path

    async def dispatch(self, request: Request, call_next):
        # Skip non-API and static file requests
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        start = time.time()

        # Read body for audit (only for mutating requests)
        body_str = ""
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8", errors="replace")[:2000]
            except Exception:
                body_str = "<unreadable>"

        response = await call_next(request)

        elapsed_ms = round((time.time() - start) * 1000, 2)

        entry = {
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else "",
            "body": body_str,
            "status": response.status_code,
            "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "duration_ms": elapsed_ms,
        }

        # Append to JSONL file
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Don't break requests on audit failure

        return response
