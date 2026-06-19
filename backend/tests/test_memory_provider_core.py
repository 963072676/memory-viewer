"""Tests for the provider-neutral memory core layer."""

from __future__ import annotations

import pytest

from app.adapters.base import MemoryItem as LegacyMemoryItem
from app.adapters.base import MemorySource
from app.adapters.agentmemory import AgentMemoryAdapter
from app.adapters.registry import init_registry_from_config
from app.core.errors import MemoryNotFoundError, ProviderUnavailableError
from app.core.memory_provider import MemoryProvider
from app.core.memory_schema import MemoryInput, MemoryItem, MemoryMetadata, MemoryQuery, MemoryQueryResult, Session
from app.core.provider_factory import ProviderFactory


class FakeProvider(MemoryProvider):
    provider_type = "fake"

    def __init__(
        self,
        name: str,
        *,
        fail_query: bool = False,
        ids: list[str] | None = None,
        capabilities: set[str] | None = None,
    ):
        self.name = name
        self.fail_query = fail_query
        self.ids = ids or [name]
        self.capabilities = capabilities or {"query", "keyword_search"}
        self.seen_query_modes: list[str] = []

    async def store_memory(self, input: MemoryInput) -> MemoryItem:
        return MemoryItem(
            id="stored",
            content=input.content,
            metadata=MemoryMetadata(source=self.name, timestamp=1),
            embedding=input.embedding,
        )

    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        self.seen_query_modes.append(query.mode)
        if self.fail_query:
            raise ProviderUnavailableError("boom", provider=self.name, operation="query_memory")
        items = [
            MemoryItem(
                id=item_id,
                content=f"{self.name}:{query.query}",
                metadata=MemoryMetadata(source=self.name, timestamp=1),
            )
            for item_id in self.ids
        ]
        return MemoryQueryResult(items=items, latency=3, provider=self.name)

    async def update_memory(self, id: str, patch: dict) -> None:
        return None

    async def delete_memory(self, id: str) -> None:
        return None

    async def get_memory_by_id(self, id: str) -> MemoryItem:
        return MemoryItem(id=id, content=id, metadata=MemoryMetadata(source=self.name, timestamp=1))

    async def list_sessions(self) -> list[Session]:
        return []

    async def health_check(self) -> bool:
        return not self.fail_query


class FakeSource(MemorySource):
    source_type = "fake-source"

    async def list(self, limit: int = 50, offset: int = 0) -> list[LegacyMemoryItem]:
        return [
            LegacyMemoryItem(
                id="legacy-1",
                title="Legacy",
                content="hello world",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-02T00:00:00Z",
                source=self.name,
                metadata={"tags": ["test"], "sessionIds": ["session-1"]},
            )
        ]

    async def get(self, id: str) -> LegacyMemoryItem | None:
        items = await self.list()
        return items[0] if id == "legacy-1" else None

    async def search(self, query: str, limit: int = 20) -> list[LegacyMemoryItem]:
        return await self.list(limit=limit)

    async def health(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_provider_factory_falls_back_when_primary_query_fails():
    factory = ProviderFactory()
    factory.register_instance(FakeProvider("primary", fail_query=True))
    factory.register_instance(FakeProvider("fallback", ids=["fb-1"]))
    factory.configure_strategy(
        active_provider="primary",
        fallback_providers=["fallback"],
        retry_attempts=1,
        timeout_seconds=1,
    )

    result = await factory.query_memory(MemoryQuery(query="hello"))

    assert result.provider == "fallback"
    assert [item.id for item in result.items] == ["fb-1"]
    assert result.items[0].metadata.source == "fallback"


@pytest.mark.asyncio
async def test_provider_factory_normalizes_query_mode_for_provider_capabilities():
    factory = ProviderFactory()
    keyword = FakeProvider("keyword", capabilities={"query", "keyword_search"})
    semantic = FakeProvider("semantic", capabilities={"semantic_search"})
    hybrid = FakeProvider("hybrid", capabilities={"semantic_search", "hybrid_search"})
    factory.register_instance(keyword)
    factory.register_instance(semantic)
    factory.register_instance(hybrid)
    factory.configure_strategy(active_provider="keyword", timeout_seconds=1)

    await factory.query_memory_from_provider("keyword", MemoryQuery(query="hello", mode="hybrid"))
    await factory.query_memory_from_provider("semantic", MemoryQuery(query="hello", mode="keyword"))
    await factory.query_memory_from_provider("hybrid", MemoryQuery(query="hello", mode="semantic"))

    assert keyword.seen_query_modes == ["keyword"]
    assert semantic.seen_query_modes == ["semantic"]
    assert hybrid.seen_query_modes == ["semantic"]


@pytest.mark.asyncio
async def test_provider_factory_observability_tracks_fallback_route_and_errors():
    factory = ProviderFactory()
    factory.register_instance(FakeProvider("primary", fail_query=True))
    factory.register_instance(FakeProvider("fallback", ids=["fb-1"]))
    factory.configure_strategy(
        active_provider="primary",
        fallback_providers=["fallback"],
        retry_attempts=1,
        timeout_seconds=1,
    )

    result = await factory.query_memory(MemoryQuery(query="hello"))
    snapshot = factory.get_observability_snapshot()

    assert result.provider == "fallback"
    assert snapshot["providers"]["primary"]["errors"] == 1
    assert snapshot["providers"]["primary"]["operations"]["query_memory"]["errors"] == 1
    assert snapshot["providers"]["fallback"]["successes"] == 1
    assert snapshot["providers"]["fallback"]["fallbackSuccesses"] == 1

    route = snapshot["routing"]["recentRoutes"][-1]
    assert route["strategy"] == "fallback"
    assert route["providers"] == ["primary", "fallback"]
    assert route["successfulProvider"] == "fallback"
    assert route["fallbackUsed"] is True
    assert route["errors"][0]["code"] == "provider_unavailable"
    assert route["errors"][0]["provider"] == "primary"


@pytest.mark.asyncio
async def test_provider_factory_parallel_query_merges_provider_results():
    factory = ProviderFactory()
    factory.register_instance(FakeProvider("primary", ids=["p-1", "p-2"]))
    factory.register_instance(FakeProvider("fallback", ids=["f-1"]))
    factory.configure_strategy(
        active_provider="primary",
        fallback_providers=["fallback"],
        parallel_query=True,
        timeout_seconds=1,
    )

    result = await factory.query_memory(MemoryQuery(query="hello", limit=10))

    assert result.provider == "primary,fallback"
    assert [item.id for item in result.items] == ["p-1", "p-2", "f-1"]


@pytest.mark.asyncio
async def test_provider_factory_parallel_query_normalizes_each_provider_mode():
    factory = ProviderFactory()
    keyword = FakeProvider("keyword", ids=["k-1"], capabilities={"query", "keyword_search"})
    semantic = FakeProvider("semantic", ids=["s-1"], capabilities={"semantic_search"})
    factory.register_instance(keyword)
    factory.register_instance(semantic)
    factory.configure_strategy(
        active_provider="keyword",
        fallback_providers=["semantic"],
        parallel_query=True,
        timeout_seconds=1,
    )

    result = await factory.query_memory(MemoryQuery(query="hello", mode="hybrid", limit=10))

    assert result.provider == "keyword,semantic"
    assert keyword.seen_query_modes == ["keyword"]
    assert semantic.seen_query_modes == ["semantic"]


@pytest.mark.asyncio
async def test_memory_source_bridge_returns_unified_schema_with_raw_debug():
    source = FakeSource(name="legacy")

    result = await source.query_memory(MemoryQuery(query="hello", include_raw=True))

    assert result.provider == "legacy"
    assert result.items[0].to_dict() == {
        "id": "legacy-1",
        "content": "hello world",
        "metadata": {
            "source": "legacy",
            "timestamp": 1767312000000,
            "sessionId": "session-1",
            "tags": ["test"],
            "raw": {
                "id": "legacy-1",
                "title": "Legacy",
                "content": "hello world",
                "type": "unknown",
                "concepts": [],
                "strength": 5.0,
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-02T00:00:00Z",
                "source": "legacy",
                "metadata": {"tags": ["test"], "sessionIds": ["session-1"]},
            },
        },
    }


def test_registry_strategy_prunes_unregistered_auto_providers(cache_file, monkeypatch):
    monkeypatch.delenv("MEM0_API_KEY", raising=False)

    registry = init_registry_from_config(
        {
            "memory_providers": {
                "activeProvider": "mem0",
                "fallbackProviders": ["agentmemory"],
            },
            "sources": [
                {
                    "name": "agentmemory",
                    "type": "agentmemory",
                    "enabled": True,
                    "config": {"cache_path": cache_file},
                },
                {
                    "name": "mem0",
                    "type": "mem0",
                    "enabled": "auto",
                    "config": {},
                },
            ],
        }
    )

    assert registry.provider_factory.strategy.active_provider == "agentmemory"
    assert registry.provider_factory.strategy.fallback_providers == []


@pytest.mark.asyncio
async def test_agentmemory_adapter_implements_provider_crud(cache_file):
    adapter = AgentMemoryAdapter(name="agentmemory", config={"cache_path": cache_file})

    created = await adapter.store_memory(
        MemoryInput(
            content="Created through provider",
            metadata={
                "title": "Provider Created",
                "type": "fact",
                "concepts": ["provider"],
                "strength": 6,
                "tags": ["Provider", "Test"],
                "sessionId": "session-provider",
            },
        )
    )

    assert created.content == "Created through provider"
    assert created.metadata.source == "agentmemory"
    assert created.metadata.tags == ["provider", "test"]
    assert created.metadata.session_id == "session-provider"

    fetched = await adapter.get_memory_by_id(created.id)
    assert fetched.id == created.id

    await adapter.update_memory(
        created.id,
        {
            "content": "Updated through provider",
            "metadata": {"tags": ["Updated"], "strength": 7},
        },
    )
    updated = await adapter.get_memory_by_id(created.id)
    assert updated.content == "Updated through provider"
    assert updated.metadata.tags == ["updated"]

    sessions = await adapter.list_sessions()
    assert any(session.id == "session-provider" for session in sessions)

    await adapter.delete_memory(created.id)
    with pytest.raises(MemoryNotFoundError):
        await adapter.get_memory_by_id(created.id)
