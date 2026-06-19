"""Tests for provider-neutral Memory Copilot actions."""

from app.core.memory_schema import MemoryItem, MemoryMetadata
from app.services.copilot import run_copilot_action_from_items


def _items():
    return [
        MemoryItem(
            id="a",
            content="User prefers dark mode for hermes interface",
            metadata=MemoryMetadata(source="agentmemory", timestamp=1, tags=["ui"]),
        ),
        MemoryItem(
            id="b",
            content="User does not prefer dark mode for hermes interface",
            metadata=MemoryMetadata(source="zep", timestamp=2, tags=[]),
        ),
        MemoryItem(
            id="c",
            content="Provider routing should record fallback latency",
            metadata=MemoryMetadata(source="zep", timestamp=3, tags=["observability"]),
        ),
    ]


def test_copilot_runs_provider_neutral_actions():
    items = _items()

    summary = run_copilot_action_from_items("summarize_session", items)
    compression = run_copilot_action_from_items("compress_memory", items, max_chars=180)
    contradictions = run_copilot_action_from_items("detect_contradictions", items)
    optimization = run_copilot_action_from_items("optimize_memory_structure", items)

    assert summary["memoryCount"] == 3
    assert summary["providers"] == ["agentmemory", "zep"]
    assert compression["result"]["compressedCount"] == 3
    assert len(compression["message"]) <= 180
    assert contradictions["status"] == "attention"
    assert contradictions["result"]["total"] == 1
    assert optimization["recommendations"]
    assert any(item["kind"] == "tagging" for item in optimization["recommendations"])


def test_copilot_api_passes_filters_to_unified_loader(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.routers import copilot as copilot_router
    import app.services.copilot as copilot_service

    calls = {}

    async def fake_load_unified_memories(*, provider: str, session_id: str, limit: int):
        calls.update({"provider": provider, "session_id": session_id, "limit": limit})
        return _items()

    monkeypatch.setattr(copilot_service, "load_unified_memories", fake_load_unified_memories)

    app = FastAPI()
    app.include_router(copilot_router.router, prefix="/api/copilot")
    resp = TestClient(app).post(
        "/api/copilot/run",
        json={
            "action": "optimize_memory_structure",
            "provider": "zep",
            "sessionId": "session-a",
            "limit": 25,
        },
    )

    assert resp.status_code == 200
    assert calls == {"provider": "zep", "session_id": "session-a", "limit": 25}
    data = resp.json()
    assert data["action"] == "optimize_memory_structure"
    assert data["recommendations"]
