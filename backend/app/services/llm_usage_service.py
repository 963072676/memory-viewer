"""LLM Usage & Cost Dashboard service (F-61).

Track token usage per feature/endpoint.
Cost calculation with configurable rates.
Storage: llm_usage.jsonl (append-only) + llm_usage_rollups.json.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

USAGE_LOG_PATH = os.path.join(settings.cache_dir, "llm_usage.jsonl")
ROLLUPS_PATH = os.path.join(settings.cache_dir, "llm_usage_rollups.json")
USAGE_CONFIG_PATH = os.path.join(settings.cache_dir, "llm_usage_config.json")

DEFAULT_PRICING = {
    "gpt-4o": {"input_per_mtok": 2.50, "output_per_mtok": 10.00},
    "gpt-4o-mini": {"input_per_mtok": 0.15, "output_per_mtok": 0.60},
    "claude-3-haiku": {"input_per_mtok": 0.25, "output_per_mtok": 1.25},
    "claude-3-sonnet": {"input_per_mtok": 3.00, "output_per_mtok": 15.00},
    "llama3": {"input_per_mtok": 0.0, "output_per_mtok": 0.0},
    "ollama": {"input_per_mtok": 0.0, "output_per_mtok": 0.0},
}

DEFAULT_CONFIG = {
    "pricing": DEFAULT_PRICING,
    "alerts": {
        "daily_limit_usd": 10.0,
        "weekly_limit_usd": 50.0,
        "monthly_limit_usd": 200.0,
        "enabled": True,
    },
}


def _load_config() -> dict:
    try:
        with open(USAGE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)


def _save_config(config: dict) -> None:
    os.makedirs(os.path.dirname(USAGE_CONFIG_PATH), exist_ok=True)
    _atomic_write_json(USAGE_CONFIG_PATH, config)


def _append_usage(record: dict) -> None:
    os.makedirs(os.path.dirname(USAGE_LOG_PATH), exist_ok=True)
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _load_usage_log(limit: int = 10000) -> list[dict]:
    """Load usage log (most recent entries)."""
    records = []
    try:
        with open(USAGE_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except FileNotFoundError:
        pass
    return records[-limit:]


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on model pricing."""
    config = _load_config()
    pricing = config.get("pricing", DEFAULT_PRICING)

    # Find pricing for model
    model_pricing = pricing.get(model, pricing.get("ollama", {"input_per_mtok": 0, "output_per_mtok": 0}))

    input_cost = (input_tokens / 1_000_000) * model_pricing.get("input_per_mtok", 0)
    output_cost = (output_tokens / 1_000_000) * model_pricing.get("output_per_mtok", 0)

    return round(input_cost + output_cost, 6)


# ─── Usage Tracking ──────────────────────────────────────────────────────────

def record_usage(
    feature: str,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int = 0,
    memory_id: str = "",
    user_id: str = "",
) -> dict:
    """Record an LLM usage event."""
    import hashlib

    total_tokens = input_tokens + output_tokens
    cost_usd = _calculate_cost(model, input_tokens, output_tokens)

    record = {
        "id": f"usage_{hashlib.md5(f'{feature}:{time.time()}'.encode()).hexdigest()[:10]}",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "feature": feature,
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "memory_id": memory_id,
        "user_id": user_id,
    }

    _append_usage(record)
    return record


# ─── Query Endpoints ─────────────────────────────────────────────────────────

def get_summary(days: int = 30) -> dict:
    """Get usage summary for the specified time period."""
    records = _load_usage_log()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat().replace("+00:00", "Z")

    filtered = [r for r in records if r.get("timestamp", "") >= cutoff_str]

    total_input = sum(r.get("input_tokens", 0) for r in filtered)
    total_output = sum(r.get("output_tokens", 0) for r in filtered)
    total_tokens = sum(r.get("total_tokens", 0) for r in filtered)
    total_cost = sum(r.get("cost_usd", 0) for r in filtered)
    avg_latency = sum(r.get("latency_ms", 0) for r in filtered) / max(len(filtered), 1)

    # Breakdown by feature
    by_feature = {}
    for r in filtered:
        feat = r.get("feature", "unknown")
        if feat not in by_feature:
            by_feature[feat] = {"calls": 0, "tokens": 0, "cost_usd": 0}
        by_feature[feat]["calls"] += 1
        by_feature[feat]["tokens"] += r.get("total_tokens", 0)
        by_feature[feat]["cost_usd"] += r.get("cost_usd", 0)

    # Breakdown by model
    by_model = {}
    for r in filtered:
        model = r.get("model", "unknown")
        if model not in by_model:
            by_model[model] = {"calls": 0, "tokens": 0, "cost_usd": 0}
        by_model[model]["calls"] += 1
        by_model[model]["tokens"] += r.get("total_tokens", 0)
        by_model[model]["cost_usd"] += r.get("cost_usd", 0)

    # Breakdown by provider
    by_provider = {}
    for r in filtered:
        prov = r.get("provider", "unknown")
        if prov not in by_provider:
            by_provider[prov] = {"calls": 0, "tokens": 0, "cost_usd": 0}
        by_provider[prov]["calls"] += 1
        by_provider[prov]["tokens"] += r.get("total_tokens", 0)
        by_provider[prov]["cost_usd"] += r.get("cost_usd", 0)

    # Top feature
    top_feature = max(by_feature.items(), key=lambda x: x[1]["cost_usd"])[0] if by_feature else "none"

    return {
        "period_days": days,
        "total_calls": len(filtered),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "avg_latency_ms": round(avg_latency),
        "top_feature": top_feature,
        "by_feature": by_feature,
        "by_model": by_model,
        "by_provider": by_provider,
    }


def get_timeline(days: int = 30) -> dict:
    """Get daily cost timeline for charting."""
    records = _load_usage_log()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat().replace("+00:00", "Z")

    filtered = [r for r in records if r.get("timestamp", "") >= cutoff_str]

    # Group by date
    daily = {}
    for r in filtered:
        date = r.get("timestamp", "")[:10]
        if date not in daily:
            daily[date] = {"cost_usd": 0, "tokens": 0, "calls": 0}
        daily[date]["cost_usd"] += r.get("cost_usd", 0)
        daily[date]["tokens"] += r.get("total_tokens", 0)
        daily[date]["calls"] += 1

    # Also group by date + feature for stacked chart
    daily_by_feature = {}
    for r in filtered:
        date = r.get("timestamp", "")[:10]
        feat = r.get("feature", "unknown")
        key = f"{date}|{feat}"
        if key not in daily_by_feature:
            daily_by_feature[key] = {"date": date, "feature": feat, "cost_usd": 0, "tokens": 0}
        daily_by_feature[key]["cost_usd"] += r.get("cost_usd", 0)
        daily_by_feature[key]["tokens"] += r.get("total_tokens", 0)

    # Format timeline
    timeline = []
    for date in sorted(daily.keys()):
        entry = daily[date]
        entry["date"] = date
        entry["cost_usd"] = round(entry["cost_usd"], 4)
        timeline.append(entry)

    # Format feature timeline
    feature_timeline = sorted(daily_by_feature.values(), key=lambda x: x["date"])
    for item in feature_timeline:
        item["cost_usd"] = round(item["cost_usd"], 4)

    return {
        "period_days": days,
        "timeline": timeline,
        "feature_timeline": feature_timeline,
    }


def get_recent(page: int = 1, per_page: int = 50) -> dict:
    """Get recent usage records (paginated)."""
    records = _load_usage_log(limit=10000)
    records.reverse()  # Most recent first

    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "records": records[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


def get_config() -> dict:
    """Get pricing and alert configuration."""
    return _load_config()


def update_config(updates: dict) -> dict:
    """Update pricing and alert configuration."""
    config = _load_config()
    if "pricing" in updates:
        config["pricing"].update(updates["pricing"])
    if "alerts" in updates:
        config["alerts"].update(updates["alerts"])
    _save_config(config)
    return config
