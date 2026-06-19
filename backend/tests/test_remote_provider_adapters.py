"""Tests for remote provider adapter skeletons."""

import json

import pytest

from app.adapters.letta import LettaAdapter
from app.adapters.registry import init_registry_from_config
from app.adapters.supermemory import SupermemoryAdapter
from app.adapters.zep import ZepAdapter
from app.core.memory_schema import MemoryInput, MemoryQuery


def test_registry_loads_remote_provider_adapters_when_enabled():
    registry = init_registry_from_config(
        {
            "sources": [
                {"name": "zep", "type": "zep", "enabled": True, "config": {"api_key": "test", "base_url": "https://zep.test"}},
                {"name": "letta", "type": "letta", "enabled": True, "config": {"api_key": "test", "base_url": "https://letta.test"}},
                {
                    "name": "supermemory",
                    "type": "supermemory",
                    "enabled": True,
                    "config": {"api_key": "test", "base_url": "https://supermemory.test"},
                },
            ],
        }
    )

    assert [source["type"] for source in registry.list_sources()] == ["zep", "letta", "supermemory"]
    assert registry.provider_factory.list_providers() == ["zep", "letta", "supermemory"]


def test_remote_provider_auto_enabled_uses_provider_api_keys(monkeypatch):
    monkeypatch.delenv("ZEP_API_KEY", raising=False)
    skipped = init_registry_from_config(
        {"sources": [{"name": "zep", "type": "zep", "enabled": "auto", "config": {}}]}
    )
    assert skipped.list_sources() == []

    monkeypatch.setenv("ZEP_API_KEY", "test")
    registered = init_registry_from_config(
        {"sources": [{"name": "zep", "type": "zep", "enabled": "auto", "config": {}}]}
    )
    assert [source["name"] for source in registered.list_sources()] == ["zep"]


@pytest.mark.asyncio
async def test_zep_adapter_builds_graph_search_payload_and_normalizes(monkeypatch):
    adapter = ZepAdapter(
        name="zep",
        config={"api_key": "test", "base_url": "https://zep.test", "user_id": "user-1"},
    )
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = json.loads(kwargs["content"])
        return {
            "results": [
                {
                    "id": "zep-1",
                    "fact": "Zep remembers graph facts",
                    "metadata": {"tags": ["graph"]},
                    "score": 0.9,
                }
            ]
        }

    monkeypatch.setattr(adapter, "_request", fake_request)

    items = await adapter.search("graph", limit=3)

    assert captured == {
        "method": "POST",
        "path": "/api/v2/graph/search",
        "payload": {"query": "graph", "limit": 3, "user_id": "user-1"},
    }
    assert items[0].id == "zep-1"
    assert items[0].content == "Zep remembers graph facts"
    assert items[0].metadata["tags"] == ["graph"]


@pytest.mark.asyncio
async def test_letta_adapter_maps_memory_input_to_block_payload(monkeypatch):
    adapter = LettaAdapter(name="letta", config={"api_key": "test", "base_url": "https://letta.test"})
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = json.loads(kwargs["content"])
        return {"id": "block-1", "label": "profile", "value": "User likes quiet tools"}

    monkeypatch.setattr(adapter, "_request", fake_request)

    item = await adapter.store_memory(
        MemoryInput(content="User likes quiet tools", metadata={"label": "profile", "tags": ["preference"]})
    )

    assert captured == {
        "method": "POST",
        "path": "/v1/blocks/",
        "payload": {
            "label": "profile",
            "value": "User likes quiet tools",
            "description": None,
            "metadata": {"label": "profile", "tags": ["preference"]},
            "tags": ["preference"],
        },
    }
    assert item.id == "block-1"
    assert item.content == "User likes quiet tools"


@pytest.mark.asyncio
async def test_supermemory_adapter_uses_v4_search_and_normalizes_results(monkeypatch):
    adapter = SupermemoryAdapter(
        name="supermemory",
        config={"api_key": "test", "base_url": "https://supermemory.test", "container_tag": "agent-a"},
    )
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = json.loads(kwargs["content"])
        return {
            "results": [
                {
                    "id": "doc-1",
                    "content": "Supermemory search result",
                    "metadata": {"title": "Result"},
                    "containerTags": ["agent-a"],
                }
            ]
        }

    monkeypatch.setattr(adapter, "_request", fake_request)

    items = await adapter.search("search result", limit=5)

    assert captured == {
        "method": "POST",
        "path": "/v4/search",
        "payload": {
            "q": "search result",
            "searchMode": "hybrid",
            "limit": 5,
            "containerTag": "agent-a",
        },
    }
    assert items[0].id == "doc-1"
    assert items[0].title == "Result"
    assert items[0].metadata["tags"] == ["agent-a"]


@pytest.mark.asyncio
async def test_supermemory_query_memory_uses_normalized_search_mode(monkeypatch):
    adapter = SupermemoryAdapter(
        name="supermemory",
        config={"api_key": "test", "base_url": "https://supermemory.test"},
    )
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = json.loads(kwargs["content"])
        return {
            "results": [
                {
                    "id": "doc-2",
                    "content": "Semantic Supermemory result",
                    "metadata": {"title": "Semantic"},
                }
            ]
        }

    monkeypatch.setattr(adapter, "_request", fake_request)

    result = await adapter.query_memory(MemoryQuery(query="semantic result", mode="semantic", limit=4))

    assert captured == {
        "method": "POST",
        "path": "/v4/search",
        "payload": {
            "q": "semantic result",
            "searchMode": "semantic",
            "limit": 4,
        },
    }
    assert result.provider == "supermemory"
    assert result.items[0].content == "Semantic Supermemory result"
