"""Feishu summary service (F-25). Generates memory summary and sends to Feishu."""

import time
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.services import agentmemory as am_service
from app.services.notification import load_webhook_config


def generate_summary() -> dict:
    """Generate a summary of all memories."""
    memories = am_service.get_all_memories()
    total = len(memories)

    # Type distribution
    by_type = {}
    for m in memories:
        t = m.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    # Strength stats
    strengths = [m.get("strength", 0) for m in memories]
    avg_strength = round(sum(strengths) / len(strengths), 1) if strengths else 0

    # Latest 5 memories
    sorted_memories = sorted(memories, key=lambda m: m.get("updatedAt", ""), reverse=True)
    latest = []
    for m in sorted_memories[:5]:
        latest.append({
            "title": m.get("title", ""),
            "type": m.get("type", ""),
            "strength": m.get("strength", 0),
            "updatedAt": m.get("updatedAt", ""),
        })

    # Concept frequency
    concept_count = {}
    for m in memories:
        for c in m.get("concepts", []):
            concept_count[c] = concept_count.get(c, 0) + 1
    top_concepts = sorted(concept_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_memories": total,
        "by_type": by_type,
        "avg_strength": avg_strength,
        "latest": latest,
        "top_concepts": [{"concept": c, "count": n} for c, n in top_concepts],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def build_feishu_card(summary: dict) -> dict:
    """Build a Feishu interactive card from the summary."""
    lines = [
        f"**总记忆数**: {summary['total_memories']}",
        f"**平均强度**: {summary['avg_strength'] * 10}%",
        "",
        "**类型分布**:",
    ]
    for type_, count in summary.get("by_type", {}).items():
        lines.append(f"  • {type_}: {count}")

    if summary.get("top_concepts"):
        lines.append("")
        lines.append("**热门概念**:")
        for tc in summary["top_concepts"][:5]:
            lines.append(f"  • {tc['concept']} ({tc['count']})")

    if summary.get("latest"):
        lines.append("")
        lines.append("**最新记忆**:")
        for item in summary["latest"]:
            lines.append(f"  • {item['title']} ({item['type']}, {item['strength'] * 10}%)")

    content = "\n".join(lines)

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📊 Memory Viewer — 记忆系统摘要"},
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content},
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"Memory Viewer v2.1.0 · {time.strftime('%Y-%m-%d %H:%M:%S')}",
                        }
                    ],
                },
            ],
        },
    }


def send_summary_to_feishu() -> dict:
    """Generate summary and send to configured Feishu webhook."""
    config = load_webhook_config()
    webhook_url = config.get("webhook_url", "")

    if not webhook_url:
        return {"success": False, "error": "Webhook URL not configured"}

    summary = generate_summary()
    card = build_feishu_card(summary)

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(webhook_url, json=card)
            if resp.status_code == 200:
                return {"success": True, "summary": summary}
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
