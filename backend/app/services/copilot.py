"""Provider-neutral AI Copilot actions for memory operations."""

from __future__ import annotations

import time
from typing import Any, Literal

from app.core.memory_schema import MemoryItem
from app.services.intelligence import (
    cluster_memories,
    compress_memories,
    detect_contradictions,
    load_unified_memories,
    summarize_memories,
)

CopilotAction = Literal[
    "summarize_session",
    "compress_memory",
    "detect_contradictions",
    "optimize_memory_structure",
]

ACTION_TITLES: dict[str, str] = {
    "summarize_session": "Summarize session",
    "compress_memory": "Compress memory",
    "detect_contradictions": "Detect contradictions",
    "optimize_memory_structure": "Optimize memory structure",
}


def _raw(item: MemoryItem) -> dict[str, Any]:
    return item.metadata.raw if isinstance(item.metadata.raw, dict) else {}


def _recommendations(items: list[MemoryItem]) -> list[dict[str, Any]]:
    clusters = cluster_memories(items)
    contradictions = detect_contradictions(items)
    tagless_count = sum(1 for item in items if not item.metadata.tags)
    providers = sorted({item.metadata.source for item in items})
    sessions = sorted({item.metadata.session_id for item in items if item.metadata.session_id})
    archived_count = sum(1 for item in items if bool(_raw(item).get("archived", False)))

    recommendations: list[dict[str, Any]] = []
    if contradictions["total"]:
        recommendations.append(
            {
                "priority": "high",
                "kind": "contradiction",
                "title": "Review contradiction candidates",
                "detail": f"{contradictions['total']} candidate pairs may need user or agent confirmation.",
            }
        )
    if tagless_count:
        recommendations.append(
            {
                "priority": "medium",
                "kind": "tagging",
                "title": "Add missing topic tags",
                "detail": f"{tagless_count} memories have no normalized tags, which weakens filtering and clustering.",
            }
        )
    if clusters["total"] > max(3, len(items) // 3):
        recommendations.append(
            {
                "priority": "medium",
                "kind": "clustering",
                "title": "Merge tiny topic clusters",
                "detail": f"{clusters['total']} clusters for {len(items)} memories suggests fragmented structure.",
            }
        )
    if len(providers) > 1 and not sessions:
        recommendations.append(
            {
                "priority": "low",
                "kind": "session",
                "title": "Introduce session anchors",
                "detail": "Cross-provider memories are present but no session ids were found in this slice.",
            }
        )
    if archived_count:
        recommendations.append(
            {
                "priority": "low",
                "kind": "archive",
                "title": "Keep archived memories out of active workflows",
                "detail": f"{archived_count} archived memories appeared in the current slice.",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "priority": "low",
                "kind": "structure",
                "title": "Structure looks stable",
                "detail": "No immediate tagging, clustering, or contradiction cleanup was detected.",
            }
        )
    return recommendations


def run_copilot_action_from_items(
    action: CopilotAction,
    items: list[MemoryItem],
    *,
    provider: str = "",
    session_id: str = "",
    max_chars: int = 800,
) -> dict[str, Any]:
    """Run a deterministic copilot action over unified memory items."""
    summary = summarize_memories(items)
    title = ACTION_TITLES[action]
    base: dict[str, Any] = {
        "action": action,
        "title": title,
        "provider": provider,
        "sessionId": session_id,
        "memoryCount": len(items),
        "providers": summary["providers"],
        "sessionIds": summary["sessionIds"],
        "generatedAt": int(time.time() * 1000),
    }

    if not items:
        return {
            **base,
            "status": "empty",
            "message": "No memories matched this copilot action.",
            "result": summary,
            "recommendations": [],
        }

    if action == "summarize_session":
        return {
            **base,
            "status": "ready",
            "message": summary["summary"],
            "result": summary,
            "recommendations": _recommendations(items)[:3],
        }

    if action == "compress_memory":
        compression = compress_memories(items, max_chars=max_chars)
        return {
            **base,
            "status": "ready",
            "message": compression["compressed"] or "No compressible memory content found.",
            "result": compression,
            "recommendations": _recommendations(items)[:3],
        }

    if action == "detect_contradictions":
        contradictions = detect_contradictions(items)
        message = (
            f"{contradictions['total']} contradiction candidates detected."
            if contradictions["total"]
            else "No contradiction candidates detected."
        )
        return {
            **base,
            "status": "attention" if contradictions["total"] else "ready",
            "message": message,
            "result": contradictions,
            "recommendations": _recommendations(items)[:3],
        }

    optimization = {
        "summary": summary,
        "clusters": cluster_memories(items),
        "recommendations": _recommendations(items),
    }
    return {
        **base,
        "status": "attention" if any(r["priority"] == "high" for r in optimization["recommendations"]) else "ready",
        "message": "Memory structure analysis is ready.",
        "result": optimization,
        "recommendations": optimization["recommendations"],
    }


async def run_copilot_action(
    action: CopilotAction,
    *,
    provider: str = "",
    session_id: str = "",
    limit: int = 200,
    max_chars: int = 800,
) -> dict[str, Any]:
    """Load unified memories and run one copilot action."""
    items = await load_unified_memories(provider=provider, session_id=session_id, limit=limit)
    return run_copilot_action_from_items(
        action,
        items,
        provider=provider,
        session_id=session_id,
        max_chars=max_chars,
    )
