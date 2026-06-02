"""Anomaly Detection & Alerts service (F-43) — Proactive monitoring.

Monitors memory count changes, strength distribution, API latency, and error rates.
Uses Z-score detection for statistical anomalies.
"""

import json
import logging
import math
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

_ANOMALIES_PATH = os.path.join(settings.cache_dir, "anomalies.json")
_HISTORY_PATH = os.path.join(settings.cache_dir, "metrics_history.json")


@dataclass
class Anomaly:
    """A detected anomaly event."""
    id: str
    anomaly_type: str        # "count_change", "strength_shift", "api_latency", "error_rate", "type_distribution"
    severity: str            # "info", "warning", "critical"
    title: str
    description: str
    detected_at: str         # ISO timestamp
    metric_value: float
    threshold: float
    suggested_action: str
    resolved: bool = False


@dataclass
class HealthScore:
    """System health score breakdown."""
    overall: int             # 0-100
    memory_stability: int    # 0-100
    strength_health: int     # 0-100
    api_performance: int     # 0-100
    error_rate: int          # 0-100
    status: str              # "healthy", "warning", "critical"


# In-memory history for Z-score calculations
_metrics_history: dict[str, deque] = {
    "memory_count": deque(maxlen=168),   # 7 days of hourly snapshots
    "avg_strength": deque(maxlen=168),
    "api_p95": deque(maxlen=168),
    "error_rate": deque(maxlen=168),
}

# Anomaly storage
_anomalies: list[dict] = []

# Thresholds (configurable)
_thresholds = {
    "count_change_pct": 20.0,       # >20% daily change
    "strength_change_pct": 15.0,    # >15% weekly change
    "api_p95_ms": 500.0,            # >500ms P95 latency
    "error_rate_pct": 5.0,          # >5% error rate
    "type_shift_pct": 30.0,         # >30% shift in type distribution
    "z_score_threshold": 2.0,       # Z-score > 2
}


def _load_anomalies() -> list[dict]:
    """Load anomalies from persistent storage."""
    try:
        with open(_ANOMALIES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_anomalies(anomalies: list[dict]) -> None:
    """Save anomalies to persistent storage."""
    os.makedirs(os.path.dirname(_ANOMALIES_PATH), exist_ok=True)
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(_ANOMALIES_PATH), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(anomalies, f, indent=2, ensure_ascii=False)
        os.replace(tmp, _ANOMALIES_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _load_history() -> dict[str, list]:
    """Load metrics history."""
    try:
        with open(_HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_history(history: dict[str, list]) -> None:
    """Save metrics history."""
    os.makedirs(os.path.dirname(_HISTORY_PATH), exist_ok=True)
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(_HISTORY_PATH), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        os.replace(tmp, _HISTORY_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _z_score(values: list[float], current: float) -> float:
    """Calculate Z-score of current value against historical values."""
    if len(values) < 3:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance) if variance > 0 else 0
    if std == 0:
        return 0.0
    return (current - mean) / std


def _record_metric(name: str, value: float, timestamp: float = None) -> None:
    """Record a metric data point."""
    ts = timestamp or time.time()
    history = _load_history()
    if name not in history:
        history[name] = []
    history[name].append({"value": value, "timestamp": ts})
    # Keep last 168 entries (7 days hourly)
    history[name] = history[name][-168:]
    _save_history(history)


def _create_anomaly(
    anomaly_type: str,
    severity: str,
    title: str,
    description: str,
    metric_value: float,
    threshold: float,
    suggested_action: str,
) -> dict:
    """Create and store an anomaly event."""
    import uuid
    anomaly = {
        "id": str(uuid.uuid4())[:8],
        "anomaly_type": anomaly_type,
        "severity": severity,
        "title": title,
        "description": description,
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "metric_value": round(metric_value, 2),
        "threshold": round(threshold, 2),
        "suggested_action": suggested_action,
        "resolved": False,
    }

    anomalies = _load_anomalies()
    anomalies.append(anomaly)
    # Keep last 500 anomalies
    anomalies = anomalies[-500:]
    _save_anomalies(anomalies)

    logger.warning(f"Anomaly detected: [{severity}] {title}")
    return anomaly


def run_detection() -> list[dict]:
    """Run anomaly detection cycle.
    
    Checks all monitored metrics and creates anomaly events.
    Returns list of newly detected anomalies.
    
    AC-F43-1: Memory count sudden change triggers anomaly.
    AC-F43-4: Alert thresholds are configurable.
    """
    from app.services.agentmemory import get_all_memories
    from app.middleware.metrics import metrics_collector

    memories = get_all_memories()
    current_count = len(memories)
    new_anomalies: list[dict] = []

    # Record current metrics
    _record_metric("memory_count", current_count)

    # 1. Memory count change
    history = _load_history()
    count_history = [e["value"] for e in history.get("memory_count", [])]
    if count_history:
        prev_count = count_history[-1] if count_history else current_count
        if prev_count > 0:
            change_pct = abs(current_count - prev_count) / prev_count * 100
            if change_pct > _thresholds["count_change_pct"]:
                direction = "增加" if current_count > prev_count else "减少"
                anomaly = _create_anomaly(
                    anomaly_type="count_change",
                    severity="warning" if change_pct < 50 else "critical",
                    title=f"记忆数量异常{direction}",
                    description=f"记忆数量从 {prev_count} 变为 {current_count}，变化 {change_pct:.1f}%",
                    metric_value=change_pct,
                    threshold=_thresholds["count_change_pct"],
                    suggested_action="检查是否有批量删除或导入操作",
                )
                new_anomalies.append(anomaly)

    # Record average strength
    if memories:
        avg_strength = sum(m.get("strength", 5) for m in memories) / len(memories)
        _record_metric("avg_strength", avg_strength)

        # 2. Strength shift
        strength_history = [e["value"] for e in history.get("avg_strength", [])]
        if strength_history:
            z = _z_score(strength_history, avg_strength)
            if abs(z) > _thresholds["z_score_threshold"]:
                anomaly = _create_anomaly(
                    anomaly_type="strength_shift",
                    severity="warning",
                    title="平均强度异常偏移",
                    description=f"当前平均强度 {avg_strength:.1f}，Z-score {z:.2f}",
                    metric_value=avg_strength,
                    threshold=_thresholds["z_score_threshold"],
                    suggested_action="检查是否有大量低强度或高强度记忆被创建",
                )
                new_anomalies.append(anomaly)

    # 3. API latency
    metrics = metrics_collector.get_metrics()
    p95 = metrics.get("p95_ms", 0)
    _record_metric("api_p95", p95)

    if p95 > _thresholds["api_p95_ms"]:
        anomaly = _create_anomaly(
            anomaly_type="api_latency",
            severity="warning" if p95 < 1000 else "critical",
            title="API 响应延迟异常",
            description=f"P95 延迟 {p95:.0f}ms 超过阈值 {_thresholds['api_p95_ms']}ms",
            metric_value=p95,
            threshold=_thresholds["api_p95_ms"],
            suggested_action="检查系统负载和数据库性能",
        )
        new_anomalies.append(anomaly)

    # 4. Error rate
    total = metrics.get("total_requests", 0)
    if total > 10:  # Need minimum sample
        recent = metrics.get("recent", [])
        errors = sum(1 for r in recent if r.get("status", 200) >= 500)
        error_rate = (errors / len(recent) * 100) if recent else 0
        _record_metric("error_rate", error_rate)

        if error_rate > _thresholds["error_rate_pct"]:
            anomaly = _create_anomaly(
                anomaly_type="error_rate",
                severity="critical",
                title="错误率异常",
                description=f"错误率 {error_rate:.1f}% 超过阈值 {_thresholds['error_rate_pct']}%",
                metric_value=error_rate,
                threshold=_thresholds["error_rate_pct"],
                suggested_action="检查后端日志排查错误原因",
            )
            new_anomalies.append(anomaly)

    # 5. Type distribution shift
    if memories:
        type_dist: dict[str, int] = {}
        for m in memories:
            t = m.get("type", "unknown")
            type_dist[t] = type_dist.get(t, 0) + 1

        type_history = history.get("type_distribution", [])
        if type_history:
            prev_dist = type_history[-1].get("value", {})
            if isinstance(prev_dist, dict) and prev_dist:
                for t, count in type_dist.items():
                    prev_count = prev_dist.get(t, 0)
                    if prev_count > 0:
                        shift = abs(count - prev_count) / prev_count * 100
                        if shift > _thresholds["type_shift_pct"]:
                            anomaly = _create_anomaly(
                                anomaly_type="type_distribution",
                                severity="info",
                                title=f"类型 '{t}' 分布变化",
                                description=f"类型 '{t}' 数量从 {prev_count} 变为 {count}，变化 {shift:.1f}%",
                                metric_value=shift,
                                threshold=_thresholds["type_shift_pct"],
                                suggested_action="可能是正常使用模式变化",
                            )
                            new_anomalies.append(anomaly)

        _record_metric("type_distribution", type_dist)

    return new_anomalies


def get_anomalies(
    limit: int = 50,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    resolved: Optional[bool] = None,
) -> list[dict]:
    """Get anomaly history with optional filters.
    
    AC-F43-5: Anomaly history is traceable (30-day retention).
    """
    anomalies = _load_anomalies()

    # Apply filters
    if severity:
        anomalies = [a for a in anomalies if a.get("severity") == severity]
    if anomaly_type:
        anomalies = [a for a in anomalies if a.get("anomaly_type") == anomaly_type]
    if resolved is not None:
        anomalies = [a for a in anomalies if a.get("resolved") == resolved]

    # Filter to 30 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    anomalies = [a for a in anomalies if a.get("detected_at", "") >= cutoff]

    # Sort by detected_at descending
    anomalies.sort(key=lambda a: a.get("detected_at", ""), reverse=True)

    return anomalies[:limit]


def get_health_score() -> dict:
    """Compute overall system health score (0-100).
    
    AC-F43-2: Health score correctly reflects system state.
    AC-F43-6: Dashboard displays current health score.
    """
    from app.services.agentmemory import get_all_memories
    from app.middleware.metrics import metrics_collector

    history = _load_history()

    # Memory stability (based on count variance)
    count_history = [e["value"] for e in history.get("memory_count", [])]
    if len(count_history) >= 2:
        mean_count = sum(count_history) / len(count_history)
        variance = sum((v - mean_count) ** 2 for v in count_history) / len(count_history)
        cv = math.sqrt(variance) / mean_count if mean_count > 0 else 0
        memory_stability = max(0, min(100, int(100 - cv * 100)))
    else:
        memory_stability = 80  # Default

    # Strength health
    memories = get_all_memories()
    if memories:
        avg_strength = sum(m.get("strength", 5) for m in memories) / len(memories)
        strength_health = min(100, int(avg_strength * 12))  # 8+ = 100
    else:
        strength_health = 50

    # API performance
    metrics = metrics_collector.get_metrics()
    p95 = metrics.get("p95_ms", 0)
    if p95 <= 100:
        api_performance = 100
    elif p95 <= 300:
        api_performance = 80
    elif p95 <= 500:
        api_performance = 60
    else:
        api_performance = max(0, 100 - int(p95 / 10))

    # Error rate
    total = metrics.get("total_requests", 0)
    recent = metrics.get("recent", [])
    if recent:
        errors = sum(1 for r in recent if r.get("status", 200) >= 500)
        error_pct = errors / len(recent) * 100
        error_rate = max(0, 100 - int(error_pct * 10))
    else:
        error_rate = 100  # No requests = no errors

    # Overall health (weighted average)
    overall = int(
        memory_stability * 0.25 +
        strength_health * 0.25 +
        api_performance * 0.25 +
        error_rate * 0.25
    )

    # Determine status
    if overall >= 80:
        status = "healthy"
    elif overall >= 50:
        status = "warning"
    else:
        status = "critical"

    return {
        "overall": overall,
        "memory_stability": memory_stability,
        "strength_health": strength_health,
        "api_performance": api_performance,
        "error_rate": error_rate,
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def get_thresholds() -> dict:
    """Get current anomaly detection thresholds."""
    return dict(_thresholds)


def update_threshold(key: str, value: float) -> bool:
    """Update an anomaly detection threshold."""
    if key in _thresholds:
        _thresholds[key] = value
        return True
    return False
