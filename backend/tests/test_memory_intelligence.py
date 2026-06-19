"""Tests for provider-neutral Memory Intelligence API."""

from app.core.memory_schema import MemoryItem, MemoryMetadata
from app.services.intelligence import detect_contradictions


def test_memory_intelligence_summary_clusters_and_compression(client):
    summary_response = client.get("/api/intelligence/summary?provider=agentmemory&limit=10")

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["memoryCount"] == 3
    assert summary["providers"] == ["agentmemory"]
    assert "hermes" in summary["keywords"]
    assert summary["summary"]

    clusters_response = client.get("/api/intelligence/clusters?provider=agentmemory&limit=10")
    assert clusters_response.status_code == 200
    clusters = clusters_response.json()
    assert clusters["memoryCount"] == 3
    assert clusters["total"] >= 1
    assert clusters["clusters"][0]["memoryIds"]

    compression_response = client.post(
        "/api/intelligence/compress",
        json={"provider": "agentmemory", "limit": 10, "maxChars": 240},
    )
    assert compression_response.status_code == 200
    compression = compression_response.json()
    assert compression["originalCount"] == 3
    assert compression["compressedCount"] == 3
    assert len(compression["compressed"]) <= 240


def test_memory_intelligence_detects_provider_neutral_contradictions():
    items = [
        MemoryItem(
            id="a",
            content="User prefers dark mode for hermes interface",
            metadata=MemoryMetadata(source="agentmemory", timestamp=1),
        ),
        MemoryItem(
            id="b",
            content="User does not prefer dark mode for hermes interface",
            metadata=MemoryMetadata(source="hermes", timestamp=2),
        ),
    ]

    result = detect_contradictions(items)

    assert result["total"] == 1
    contradiction = result["contradictions"][0]
    assert contradiction["memoryA"]["provider"] == "agentmemory"
    assert contradiction["memoryB"]["provider"] == "hermes"
    assert {"dark", "mode", "hermes", "interface"}.intersection(contradiction["sharedTerms"])
