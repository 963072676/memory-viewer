"""Real-time Updates API router (F-55) — WebSocket and SSE endpoints."""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse

from app.services.realtime_service import manager, heartbeat_loop, build_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/memories")
async def websocket_memories(websocket: WebSocket, workspace_id: str = Query(default="default"), user_id: str = Query(default="anonymous")):
    """WebSocket endpoint for real-time memory updates.

    AC-F55-1: WebSocket endpoint for live updates.
    AC-F55-2: Events for memory CRUD and presence.
    AC-F55-3: Heartbeat every 30s.
    AC-F55-4: Per-workspace channels.
    """
    ws_id = await manager.connect(websocket, workspace_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({"event": "pong", "timestamp": asyncio.get_event_loop().time()})
                elif msg_type == "presence":
                    await manager.broadcast(workspace_id, build_event("user.presence", {
                        "user_id": user_id,
                        "status": msg.get("status", "online"),
                        "workspace": workspace_id,
                    }), exclude=websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket, workspace_id)
        await manager.broadcast(workspace_id, build_event("user.presence", {
            "user_id": user_id,
            "status": "offline",
            "workspace": workspace_id,
        }))


@router.get("/realtime/status")
def realtime_status():
    """Get realtime service status.

    AC-F55-5: Connection status visible.
    """
    return manager.get_status()


@router.get("/realtime/sse")
async def sse_fallback(workspace_id: str = Query(default="default")):
    """SSE fallback endpoint for environments without WebSocket support.

    AC-F55-5: Fallback SSE endpoint.
    """
    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()
        # Simple SSE that emits heartbeat
        while True:
            yield f"data: {json.dumps({'event': 'heartbeat', 'workspace': workspace_id})}\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
