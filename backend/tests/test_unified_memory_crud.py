"""Tests for unified /api/memories CRUD endpoints."""


def test_unified_memory_crud_with_selected_provider(client):
    create_response = client.post(
        "/api/memories",
        json={
            "provider": "agentmemory",
            "title": "Unified CRUD Memory",
            "content": "Created through unified provider API",
            "type": "fact",
            "concepts": ["unified", "provider"],
            "strength": 6,
            "tags": ["Unified", "CRUD"],
            "sessionId": "session-unified",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["memory"]
    memory_id = created["id"]
    assert created["content"] == "Created through unified provider API"
    assert created["metadata"]["source"] == "agentmemory"
    assert created["metadata"]["tags"] == ["unified", "crud"]
    assert created["metadata"]["sessionId"] == "session-unified"

    get_response = client.get(f"/api/memories/{memory_id}?provider=agentmemory")
    assert get_response.status_code == 200
    assert get_response.json()["memory"]["id"] == memory_id

    update_response = client.put(
        f"/api/memories/{memory_id}",
        json={
            "provider": "agentmemory",
            "content": "Updated through unified provider API",
            "tags": ["Updated"],
            "strength": 7,
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()["memory"]
    assert updated["content"] == "Updated through unified provider API"
    assert updated["metadata"]["tags"] == ["updated"]

    delete_response = client.delete(f"/api/memories/{memory_id}?provider=agentmemory")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True, "deleted_id": memory_id}

    missing_response = client.get(f"/api/memories/{memory_id}?provider=agentmemory")
    assert missing_response.status_code == 404


def test_unified_memory_list_uses_canonical_schema(client):
    response = client.get("/api/memories?provider=agentmemory&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "agentmemory"
    assert data["limit"] == 2
    assert data["total"] >= 2
    assert len(data["items"]) == 2
    assert {"id", "content", "metadata"}.issubset(data["items"][0].keys())
    assert data["items"][0]["metadata"]["source"] == "agentmemory"


def test_unified_memory_crud_rejects_unknown_provider(client):
    response = client.post(
        "/api/memories",
        json={
            "provider": "not-a-provider",
            "content": "No provider should handle this",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "provider_config_error"


def test_existing_unified_sources_route_still_wins(client):
    response = client.get("/api/memories/unified?limit=2")

    assert response.status_code == 200
    data = response.json()
    assert "memories" in data
    assert "items" not in data
