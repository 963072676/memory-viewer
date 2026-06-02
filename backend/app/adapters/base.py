"""Base classes for memory source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


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


class MemorySource(ABC):
    """Abstract base class for memory source adapters."""

    name: str = ""
    source_type: str = ""
    enabled: bool = True

    def __init__(self, name: str = "", config: dict | None = None):
        if name:
            self.name = name
        self.config = config or {}

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
