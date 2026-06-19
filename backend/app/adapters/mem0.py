"""Mem0 adapter — interfaces with the mem0 REST API."""

from __future__ import annotations

import os
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource


class Mem0Adapter(MemorySource):
    """Adapter for mem0 cloud API."""

    source_type = "mem0"
    capabilities = {"query", "semantic_search", "hybrid_search", "get", "list", "health"}

    def __init__(self, name: str = "mem0", config: dict | None = None):
        super().__init__(name=name, config=config)
        self.api_key: str = (config or {}).get("api_key", "")
        if not self.api_key:
            self.api_key = os.environ.get("MEM0_API_KEY", "")
        self.base_url: str = (config or {}).get("base_url", "https://api.mem0.ai/v1")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    def _available(self) -> bool:
        return bool(self.api_key)

    async def _request(self, method: str, path: str, **kwargs) -> dict | list | None:
        """Make an HTTP request to mem0 API. Returns None on failure."""
        if not self._available():
            return None
        try:
            import httpx  # lightweight async HTTP client
        except ImportError:
            # Fallback to urllib if httpx not available
            import asyncio
            import json
            import urllib.request
            import urllib.error

            url = f"{self.base_url}{path}"
            headers = self._headers()
            try:
                req = urllib.request.Request(url, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return json.loads(resp.read().decode())
            except Exception:
                return None

        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.request(method, url, headers=self._headers(), **kwargs)
                if resp.status_code >= 400:
                    return None
                return resp.json()
        except Exception:
            return None

    def _to_item(self, raw: dict) -> MemoryItem:
        """Convert a mem0 memory dict to MemoryItem."""
        return MemoryItem(
            id=raw.get("id", ""),
            title=raw.get("metadata", {}).get("title", raw.get("memory", "")[:80]),
            content=raw.get("memory", raw.get("text", "")),
            type=raw.get("metadata", {}).get("type", "fact"),
            concepts=raw.get("metadata", {}).get("concepts", []),
            strength=float(raw.get("metadata", {}).get("strength", 5.0)),
            created_at=raw.get("created_at", ""),
            updated_at=raw.get("updated_at", ""),
            source=self.name,
            metadata=raw.get("metadata", {}),
        )

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        data = await self._request("GET", "/memories/")
        if data is None:
            return []
        memories = data if isinstance(data, list) else data.get("results", [])
        sliced = memories[offset : offset + limit]
        return [self._to_item(m) for m in sliced]

    async def get(self, id: str) -> Optional[MemoryItem]:
        data = await self._request("GET", f"/memories/{id}/")
        if data is None:
            return None
        return self._to_item(data)

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        import json as _json
        data = await self._request(
            "POST",
            "/memories/search/",
            content=_json.dumps({"query": query, "limit": limit}),
        )
        if data is None:
            return []
        memories = data if isinstance(data, list) else data.get("results", [])
        return [self._to_item(m) for m in memories[:limit]]

    async def health(self) -> bool:
        if not self._available():
            return False
        data = await self._request("GET", "/memories/", params={"page_size": 1})
        return data is not None
