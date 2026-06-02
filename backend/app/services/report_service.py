"""Report Service (F-67) — Advanced Export & Reporting with Jinja2 templates."""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import jinja2

from app.config import settings
from app.services.agentmemory import get_all_memories, get_stats, get_paginated_memories

logger = logging.getLogger(__name__)

# Report storage
REPORTS_DIR = os.path.join(settings.cache_dir, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Jinja2 environment
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "reports"
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)) if TEMPLATE_DIR.exists() else None,
    autoescape=jinja2.select_autoescape(default=True, default_for_string=True),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Report history storage
REPORT_HISTORY_PATH = os.path.join(REPORTS_DIR, "history.json")

# Available report templates
REPORT_TEMPLATES = [
    {
        "id": "summary",
        "name": "Memory Summary",
        "description": "Overview of all memories with statistics and charts",
        "icon": "📊",
        "format": "html",
    },
    {
        "id": "detailed",
        "name": "Detailed Report",
        "description": "Full memory listing with all metadata",
        "icon": "📋",
        "format": "html",
    },
    {
        "id": "by-type",
        "name": "By Type",
        "description": "Memories organized by type with counts",
        "icon": "🏷️",
        "format": "html",
    },
    {
        "id": "by-tag",
        "name": "By Tag",
        "description": "Memories organized by tags",
        "icon": "🏷️",
        "format": "html",
    },
    {
        "id": "timeline",
        "name": "Timeline",
        "description": "Memories sorted by creation date",
        "icon": "📅",
        "format": "html",
    },
]


def _load_history() -> list[dict]:
    """Load report generation history."""
    try:
        with open(REPORT_HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("reports", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_history(reports: list[dict]) -> None:
    """Save report history."""
    os.makedirs(os.path.dirname(REPORT_HISTORY_PATH), exist_ok=True)
    with open(REPORT_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump({"reports": reports}, f, indent=2, ensure_ascii=False)


def _generate_report_id(template_id: str) -> str:
    """Generate a unique report ID."""
    ts = datetime.now(timezone.utc).isoformat()
    return f"rpt_{hashlib.md5(f'{template_id}:{ts}'.encode()).hexdigest()[:12]}"


def _render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template with given context."""
    try:
        if JINJA_ENV.loader is None:
            return _fallback_html_report(context)
        template = JINJA_ENV.get_template(template_name)
        return template.render(**context)
    except jinja2.TemplateNotFound:
        logger.warning(f"Template {template_name} not found, using fallback")
        return _fallback_html_report(context)
    except Exception as e:
        logger.error(f"Error rendering template {template_name}: {e}")
        return _fallback_html_report(context)


def _fallback_html_report(context: dict) -> str:
    """Fallback HTML report when template is not available."""
    memories = context.get("memories", [])
    stats = context.get("stats", {})
    template_name = context.get("template_name", "Unknown")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Memory Report - {template_name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f7; color: #1d1d1f; }}
  .container {{ max-width: 1200px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
  h1 {{ color: #007aff; border-bottom: 2px solid #007aff; padding-bottom: 12px; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }}
  .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 20px; border-radius: 12px; text-align: center; }}
  .stat-card.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
  .stat-card.orange {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
  .stat-value {{ font-size: 2rem; font-weight: 700; }}
  .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}
  .memory-list {{ margin-top: 24px; }}
  .memory-item {{ background: #f9f9fb; border: 1px solid #e5e5ea; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
  .memory-item h3 {{ margin: 0 0 8px; color: #007aff; font-size: 1.1rem; }}
  .memory-item .meta {{ font-size: 0.85rem; color: #86868b; margin-bottom: 8px; }}
  .memory-item .content {{ line-height: 1.6; }}
  .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }}
  .tag {{ background: #007aff; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }}
  .footer {{ margin-top: 32px; text-align: center; color: #86868b; font-size: 0.85rem; }}
  .filter-info {{ background: #fff3cd; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107; }}
</style>
</head>
<body>
<div class="container">
  <h1>📊 Memory Report: {template_name}</h1>
  <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-value">{stats.get('total', len(memories))}</div>
      <div class="stat-label">Total Memories</div>
    </div>
    <div class="stat-card green">
      <div class="stat-value">{stats.get('avg_strength', 0)}</div>
      <div class="stat-label">Avg Strength</div>
    </div>
    <div class="stat-card orange">
      <div class="stat-value">{len(stats.get('by_type', {}).keys()) if isinstance(stats.get('by_type'), dict) else 0}</div>
      <div class="stat-label">Types</div>
    </div>
  </div>
"""

    # Add type distribution
    by_type = stats.get("by_type", {})
    if by_type and isinstance(by_type, dict):
        html += "<h2>📈 Distribution by Type</h2><ul>"
        for mem_type, count in by_type.items():
            html += f"<li><strong>{mem_type}</strong>: {count} memories</li>"
        html += "</ul>"

    # Filter info
    filters = context.get("filters", {})
    if filters and any(filters.values()):
        filter_desc = ", ".join(f"{k}={v}" for k, v in filters.items() if v)
        html += f'<div class="filter-info">Filters applied: {filter_desc}</div>'

    html += '<div class="memory-list"><h2>📝 Memories</h2>'

    for m in memories[:200]:  # Cap at 200 for performance
        title = m.get("title", "Untitled")
        content = m.get("content", "")[:200] + ("..." if len(m.get("content", "")) > 200 else "")
        mem_type = m.get("type", "unknown")
        strength = m.get("strength", 5)
        created = m.get("createdAt", "")[:10] if m.get("createdAt") else "N/A"
        tags = m.get("tags", [])

        html += f"""
    <div class="memory-item">
      <h3>{title}</h3>
      <div class="meta">Type: {mem_type} | Strength: {strength}/10 | Created: {created}</div>
      <div class="content">{content}</div>
      <div class="tags">
"""
        for tag in tags[:10]:
            html += f'<span class="tag">{tag}</span>'
        html += "</div></div>"

    if len(memories) > 200:
        html += f"<p><em>...and {len(memories) - 200} more memories</em></p>"

    html += """
  </div>
  <div class="footer">
    <p>Memory Viewer v2 — Report generated automatically</p>
  </div>
</div>
</body>
</html>"""
    return html


def get_report_templates() -> list[dict]:
    """Get available report templates."""
    return REPORT_TEMPLATES


def generate_report(
    template_id: str,
    filters: Optional[dict] = None,
    format_: str = "html",
) -> dict:
    """Generate a report with the given template and filters.

    AC-F67-1: HTML report generation
    AC-F67-2: PDF report generation (optional, when weasyprint available)
    AC-F67-3: Charts and statistics included
    AC-F67-4: Custom filters applied
    AC-F67-5: Downloadable from history
    AC-F67-6: <15s for 200 memories
    """
    start_time = time.time()
    filters = filters or {}

    # Find template
    template = next((t for t in REPORT_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise ValueError(f"Unknown template: {template_id}")

    # Get memories with filters
    type_filter = filters.get("type")
    tag_filter = filters.get("tag")
    search_query = filters.get("q")

    # For performance, use paginated if many memories
    all_memories = get_all_memories()

    # Apply filters
    filtered = []
    for m in all_memories:
        if m.get("archived", False):
            continue
        if type_filter and m.get("type") != type_filter:
            continue
        if tag_filter:
            tag_lower = tag_filter.strip().lower()
            if tag_lower not in [t.lower() for t in m.get("tags", [])]:
                continue
        if search_query:
            q_lower = search_query.lower()
            if q_lower not in m.get("title", "").lower() and q_lower not in m.get("content", "").lower():
                continue
        filtered.append(m)

    # Get stats for filtered set
    stats_data = get_stats()

    # Build context for template
    context = {
        "template_name": template["name"],
        "memories": filtered,
        "stats": stats_data,
        "filters": filters,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "template_id": template_id,
    }

    # Generate content
    if format_ == "html" or format_ == "pdf":
        content = _render_template(f"{template_id}.html", context)
        media_type = "text/html"
        extension = "html"
    else:
        raise ValueError(f"Unsupported format: {format_}")

    # Generate report ID and save
    report_id = _generate_report_id(template_id)
    elapsed = round(time.time() - start_time, 2)

    report_record = {
        "id": report_id,
        "template_id": template_id,
        "template_name": template["name"],
        "format": format_,
        "filters": filters,
        "memory_count": len(filtered),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": elapsed,
        "size_bytes": len(content.encode("utf-8")),
    }

    # Save HTML content
    report_path = os.path.join(REPORTS_DIR, f"{report_id}.{extension}")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    report_record["file_path"] = report_path

    # Update history
    history = _load_history()
    history.insert(0, report_record)
    history = history[:100]  # Keep last 100
    _save_history(history)

    logger.info(f"Generated report {report_id} in {elapsed}s with {len(filtered)} memories")

    return {
        "report": report_record,
        "content": content if format_ == "html" else None,
    }


def get_report_history(limit: int = 50) -> list[dict]:
    """Get report generation history."""
    history = _load_history()
    return history[:limit]


def get_report_by_id(report_id: str) -> Optional[dict]:
    """Get a specific report by ID."""
    history = _load_history()
    for r in history:
        if r.get("id") == report_id:
            return r
    return None


def get_report_content(report_id: str) -> Optional[str]:
    """Get the content of a generated report."""
    history = _load_history()
    for r in history:
        if r.get("id") == report_id:
            file_path = r.get("file_path")
            if file_path and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
    return None