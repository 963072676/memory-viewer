"""In-memory observability for provider calls and routing decisions."""

from __future__ import annotations

import time
from collections import deque
from copy import deepcopy
from typing import Any


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_operation_stats() -> dict[str, Any]:
    return {
        "calls": 0,
        "successes": 0,
        "errors": 0,
        "totalLatencyMs": 0,
        "maxLatencyMs": 0,
        "avgLatencyMs": 0,
        "errorRate": 0,
    }


def _new_provider_stats(provider_type: str = "") -> dict[str, Any]:
    return {
        "type": provider_type,
        "calls": 0,
        "successes": 0,
        "errors": 0,
        "retryEvents": 0,
        "fallbackSuccesses": 0,
        "totalLatencyMs": 0,
        "maxLatencyMs": 0,
        "avgLatencyMs": 0,
        "errorRate": 0,
        "lastSuccessAt": None,
        "lastFailureAt": None,
        "lastError": None,
        "operations": {},
    }


class ProviderObservability:
    """Tracks recent provider calls and route-level memory query decisions."""

    def __init__(self, max_events: int = 200):
        self.max_events = max_events
        self._call_events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._route_events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._provider_stats: dict[str, dict[str, Any]] = {}
        self._route_counts = {
            "direct": 0,
            "fallback": 0,
            "parallel": 0,
            "fallbackUsed": 0,
            "routeErrors": 0,
        }

    def record_call(
        self,
        *,
        provider: str,
        provider_type: str,
        operation: str,
        success: bool,
        latency_ms: int,
        attempt: int,
        error: dict[str, Any] | None = None,
    ) -> None:
        timestamp = _now_ms()
        event = {
            "timestamp": timestamp,
            "provider": provider,
            "type": provider_type,
            "operation": operation,
            "success": success,
            "latencyMs": latency_ms,
            "attempt": attempt,
            "error": error,
        }
        self._call_events.append(event)

        stats = self._provider_stats.setdefault(provider, _new_provider_stats(provider_type))
        if provider_type:
            stats["type"] = provider_type
        operation_stats = stats["operations"].setdefault(operation, _new_operation_stats())

        stats["calls"] += 1
        stats["totalLatencyMs"] += latency_ms
        stats["maxLatencyMs"] = max(stats["maxLatencyMs"], latency_ms)
        if attempt > 1:
            stats["retryEvents"] += 1

        operation_stats["calls"] += 1
        operation_stats["totalLatencyMs"] += latency_ms
        operation_stats["maxLatencyMs"] = max(operation_stats["maxLatencyMs"], latency_ms)

        if success:
            stats["successes"] += 1
            stats["lastSuccessAt"] = timestamp
            operation_stats["successes"] += 1
        else:
            stats["errors"] += 1
            stats["lastFailureAt"] = timestamp
            stats["lastError"] = error
            operation_stats["errors"] += 1

    def record_route(
        self,
        *,
        operation: str,
        strategy: str,
        providers: list[str],
        successful_provider: str = "",
        successful_providers: list[str] | None = None,
        fallback_used: bool = False,
        latency_ms: int = 0,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        successful_providers = successful_providers or ([successful_provider] if successful_provider else [])
        errors = errors or []
        event = {
            "timestamp": _now_ms(),
            "operation": operation,
            "strategy": strategy,
            "providers": providers,
            "successfulProvider": successful_provider,
            "successfulProviders": successful_providers,
            "fallbackUsed": fallback_used,
            "latencyMs": latency_ms,
            "errors": errors,
        }
        self._route_events.append(event)

        if strategy in self._route_counts:
            self._route_counts[strategy] += 1
        if fallback_used:
            self._route_counts["fallbackUsed"] += 1
            if successful_provider in self._provider_stats:
                self._provider_stats[successful_provider]["fallbackSuccesses"] += 1
        if errors:
            self._route_counts["routeErrors"] += len(errors)

    def snapshot(
        self,
        *,
        provider_types: dict[str, str],
        strategy: dict[str, Any],
        limit: int = 50,
    ) -> dict[str, Any]:
        providers: dict[str, Any] = {}
        for provider, provider_type in provider_types.items():
            providers[provider] = self._finalize_provider_stats(
                deepcopy(self._provider_stats.get(provider, _new_provider_stats(provider_type))),
                provider_type,
            )

        return {
            "strategy": strategy,
            "providers": providers,
            "routing": {
                **self._route_counts,
                "recentRoutes": list(self._route_events)[-limit:],
            },
            "recentCalls": list(self._call_events)[-limit:],
        }

    def _finalize_provider_stats(self, stats: dict[str, Any], provider_type: str) -> dict[str, Any]:
        stats["type"] = stats["type"] or provider_type
        calls = stats["calls"]
        stats["avgLatencyMs"] = round(stats["totalLatencyMs"] / calls, 2) if calls else 0
        stats["errorRate"] = round(stats["errors"] / calls, 4) if calls else 0

        for operation_stats in stats["operations"].values():
            operation_calls = operation_stats["calls"]
            operation_stats["avgLatencyMs"] = (
                round(operation_stats["totalLatencyMs"] / operation_calls, 2)
                if operation_calls
                else 0
            )
            operation_stats["errorRate"] = (
                round(operation_stats["errors"] / operation_calls, 4)
                if operation_calls
                else 0
            )
        return stats
