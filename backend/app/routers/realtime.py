"""Realtime memory update API."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.services.realtime_service import build_event, manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/memories")
async def websocket_memories(
    websocket: WebSocket,
    workspace_id: str = Query(default="default"),
    user_id: str = Query(default="anonymous"),
):
    """Subscribe to realtime memory and presence events."""
    await manager.connect(websocket, workspace_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue

            message_type = message.get("type", "")
            if message_type == "ping":
                await websocket.send_json({
                    "event": "pong",
                    "timestamp": asyncio.get_event_loop().time(),
                })
            elif message_type == "presence":
                await manager.broadcast(
                    workspace_id,
                    build_event(
                        "user.presence",
                        {
                            "user_id": user_id,
                            "status": message.get("status", "online"),
                            "workspace": workspace_id,
                        },
                        workspace_id,
                    ),
                    exclude=websocket,
                )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, workspace_id)
        await manager.broadcast(
            workspace_id,
            build_event(
                "user.presence",
                {
                    "user_id": user_id,
                    "status": "offline",
                    "workspace": workspace_id,
                },
                workspace_id,
            ),
        )
    except Exception as exc:
        logger.warning("Realtime websocket closed unexpectedly: %s", exc)
        await manager.disconnect(websocket, workspace_id)


@router.get("/realtime/status")
def realtime_status():
    """Return realtime service status for UI health badges."""
    return manager.get_status()


@router.get("/realtime/sse")
async def sse_fallback(workspace_id: str = Query(default="default")):
    """SSE heartbeat fallback for clients that cannot use WebSocket."""

    async def event_generator():
        while True:
            yield f"data: {json.dumps({'event': 'heartbeat', 'workspace': workspace_id})}\n\n"
            await asyncio.sleep(manager._heartbeat_interval)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
