"""Tests for agentmemory API endpoints."""

import json
import io


def test_get_agentmemory(client):
    """Test GET /api/agentmemory returns all memories."""
    resp = client.get("/api/agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert "memories" in data
    assert len(data["memories"]) == 3


def test_get_agentmemory_paginated(client):
    """Test GET /api/agentmemory/paginated with pagination."""
    resp = client.get("/api/agentmemory/paginated?limit=2&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["memories"]) == 2


def test_get_agentmemory_paginated_sort_by_strength(client):
    """Test paginated endpoint with strength sorting."""
    resp = client.get("/api/agentmemory/paginated?sort=strength&order=desc")
    assert resp.status_code == 200
    data = resp.json()
    strengths = [m["strength"] for m in data["memories"]]
    assert strengths == sorted(strengths, reverse=True)


def test_get_agentmemory_paginated_sort_by_type(client):
    """Test paginated endpoint with type sorting."""
    resp = client.get("/api/agentmemory/paginated?sort=type&order=asc")
    assert resp.status_code == 200
    data = resp.json()
    types = [m["type"] for m in data["memories"]]
    assert types == sorted(types)


def test_get_agentmemory_paginated_filter_type(client):
    """Test paginated endpoint with type filter."""
    resp = client.get("/api/agentmemory/paginated?type=pattern")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert all(m["type"] == "pattern" for m in data["memories"])


def test_create_agentmemory(client, cache_file):
    """Test POST /api/agentmemory creates a new memory."""
    resp = client.post("/api/agentmemory", json={
        "title": "New Test Memory",
        "content": "This is a newly created memory",
        "type": "workflow",
        "concepts": ["new", "test"],
        "strength": 6,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["memory"]["title"] == "New Test Memory"
    assert data["memory"]["type"] == "workflow"

    # Verify it was persisted
    resp2 = client.get("/api/agentmemory")
    assert len(resp2.json()["memories"]) == 4


def test_import_agentmemory_json(client, cache_file):
    """Test POST /api/agentmemory/import with JSON file."""
    import_data = {
        "memories": [
            {
                "title": "Imported Memory",
                "content": "This was imported",
                "type": "fact",
                "concepts": ["import"],
                "strength": 4,
            }
        ]
    }
    file_content = json.dumps(import_data).encode()
    resp = client.post(
        "/api/agentmemory/import",
        files={"file": ("test.json", io.BytesIO(file_content), "application/json")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["imported"] == 1


def test_export_agentmemory_json(client):
    """Test GET /api/agentmemory/export returns JSON."""
    resp = client.get("/api/agentmemory/export?format=json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    data = resp.json()
    assert "memories" in data
    assert len(data["memories"]) == 3


def test_export_agentmemory_markdown(client):
    """Test GET /api/agentmemory/export returns Markdown."""
    resp = client.get("/api/agentmemory/export?format=markdown")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    assert "##" in resp.text
