"""Base classes for memory source adapters."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.core.errors import MemoryNotFoundError, UnsupportedCapabilityError
from app.core.memory_provider import MemoryProvider
from app.core.memory_schema import (
    MemoryInput,
    MemoryItem as CoreMemoryItem,
    MemoryMetadata,
    MemoryQuery,
    MemoryQueryResult,
    Session,
)


def _timestamp_ms(*values: Any) -> int:
    """Convert provider timestamps to epoch milliseconds."""
    for value in values:
        if value is None or value == "":
            continue
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                normalized = value.replace("Z", "+00:00")
                return int(datetime.fromisoformat(normalized).timestamp() * 1000)
            except ValueError:
                continue
    return int(time.time() * 1000)


@dataclass
class MemoryItem:
    """Unified memory item used across all adapters."""

    id: str
    title: str
    content: str
    type: str = "unknown"
    concepts: list[str] = field(default_factory=list)
    strength: float = 5.0
    created_at: str = ""
    updated_at: str = ""
    source: str = ""  # adapter name
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.type,
            "concepts": self.concepts,
            "strength": self.strength,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "source": self.source,
            "metadata": self.metadata,
        }

    def to_core(self, *, include_raw: bool = False) -> CoreMemoryItem:
        tags = self.metadata.get("tags", []) if isinstance(self.metadata, dict) else []
        agent_id = None
        session_id = None
        embedding = None

        if isinstance(self.metadata, dict):
            agent_id = self.metadata.get("agentId") or self.metadata.get("agent_id")
            session_id = self.metadata.get("sessionId") or self.metadata.get("session_id")
            session_ids = self.metadata.get("sessionIds") or self.metadata.get("session_ids")
            if not session_id and isinstance(session_ids, list) and session_ids:
                session_id = session_ids[0]
            embedding = self.metadata.get("embedding")

        raw = None
        if include_raw:
            raw = self.metadata.get("raw", self.to_dict()) if isinstance(self.metadata, dict) else self.to_dict()
        return CoreMemoryItem(
            id=self.id,
            content=self.content,
            embedding=embedding if isinstance(embedding, list) else None,
            metadata=MemoryMetadata(
                source=self.source,
                timestamp=_timestamp_ms(
                    self.updated_at,
                    self.created_at,
                    self.metadata.get("timestamp") if isinstance(self.metadata, dict) else None,
                ),
                agent_id=agent_id,
                session_id=session_id,
                tags=tags if isinstance(tags, list) else [],
                raw=raw,
            ),
        )


class MemorySource(MemoryProvider, ABC):
    """Abstract base class for memory source adapters."""

    name: str = ""
    source_type: str = ""
    provider_type: str = ""
    enabled: bool = True
    capabilities: set[str] = {"query", "keyword_search", "get", "list", "health"}

    def __init__(self, name: str = "", config: dict | None = None):
        if name:
            self.name = name
        self.config = config or {}
        self.provider_type = self.source_type or self.provider_type

    @abstractmethod
    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        """List memories from this source."""
        ...

    @abstractmethod
    async def get(self, id: str) -> Optional[MemoryItem]:
        """Get a single memory by ID."""
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        """Search memories matching query."""
        ...

    @abstractmethod
    async def health(self) -> bool:
        """Health check for this source."""
        ...

    async def count(self) -> int:
        """Total number of memories."""
        items = await self.list(limit=999999)
        return len(items)

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        raise UnsupportedCapabilityError(
            f"Provider does not support storing memories: {self.name}",
            provider=self.name,
            operation="store_memory",
        )

    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        started = time.perf_counter()
        if query.query:
            items = await self.search(query.query, limit=query.limit)
        else:
            items = await self.list(limit=query.limit)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return MemoryQueryResult(
            items=[item.to_core(include_raw=query.include_raw) for item in items],
            latency=latency_ms,
            provider=self.name,
        )

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        raise UnsupportedCapabilityError(
            f"Provider does not support updating memories: {self.name}",
            provider=self.name,
            operation="update_memory",
        )

    async def delete_memory(self, id: str) -> None:
        raise UnsupportedCapabilityError(
            f"Provider does not support deleting memories: {self.name}",
            provider=self.name,
            operation="delete_memory",
        )

    async def get_memory_by_id(self, id: str) -> CoreMemoryItem:
        item = await self.get(id)
        if item is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="get_memory_by_id",
            )
        return item.to_core()

    async def list_sessions(self) -> list[Session]:
        return []

    async def health_check(self) -> bool:
        return await self.health()
