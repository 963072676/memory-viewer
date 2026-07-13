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


def test_unified_memory_detail_preserves_provider_display_fields(client):
    agentmemory = client.get(
        "/api/memories/unified/detail",
        params={"source": "agentmemory", "id": "mem_test1_abcd1234"},
    )
    assert agentmemory.status_code == 200
    agentmemory_item = agentmemory.json()["memory"]
    assert agentmemory_item["title"] == "Test Pattern Memory"
    assert agentmemory_item["type"] == "pattern"
    assert agentmemory_item["concepts"] == ["hermes", "test"]
    assert agentmemory_item["source"] == "agentmemory"

    hermes_list = client.get("/api/memories/unified?source=hermes&limit=1")
    assert hermes_list.status_code == 200
    hermes_id = hermes_list.json()["memories"][0]["id"]

    hermes = client.get(
        "/api/memories/unified/detail",
        params={"source": "hermes", "id": hermes_id},
    )
    assert hermes.status_code == 200
    hermes_item = hermes.json()["memory"]
    assert hermes_item["id"] == hermes_id
    assert hermes_item["content"]
    assert hermes_item["source"] == "hermes"


def test_unified_memory_detail_rejects_unknown_source_and_memory(client):
    unknown_source = client.get(
        "/api/memories/unified/detail",
        params={"source": "missing-provider", "id": "memory-1"},
    )
    assert unknown_source.status_code == 404

    unknown_memory = client.get(
        "/api/memories/unified/detail",
        params={"source": "hermes", "id": "missing-memory"},
    )
    assert unknown_memory.status_code == 404


def test_unified_search_uses_registered_sources(client):
    """GET /api/memories/unified/search should search through the registry."""
    response = client.get("/api/memories/unified/search?q=hermes&limit=10")

    assert response.status_code == 200
    data = response.json()

    assert data["query"] == "hermes"
    assert data["total"] >= 2
    assert any(memory["source"] == "agentmemory" for memory in data["memories"])
