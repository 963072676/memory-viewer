"""Qdrant adapter — reads/writes points in a Qdrant collection via REST API.

Qdrant is a vector database. For memory browsing without embeddings,
we use scroll (payload-based listing) and payload filter search.
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from app.adapters.http_provider import HTTPMemoryAdapter
from app.adapters.base import MemoryItem
from app.core.errors import MemoryNotFoundError, UnsupportedCapabilityError
from app.core.memory_schema import MemoryInput, MemoryItem as CoreMemoryItem, MemoryQuery, MemoryQueryResult, Session


class QdrantAdapter(HTTPMemoryAdapter):
    """Adapter for Qdrant vector database memory collections."""

    source_type = "qdrant"
    default_base_url = "http://localhost:6333"
    default_auth_env = "QDRANT_API_KEY"
    default_auth_scheme = "api-key"
    default_auth_header = "api-key"
    default_requires_auth = False  # local Qdrant typically has no auth
    default_paths = {
        "scroll": "/collections/{collection}/points/scroll",
        "get": "/collections/{collection}/points/{id}",
        "search": "/collections/{collection}/points/search",
        "store": "/collections/{collection}/points",
        "delete": "/collections/{collection}/points/delete",
        "health": "/healthz",
        "collections": "/collections",
    }

    def __init__(self, name: str = "qdrant", config: dict | None = None):
        super().__init__(name=name, config=config)
        cfg = config or {}
        self.collection: str = cfg.get("collection", "memories")
        self.payload_content_key: str = cfg.get("payload_content_key", "content")
        self.payload_title_key: str = cfg.get("payload_title_key", "title")
        self.payload_type_key: str = cfg.get("payload_type_key", "type")
        self.payload_tags_key: str = cfg.get("payload_tags_key", "tags")

    def _path(self, key: str, **values: Any) -> str:
        """Override to inject collection name into path templates."""
        values.setdefault("collection", self.collection)
        return super()._path(key, **values)

    def _payload_to_item(self, point_id: str | int, payload: dict, score: float | None = None) -> MemoryItem:
        """Convert a Qdrant point's payload to a MemoryItem."""
        content = payload.get(self.payload_content_key, "")
        if not content:
            # Try common fallback keys
            for key in ("text", "memory", "document", "chunk", "value"):
                if payload.get(key):
                    content = str(payload[key])
                    break

        title = payload.get(self.payload_title_key) or content[:80] if content else str(point_id)
        tags = payload.get(self.payload_tags_key, [])
        if not isinstance(tags, list):
            tags = [str(tags)] if tags else []

        return MemoryItem(
            id=str(point_id),
            title=str(title),
            content=content,
            type=str(payload.get(self.payload_type_key, "fact")),
            concepts=payload.get("concepts", []) or [],
            strength=float(payload.get("strength", 5.0)),
            created_at=str(payload.get("created_at", payload.get("createdAt", ""))),
            updated_at=str(payload.get("updated_at", payload.get("updatedAt", ""))),
            source=self.name,
            metadata={
                **payload,
                "tags": tags,
                "score": score,
            },
        )

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        path = self._path("scroll")
        payload: dict[str, Any] = {
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
        }
        if offset:
            payload["offset"] = offset

        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None:
            return []

        result = data.get("result", data) if isinstance(data, dict) else data
        points = result.get("points", []) if isinstance(result, dict) else []

        return [
            self._payload_to_item(p["id"], p.get("payload", {}))
            for p in points
            if isinstance(p, dict) and "id" in p
        ]

    async def get(self, id: str) -> Optional[MemoryItem]:
        path = self._path("get", id=id)
        data = await self._request("GET", path)
        if data is None:
            return None

        result = data.get("result", data) if isinstance(data, dict) else data
        if not isinstance(result, dict) or "id" not in result:
            return None

        return self._payload_to_item(result["id"], result.get("payload", {}))

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        """Text-based search using Qdrant scroll with payload filter.

        Since Qdrant's /search endpoint requires a vector, we use scroll
        with a match-any filter on common text fields.
        """
        path = self._path("scroll")
        # Build filter: match query in content, title, or any text payload field
        payload: dict[str, Any] = {
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
            "filter": {
                "should": [
                    {"key": self.payload_content_key, "match": {"text": query}},
                    {"key": self.payload_title_key, "match": {"text": query}},
                ]
            },
        }

        data = await self._request("POST", path, content=json.dumps(payload))
        if data is None:
            # Fallback: fetch all and filter client-side
            all_items = await self.list(limit=limit * 5)
            query_lower = query.lower()
            return [
                item for item in all_items
                if query_lower in item.content.lower()
                or query_lower in item.title.lower()
            ][:limit]

        result = data.get("result", data) if isinstance(data, dict) else data
        points = result.get("points", []) if isinstance(result, dict) else []

        return [
            self._payload_to_item(p["id"], p.get("payload", {}))
            for p in points
            if isinstance(p, dict) and "id" in p
        ]

    async def count(self) -> int:
        """Use scroll with limit=0 to get approximate count."""
        path = self._path("scroll")
        payload = {"limit": 0, "with_payload": False, "with_vector": False}
        data = await self._request("POST", path, content=json.dumps(payload))
        if data and isinstance(data, dict):
            result = data.get("result", {})
            # Qdrant doesn't return total count in scroll; fall back to list
        items = await self.list(limit=999999)
        return len(items)

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        import uuid
        metadata = input.metadata or {}
        point_id = str(uuid.uuid4())

        payload_data = {
            self.payload_content_key: input.content,
            self.payload_title_key: metadata.get("title", input.content[:80]),
            self.payload_type_key: metadata.get("type", "fact"),
            self.payload_tags_key: metadata.get("tags", []),
            "concepts": metadata.get("concepts", []),
            "strength": metadata.get("strength", 5.0),
            "created_at": metadata.get("created_at", ""),
            "updated_at": metadata.get("updated_at", ""),
        }
        # Merge any extra metadata
        for k, v in metadata.items():
            if k not in payload_data and k not in ("embedding", "vector"):
                payload_data[k] = v

        # Build point — include vector if embedding is provided
        point: dict[str, Any] = {"id": point_id, "payload": payload_data}
        embedding = metadata.get("embedding") or metadata.get("vector")
        if isinstance(embedding, list) and embedding:
            point["vector"] = embedding

        path = self._path("store")
        body = {"points": [point]}
        await self._request("PUT", path, content=json.dumps(body), params={"wait": "true"})

        return self._payload_to_item(point_id, payload_data).to_core(include_raw=True)

    async def delete_memory(self, id: str) -> None:
        path = self._path("delete")
        body = {"points": [id]}
        data = await self._request("POST", path, content=json.dumps(body))
        if data is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        """Update by re-storing the point with merged payload."""
        existing = await self.get(id)
        if existing is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="update_memory",
            )

        merged_payload = {**existing.metadata, **patch}
        point: dict[str, Any] = {"id": id, "payload": merged_payload}

        path = self._path("store")
        body = {"points": [point]}
        await self._request("PUT", path, content=json.dumps(body), params={"wait": "true"})

    async def health(self) -> bool:
        if not self.base_url:
            return False
        try:
            data = await self._request("GET", "/healthz")
            return data is not None
        except Exception:
            return False
