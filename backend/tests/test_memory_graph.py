"""Tests for provider-neutral Memory Graph API."""

from app.core.memory_schema import MemoryItem, MemoryMetadata
from app.services.graph import build_graph_from_items


def test_memory_graph_api_uses_unified_loader(monkeypatch):
    """Graph API should pass provider/session filters to the unified loader."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.routers import graph as graph_router
    import app.services.agentmemory as agentmemory_service
    import app.services.graph as graph_service

    calls = {}

    async def fake_load_unified_memories(*, provider: str, session_id: str, limit: int):
        calls.update({"provider": provider, "session_id": session_id, "limit": limit})
        return [
            MemoryItem(
                id="a",
                content="Hermes graph memory",
                metadata=MemoryMetadata(source=provider or "agentmemory", timestamp=1, tags=["graph"]),
            )
        ]

    def fail_direct_read(*args, **kwargs):
        raise AssertionError("graph should use provider adapters")

    monkeypatch.setattr(agentmemory_service, "get_all_memories", fail_direct_read)
    monkeypatch.setattr(graph_service, "load_unified_memories", fake_load_unified_memories)

    app = FastAPI()
    app.include_router(graph_router.router, prefix="/api/graph")
    resp = TestClient(app).get("/api/graph?provider=agentmemory&sessionId=session-a&limit=10")

    assert resp.status_code == 200
    data = resp.json()
    assert calls == {"provider": "agentmemory", "session_id": "session-a", "limit": 10}
    assert data["meta"]["node_count"] == 1
    assert data["meta"]["providers"] == ["agentmemory"]
    assert data["nodes"][0]["provider"] == "agentmemory"


def test_memory_graph_builds_edges_from_provider_neutral_signals():
    items = [
        MemoryItem(
            id="a",
            content="Hermes dashboard stores provider latency",
            metadata=MemoryMetadata(source="agentmemory", timestamp=1, tags=["observability"]),
        ),
        MemoryItem(
            id="b",
            content="Provider routing dashboard shows latency",
            metadata=MemoryMetadata(source="zep", timestamp=2, tags=["observability"]),
        ),
        MemoryItem(
            id="c",
            content="Cooking preferences for dinner",
            metadata=MemoryMetadata(source="mem0", timestamp=3, tags=["personal"]),
        ),
    ]

    graph = build_graph_from_items(items)

    assert graph["meta"]["node_count"] == 3
    assert graph["meta"]["edge_count"] >= 1
    linked = [edge for edge in graph["edges"] if edge["source"] == "a" and edge["target"] == "b"]
    assert linked
    assert "observability" in linked[0]["shared_concepts"]
