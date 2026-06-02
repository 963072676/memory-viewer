"""Tests for health check API endpoint."""


def test_health_check(client):
    """Test GET /api/health returns service status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    assert "uptime_seconds" in data
    assert "cache_age_seconds" in data
    assert "agentmemory_count" in data
    assert "hermes_memory_count" in data
    assert data["agentmemory_count"] == 3
