"""Adapter registry — manages all memory source adapters."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource

logger = logging.getLogger(__name__)

# Source type → adapter class mapping
_ADAPTER_CLASSES: dict[str, type[MemorySource]] = {}


def _load_adapter_classes():
    """Lazily import adapter classes to avoid circular imports."""
    global _ADAPTER_CLASSES
    if _ADAPTER_CLASSES:
        return
    from app.adapters.hermes import HermesAdapter
    from app.adapters.agentmemory import AgentMemoryAdapter
    from app.adapters.mem0 import Mem0Adapter

    _ADAPTER_CLASSES = {
        "hermes": HermesAdapter,
        "agentmemory": AgentMemoryAdapter,
        "mem0": Mem0Adapter,
    }


class AdapterRegistry:
    """Central registry of memory source adapters."""

    def __init__(self):
        self._sources: dict[str, MemorySource] = {}

    def register(self, source: MemorySource):
        """Register a memory source adapter."""
        self._sources[source.name] = source
        logger.info("Registered memory source: %s (type=%s)", source.name, source.source_type)

    def get(self, name: str) -> Optional[MemorySource]:
        """Get a registered source by name."""
        return self._sources.get(name)

    def list_sources(self) -> list[dict]:
        """List all registered sources with basic metadata."""
        return [
            {
                "name": s.name,
                "type": s.source_type,
                "enabled": s.enabled,
            }
            for s in self._sources.values()
        ]

    async def list_all(self, limit: int = 50) -> list[MemoryItem]:
        """Aggregate memories from all enabled sources."""
        tasks = []
        for s in self._sources.values():
            if s.enabled:
                tasks.append(s.list(limit=limit))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items: list[MemoryItem] = []
        for r in results:
            if isinstance(r, list):
                items.extend(r)
        return items

    async def search_all(self, query: str, limit: int = 20) -> list[MemoryItem]:
        """Search across all enabled sources."""
        tasks = []
        for s in self._sources.values():
            if s.enabled:
                tasks.append(s.search(query, limit=limit))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items: list[MemoryItem] = []
        for r in results:
            if isinstance(r, list):
                items.extend(r)
        return items

    async def get_by_id(self, id: str) -> Optional[MemoryItem]:
        """Find a memory by ID across all enabled sources."""
        tasks = []
        sources = [s for s in self._sources.values() if s.enabled]
        for s in sources:
            tasks.append(s.get(id))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, MemoryItem):
                return r
        return None

    async def health_check(self) -> dict:
        """Run health checks on all registered sources."""
        result: dict = {}
        for s in self._sources.values():
            try:
                healthy = await s.health()
            except Exception:
                healthy = False
            count = 0
            if healthy and s.enabled:
                try:
                    count = await s.count()
                except Exception:
                    pass
            result[s.name] = {
                "type": s.source_type,
                "enabled": s.enabled,
                "healthy": healthy,
                "count": count,
            }
        return result


def init_registry_from_config(config: dict) -> AdapterRegistry:
    """Create and populate a registry from YAML config sources section.

    Args:
        config: The full resolved YAML config dict.

    Returns:
        Initialized AdapterRegistry.
    """
    _load_adapter_classes()

    import os

    registry = AdapterRegistry()
    sources_config = config.get("sources", [])

    if not sources_config:
        # Auto-register defaults from app settings
        from app.config import settings

        registry.register(
            _ADAPTER_CLASSES["hermes"](
                name="hermes",
                config={"memories_dir": settings.HERMES_MEMORIES_DIR},
            )
        )
        registry.register(
            _ADAPTER_CLASSES["agentmemory"](
                name="agentmemory",
                config={"cache_path": settings.AGENTMEMORY_CACHE},
            )
        )
        # mem0 auto — only if API key present
        if os.environ.get("MEM0_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["mem0"](name="mem0", config={})
            )
        return registry

    for src in sources_config:
        src_type = src.get("type", "")
        src_name = src.get("name", src_type)
        src_enabled = src.get("enabled", True)
        src_config = src.get("config", {})

        # Handle "auto" enabled — enable only if conditions met
        if src_enabled == "auto":
            if src_type == "mem0":
                src_enabled = bool(os.environ.get("MEM0_API_KEY"))
            else:
                src_enabled = True

        if not src_enabled:
            continue

        cls = _ADAPTER_CLASSES.get(src_type)
        if cls is None:
            logger.warning("Unknown source type: %s (skipping %s)", src_type, src_name)
            continue

        adapter = cls(name=src_name, config=src_config)
        registry.register(adapter)

    return registry


# Global registry instance (initialized in main.py lifespan)
registry: AdapterRegistry | None = None
