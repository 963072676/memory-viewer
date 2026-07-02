"""Cognee adapter — reads/writes memories via Cognee's REST API.

Cognee is a knowledge graph engine for AI agents that builds structured
memory from unstructured text using graph + vector retrieval.
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from app.adapters.http_provider import HTTPMemoryAdapter
from app.adapters.base import MemoryItem
from app.core.errors import MemoryNotFoundError, ProviderUnavailableError
from app.core.memory_schema import MemoryInput, MemoryItem as CoreMemoryItem, MemoryQuery, MemoryQueryResult, Session


class CogneeAdapter(HTTPMemoryAdapter):
    """Adapter for Cognee knowledge graph memory engine."""

    source_type = "cognee"
    default_base_url = "http://localhost:8000"
    default_auth_env = "COGNEE_API_KEY"
    default_auth_scheme = "api-key"
    default_auth_header = "X-Api-Key"
    default_requires_auth = False  # local Cognee doesn't require auth by default
    default_paths = {
        "search": "/api/v1/search",
        "add": "/api/v1/add",
        "remember": "/api/v1/remember",
        "remember_entry": "/api/v1/remember/entry",
        "datasets": "/api/v1/datasets",
        "dataset_data": "/api/v1/datasets/{dataset_id}/data",
        "delete_data": "/api/v1/datasets/{dataset_id}/data/{data_id}",
        "cognify": "/api/v1/cognify",
    }

    def __init__(self, name: str = "cognee", config: dict | None = None):
        super().__init__(name=name, config=config)
        cfg = config or {}
        self.dataset: str = cfg.get("dataset", "default")
        self._auth_scheme = cfg.get("auth_scheme", "api-key")
        # Cognee cloud uses X-Api-Key; local uses Bearer token
        if self._auth_scheme == "bearer":
            self.auth_scheme = "Bearer"
            self.auth_header = "Authorization"

    def _result_to_item(self, raw: dict) -> MemoryItem:
        """Convert a Cognee search/dataset result to a MemoryItem."""
        # Cognee results can have various shapes depending on the query type
        content = (
            raw.get("content")
            or raw.get("text")
            or raw.get("description")
            or raw.get("value")
            or raw.get("answer")
            or ""
        )
        title = raw.get("title") or raw.get("name") or content[:80] if content else "cognee-result"

        return MemoryItem(
            id=str(raw.get("id", raw.get("data_id", raw.get("node_id", "")))),
            title=str(title),
            content=str(content),
            type=str(raw.get("type", raw.get("node_type", "fact"))),
            concepts=raw.get("concepts", raw.get("topics", [])) or [],
            strength=float(raw.get("strength", raw.get("score", 5.0))),
            created_at=str(raw.get("created_at", raw.get("createdAt", ""))),
            updated_at=str(raw.get("updated_at", raw.get("updatedAt", ""))),
            source=self.name,
            metadata={
                **raw,
                "tags": raw.get("tags", []),
                "raw": raw,
            },
        )

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        """List memories from the configured dataset."""
        # First, resolve dataset name to ID
        datasets_path = self._path("datasets")
        datasets_data = await self._request("GET", datasets_path)
        dataset_id = None

        if isinstance(datasets_data, list):
            for ds in datasets_data:
                if isinstance(ds, dict) and ds.get("name") == self.dataset:
                    dataset_id = ds.get("id")
                    break
        elif isinstance(datasets_data, dict):
            items = datasets_data.get("datasets", datasets_data.get("items", []))
            for ds in items:
                if isinstance(ds, dict) and ds.get("name") == self.dataset:
                    dataset_id = ds.get("id")
                    break

        if not dataset_id:
            # Try using dataset name directly as ID
            dataset_id = self.dataset

        path = self._path("dataset_data", dataset_id=dataset_id)
        data = await self._request("GET", path, params={"limit": limit, "offset": offset})
        if data is None:
            return []

        items_raw = data if isinstance(data, list) else data.get("items", data.get("data", []))
        if not isinstance(items_raw, list):
            items_raw = [items_raw] if isinstance(items_raw, dict) else []

        return [self._result_to_item(raw) for raw in items_raw if isinstance(raw, dict)]

    async def get(self, id: str) -> Optional[MemoryItem]:
        """Get a specific memory. Cognee doesn't have a direct get-by-ID endpoint,
        so we search and filter."""
        items = await self.search(id, limit=50)
        for item in items:
            if item.id == id:
                return item
        return None

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        """Search using Cognee's /api/v1/search endpoint."""
        path = self._path("search")
        payload = {
            "query": query,
            "dataset": self.dataset,
        }
        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None:
            return []

        # Cognee search results can be in various formats
        items_raw = []
        if isinstance(data, list):
            items_raw = data
        elif isinstance(data, dict):
            items_raw = (
                data.get("results", [])
                or data.get("items", [])
                or data.get("data", [])
                or data.get("nodes", [])
            )
            if not isinstance(items_raw, list):
                # Single result wrapped in dict
                items_raw = [data] if data.get("content") or data.get("text") else []

        results = [self._result_to_item(raw) for raw in items_raw if isinstance(raw, dict)]
        return results[:limit]

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        """Store memory using Cognee's /api/v1/remember/entry endpoint."""
        metadata = input.metadata or {}
        path = self._path("remember_entry")
        payload = {
            "entry": input.content,
            "session_id": metadata.get("session_id", metadata.get("sessionId", "memory-viewer")),
            "dataset": self.dataset,
        }
        data = await self._request("POST", path, content=json.dumps(payload))

        raw = data if isinstance(data, dict) else {"content": input.content}
        return self._result_to_item(raw).to_core(include_raw=True)

    async def delete_memory(self, id: str) -> None:
        """Delete a specific data item from the dataset."""
        # Resolve dataset ID
        datasets_path = self._path("datasets")
        datasets_data = await self._request("GET", datasets_path)
        dataset_id = self.dataset
        if isinstance(datasets_data, list):
            for ds in datasets_data:
                if isinstance(ds, dict) and ds.get("name") == self.dataset:
                    dataset_id = ds.get("id", self.dataset)
                    break

        path = self._path("delete_data", dataset_id=dataset_id, data_id=id)
        data = await self._request("DELETE", path)
        if data is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        """Cognee doesn't support direct updates; delete and re-add."""
        await self.delete_memory(id)
        if "content" in patch:
            input_data = MemoryInput(content=patch["content"], metadata=patch)
            await self.store_memory(input_data)

    async def health(self) -> bool:
        if not self.base_url:
            return False
        try:
            # Try the datasets endpoint as health check
            data = await self._request("GET", self._path("datasets"))
            return data is not None
        except Exception:
            # Try a simple root endpoint
            try:
                data = await self._request("GET", "/docs")
                return data is not None
            except Exception:
                return False
