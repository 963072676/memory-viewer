"""Canonical memory schema shared by providers, services, and APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

QueryMode = Literal["semantic", "keyword", "hybrid"]


@dataclass(slots=True)
class MemoryMetadata:
    """Provider-neutral metadata attached to every memory item."""

    source: str
    timestamp: int
    agent_id: str | None = None
    session_id: str | None = None
    tags: list[str] = field(default_factory=list)
    raw: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "source": self.source,
            "timestamp": self.timestamp,
        }
        if self.agent_id is not None:
            data["agentId"] = self.agent_id
        if self.session_id is not None:
            data["sessionId"] = self.session_id
        if self.tags:
            data["tags"] = self.tags
        if self.raw is not None:
            data["raw"] = self.raw
        return data


@dataclass(slots=True)
class MemoryItem:
    """Unified memory item returned by every provider."""

    id: str
    content: str
    metadata: MemoryMetadata
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
        }
        if self.embedding is not None:
            data["embedding"] = self.embedding
        return data


@dataclass(slots=True)
class MemoryInput:
    """Input for storing a memory through a provider."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None


@dataclass(slots=True)
class MemoryQuery:
    """Provider-neutral query request."""

    query: str = ""
    mode: QueryMode = "hybrid"
    limit: int = 20
    filters: dict[str, Any] = field(default_factory=dict)
    include_raw: bool = False


@dataclass(slots=True)
class MemoryQueryResult:
    """Provider-neutral query response."""

    items: list[MemoryItem]
    latency: int
    provider: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "latency": self.latency,
            "provider": self.provider,
        }


@dataclass(slots=True)
class Session:
    """Provider-neutral session descriptor."""

    id: str
    agent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"id": self.id, "metadata": self.metadata}
        if self.agent_id is not None:
            data["agentId"] = self.agent_id
        return data
