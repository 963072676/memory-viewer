"""Tests for F46 Tag System."""

import json
import pytest
from fastapi.testclient import TestClient


# ─── F46: Tag System Tests ───

def test_create_memory_with_tags(client, cache_file):
    """F46: Create memory with tags, verify tags stored."""
    resp = client.post("/api/agentmemory", json={
        "title": "Tagged Memory",
        "content": "A memory with tags",
        "type": "pattern",
        "tags": ["ai", "testing", "backend"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    memory = data["memory"]
    assert "ai" in memory["tags"]
    assert "testing" in memory["tags"]
    assert "backend" in memory["tags"]
    assert len(memory["tags"]) == 3


def test_create_memory_tags_normalized(client, cache_file):
    """F46: Tags are lowercased, trimmed, and deduplicated on create."""
    resp = client.post("/api/agentmemory", json={
        "title": "Tagged Memory",
        "content": "A memory with messy tags",
        "type": "pattern",
        "tags": ["  AI  ", "Testing", "ai", "backend", ""],
    })
    assert resp.status_code == 200
    tags = resp.json()["memory"]["tags"]
    assert tags == ["ai", "testing", "backend"]


def test_create_memory_without_tags(client, cache_file):
    """F46: Creating memory without tags defaults to empty list."""
    resp = client.post("/api/agentmemory", json={
        "title": "No Tags Memory",
        "content": "No tags here",
        "type": "pattern",
    })
    assert resp.status_code == 200
    assert resp.json()["memory"]["tags"] == []


def test_update_memory_tags(client, cache_file):
    """F46: Update tags via PUT endpoint."""
    # First create
    resp = client.post("/api/agentmemory", json={
        "title": "Update Tags Memory",
        "content": "Will update tags",
        "tags": ["old"],
    })
    mem_id = resp.json()["memory"]["id"]

    # Update
    resp = client.put(f"/api/agentmemory/{mem_id}", json={
        "tags": ["new-tag", "another"],
    })
    assert resp.status_code == 200
    tags = resp.json()["memory"]["tags"]
    assert "new-tag" in tags
    assert "another" in tags
    assert "old" not in tags


def test_set_memory_tags_endpoint(client, cache_file):
    """F46: PUT /{id}/tags sets tags."""
    # Use existing test memory
    mem_id = "mem_test1_abcd1234"

    resp = client.put(f"/api/agentmemory/{mem_id}/tags", json={
        "tags": ["hermes", "ai", "pattern"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    memory = data["memory"]
    assert "hermes" in memory["tags"]
    assert "ai" in memory["tags"]
    assert "pattern" in memory["tags"]


def test_set_memory_tags_not_found(client, cache_file):
    """F46: PUT /{id}/tags with non-existent ID returns 404."""
    resp = client.put("/api/agentmemory/mem_nonexistent/tags", json={
        "tags": ["test"],
    })
    assert resp.status_code == 404


def test_get_all_tags(client, cache_file):
    """F46: GET /tags returns correct counts."""
    # First create some memories with tags
    client.post("/api/agentmemory", json={
        "title": "Tagged 1",
        "content": "content",
        "tags": ["ai", "python"],
    })
    client.post("/api/agentmemory", json={
        "title": "Tagged 2",
        "content": "content",
        "tags": ["ai", "testing"],
    })
    client.post("/api/agentmemory", json={
        "title": "Tagged 3",
        "content": "content",
        "tags": ["ai"],
    })

    resp = client.get("/api/agentmemory/tags")
    assert resp.status_code == 200
    tags = resp.json()["tags"]

    # Find ai tag - should have count 3
    ai_tag = next((t for t in tags if t["tag"] == "ai"), None)
    assert ai_tag is not None
    assert ai_tag["count"] == 3

    # python and testing should each have count 1
    python_tag = next((t for t in tags if t["tag"] == "python"), None)
    assert python_tag is not None
    assert python_tag["count"] == 1


def test_get_all_tags_sorted_by_count(client, cache_file):
    """F46: Tags are sorted by count descending."""
    client.post("/api/agentmemory", json={
        "title": "Tagged A",
        "content": "content",
        "tags": ["rare"],
    })
    client.post("/api/agentmemory", json={
        "title": "Tagged B",
        "content": "content",
        "tags": ["common", "common"],
    })
    # Note: within same memory, duplicates are removed by normalization
    # So create two memories with "common" tag
    client.post("/api/agentmemory", json={
        "title": "Tagged C",
        "content": "content",
        "tags": ["common"],
    })

    resp = client.get("/api/agentmemory/tags")
    tags = resp.json()["tags"]
    # "common" should be first (count=2), "rare" second (count=1)
    assert tags[0]["tag"] == "common"
    assert tags[0]["count"] == 2
    assert tags[1]["tag"] == "rare"
    assert tags[1]["count"] == 1


def test_paginated_filter_by_tag(client, cache_file):
    """F46: GET /paginated?tag=xxx filters correctly."""
    # Create memories with different tags
    client.post("/api/agentmemory", json={
        "title": "AI Memory 1",
        "content": "content",
        "tags": ["ai", "ml"],
    })
    client.post("/api/agentmemory", json={
        "title": "AI Memory 2",
        "content": "content",
        "tags": ["ai"],
    })
    client.post("/api/agentmemory", json={
        "title": "Python Memory",
        "content": "content",
        "tags": ["python"],
    })

    # Filter by "ai" tag
    resp = client.get("/api/agentmemory/paginated?tag=ai")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    for m in data["memories"]:
        assert "ai" in m["tags"]

    # Filter by "ml" tag
    resp = client.get("/api/agentmemory/paginated?tag=ml")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["memories"][0]["title"] == "AI Memory 1"


def test_paginated_filter_tag_case_insensitive(client, cache_file):
    """F46: Tag filter is case-insensitive."""
    client.post("/api/agentmemory", json={
        "title": "Tagged Memory",
        "content": "content",
        "tags": ["ai"],
    })

    resp = client.get("/api/agentmemory/paginated?tag=AI")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_batch_add_tags(client, cache_file):
    """F46: Batch action add_tags works."""
    # First set some initial tags
    client.put("/api/agentmemory/mem_test1_abcd1234/tags", json={
        "tags": ["existing"],
    })

    # Add tags via batch
    resp = client.post("/api/agentmemory/batch", json={
        "action": "add_tags",
        "ids": ["mem_test1_abcd1234", "mem_test2_efgh5678"],
        "params": {"tags": ["new-tag", "another"]},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["action"] == "add_tags"
    assert data["affected_count"] == 2

    # Verify tags were added (merged, not replaced)
    resp = client.get("/api/agentmemory")
    memories = resp.json()["memories"]
    for m in memories:
        if m["id"] == "mem_test1_abcd1234":
            assert "existing" in m["tags"]
            assert "new-tag" in m["tags"]
            assert "another" in m["tags"]
        elif m["id"] == "mem_test2_efgh5678":
            assert "new-tag" in m["tags"]
            assert "another" in m["tags"]


def test_batch_add_tags_not_found(client, cache_file):
    """F46: Batch add_tags with non-existent IDs returns not_found_ids."""
    resp = client.post("/api/agentmemory/batch", json={
        "action": "add_tags",
        "ids": ["mem_nonexistent_xyz", "mem_test1_abcd1234"],
        "params": {"tags": ["test"]},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["affected_count"] == 1
    assert "mem_nonexistent_xyz" in data["not_found_ids"]


def test_tags_persistence(client, cache_file):
    """F46: Tags survive re-read (persistence check)."""
    # Create memory with tags
    resp = client.post("/api/agentmemory", json={
        "title": "Persistent Tags",
        "content": "content",
        "tags": ["persistent", "test"],
    })
    mem_id = resp.json()["memory"]["id"]

    # Read directly from cache file
    with open(cache_file) as f:
        data = json.load(f)

    found = False
    for m in data["memories"]:
        if m["id"] == mem_id:
            assert "persistent" in m["tags"]
            assert "test" in m["tags"]
            found = True
            break
    assert found, "Memory not found in cache file"


def test_existing_memories_default_empty_tags(client, cache_file):
    """F46: Existing memories without tags field default to empty list."""
    # The test fixtures don't have tags field
    resp = client.get("/api/agentmemory")
    memories = resp.json()["memories"]
    for m in memories:
        # Should have tags as empty list (default)
        assert m.get("tags") is not None
        assert isinstance(m["tags"], list)
        assert len(m["tags"]) == 0
