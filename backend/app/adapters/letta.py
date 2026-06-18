"""Letta adapter for block-based agent memory."""

from __future__ import annotations

from app.adapters.http_provider import HTTPMemoryAdapter


class LettaAdapter(HTTPMemoryAdapter):
    """Adapter for Letta memory blocks."""

    source_type = "letta"
    default_base_url = "https://api.letta.com"
    default_auth_env = "LETTA_API_KEY"
    default_paths = {
        "list": "/v1/blocks/",
        "get": "/v1/blocks/{id}",
        "store": "/v1/blocks/",
        "update": "/v1/blocks/{id}",
        "delete": "/v1/blocks/{id}",
        "health": "/v1/health",
    }

    def _content_from_raw(self, raw: dict) -> str:
        value = raw.get("value")
        return value if isinstance(value, str) else super()._content_from_raw(raw)

    def _store_payload(self, input):
        metadata = input.metadata or {}
        return {
            "label": metadata.get("label") or metadata.get("title") or input.content[:40] or "memory",
            "value": input.content,
            "description": metadata.get("description"),
            "metadata": metadata,
            "tags": metadata.get("tags", []),
        }

    def _update_payload(self, patch):
        metadata = patch.get("metadata", {}) if isinstance(patch.get("metadata"), dict) else {}
        payload = dict(metadata)
        if "content" in patch:
            payload["value"] = patch["content"]
        if "title" in patch:
            payload["label"] = patch["title"]
        if "tags" in patch:
            payload["tags"] = patch["tags"]
        return payload

    async def search(self, query: str, limit: int = 20):
        query_lower = query.lower()
        results = []
        for item in await self.list(limit=max(limit, 200)):
            if query_lower in item.title.lower() or query_lower in item.content.lower():
                results.append(item)
                if len(results) >= limit:
                    break
        return results
