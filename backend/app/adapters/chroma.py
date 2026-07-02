"""Chroma adapter — reads/writes documents in a Chroma collection via REST API.

Chroma is an embedding database. For memory browsing without embeddings,
we use get (with where_document filter for text search) and list via pagination.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Optional

from app.adapters.http_provider import HTTPMemoryAdapter
from app.adapters.base import MemoryItem
from app.core.errors import MemoryNotFoundError, UnsupportedCapabilityError
from app.core.memory_schema import MemoryInput, MemoryItem as CoreMemoryItem, MemoryQuery, MemoryQueryResult, Session


class ChromaAdapter(HTTPMemoryAdapter):
    """Adapter for Chroma embedding database collections."""

    source_type = "chroma"
    default_base_url = "http://localhost:8000"
    default_auth_env = "CHROMA_API_KEY"
    default_auth_scheme = "api-key"
    default_auth_header = "x-chroma-token"
    default_requires_auth = False  # local Chroma has no auth by default
    default_paths = {
        "get_collection": "/api/v1/collections/{collection_name}",
        "get": "/api/v1/collections/{collection_id}/get",
        "search": "/api/v1/collections/{collection_id}/get",
        "store": "/api/v1/collections/{collection_id}/add",
        "upsert": "/api/v1/collections/{collection_id}/upsert",
        "delete": "/api/v1/collections/{collection_id}/delete",
        "health": "/api/v1/heartbeat",
        "count": "/api/v1/collections/{collection_id}/count",
    }

    def __init__(self, name: str = "chroma", config: dict | None = None):
        super().__init__(name=name, config=config)
        cfg = config or {}
        self.collection_name: str = cfg.get("collection", "memories")
        self._collection_id: str | None = cfg.get("collection_id")
        self._tenant: str = cfg.get("tenant", "default_tenant")
        self._database: str = cfg.get("database", "default_database")

    async def _resolve_collection_id(self) -> str | None:
        """Resolve collection name to UUID. Cached after first lookup."""
        if self._collection_id:
            return self._collection_id

        path = self._path("get_collection", collection_name=self.collection_name)
        data = await self._request("GET", path)
        if data and isinstance(data, dict):
            self._collection_id = data.get("id")
        elif isinstance(data, list) and data:
            # Some Chroma versions return a list
            for coll in data:
                if isinstance(coll, dict) and coll.get("name") == self.collection_name:
                    self._collection_id = coll.get("id")
                    break
        return self._collection_id

    def _path(self, key: str, **values: Any) -> str:
        """Override to inject collection_id into path templates."""
        cid = self._collection_id or "PLACEHOLDER"
        values.setdefault("collection_id", cid)
        values.setdefault("collection_name", self.collection_name)
        return super()._path(key, **values)

    def _docs_to_items(self, data: dict) -> list[MemoryItem]:
        """Convert Chroma's flat-arrays get response to MemoryItem list."""
        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        distances = data.get("distances", [])

        items: list[MemoryItem] = []
        for i, doc_id in enumerate(ids):
            doc = documents[i] if i < len(documents) else ""
            meta = metadatas[i] if i < len(metadatas) else {}
            if not isinstance(meta, dict):
                meta = {}
            distance = distances[i] if i < len(distances) else None

            title = meta.get("title") or (doc[:80] if doc else str(doc_id))
            tags = meta.get("tags", [])
            if not isinstance(tags, list):
                tags = [str(tags)] if tags else []

            items.append(MemoryItem(
                id=str(doc_id),
                title=str(title),
                content=doc or "",
                type=str(meta.get("type", "fact")),
                concepts=meta.get("concepts", []) or [],
                strength=float(meta.get("strength", 5.0)),
                created_at=str(meta.get("created_at", meta.get("createdAt", ""))),
                updated_at=str(meta.get("updated_at", meta.get("updatedAt", ""))),
                source=self.name,
                metadata={
                    **meta,
                    "tags": tags,
                    "distance": distance,
                    "raw": {"id": doc_id, "document": doc, "metadata": meta},
                },
            ))
        return items

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        cid = await self._resolve_collection_id()
        if not cid:
            return []

        path = f"/api/v1/collections/{cid}/get"
        payload: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "include": ["metadatas", "documents"],
        }
        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None or not isinstance(data, dict):
            return []
        return self._docs_to_items(data)

    async def get(self, id: str) -> Optional[MemoryItem]:
        cid = await self._resolve_collection_id()
        if not cid:
            return None

        path = f"/api/v1/collections/{cid}/get"
        payload = {
            "ids": [id],
            "include": ["metadatas", "documents"],
        }
        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None or not isinstance(data, dict):
            return None
        items = self._docs_to_items(data)
        return items[0] if items else None

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        """Text-based search using Chroma's where_document $contains filter."""
        cid = await self._resolve_collection_id()
        if not cid:
            return []

        path = f"/api/v1/collections/{cid}/get"
        payload = {
            "where_document": {"$contains": query},
            "limit": limit,
            "include": ["metadatas", "documents"],
        }
        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None or not isinstance(data, dict):
            # Fallback: fetch all and filter client-side
            all_items = await self.list(limit=limit * 5)
            query_lower = query.lower()
            return [
                item for item in all_items
                if query_lower in item.content.lower() or query_lower in item.title.lower()
            ][:limit]
        return self._docs_to_items(data)

    async def count(self) -> int:
        cid = await self._resolve_collection_id()
        if not cid:
            return 0
        path = f"/api/v1/collections/{cid}/count"
        data = await self._request("GET", path)
        if isinstance(data, (int, float)):
            return int(data)
        return 0

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        cid = await self._resolve_collection_id()
        if not cid:
            raise UnsupportedCapabilityError(
                f"Cannot resolve collection '{self.collection_name}' in provider {self.name}",
                provider=self.name,
                operation="store_memory",
            )

        metadata = input.metadata or {}
        doc_id = str(metadata.get("id") or uuid.uuid4())

        payload_meta = {
            "title": metadata.get("title", input.content[:80]),
            "type": metadata.get("type", "fact"),
            "tags": metadata.get("tags", []),
            "concepts": metadata.get("concepts", []),
            "strength": metadata.get("strength", 5.0),
        }

        path = f"/api/v1/collections/{cid}/add"
        body = {
            "ids": [doc_id],
            "documents": [input.content],
            "metadatas": [payload_meta],
        }
        # Include embedding if provided
        embedding = metadata.get("embedding") or metadata.get("vector")
        if isinstance(embedding, list) and embedding:
            body["embeddings"] = [embedding]

        await self._request("POST", path, content=json.dumps(body))

        return MemoryItem(
            id=doc_id,
            content=input.content,
            metadata={**payload_meta, "raw": {"id": doc_id, "document": input.content, "metadata": payload_meta}},
            source=self.name,
        ).to_core(include_raw=True)

    async def delete_memory(self, id: str) -> None:
        cid = await self._resolve_collection_id()
        if not cid:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )
        path = f"/api/v1/collections/{cid}/delete"
        body = {"ids": [id]}
        data = await self._request("POST", path, content=json.dumps(body))
        if data is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        """Update via Chroma's upsert (insert-or-update)."""
        cid = await self._resolve_collection_id()
        if not cid:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="update_memory",
            )
        existing = await self.get(id)
        if existing is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="update_memory",
            )

        new_content = patch.get("content", existing.content)
        new_meta = {**existing.metadata, **patch}
        # Clean up non-payload fields
        new_meta.pop("raw", None)
        new_meta.pop("distance", None)

        path = f"/api/v1/collections/{cid}/upsert"
        body = {
            "ids": [id],
            "documents": [new_content],
            "metadatas": [new_meta],
        }
        await self._request("POST", path, content=json.dumps(body))

    async def health(self) -> bool:
        if not self.base_url:
            return False
        try:
            data = await self._request("GET", "/api/v1/heartbeat")
            return data is not None
        except Exception:
            return False
