"""Adapter registry — manages all memory source adapters."""

from __future__ import annotations

import asyncio
import copy
import logging
import os
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource
from app.core.memory_schema import MemoryQuery, MemoryQueryResult
from app.core.provider_factory import ProviderFactory

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
    from app.adapters.zep import ZepAdapter
    from app.adapters.letta import LettaAdapter
    from app.adapters.supermemory import SupermemoryAdapter
    from app.adapters.qdrant import QdrantAdapter
    from app.adapters.chroma import ChromaAdapter
    from app.adapters.cognee import CogneeAdapter

    _ADAPTER_CLASSES = {
        "hermes": HermesAdapter,
        "agentmemory": AgentMemoryAdapter,
        "mem0": Mem0Adapter,
        "zep": ZepAdapter,
        "letta": LettaAdapter,
        "supermemory": SupermemoryAdapter,
        "qdrant": QdrantAdapter,
        "chroma": ChromaAdapter,
        "cognee": CogneeAdapter,
    }


class AdapterRegistry:
    """Central registry of memory source adapters."""

    def __init__(self):
        self._sources: dict[str, MemorySource] = {}
        self.provider_factory = ProviderFactory()

    def register(self, source: MemorySource):
        """Register a memory source adapter."""
        self._sources[source.name] = source
        self.provider_factory.register_instance(source, source.source_type)
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

    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        """Query through the provider factory strategy."""
        return await self.provider_factory.query_memory(query)

    async def query_provider_memory(self, provider_name: str, query: MemoryQuery) -> MemoryQueryResult:
        """Query one provider through the shared policy layer."""
        return await self.provider_factory.query_memory_from_provider(provider_name, query)

    async def query_all_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        """Fan out a query to every registered provider."""
        return await self.provider_factory.query_memory_parallel(
            query,
            provider_names=self.provider_factory.list_providers(),
        )


def init_registry_from_config(config: dict) -> AdapterRegistry:
    """Create and populate a registry from YAML config sources section.

    Args:
        config: The full resolved YAML config dict.

    Returns:
        Initialized AdapterRegistry.
    """
    _load_adapter_classes()

    registry = AdapterRegistry()
    sources_config = config.get("sources", [])

    if not sources_config:
        # Auto-register defaults from app settings
        from app.config import settings

        registry.register(
            _ADAPTER_CLASSES["hermes"](
                name="hermes",
                config={
                    "memories_dir": settings.HERMES_MEMORIES_DIR,
                    "profiles_dir": settings.HERMES_PROFILES_DIR,
                },
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
        if os.environ.get("ZEP_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["zep"](name="zep", config={})
            )
        if os.environ.get("LETTA_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["letta"](name="letta", config={})
            )
        if os.environ.get("SUPERMEMORY_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["supermemory"](name="supermemory", config={})
            )
        # Qdrant auto — enable if base_url or API key is set
        if os.environ.get("QDRANT_BASE_URL") or os.environ.get("QDRANT_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["qdrant"](name="qdrant", config={
                    "base_url": os.environ.get("QDRANT_BASE_URL", "http://localhost:6333"),
                    "collection": os.environ.get("QDRANT_COLLECTION", "memories"),
                })
            )
        # Chroma auto — enable if base_url or API key is set
        if os.environ.get("CHROMA_BASE_URL") or os.environ.get("CHROMA_API_KEY"):
            registry.register(
                _ADAPTER_CLASSES["chroma"](name="chroma", config={
                    "base_url": os.environ.get("CHROMA_BASE_URL", "http://localhost:8000"),
                    "collection": os.environ.get("CHROMA_COLLECTION", "memories"),
                })
            )
        # Cognee auto — enable if API key or base_url is set
        if os.environ.get("COGNEE_API_KEY") or os.environ.get("COGNEE_BASE_URL"):
            registry.register(
                _ADAPTER_CLASSES["cognee"](name="cognee", config={})
            )
        _finalize_provider_strategy(registry, config)
        return registry

    for src in sources_config:
        src_type = src.get("type", "")
        src_name = src.get("name", src_type)
        src_enabled = src.get("enabled", True)
        src_config = src.get("config", {})

        # Handle "auto" enabled — enable only if conditions met
        if src_enabled == "auto":
            src_enabled = _auto_enabled(src_type)

        if not src_enabled:
            continue

        cls = _ADAPTER_CLASSES.get(src_type)
        if cls is None:
            logger.warning("Unknown source type: %s (skipping %s)", src_type, src_name)
            continue

        adapter = cls(name=src_name, config=src_config)
        registry.register(adapter)

    _finalize_provider_strategy(registry, config)
    return registry


# Global registry instance (initialized in main.py lifespan)
registry: AdapterRegistry | None = None
_registry_signature: tuple[str, str, str, bool, bool, bool, bool] | None = None


def _current_runtime_signature() -> tuple[str, str, str, bool, bool, bool, bool]:
    """Track runtime settings that should rebuild the global registry."""
    from app.config import settings

    return (
        settings.HERMES_MEMORIES_DIR,
        settings.HERMES_PROFILES_DIR,
        settings.AGENTMEMORY_CACHE,
        bool(os.environ.get("MEM0_API_KEY")),
        bool(os.environ.get("ZEP_API_KEY")),
        bool(os.environ.get("LETTA_API_KEY")),
        bool(os.environ.get("SUPERMEMORY_API_KEY")),
    )


def _runtime_config_from_settings(config: dict | None = None) -> dict:
    """Apply environment-backed runtime overrides to provider config."""
    from app.config import settings

    runtime_config = copy.deepcopy(config or {})
    sources = runtime_config.get("sources") or []

    agentmemory_override = os.environ.get("MV_AGENTMEMORY_CACHE") or os.environ.get("AGENTMEMORY_CACHE")
    hermes_override = os.environ.get("MV_HERMES_MEMORIES_DIR") or os.environ.get("HERMES_MEMORIES_DIR")
    hermes_profiles_override = os.environ.get("MV_HERMES_PROFILES_DIR") or os.environ.get("HERMES_PROFILES_DIR")

    for source in sources:
        source_type = source.get("type")
        source_config = source.setdefault("config", {})
        if source_type == "agentmemory" and agentmemory_override:
            source_config["cache_path"] = settings.AGENTMEMORY_CACHE
        elif source_type == "hermes":
            if hermes_override:
                source_config["memories_dir"] = settings.HERMES_MEMORIES_DIR
            if hermes_profiles_override:
                source_config["profiles_dir"] = settings.HERMES_PROFILES_DIR

    return runtime_config


def _auto_enabled(source_type: str) -> bool:
    env_by_type = {
        "mem0": "MEM0_API_KEY",
        "zep": "ZEP_API_KEY",
        "letta": "LETTA_API_KEY",
        "supermemory": "SUPERMEMORY_API_KEY",
        "qdrant": "QDRANT_API_KEY",
        "chroma": "CHROMA_API_KEY",
        "cognee": "COGNEE_API_KEY",
    }
    env_name = env_by_type.get(source_type)
    # Qdrant and Chroma work without auth (local), auto-enable if base_url is set
    if source_type in ("qdrant", "chroma"):
        return True  # enabled by default when explicitly configured
    return bool(os.environ.get(env_name)) if env_name else True


def initialize_registry(config: dict | None = None) -> AdapterRegistry:
    """Initialize the process-wide adapter registry from config and settings."""
    global registry, _registry_signature

    if config is None:
        from app.config import _PROJECT_ROOT
        from app.config_loader import load_config

        config = load_config(_PROJECT_ROOT)

    registry = init_registry_from_config(_runtime_config_from_settings(config))
    _registry_signature = _current_runtime_signature()
    return registry


def get_registry() -> AdapterRegistry:
    """Return an initialized registry, rebuilding when runtime paths change."""
    global registry

    current_signature = _current_runtime_signature()
    if registry is None or _registry_signature != current_signature:
        return initialize_registry()
    return registry


def _finalize_provider_strategy(adapter_registry: AdapterRegistry, config: dict) -> None:
    """Keep provider strategy aligned with successfully registered adapters."""
    adapter_registry.provider_factory.configure_from_dict(config)
    available = adapter_registry.provider_factory.list_providers()
    if not available:
        return

    active = adapter_registry.provider_factory.strategy.active_provider
    if active not in available:
        active = available[0]

    fallback = [
        name
        for name in adapter_registry.provider_factory.strategy.fallback_providers
        if name in available and name != active
    ]
    if not fallback:
        fallback = [name for name in available if name != active]

    adapter_registry.provider_factory.configure_strategy(
        active_provider=active,
        fallback_providers=fallback,
    )
