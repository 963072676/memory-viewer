"""Tests for initialized unified memory source endpoints."""


def test_runtime_config_injects_hermes_profiles_path(monkeypatch, profiles_dir):
    from app.adapters.registry import _runtime_config_from_settings
    from app.config import settings

    monkeypatch.delenv("MV_HERMES_PROFILES_DIR", raising=False)
    monkeypatch.delenv("HERMES_PROFILES_DIR", raising=False)
    monkeypatch.setattr(settings, "HERMES_PROFILES_DIR", profiles_dir)

    config = {
        "sources": [
            {
                "name": "hermes",
                "type": "hermes",
                "enabled": True,
                "config": {"memories_dir": "data/memories"},
            }
        ]
    }

    runtime = _runtime_config_from_settings(config)

    assert runtime["sources"][0]["config"]["profiles_dir"] == profiles_dir


def test_sources_endpoint_initializes_runtime_registry(client):
    """GET /api/sources should expose configured providers after app import."""
    response = client.get("/api/sources")

    assert response.status_code == 200
    sources = response.json()["sources"]
    by_name = {source["name"]: source for source in sources}

    assert "agentmemory" in by_name
    assert "hermes" in by_name
    assert by_name["agentmemory"]["healthy"] is True
    assert by_name["hermes"]["healthy"] is True


def test_unified_memories_endpoint_reads_registered_sources(client):
    """GET /api/memories/unified should aggregate configured sources."""
    response = client.get("/api/memories/unified?limit=20")

    assert response.status_code == 200
    data = response.json()
    sources = {memory["source"] for memory in data["memories"]}

    assert data["total"] >= 5
    assert {"agentmemory", "hermes"}.issubset(sources)


def test_unified_search_uses_registered_sources(client):
    """GET /api/memories/unified/search should search through the registry."""
    response = client.get("/api/memories/unified/search?q=hermes&limit=10")

    assert response.status_code == 200
    data = response.json()

    assert data["query"] == "hermes"
    assert data["total"] >= 2
    assert any(memory["source"] == "agentmemory" for memory in data["memories"])
