"""AgentMemory adapter — wraps existing JSON cache reading logic."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource
from app.core.errors import MemoryNotFoundError
from app.core.memory_schema import MemoryInput, MemoryItem as CoreMemoryItem, Session


class AgentMemoryAdapter(MemorySource):
    """Adapter for agentmemory JSON cache."""

    source_type = "agentmemory"

    def __init__(self, name: str = "agentmemory", config: dict | None = None):
        super().__init__(name=name, config=config)
        self.cache_path: str = config.get("cache_path", "") if config else ""

    def _cache_file(self) -> str:
        path = self._resolve_path(self.cache_path)
        if not path:
            from app.config import settings
            path = settings.AGENTMEMORY_CACHE
        return path

    def _resolve_path(self, p: str) -> str:
        from app.config import _PROJECT_ROOT
        p = os.path.expandvars(p)
        if not os.path.isabs(p):
            p = str(_PROJECT_ROOT / p)
        return p

    def _raw_memories(self) -> list[dict]:
        """Read raw memory dicts from JSON cache."""
        path = self._cache_file()
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

    def _read_cache(self) -> dict:
        """Read cache in a write-friendly normalized format."""
        path = self._cache_file()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {"memories": []}

        if isinstance(data, dict) and "memories" in data:
            return data
        if isinstance(data, dict) and "mem:memories" in data:
            value = data["mem:memories"]
            memories = list(value.values()) if isinstance(value, dict) else value
            return {"memories": memories if isinstance(memories, list) else []}
        if isinstance(data, list):
            return {"memories": data}
        return {"memories": []}

    def _write_cache(self, data: dict) -> None:
        """Write cache atomically."""
        path = self._cache_file()
        dir_name = os.path.dirname(path)
        os.makedirs(dir_name, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _normalize_tags(self, tags: Any) -> list[str]:
        if not isinstance(tags, list):
            return []
        normalized: list[str] = []
        seen: set[str] = set()
        for tag in tags:
            tag_value = str(tag).strip().lower()
            if tag_value and tag_value not in seen:
                seen.add(tag_value)
                normalized.append(tag_value)
        return normalized

    def _new_id(self, title: str, content: str, created_at: str) -> str:
        digest = hashlib.md5(f"{title}{content}{created_at}".encode()).hexdigest()[:16]
        return f"mem_{digest}"

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
                "sessionIds": raw.get("sessionIds", []),
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
        return os.path.isfile(self._cache_file())

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        metadata = input.metadata or {}
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        title = str(metadata.get("title") or input.content[:80] or "Untitled memory")
        session_id = metadata.get("sessionId") or metadata.get("session_id")
        session_ids = metadata.get("sessionIds") or metadata.get("session_ids") or []
        if session_id and session_id not in session_ids:
            session_ids = [session_id, *session_ids]

        raw = {
            "id": self._new_id(title, input.content, now),
            "type": str(metadata.get("type", "fact")),
            "title": title,
            "content": input.content,
            "concepts": metadata.get("concepts", []),
            "files": metadata.get("files", []),
            "createdAt": now,
            "updatedAt": now,
            "strength": int(metadata.get("strength", 5)),
            "version": 1,
            "isLatest": True,
            "sessionIds": session_ids,
            "tags": self._normalize_tags(metadata.get("tags", [])),
        }

        data = self._read_cache()
        data.setdefault("memories", []).append(raw)
        self._write_cache(data)
        return self._to_item(raw).to_core(include_raw=True)

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        data = self._read_cache()
        memories = data.setdefault("memories", [])
        metadata = patch.get("metadata", {}) if isinstance(patch.get("metadata"), dict) else {}

        for raw in memories:
            if raw.get("id") != id:
                continue
            if "content" in patch:
                raw["content"] = patch["content"]
            if "title" in patch:
                raw["title"] = patch["title"]
            if "concepts" in patch or "concepts" in metadata:
                raw["concepts"] = patch.get("concepts", metadata.get("concepts", raw.get("concepts", [])))
            if "strength" in patch or "strength" in metadata:
                raw["strength"] = patch.get("strength", metadata.get("strength", raw.get("strength", 5)))
            if "tags" in patch or "tags" in metadata:
                raw["tags"] = self._normalize_tags(patch.get("tags", metadata.get("tags", [])))
            if "sessionId" in metadata or "session_id" in metadata:
                raw["sessionIds"] = [metadata.get("sessionId") or metadata.get("session_id")]
            raw["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            raw["version"] = raw.get("version", 1) + 1
            self._write_cache(data)
            return

        raise MemoryNotFoundError(
            f"Memory not found in provider {self.name}: {id}",
            provider=self.name,
            operation="update_memory",
        )

    async def delete_memory(self, id: str) -> None:
        data = self._read_cache()
        memories = data.setdefault("memories", [])
        next_memories = [raw for raw in memories if raw.get("id") != id]
        if len(next_memories) == len(memories):
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )
        data["memories"] = next_memories
        self._write_cache(data)

    async def get_memory_by_id(self, id: str) -> CoreMemoryItem:
        item = await self.get(id)
        if item is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="get_memory_by_id",
            )
        return item.to_core(include_raw=True)

    async def list_sessions(self) -> list[Session]:
        sessions: dict[str, Session] = {}
        for raw in self._raw_memories():
            for session_id in raw.get("sessionIds", []) or []:
                if session_id not in sessions:
                    sessions[session_id] = Session(id=session_id, metadata={"source": self.name})
        return list(sessions.values())
