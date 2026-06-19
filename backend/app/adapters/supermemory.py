"""Supermemory adapter for memory and document search."""

from __future__ import annotations

from app.adapters.http_provider import HTTPMemoryAdapter


class SupermemoryAdapter(HTTPMemoryAdapter):
    """Adapter for Supermemory's Memory API."""

    source_type = "supermemory"
    capabilities = {"query", "keyword_search", "semantic_search", "hybrid_search", "store", "health"}
    default_base_url = "https://api.supermemory.ai"
    default_auth_env = "SUPERMEMORY_API_KEY"
    default_paths = {
        "search": "/v4/search",
        "store": "/v3/documents",
        "health": "/health",
    }

    def _search_payload(self, query: str, limit: int, mode: str | None = None) -> dict:
        payload = {
            "q": query,
            "searchMode": mode or self.config.get("search_mode", "hybrid"),
            "limit": limit,
        }
        container_tag = self.config.get("container_tag") or self.config.get("containerTag")
        if container_tag:
            payload["containerTag"] = container_tag
        threshold = self.config.get("threshold")
        if threshold is not None:
            payload["threshold"] = threshold
        filters = self.config.get("filters")
        if filters:
            payload["filters"] = filters
        return payload

    def _store_payload(self, input):
        metadata = input.metadata or {}
        payload = {
            "content": input.content,
            "metadata": metadata,
        }
        custom_id = metadata.get("customId") or metadata.get("custom_id")
        if custom_id:
            payload["customId"] = custom_id
        container_tags = metadata.get("containerTags") or metadata.get("container_tags")
        if container_tags:
            payload["containerTags"] = container_tags
        elif self.config.get("container_tag"):
            payload["containerTags"] = [self.config["container_tag"]]
        return payload
