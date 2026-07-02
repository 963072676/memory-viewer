"""API Usage Analytics tracker middleware (F-49) — Track API consumption patterns and costs.

Records endpoint, method, response_time, status_code, timestamp, request_size, response_size.
Aggregates hourly/daily rollups.
"""

import json
import logging
import os
import time
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger(__name__)

USAGE_STATS_PATH = os.path.join(settings.cache_dir, "usage_stats.json")

# Cost per 1K tokens (configurable)
DEFAULT_COST_PER_1K_TOKENS = {
    "input": 0.0015,
    "output": 0.002,
}


class UsageTracker:
    """Tracks API usage with in-memory buffer and periodic persistence."""

    FLUSH_INTERVAL = 100  # flush every N records

    def __init__(self, max_buffer: int = 500):
        self._buffer: deque[dict] = deque(maxlen=max_buffer)
        self._llm_usage: dict[str, dict] = {}  # feature -> {tokens_in, tokens_out, cost}
        self._cost_config = dict(DEFAULT_COST_PER_1K_TOKENS)
        self._unflushed_count: int = 0  # tracks records since last flush

    def record(self, path: str, method: str, status: int, duration_ms: float,
               request_size: int = 0, response_size: int = 0):
        """Record an API request."""
        self._buffer.append({
            "path": path,
            "method": method,
            "status": status,
            "duration_ms": duration_ms,
            "request_size": request_size,
            "response_size": response_size,
            "timestamp": time.time(),
        })
        self._unflushed_count += 1
        # Periodic flush based on record count since last flush
        if self._unflushed_count >= self.FLUSH_INTERVAL:
            self._flush()
            self._unflushed_count = 0

    def record_llm_usage(self, feature: str, tokens_in: int, tokens_out: int):
        """Record LLM token usage for a feature."""
        if feature not in self._llm_usage:
            self._llm_usage[feature] = {"tokens_in": 0, "tokens_out": 0, "calls": 0}
        self._llm_usage[feature]["tokens_in"] += tokens_in
        self._llm_usage[feature]["tokens_out"] += tokens_out
        self._llm_usage[feature]["calls"] += 1

    def get_usage_summary(self, period: str = "24h") -> dict:
        """Get usage summary for a time period."""
        now = time.time()
        period_seconds = {"1h": 3600, "24h": 86400, "7d": 604800, "30d": 2592000}
        cutoff = now - period_seconds.get(period, 86400)

        relevant = [e for e in self._buffer if e["timestamp"] >= cutoff]
        if not relevant:
            return {
                "period": period,
                "total_requests": 0,
                "avg_latency_ms": 0,
                "error_rate": 0,
                "p50_ms": 0,
                "p95_ms": 0,
            }

        durations = sorted(e["duration_ms"] for e in relevant)
        errors = sum(1 for e in relevant if e["status"] >= 400)
        n = len(durations)

        return {
            "period": period,
            "total_requests": n,
            "avg_latency_ms": round(sum(durations) / n, 2),
            "error_rate": round(errors / n * 100, 2) if n > 0 else 0,
            "p50_ms": round(durations[n // 2], 2),
            "p95_ms": round(durations[int(n * 0.95)], 2) if n > 0 else 0,
            "total_request_bytes": sum(e.get("request_size", 0) for e in relevant),
            "total_response_bytes": sum(e.get("response_size", 0) for e in relevant),
        }

    def get_endpoint_breakdown(self, period: str = "24h") -> list[dict]:
        """Get per-endpoint usage breakdown."""
        now = time.time()
        period_seconds = {"1h": 3600, "24h": 86400, "7d": 604800, "30d": 2592000}
        cutoff = now - period_seconds.get(period, 86400)

        relevant = [e for e in self._buffer if e["timestamp"] >= cutoff]

        endpoints: dict[str, list] = {}
        for e in relevant:
            key = f"{e['method']} {e['path']}"
            endpoints.setdefault(key, []).append(e)

        result = []
        for key, entries in endpoints.items():
            durations = sorted(e["duration_ms"] for e in entries)
            n = len(durations)
            errors = sum(1 for e in entries if e["status"] >= 400)
            result.append({
                "endpoint": key,
                "count": n,
                "avg_ms": round(sum(durations) / n, 2),
                "p50_ms": round(durations[n // 2], 2),
                "p95_ms": round(durations[int(n * 0.95)], 2) if n > 0 else 0,
                "error_count": errors,
                "error_rate": round(errors / n * 100, 2) if n > 0 else 0,
            })

        result.sort(key=lambda x: x["count"], reverse=True)
        return result

    def get_cost_breakdown(self) -> dict:
        """Get LLM token usage and estimated cost."""
        feature_costs = []
        total_in = 0
        total_out = 0
        total_cost = 0.0

        for feature, usage in self._llm_usage.items():
            cost_in = (usage["tokens_in"] / 1000) * self._cost_config["input"]
            cost_out = (usage["tokens_out"] / 1000) * self._cost_config["output"]
            cost = cost_in + cost_out
            total_in += usage["tokens_in"]
            total_out += usage["tokens_out"]
            total_cost += cost
            feature_costs.append({
                "feature": feature,
                "tokens_in": usage["tokens_in"],
                "tokens_out": usage["tokens_out"],
                "calls": usage["calls"],
                "estimated_cost": round(cost, 6),
            })

        return {
            "features": sorted(feature_costs, key=lambda x: x["estimated_cost"], reverse=True),
            "total_tokens_in": total_in,
            "total_tokens_out": total_out,
            "total_estimated_cost": round(total_cost, 6),
            "cost_per_1k": self._cost_config,
        }

    def get_trends(self, period: str = "24h", granularity: str = "hourly") -> list[dict]:
        """Get time-series data for charts."""
        now = time.time()
        period_seconds = {"1h": 3600, "24h": 86400, "7d": 604800, "30d": 2592000}
        cutoff = now - period_seconds.get(period, 86400)
        bucket_size = 3600 if granularity == "hourly" else 86400

        relevant = [e for e in self._buffer if e["timestamp"] >= cutoff]

        buckets: dict[int, list] = {}
        for e in relevant:
            bucket_key = int(e["timestamp"] // bucket_size) * bucket_size
            buckets.setdefault(bucket_key, []).append(e)

        trends = []
        for ts in sorted(buckets.keys()):
            entries = buckets[ts]
            durations = [e["duration_ms"] for e in entries]
            errors = sum(1 for e in entries if e["status"] >= 400)
            n = len(durations)
            trends.append({
                "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                "requests": n,
                "avg_latency_ms": round(sum(durations) / n, 2) if n else 0,
                "errors": errors,
                "error_rate": round(errors / n * 100, 2) if n else 0,
            })

        return trends

    def set_cost_config(self, input_cost: float, output_cost: float):
        """Update cost per 1K tokens configuration."""
        self._cost_config = {"input": input_cost, "output": output_cost}

    def _flush(self):
        """Flush buffer to disk (append to stats file)."""
        try:
            os.makedirs(os.path.dirname(USAGE_STATS_PATH), exist_ok=True)
            existing = []
            try:
                with open(USAGE_STATS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "entries" in data:
                        existing = data["entries"]
            except (FileNotFoundError, json.JSONDecodeError):
                pass

            new_entries = list(self._buffer)
            # Retention: raw data 7 days
            cutoff = time.time() - 7 * 86400
            existing = [e for e in existing if e.get("timestamp", 0) >= cutoff]
            existing.extend(new_entries)

            with open(USAGE_STATS_PATH, "w", encoding="utf-8") as f:
                json.dump({"entries": existing[-2000:]}, f, indent=1)
        except Exception as e:
            logger.warning(f"Failed to flush usage stats: {e}")


# Global singleton
usage_tracker = UsageTracker()


class UsageTrackerMiddleware(BaseHTTPMiddleware):
    """Middleware that records API request details for analytics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Skip analytics endpoints to avoid recursion
        if "/analytics/" in request.url.path:
            return await call_next(request)

        start = time.time()
        request_size = int(request.headers.get("content-length", 0) or 0)

        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        response_size = int(response.headers.get("content-length", 0) or 0)

        usage_tracker.record(
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            duration_ms=elapsed_ms,
            request_size=request_size,
            response_size=response_size,
        )
        return response
