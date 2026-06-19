"""AI Copilot API for provider-neutral memory actions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.errors import MemoryProviderError
from app.services.copilot import CopilotAction, run_copilot_action

router = APIRouter()


class CopilotRunRequest(BaseModel):
    action: CopilotAction
    provider: str = ""
    sessionId: str = ""
    limit: int = Field(default=200, ge=1, le=500)
    maxChars: int = Field(default=800, ge=120, le=4000)


def _provider_error(exc: MemoryProviderError) -> HTTPException:
    status_code = 404 if exc.code == "provider_config_error" else 400
    return HTTPException(status_code=status_code, detail=exc.to_dict())


@router.post("/run")
async def run_memory_copilot(req: CopilotRunRequest):
    """Run one AI Copilot memory action through the unified memory layer."""
    try:
        return await run_copilot_action(
            req.action,
            provider=req.provider,
            session_id=req.sessionId,
            limit=req.limit,
            max_chars=req.maxChars,
        )
    except MemoryProviderError as exc:
        raise _provider_error(exc) from exc
