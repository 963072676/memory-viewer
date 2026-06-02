"""Tests for hermes memory API endpoints."""


def test_get_hermes_memory(client):
    """Test GET /api/hermes-memory returns global + profile data."""
    resp = client.get("/api/hermes-memory")
    assert resp.status_code == 200
    data = resp.json()
    assert "global" in data
    assert "profiles" in data
    assert len(data["global"]["memory"]) == 2
    assert len(data["global"]["user"]) == 1


def test_get_hermes_memory_profiles(client):
    """Test hermes memory includes profile data."""
    resp = client.get("/api/hermes-memory")
    data = resp.json()
    assert "chief-agent" in data["profiles"]
    assert "daily" in data["profiles"]
    assert len(data["profiles"]["chief-agent"]["memory"]) == 1
