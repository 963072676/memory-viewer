"""Real-time Updates service (F-55) — WebSocket and SSE for live memory updates.

WebSocket endpoint: ws://host/ws/memories
Events: memory.created/updated/deleted/archived, user.presence
Heartbeat 30s, per-workspace channels.
Fallback SSE endpoint.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with per-workspace channels."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}  # workspace_id -> [ws]
        self._user_ws: dict[str, str] = {}  # ws_id -> user_id
        self._presence: dict[str, dict] = {}  # user_id -> {status, last_seen, workspace}
        self._heartbeat_interval = 30  # seconds
        self._ws_counter = 0

    async def connect(self, websocket: WebSocket, workspace_id: str = "default", user_id: str = "anonymous"):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self._ws_counter += 1
        ws_id = f"ws-{self._ws_counter}"

        if workspace_id not in self._connections:
            self._connections[workspace_id] = []
        self._connections[workspace_id].append(websocket)
        self._user_ws[ws_id] = user_id

        # Update presence
        self._presence[user_id] = {
            "status": "online",
            "last_seen": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "workspace": workspace_id,
            "ws_id": ws_id,
        }

        # Notify others
        await self.broadcast(workspace_id, {
            "event": "user.presence",
            "data": {"user_id": user_id, "status": "online", "workspace": workspace_id},
        }, exclude=websocket)

        return ws_id

    async def disconnect(self, websocket: WebSocket, workspace_id: str = "default"):
        """Remove a WebSocket connection."""
        if workspace_id in self._connections:
            if websocket in self._connections[workspace_id]:
                self._connections[workspace_id].remove(websocket)

        # Find and update user presence
        user_to_remove = None
        for ws_id, uid in self._user_ws.items():
            # We track via presence
            pass

        # Clean up empty workspaces
        if workspace_id in self._connections and not self._connections[workspace_id]:
            del self._connections[workspace_id]

    async def broadcast(self, workspace_id: str, message: dict, exclude: Optional[WebSocket] = None):
        """Broadcast a message to all connections in a workspace."""
        connections = self._connections.get(workspace_id, [])
        dead = []
        for ws in connections:
            if ws == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        # Clean up dead connections
        for ws in dead:
            if ws in connections:
                connections.remove(ws)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    def get_online_users(self, workspace_id: Optional[str] = None) -> list[dict]:
        """Get currently online users."""
        users = []
        for user_id, info in self._presence.items():
            if info.get("status") == "online":
                if workspace_id is None or info.get("workspace") == workspace_id:
                    users.append({"user_id": user_id, **info})
        return users

    def get_connection_count(self) -> int:
        """Get total active connections."""
        return sum(len(conns) for conns in self._connections.values())

    def get_status(self) -> dict:
        """Get realtime service status."""
        return {
            "total_connections": self.get_connection_count(),
            "workspaces_active": len(self._connections),
            "online_users": len([u for u in self._presence.values() if u.get("status") == "online"]),
            "heartbeat_interval": self._heartbeat_interval,
        }

    async def send_heartbeat(self):
        """Send heartbeat to all connections."""
        for workspace_id, connections in self._connections.items():
            dead = []
            for ws in connections:
                try:
                    await ws.send_json({"event": "heartbeat", "timestamp": time.time()})
                except Exception:
                    dead.append(ws)
            for ws in dead:
                connections.remove(ws)


# Singleton
manager = ConnectionManager()


async def heartbeat_loop():
    """Background heartbeat loop."""
    while True:
        await asyncio.sleep(manager._heartbeat_interval)
        try:
            await manager.send_heartbeat()
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")


def build_event(event_type: str, data: dict, workspace_id: str = "default") -> dict:
    """Build a standard event message."""
    return {
        "event": event_type,
        "data": data,
        "workspace_id": workspace_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


async def emit_memory_event(event_type: str, memory: dict, workspace_id: str = "default"):
    """Emit a memory-related event to workspace subscribers."""
    event = build_event(event_type, {
        "memory_id": memory.get("id"),
        "title": memory.get("title", ""),
        "type": memory.get("type", ""),
    }, workspace_id)
    await manager.broadcast(workspace_id, event)
