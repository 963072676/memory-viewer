"""Reusable HTTP adapter primitives for remote memory providers."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

from app.adapters.base import MemoryItem, MemorySource
from app.core.errors import MemoryNotFoundError, ProviderUnavailableError, UnsupportedCapabilityError
from app.core.memory_schema import MemoryInput, MemoryItem as CoreMemoryItem, MemoryQuery, MemoryQueryResult, Session

# Module-level shared httpx client for connection pooling across all adapter instances.
# Lazily initialized on first use; call close_shared_client() on app shutdown.
_shared_client = None


def _get_shared_client():
    """Get or create the shared httpx.AsyncClient with connection pooling."""
    global _shared_client
    if _shared_client is None:
        import httpx
        _shared_client = httpx.AsyncClient(
            timeout=30,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
        )
    return _shared_client


async def close_shared_client():
    """Close the shared HTTP client. Call during app shutdown."""
    global _shared_client
    if _shared_client is not None:
        await _shared_client.aclose()
        _shared_client = None


class HTTPMemoryAdapter(MemorySource):
    """Base class for provider adapters that speak JSON over HTTP.

    Subclasses configure behavior via class-level attributes:
      - default_auth_scheme: "Bearer" | "Token" | "api-key" | "none"
      - default_auth_header: header name for api-key scheme (default "x-api-key")
      - default_response_key: specific key to extract items list (skips heuristic)
      - default_content_key: specific key for content field (skips heuristic)
      - default_requires_auth: whether API key is required (default True)
    """

    source_type = "http"
    default_base_url = ""
    default_auth_env = ""
    default_paths: dict[str, str] = {}
    default_auth_scheme: str = "Bearer"
    default_auth_header: str = "x-api-key"
    default_response_key: str | None = None
    default_content_key: str | None = None
    default_requires_auth: bool = True

    def __init__(self, name: str = "", config: dict | None = None):
        super().__init__(name=name, config=config)
        cfg = config or {}
        self.api_key: str = cfg.get("api_key") or os.environ.get(self.default_auth_env, "")
        self.base_url: str = (cfg.get("base_url") or self.default_base_url).rstrip("/")
        self.timeout: float = float(cfg.get("timeout", 10))
        self.paths: dict[str, str] = {**self.default_paths, **(cfg.get("paths") or {})}
        self.headers_config: dict = cfg.get("headers") or {}
        self.auth_scheme: str = cfg.get("auth_scheme") or self.default_auth_scheme
        self.auth_header: str = cfg.get("auth_header") or self.default_auth_header
        self.response_key: str | None = cfg.get("response_key") or self.default_response_key
        self.content_key: str | None = cfg.get("content_key") or self.default_content_key
        self.requires_auth: bool = cfg.get("requires_auth", self.default_requires_auth)

    def _available(self) -> bool:
        if not self.base_url:
            return False
        if self.requires_auth and not self.api_key:
            return False
        return True

    def _auth_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            scheme = self.auth_scheme.lower()
            if scheme == "bearer":
                headers["Authorization"] = f"Bearer {self.api_key}"
            elif scheme == "token":
                headers["Authorization"] = f"Token {self.api_key}"
            elif scheme == "api-key":
                headers[self.auth_header] = self.api_key
            elif scheme == "none":
                pass  # no auth header
            else:
                headers["Authorization"] = f"{self.auth_scheme} {self.api_key}"
        headers.update({str(k): str(v) for k, v in self.headers_config.items()})
        return headers

    def _path(self, key: str, **values: Any) -> str:
        path = self.paths.get(key, "")
        return path.format(**values) if path else ""

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self._available() or not path:
            return None
        try:
            url = f"{self.base_url}{path}"
            client = _get_shared_client()
            response = await client.request(method, url, headers=self._auth_headers(), **kwargs)
            if response.status_code == 404:
                return None
            if response.status_code >= 400:
                raise ProviderUnavailableError(
                    f"{self.name} request failed with status {response.status_code}",
                    provider=self.name,
                    operation=f"{method} {path}",
                    details={"status_code": response.status_code, "body": response.text[:500]},
                )
            if not response.content:
                return {}
            return response.json()
        except ProviderUnavailableError:
            raise
        except Exception as exc:
            raise ProviderUnavailableError(
                str(exc) or exc.__class__.__name__,
                provider=self.name,
                operation=f"{method} {path}",
                details={"exception": exc.__class__.__name__},
            ) from exc

    def _extract_items(self, data: Any) -> list[dict]:
        if data is None:
            return []
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            # Use configured response_key if set
            if self.response_key:
                value = data.get(self.response_key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
                return []
            # Heuristic: try common response keys
            for key in ("results", "memories", "items", "data", "facts", "blocks"):
                value = data.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
            return [data]
        return []

    def _content_from_raw(self, raw: dict) -> str:
        # Use configured content_key if set
        if self.content_key:
            value = raw.get(self.content_key)
            if isinstance(value, str):
                return value
            return ""
        # Heuristic: try common content keys
        for key in ("content", "memory", "text", "chunk", "fact", "value", "context"):
            value = raw.get(key)
            if isinstance(value, str):
                return value
        return ""

    def _metadata_from_raw(self, raw: dict) -> dict:
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        tags = raw.get("tags") or metadata.get("tags") or raw.get("containerTags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]
        return {
            **metadata,
            "tags": tags,
            "raw": raw,
            "score": raw.get("score", raw.get("similarity")),
        }

    def _to_item(self, raw: dict) -> MemoryItem:
        metadata = self._metadata_from_raw(raw)
        content = self._content_from_raw(raw)
        title = raw.get("title") or raw.get("label") or metadata.get("title") or content[:80]
        return MemoryItem(
            id=str(raw.get("id") or raw.get("uuid") or raw.get("block_id") or raw.get("customId") or ""),
            title=str(title or ""),
            content=content,
            type=str(raw.get("type") or metadata.get("type") or "fact"),
            concepts=raw.get("concepts") or metadata.get("concepts") or [],
            strength=float(raw.get("strength") or metadata.get("strength") or 5.0),
            created_at=str(raw.get("createdAt") or raw.get("created_at") or ""),
            updated_at=str(raw.get("updatedAt") or raw.get("updated_at") or ""),
            source=self.name,
            metadata=metadata,
        )

    def _search_payload(self, query: str, limit: int, mode: str | None = None) -> dict:
        return {"query": query, "limit": limit}

    def _store_payload(self, input: MemoryInput) -> dict:
        return {
            "content": input.content,
            "metadata": input.metadata,
        }

    def _update_payload(self, patch: dict[str, Any]) -> dict:
        return patch

    async def _search_items(self, query: str, limit: int, mode: str | None = None) -> list[MemoryItem]:
        path = self._path("search")
        payload = self._search_payload(query, limit, mode=mode)
        data = await self._request("POST", path, content=json.dumps(payload))
        return [self._to_item(raw) for raw in self._extract_items(data)[:limit]]

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        path = self._path("list")
        data = await self._request("GET", path, params={"limit": limit, "offset": offset})
        return [self._to_item(raw) for raw in self._extract_items(data)]

    async def get(self, id: str) -> Optional[MemoryItem]:
        path = self._path("get", id=id)
        data = await self._request("GET", path)
        items = self._extract_items(data)
        return self._to_item(items[0]) if items else None

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        return await self._search_items(query, limit)

    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        if not query.query or not self._path("search"):
            return await super().query_memory(query)

        started = time.perf_counter()
        items = await self._search_items(query.query, query.limit, mode=query.mode)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return MemoryQueryResult(
            items=[item.to_core(include_raw=query.include_raw) for item in items],
            latency=latency_ms,
            provider=self.name,
        )

    async def health(self) -> bool:
        if not self._available():
            return False
        health_path = self._path("health")
        if not health_path:
            return True
        try:
            data = await self._request("GET", health_path)
            return data is not None
        except ProviderUnavailableError:
            return False

    async def store_memory(self, input: MemoryInput) -> CoreMemoryItem:
        path = self._path("store")
        if not path:
            raise UnsupportedCapabilityError(
                f"Provider does not support storing memories: {self.name}",
                provider=self.name,
                operation="store_memory",
            )
        data = await self._request("POST", path, content=json.dumps(self._store_payload(input)))
        items = self._extract_items(data)
        raw = items[0] if items else {"content": input.content, "metadata": input.metadata}
        return self._to_item(raw).to_core()

    async def update_memory(self, id: str, patch: dict[str, Any]) -> None:
        path = self._path("update", id=id)
        if not path:
            raise UnsupportedCapabilityError(
                f"Provider does not support updating memories: {self.name}",
                provider=self.name,
                operation="update_memory",
            )
        data = await self._request("PATCH", path, content=json.dumps(self._update_payload(patch)))
        if data is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="update_memory",
            )

    async def delete_memory(self, id: str) -> None:
        path = self._path("delete", id=id)
        if not path:
            raise UnsupportedCapabilityError(
                f"Provider does not support deleting memories: {self.name}",
                provider=self.name,
                operation="delete_memory",
            )
        data = await self._request("DELETE", path)
        if data is None:
            raise MemoryNotFoundError(
                f"Memory not found in provider {self.name}: {id}",
                provider=self.name,
                operation="delete_memory",
            )

    async def list_sessions(self) -> list[Session]:
        path = self._path("sessions")
        if not path:
            return []
        data = await self._request("GET", path)
        sessions: list[Session] = []
        for raw in self._extract_items(data):
            session_id = raw.get("id") or raw.get("session_id") or raw.get("sessionId")
            if session_id:
                sessions.append(Session(id=str(session_id), metadata={"source": self.name, "raw": raw}))
        return sessions
