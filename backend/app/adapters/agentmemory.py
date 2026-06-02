"""AgentMemory adapter — wraps existing JSON cache reading logic."""

from __future__ import annotations

import os
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource


class AgentMemoryAdapter(MemorySource):
    """Adapter for agentmemory JSON cache."""

    source_type = "agentmemory"

    def __init__(self, name: str = "agentmemory", config: dict | None = None):
        super().__init__(name=name, config=config)
        self.cache_path: str = config.get("cache_path", "") if config else ""

    def _resolve_path(self, p: str) -> str:
        from app.config import _PROJECT_ROOT
        p = os.path.expandvars(p)
        if not os.path.isabs(p):
            p = str(_PROJECT_ROOT / p)
        return p

    def _raw_memories(self) -> list[dict]:
        """Read raw memory dicts from JSON cache."""
        import json

        path = self._resolve_path(self.cache_path)
        if not path:
            # Fallback to settings
            from app.config import settings
            path = settings.AGENTMEMORY_CACHE

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "memories" in data:
                return data["memories"]
            # agentmemory MCP uses "mem:memories" key (dict of id→memory)
            if isinstance(data, dict) and "mem:memories" in data:
                val = data["mem:memories"]
                return list(val.values()) if isinstance(val, dict) else val
            if isinstance(data, list):
                return data
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return []

    def _to_item(self, raw: dict) -> MemoryItem:
        """Convert a raw agentmemory dict to MemoryItem."""
        return MemoryItem(
            id=raw.get("id", ""),
            title=raw.get("title", ""),
            content=raw.get("content", ""),
            type=raw.get("type", "unknown"),
            concepts=raw.get("concepts", []),
            strength=float(raw.get("strength", 5)),
            created_at=raw.get("createdAt", ""),
            updated_at=raw.get("updatedAt", ""),
            source=self.name,
            metadata={
                "version": raw.get("version"),
                "tags": raw.get("tags", []),
                "files": raw.get("files", []),
                "archived": raw.get("archived", False),
            },
        )

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        memories = self._raw_memories()
        # Filter archived
        active = [m for m in memories if not m.get("archived", False)]
        sliced = active[offset : offset + limit]
        return [self._to_item(m) for m in sliced]

    async def get(self, id: str) -> Optional[MemoryItem]:
        for raw in self._raw_memories():
            if raw.get("id") == id:
                return self._to_item(raw)
        return None

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        q = query.lower()
        results: list[MemoryItem] = []
        for raw in self._raw_memories():
            if raw.get("archived", False):
                continue
            title = raw.get("title", "").lower()
            content = raw.get("content", "").lower()
            concepts = [c.lower() for c in raw.get("concepts", [])]
            if q in title or q in content or q in concepts:
                results.append(self._to_item(raw))
                if len(results) >= limit:
                    break
        return results

    async def health(self) -> bool:
        path = self._resolve_path(self.cache_path)
        if not path:
            from app.config import settings
            path = settings.AGENTMEMORY_CACHE
        return os.path.isfile(path)
