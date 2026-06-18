"""Provider contract for the vendor-agnostic memory layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.memory_schema import MemoryInput, MemoryItem, MemoryQuery, MemoryQueryResult, Session


class MemoryProvider(ABC):
    """Abstract contract implemented by every memory provider adapter."""

    name: str
    provider_type: str = ""
    capabilities: set[str] = set()

    @abstractmethod
    async def store_memory(self, input: MemoryInput) -> MemoryItem:
        """Store one memory and return the normalized item."""
        ...

    @abstractmethod
    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        """Run a semantic, keyword, or hybrid memory query."""
        ...

    @abstractmethod
    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        """Patch one memory by ID."""
        ...

    @abstractmethod
    async def delete_memory(self, id: str) -> None:
        """Delete one memory by ID."""
        ...

    @abstractmethod
    async def get_memory_by_id(self, id: str) -> MemoryItem:
        """Fetch one memory by ID."""
        ...

    @abstractmethod
    async def list_sessions(self) -> list[Session]:
        """List sessions visible to this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return provider health."""
        ...
