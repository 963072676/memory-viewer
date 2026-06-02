"""Memory Viewer Python SDK — Async-capable typed client using httpx."""

import os
from typing import Optional

import httpx

from .models import (
    Memory, SearchResult, RagResponse, Digest, Template,
    Workspace, Member, ImportResult, Stats,
)


class MemoryClient:
    """Typed client for the Memory Viewer API.

    Usage:
        client = MemoryClient("http://localhost:8000")
        memories = client.list_memories(limit=10)
        result = client.search("python patterns", mode="semantic")
    """

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or os.environ.get("MV_API_KEY", "")
        self._headers = {"Content-Type": "application/json"}
        if self._api_key:
            self._headers["X-Api-Key"] = self._api_key

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, headers=self._headers, timeout=30)

    def _get(self, path: str, params: dict = None) -> dict:
        with self._client() as c:
            r = c.get(path, params=params)
            r.raise_for_status()
            return r.json()

    def _post(self, path: str, data: dict = None) -> dict:
        with self._client() as c:
            r = c.post(path, json=data or {})
            r.raise_for_status()
            return r.json()

    def _put(self, path: str, data: dict = None) -> dict:
        with self._client() as c:
            r = c.put(path, json=data or {})
            r.raise_for_status()
            return r.json()

    def _delete(self, path: str) -> dict:
        with self._client() as c:
            r = c.delete(path)
            r.raise_for_status()
            return r.json()

    # ─── Memories ──────────────────────────────────────────────────────────────

    def list_memories(self, limit: int = 50, offset: int = 0, type: str = None, tag: str = None) -> list[Memory]:
        """List memories with pagination."""
        params = {"limit": limit, "offset": offset}
        if type:
            params["type"] = type
        if tag:
            params["tag"] = tag
        result = self._get("/api/agentmemory/paginated", params)
        return [Memory(**m) for m in result.get("memories", [])]

    def get_memory(self, memory_id: str) -> Memory:
        """Get a single memory by ID."""
        result = self._get(f"/api/agentmemory/{memory_id}")
        return Memory(**result)

    def create_memory(self, title: str, content: str, type: str = "fact", tags: list[str] = None) -> Memory:
        """Create a new memory."""
        data = {"title": title, "content": content, "type": type, "tags": tags or []}
        result = self._post("/api/agentmemory", data)
        return Memory(**result.get("memory", result))

    def update_memory(self, memory_id: str, **kwargs) -> Memory:
        """Update a memory."""
        result = self._put(f"/api/agentmemory/{memory_id}", kwargs)
        return Memory(**result.get("memory", result))

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        self._delete(f"/api/agentmemory/{memory_id}")
        return True

    def archive_memory(self, memory_id: str) -> Memory:
        """Archive a memory."""
        result = self._post(f"/api/agentmemory/{memory_id}/archive")
        return Memory(**result.get("memory", result))

    # ─── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 10, mode: str = "keyword") -> list[SearchResult]:
        """Search memories."""
        if mode == "semantic":
            result = self._get("/api/search/semantic", {"q": query, "limit": limit, "mode": "semantic"})
        else:
            result = self._get("/api/search", {"q": query, "limit": limit})
        return [SearchResult(**r) for r in result.get("results", [])]

    def rag_search(self, query: str, top_k: int = 10) -> RagResponse:
        """RAG-powered search."""
        result = self._post("/api/search/rag", {"query": query, "top_k": top_k})
        return RagResponse(**result)

    # ─── Tags ──────────────────────────────────────────────────────────────────

    def list_tags(self) -> list[dict]:
        """List all tags."""
        result = self._get("/api/memories/tags")
        return result.get("tags", [])

    def auto_tag(self, memory_id: str) -> list[str]:
        """Auto-suggest tags for a memory."""
        result = self._post(f"/api/memories/{memory_id}/suggest-tags")
        return result.get("suggested_tags", [])

    # ─── Digests ───────────────────────────────────────────────────────────────

    def generate_digest(self, type: str = "daily", start_date: str = None, end_date: str = None) -> Digest:
        """Generate a memory digest."""
        body: dict = {"type": type}
        if start_date:
            body["start_date"] = start_date
        if end_date:
            body["end_date"] = end_date
        result = self._post("/api/digest/generate", body)
        return Digest(**result.get("digest", result))

    def get_latest_digest(self) -> Optional[Digest]:
        """Get the latest digest."""
        result = self._get("/api/digest/latest")
        if result.get("digest"):
            return Digest(**result["digest"])
        return None

    # ─── Templates ─────────────────────────────────────────────────────────────

    def list_templates(self) -> list[Template]:
        """List all templates."""
        result = self._get("/api/templates")
        return [Template(**t) for t in result.get("templates", [])]

    def create_from_template(self, template_id: str, values: dict) -> Memory:
        """Create a memory from a template."""
        result = self._post(f"/api/templates/{template_id}/create-memory", {"values": values})
        return Memory(**result.get("memory", result))

    # ─── Workspaces ────────────────────────────────────────────────────────────

    def list_workspaces(self) -> list[Workspace]:
        """List all workspaces."""
        result = self._get("/api/workspaces")
        return [Workspace(**w) for w in result.get("workspaces", [])]

    def create_workspace(self, name: str, description: str = "") -> Workspace:
        """Create a workspace."""
        result = self._post("/api/workspaces", {"name": name, "description": description})
        return Workspace(**result.get("workspace", result))

    # ─── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> Stats:
        """Get memory statistics."""
        result = self._get("/api/stats")
        return Stats(**result)

    # ─── Import/Export ─────────────────────────────────────────────────────────

    def export_memories(self, format: str = "json") -> str:
        """Export memories as string."""
        with self._client() as c:
            r = c.get("/api/agentmemory/export", params={"format": format})
            r.raise_for_status()
            return r.text
