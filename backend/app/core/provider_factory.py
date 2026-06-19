"""Provider factory and multi-provider query strategy."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from app.core.errors import MemoryProviderError, ProviderConfigError, normalize_provider_error
from app.core.memory_provider import MemoryProvider
from app.core.memory_schema import MemoryInput, MemoryItem, MemoryQuery, MemoryQueryResult
from app.core.observability import ProviderObservability
from app.core.query_normalization import normalize_query_for_provider

logger = logging.getLogger(__name__)

ProviderBuilder = Callable[[str, dict[str, Any]], MemoryProvider]


@dataclass(slots=True)
class RetryStrategy:
    attempts: int = 1
    backoff_seconds: float = 0.1


@dataclass(slots=True)
class ProviderStrategy:
    active_provider: str = ""
    fallback_providers: list[str] = field(default_factory=list)
    parallel_query: bool = False
    timeout_seconds: float = 10.0
    retry: RetryStrategy = field(default_factory=RetryStrategy)
    debug_raw_response: bool = False


class ProviderFactory:
    """Creates providers and executes primary/fallback/fan-out strategies."""

    def __init__(self):
        self._builders: dict[str, ProviderBuilder] = {}
        self._providers: dict[str, MemoryProvider] = {}
        self._provider_types: dict[str, str] = {}
        self.strategy = ProviderStrategy()
        self.observability = ProviderObservability()

    def register_provider_type(self, provider_type: str, builder: ProviderBuilder) -> None:
        self._builders[provider_type] = builder

    def register_instance(self, provider: MemoryProvider, provider_type: str | None = None) -> None:
        self._providers[provider.name] = provider
        self._provider_types[provider.name] = provider_type or getattr(provider, "provider_type", "") or provider.name
        if not self.strategy.active_provider:
            self.strategy.active_provider = provider.name

    def create_provider(self, provider_type: str, name: str, config: dict[str, Any]) -> MemoryProvider:
        builder = self._builders.get(provider_type)
        if builder is None:
            raise ProviderConfigError(
                f"Unknown memory provider type: {provider_type}",
                provider=name,
                operation="create_provider",
            )
        provider = builder(name, config)
        self.register_instance(provider, provider_type)
        return provider

    def get_provider(self, name: str | None = None) -> MemoryProvider:
        provider_name = name or self.strategy.active_provider
        provider = self._providers.get(provider_name)
        if provider is None:
            raise ProviderConfigError(
                f"Memory provider is not configured: {provider_name}",
                provider=provider_name or "",
                operation="get_provider",
            )
        return provider

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def get_observability_snapshot(self, limit: int = 50) -> dict[str, Any]:
        return self.observability.snapshot(
            provider_types=self._provider_types,
            strategy=self.get_strategy_config(),
            limit=limit,
        )

    def get_strategy_config(self) -> dict[str, Any]:
        return {
            "activeProvider": self.strategy.active_provider,
            "fallbackProviders": list(self.strategy.fallback_providers),
            "parallelQuery": self.strategy.parallel_query,
            "timeoutSeconds": self.strategy.timeout_seconds,
            "retryAttempts": self.strategy.retry.attempts,
            "retryBackoffSeconds": self.strategy.retry.backoff_seconds,
            "debugRawResponse": self.strategy.debug_raw_response,
        }

    def switch_provider(self, name: str) -> MemoryProvider:
        provider = self.get_provider(name)
        self.strategy.active_provider = name
        return provider

    def update_strategy(
        self,
        *,
        active_provider: str | None = None,
        fallback_providers: list[str] | None = None,
        parallel_query: bool | None = None,
        timeout_seconds: float | None = None,
        retry_attempts: int | None = None,
        retry_backoff_seconds: float | None = None,
        debug_raw_response: bool | None = None,
    ) -> None:
        available = set(self.list_providers())
        if active_provider is not None and active_provider not in available:
            raise ProviderConfigError(
                f"Memory provider is not configured: {active_provider}",
                provider=active_provider,
                operation="update_strategy",
            )
        if fallback_providers is not None:
            unknown = [name for name in fallback_providers if name not in available]
            if unknown:
                raise ProviderConfigError(
                    f"Fallback provider is not configured: {unknown[0]}",
                    provider=unknown[0],
                    operation="update_strategy",
                    details={"unknownProviders": unknown},
                )

        self.configure_strategy(
            active_provider=active_provider,
            fallback_providers=fallback_providers,
            parallel_query=parallel_query,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
            debug_raw_response=debug_raw_response,
        )

    def configure_strategy(
        self,
        *,
        active_provider: str | None = None,
        fallback_providers: list[str] | None = None,
        parallel_query: bool | None = None,
        timeout_seconds: float | None = None,
        retry_attempts: int | None = None,
        retry_backoff_seconds: float | None = None,
        debug_raw_response: bool | None = None,
    ) -> None:
        if active_provider:
            self.strategy.active_provider = active_provider
        if fallback_providers is not None:
            self.strategy.fallback_providers = fallback_providers
        if parallel_query is not None:
            self.strategy.parallel_query = parallel_query
        if timeout_seconds is not None:
            self.strategy.timeout_seconds = timeout_seconds
        if retry_attempts is not None:
            self.strategy.retry.attempts = max(1, retry_attempts)
        if retry_backoff_seconds is not None:
            self.strategy.retry.backoff_seconds = max(0.0, retry_backoff_seconds)
        if debug_raw_response is not None:
            self.strategy.debug_raw_response = debug_raw_response
        self.strategy.fallback_providers = [
            name
            for idx, name in enumerate(self.strategy.fallback_providers)
            if (
                name
                and name != self.strategy.active_provider
                and name not in self.strategy.fallback_providers[:idx]
            )
        ]

    def configure_from_dict(self, config: dict[str, Any]) -> None:
        """Load strategy from either new memory_providers config or legacy sources."""
        memory_cfg = (
            config.get("memory_providers")
            or config.get("memoryProviders")
            or config.get("memory")
            or {}
        )

        active_provider = memory_cfg.get("activeProvider") or memory_cfg.get("active_provider")
        fallback_providers = (
            memory_cfg.get("fallbackProviders")
            or memory_cfg.get("fallback_providers")
            or None
        )
        parallel_query = memory_cfg.get("parallelQuery", memory_cfg.get("parallel_query"))
        timeout_seconds = memory_cfg.get("timeoutSeconds", memory_cfg.get("timeout_seconds"))
        retry_attempts = memory_cfg.get("retryAttempts", memory_cfg.get("retry_attempts"))
        retry_backoff_seconds = memory_cfg.get("retryBackoffSeconds", memory_cfg.get("retry_backoff_seconds"))
        debug_raw_response = memory_cfg.get("debugRawResponse", memory_cfg.get("debug_raw_response"))

        sources = config.get("sources") or []
        if not active_provider and sources:
            for source in sources:
                if source.get("enabled", True):
                    active_provider = source.get("name") or source.get("type")
                    break

        if fallback_providers is None and active_provider and sources:
            fallback_providers = []
            for source in sources:
                name = source.get("name") or source.get("type")
                if name and name != active_provider and source.get("enabled", True):
                    fallback_providers.append(name)

        self.configure_strategy(
            active_provider=active_provider,
            fallback_providers=fallback_providers,
            parallel_query=parallel_query,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
            debug_raw_response=debug_raw_response,
        )

    def _provider_order(self) -> list[str]:
        names: list[str] = []
        if self.strategy.active_provider:
            names.append(self.strategy.active_provider)
        names.extend(self.strategy.fallback_providers)
        return [name for idx, name in enumerate(names) if name and name not in names[:idx]]

    def _provider_type(self, provider: MemoryProvider) -> str:
        return self._provider_types.get(provider.name, "") or getattr(provider, "provider_type", "")

    async def _run_with_policy(self, provider: MemoryProvider, operation: str, call):
        attempts = max(1, self.strategy.retry.attempts)
        last_error: MemoryProviderError | None = None

        for attempt in range(attempts):
            started = time.perf_counter()
            try:
                result = await asyncio.wait_for(call(), timeout=self.strategy.timeout_seconds)
                latency_ms = int((time.perf_counter() - started) * 1000)
                self.observability.record_call(
                    provider=provider.name,
                    provider_type=self._provider_type(provider),
                    operation=operation,
                    success=True,
                    latency_ms=latency_ms,
                    attempt=attempt + 1,
                )
                return result
            except Exception as exc:
                latency_ms = int((time.perf_counter() - started) * 1000)
                last_error = normalize_provider_error(exc, provider=provider.name, operation=operation)
                self.observability.record_call(
                    provider=provider.name,
                    provider_type=self._provider_type(provider),
                    operation=operation,
                    success=False,
                    latency_ms=latency_ms,
                    attempt=attempt + 1,
                    error=last_error.to_dict(),
                )
                if not last_error.retryable or attempt == attempts - 1:
                    break
                await asyncio.sleep(self.strategy.retry.backoff_seconds * (attempt + 1))

        assert last_error is not None
        raise last_error

    async def store_memory(self, input: MemoryInput, provider_name: str | None = None) -> MemoryItem:
        provider = self.get_provider(provider_name)
        return await self._run_with_policy(provider, "store_memory", lambda: provider.store_memory(input))

    async def query_memory(self, query: MemoryQuery) -> MemoryQueryResult:
        if self.strategy.debug_raw_response:
            query.include_raw = True
        if self.strategy.parallel_query:
            return await self.query_memory_parallel(query)
        return await self.query_memory_with_fallback(query)

    async def query_memory_from_provider(self, provider_name: str, query: MemoryQuery) -> MemoryQueryResult:
        provider = self.get_provider(provider_name)
        provider_query = normalize_query_for_provider(query, provider)
        started = time.perf_counter()
        try:
            result = await self._run_with_policy(
                provider,
                "query_memory",
                lambda: provider.query_memory(provider_query),
            )
        except Exception as exc:
            normalized = normalize_provider_error(exc, provider=provider.name, operation="query_memory")
            self.observability.record_route(
                operation="query_memory",
                strategy="direct",
                providers=[provider.name],
                latency_ms=int((time.perf_counter() - started) * 1000),
                errors=[normalized.to_dict()],
            )
            raise

        self.observability.record_route(
            operation="query_memory",
            strategy="direct",
            providers=[provider.name],
            successful_provider=result.provider or provider.name,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
        return result

    async def query_memory_with_fallback(self, query: MemoryQuery) -> MemoryQueryResult:
        last_error: MemoryProviderError | None = None
        started = time.perf_counter()
        providers_tried: list[str] = []
        route_errors: list[dict[str, Any]] = []
        for provider_name in self._provider_order():
            provider = self.get_provider(provider_name)
            provider_query = normalize_query_for_provider(query, provider)
            providers_tried.append(provider.name)
            try:
                result = await self._run_with_policy(
                    provider,
                    "query_memory",
                    lambda: provider.query_memory(provider_query),
                )
                self.observability.record_route(
                    operation="query_memory",
                    strategy="fallback",
                    providers=providers_tried,
                    successful_provider=result.provider or provider.name,
                    fallback_used=len(providers_tried) > 1,
                    latency_ms=int((time.perf_counter() - started) * 1000),
                    errors=route_errors,
                )
                return result
            except Exception as exc:
                last_error = normalize_provider_error(exc, provider=provider.name, operation="query_memory")
                route_errors.append(last_error.to_dict())
                logger.warning("Provider query failed: %s", last_error.to_dict())

        if last_error is not None:
            self.observability.record_route(
                operation="query_memory",
                strategy="fallback",
                providers=providers_tried,
                latency_ms=int((time.perf_counter() - started) * 1000),
                errors=route_errors,
            )
            raise last_error

        return MemoryQueryResult(items=[], latency=0, provider="")

    async def query_memory_parallel(
        self,
        query: MemoryQuery,
        provider_names: list[str] | None = None,
    ) -> MemoryQueryResult:
        started = time.perf_counter()
        selected_provider_names = provider_names or self._provider_order() or self.list_providers()
        providers = [self.get_provider(name) for name in selected_provider_names]

        async def run(provider: MemoryProvider):
            provider_query = normalize_query_for_provider(query, provider)
            return await self._run_with_policy(
                provider,
                "query_memory",
                lambda: provider.query_memory(provider_query),
            )

        results = await asyncio.gather(*(run(provider) for provider in providers), return_exceptions=True)
        merged: list[MemoryItem] = []
        seen: set[tuple[str, str]] = set()
        successful: list[str] = []
        errors: list[dict[str, Any]] = []

        for result in results:
            if isinstance(result, MemoryQueryResult):
                successful.append(result.provider)
                for item in result.items:
                    key = (item.metadata.source, item.id)
                    if key not in seen:
                        seen.add(key)
                        merged.append(item)
            elif isinstance(result, Exception):
                normalized = normalize_provider_error(result, operation="query_memory")
                errors.append(normalized.to_dict())
                logger.warning("Provider fan-out query failed: %s", normalized.to_dict())

        latency_ms = int((time.perf_counter() - started) * 1000)
        self.observability.record_route(
            operation="query_memory",
            strategy="parallel",
            providers=selected_provider_names,
            successful_provider=successful[0] if successful else "",
            successful_providers=successful,
            latency_ms=latency_ms,
            errors=errors,
        )
        return MemoryQueryResult(items=merged[: query.limit], latency=latency_ms, provider=",".join(successful))

    async def update_memory(self, id: str, patch: dict[str, Any], provider_name: str | None = None) -> None:
        provider = self.get_provider(provider_name)
        await self._run_with_policy(provider, "update_memory", lambda: provider.update_memory(id, patch))

    async def delete_memory(self, id: str, provider_name: str | None = None) -> None:
        provider = self.get_provider(provider_name)
        await self._run_with_policy(provider, "delete_memory", lambda: provider.delete_memory(id))

    async def get_memory_by_id(self, id: str, provider_name: str | None = None) -> MemoryItem:
        provider = self.get_provider(provider_name)
        return await self._run_with_policy(provider, "get_memory_by_id", lambda: provider.get_memory_by_id(id))

    async def health_check(self) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for name, provider in self._providers.items():
            try:
                healthy = await self._run_with_policy(provider, "health_check", provider.health_check)
                error = None
            except Exception as exc:
                healthy = False
                error = normalize_provider_error(exc, provider=name, operation="health_check").to_dict()
            results[name] = {
                "type": self._provider_types.get(name, ""),
                "active": name == self.strategy.active_provider,
                "fallback": name in self.strategy.fallback_providers,
                "healthy": healthy,
                "error": error,
            }
        return results
