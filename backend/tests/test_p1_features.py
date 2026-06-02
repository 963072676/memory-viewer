"""Tests for P1 features: F-08 (edit), F-09 (delete), F-10 (stats), F-11 (scheduler)."""


# ── F-08: Memory Edit Tests ──

def test_update_memory_content(client, cache_file):
    """Test PUT /api/agentmemory/{id} updates content."""
    resp = client.put("/api/agentmemory/mem_test1_abcd1234", json={
        "content": "Updated content for test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["memory"]["content"] == "Updated content for test"
    assert data["memory"]["id"] == "mem_test1_abcd1234"


def test_update_memory_strength(client, cache_file):
    """Test PUT /api/agentmemory/{id} updates strength."""
    resp = client.put("/api/agentmemory/mem_test2_efgh5678", json={
        "strength": 9,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["memory"]["strength"] == 9


def test_update_memory_concepts(client, cache_file):
    """Test PUT /api/agentmemory/{id} updates concepts."""
    resp = client.put("/api/agentmemory/mem_test1_abcd1234", json={
        "concepts": ["new", "updated", "concepts"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["memory"]["concepts"] == ["new", "updated", "concepts"]


def test_update_memory_not_found(client):
    """Test PUT /api/agentmemory/{id} with non-existent ID returns 404."""
    resp = client.put("/api/agentmemory/mem_nonexistent_xxxx", json={
        "content": "test",
    })
    assert resp.status_code == 404


def test_update_memory_idempotent(client, cache_file):
    """Test PUT with no changes is idempotent."""
    resp = client.put("/api/agentmemory/mem_test1_abcd1234", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["memory"]["content"] == "This is a test pattern about hermes usage"


def test_update_memory_version_increments(client, cache_file):
    """Test that version increments on update."""
    resp1 = client.put("/api/agentmemory/mem_test1_abcd1234", json={"content": "v1"})
    v1 = resp1.json()["memory"]["version"]
    resp2 = client.put("/api/agentmemory/mem_test1_abcd1234", json={"content": "v2"})
    v2 = resp2.json()["memory"]["version"]
    assert v2 > v1


# ── F-09: Memory Delete Tests ──

def test_delete_memory(client, cache_file):
    """Test DELETE /api/agentmemory/{id} deletes a memory."""
    resp = client.delete("/api/agentmemory/mem_test1_abcd1234")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["deleted_id"] == "mem_test1_abcd1234"

    # Verify it's gone
    resp2 = client.get("/api/agentmemory")
    ids = [m["id"] for m in resp2.json()["memories"]]
    assert "mem_test1_abcd1234" not in ids


def test_delete_memory_not_found(client):
    """Test DELETE with non-existent ID returns 404."""
    resp = client.delete("/api/agentmemory/mem_nonexistent_xxxx")
    assert resp.status_code == 404


def test_batch_delete(client, cache_file):
    """Test POST /api/agentmemory/batch/delete deletes multiple memories."""
    resp = client.post("/api/agentmemory/batch/delete", json={
        "ids": ["mem_test1_abcd1234", "mem_test2_efgh5678"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["deleted_count"] == 2
    assert len(data["deleted_ids"]) == 2

    # Verify they're gone
    resp2 = client.get("/api/agentmemory")
    assert len(resp2.json()["memories"]) == 1


def test_batch_delete_partial_not_found(client, cache_file):
    """Test batch delete with some non-existent IDs."""
    resp = client.post("/api/agentmemory/batch/delete", json={
        "ids": ["mem_test1_abcd1234", "mem_nonexistent_xxxx"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted_count"] == 1
    assert "mem_nonexistent_xxxx" in data["not_found_ids"]


def test_batch_delete_empty(client):
    """Test batch delete with empty list."""
    resp = client.post("/api/agentmemory/batch/delete", json={"ids": []})
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted_count"] == 0


# ── F-10: Stats Tests ──

def test_get_stats(client):
    """Test GET /api/agentmemory/stats returns statistics."""
    resp = client.get("/api/agentmemory/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert "by_type" in data
    assert "strength_distribution" in data
    assert "by_month" in data
    assert "avg_strength" in data


def test_get_stats_by_type(client):
    """Test stats returns correct type distribution."""
    resp = client.get("/api/agentmemory/stats")
    data = resp.json()
    assert data["by_type"]["pattern"] == 1
    assert data["by_type"]["fact"] == 1
    assert data["by_type"]["preference"] == 1


def test_get_stats_strength_distribution(client):
    """Test stats returns strength distribution."""
    resp = client.get("/api/agentmemory/stats")
    data = resp.json()
    dist = data["strength_distribution"]
    assert dist["7"] == 1  # mem_test1 has strength 7
    assert dist["5"] == 1  # mem_test2 has strength 5
    assert dist["8"] == 1  # mem_test3 has strength 8


def test_get_stats_by_month(client):
    """Test stats returns monthly distribution."""
    resp = client.get("/api/agentmemory/stats")
    data = resp.json()
    assert "2026-05" in data["by_month"]
    assert data["by_month"]["2026-05"] == 3


def test_get_stats_avg_strength(client):
    """Test stats returns average strength."""
    resp = client.get("/api/agentmemory/stats")
    data = resp.json()
    # (7 + 5 + 8) / 3 = 6.67 -> rounded to 6.7
    assert data["avg_strength"] == 6.7


# ── F-11: Health Scheduler Tests ──

def test_health_has_scheduler(client):
    """Test /api/health includes scheduler status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "scheduler" in data
    assert "running" in data["scheduler"]
    assert "last_refresh_at" in data["scheduler"]
    assert "next_refresh_at" in data["scheduler"]


# ── F-07: Search Enhancement Tests ──

def test_search_empty_query_pure_filter(client):
    """Test search with empty query returns filtered results."""
    resp = client.get("/api/search?q=&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3  # All agentmemory results


def test_search_multiple_types(client):
    """Test search with multiple type filters (agentmemory only)."""
    resp = client.get("/api/search?q=&types=pattern,fact&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    types = {r["type"] for r in data["results"]}
    assert types == {"pattern", "fact"}


def test_search_strength_range(client):
    """Test search with strength range filter (agentmemory only)."""
    resp = client.get("/api/search?q=&strength_min=7&strength_max=10&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2  # strength 7 and 8


def test_search_date_range(client):
    """Test search with date range filter (agentmemory only)."""
    resp = client.get("/api/search?q=&date_from=2026-05-26&date_to=2026-05-28&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2  # May 26 and May 27 entries
