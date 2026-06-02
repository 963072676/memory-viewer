"""Performance metrics middleware (F-32) — ring buffer, no persistence."""

import time
from collections import deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class MetricsCollector:
    """Singleton ring buffer for API metrics (in-memory only)."""

    def __init__(self, max_size: int = 1000):
        self._buffer: deque[dict] = deque(maxlen=max_size)

    def record(self, path: str, method: str, status: int, duration_ms: float):
        self._buffer.append({
            "path": path,
            "method": method,
            "status": status,
            "duration_ms": duration_ms,
            "timestamp": time.time(),
        })

    def get_metrics(self) -> dict:
        """Compute aggregated metrics from the ring buffer."""
        if not self._buffer:
            return {
                "total_requests": 0,
                "avg_duration_ms": 0,
                "p50_ms": 0,
                "p95_ms": 0,
                "p99_ms": 0,
                "endpoints": {},
                "recent": [],
            }

        all_durations = sorted(e["duration_ms"] for e in self._buffer)
        n = len(all_durations)

        def percentile(pct: float) -> float:
            idx = int(n * pct / 100)
            idx = min(idx, n - 1)
            return round(all_durations[idx], 2)

        # Per-endpoint stats
        endpoint_data: dict[str, list[float]] = {}
        for e in self._buffer:
            key = f"{e['method']} {e['path']}"
            endpoint_data.setdefault(key, []).append(e["duration_ms"])

        endpoints = {}
        for key, durations in endpoint_data.items():
            sd = sorted(durations)
            sn = len(sd)
            endpoints[key] = {
                "count": sn,
                "avg_ms": round(sum(sd) / sn, 2),
                "p50_ms": round(sd[sn // 2], 2) if sn > 0 else 0,
                "p95_ms": round(sd[int(sn * 0.95)], 2) if sn > 0 else 0,
            }

        recent = list(self._buffer)[-20:]

        return {
            "total_requests": n,
            "avg_duration_ms": round(sum(all_durations) / n, 2),
            "p50_ms": percentile(50),
            "p95_ms": percentile(95),
            "p99_ms": percentile(99),
            "endpoints": endpoints,
            "recent": recent,
        }


# Global singleton
metrics_collector = MetricsCollector(max_size=1000)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Records request timing to the global MetricsCollector."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        start = time.time()
        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        metrics_collector.record(
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            duration_ms=elapsed_ms,
        )
        return response
