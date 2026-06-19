"""Zep adapter for graph-backed agent memory."""

from __future__ import annotations

from app.adapters.http_provider import HTTPMemoryAdapter


class ZepAdapter(HTTPMemoryAdapter):
    """Adapter for Zep Cloud or compatible Zep servers."""

    source_type = "zep"
    capabilities = {"query", "semantic_search", "hybrid_search", "store", "sessions", "health"}
    default_base_url = "https://api.getzep.com"
    default_auth_env = "ZEP_API_KEY"
    default_paths = {
        "search": "/api/v2/graph/search",
        "store": "/api/v2/graph",
        "sessions": "/api/v2/sessions",
        "health": "/health",
    }

    def _search_payload(self, query: str, limit: int, mode: str | None = None) -> dict:
        payload = {
            "query": query,
            "limit": limit,
        }
        user_id = self.config.get("user_id")
        group_id = self.config.get("group_id")
        if user_id:
            payload["user_id"] = user_id
        if group_id:
            payload["group_id"] = group_id
        scope = self.config.get("scope")
        if scope:
            payload["scope"] = scope
        return payload

    def _store_payload(self, input):
        payload = {
            "data": input.content,
            "type": input.metadata.get("type", "text"),
            "metadata": input.metadata,
        }
        if input.metadata.get("userId") or input.metadata.get("user_id") or self.config.get("user_id"):
            payload["user_id"] = input.metadata.get("userId") or input.metadata.get("user_id") or self.config.get("user_id")
        if input.metadata.get("groupId") or input.metadata.get("group_id") or self.config.get("group_id"):
            payload["group_id"] = input.metadata.get("groupId") or input.metadata.get("group_id") or self.config.get("group_id")
        return payload
