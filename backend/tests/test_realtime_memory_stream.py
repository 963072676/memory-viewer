"""Tests for the formal realtime memory update stream."""

from app.services.realtime_service import manager


def _reset_realtime_manager():
    manager._connections.clear()
    manager._ws_meta.clear()
    manager._presence.clear()


def test_realtime_status_route_is_registered(client):
    _reset_realtime_manager()

    response = client.get("/api/realtime/status")

    assert response.status_code == 200
    data = response.json()
    assert data["total_connections"] == 0
    assert data["heartbeat_interval"] == 30
    assert data["online_users_detail"] == []


def test_unified_memory_crud_emits_realtime_events(client):
    _reset_realtime_manager()

    with client.websocket_connect("/api/ws/memories?workspace_id=default&user_id=test-ui") as websocket:
        websocket.send_json({"type": "ping"})
        assert websocket.receive_json()["event"] == "pong"

        create_response = client.post(
            "/api/memories",
            json={
                "provider": "agentmemory",
                "title": "Realtime Memory",
                "content": "Created for realtime stream",
                "type": "fact",
                "tags": ["Realtime"],
            },
        )
        assert create_response.status_code == 200
        created = create_response.json()["memory"]

        created_event = websocket.receive_json()
        assert created_event["event"] == "memory.created"
        assert created_event["workspace_id"] == "default"
        assert created_event["data"]["memory_id"] == created["id"]
        assert created_event["data"]["provider"] == "agentmemory"
        assert created_event["data"]["memory"]["content"] == "Created for realtime stream"

        update_response = client.put(
            f"/api/memories/{created['id']}",
            json={
                "provider": "agentmemory",
                "content": "Updated for realtime stream",
                "tags": ["Realtime", "Updated"],
            },
        )
        assert update_response.status_code == 200

        updated_event = websocket.receive_json()
        assert updated_event["event"] == "memory.updated"
        assert updated_event["data"]["memory_id"] == created["id"]
        assert updated_event["data"]["memory"]["content"] == "Updated for realtime stream"

        delete_response = client.delete(f"/api/memories/{created['id']}?provider=agentmemory")
        assert delete_response.status_code == 200

        deleted_event = websocket.receive_json()
        assert deleted_event["event"] == "memory.deleted"
        assert deleted_event["data"]["memory_id"] == created["id"]
