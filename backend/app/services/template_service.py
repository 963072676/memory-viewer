"""Memory Templates service (F-52) — Create memories from predefined templates.

Template schema with fields (text/select/tags/number/date).
5 built-in templates + custom template CRUD.
Storage: backend/cache/templates.json
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import create_memory, _atomic_write_json

logger = logging.getLogger(__name__)

TEMPLATES_PATH = os.path.join(settings.cache_dir, "templates.json")

# Built-in templates
BUILTIN_TEMPLATES = [
    {
        "id": "tpl-user-preference",
        "name": "User Preference",
        "icon": "⚙️",
        "description": "Record a user preference or setting",
        "builtin": True,
        "fields": [
            {"name": "preference_key", "type": "text", "label": "Preference Key", "required": True},
            {"name": "preference_value", "type": "text", "label": "Value", "required": True},
            {"name": "category", "type": "select", "label": "Category", "options": ["UI", "Language", "Workflow", "Notification", "Other"], "required": False},
            {"name": "priority", "type": "number", "label": "Priority (1-5)", "min": 1, "max": 5, "required": False},
        ],
        "title_template": "Preference: {preference_key}",
        "content_template": "User prefers {preference_key} = {preference_value}. Category: {category}. Priority: {priority}.",
        "default_type": "preference",
        "default_tags": ["preference", "user-setting"],
    },
    {
        "id": "tpl-conversation-summary",
        "name": "Conversation Summary",
        "icon": "💬",
        "description": "Summarize a conversation or meeting",
        "builtin": True,
        "fields": [
            {"name": "participants", "type": "tags", "label": "Participants", "required": True},
            {"name": "topic", "type": "text", "label": "Topic", "required": True},
            {"name": "key_decisions", "type": "text", "label": "Key Decisions", "required": False},
            {"name": "action_items", "type": "text", "label": "Action Items", "required": False},
            {"name": "date", "type": "date", "label": "Date", "required": False},
        ],
        "title_template": "Conversation: {topic}",
        "content_template": "Participants: {participants}\nTopic: {topic}\nKey Decisions: {key_decisions}\nAction Items: {action_items}",
        "default_type": "fact",
        "default_tags": ["conversation", "summary"],
    },
    {
        "id": "tpl-task-result",
        "name": "Task Result",
        "icon": "✅",
        "description": "Record the result of a completed task",
        "builtin": True,
        "fields": [
            {"name": "task_name", "type": "text", "label": "Task Name", "required": True},
            {"name": "outcome", "type": "select", "label": "Outcome", "options": ["Success", "Partial", "Failed", "Cancelled"], "required": True},
            {"name": "details", "type": "text", "label": "Details", "required": False},
            {"name": "duration", "type": "text", "label": "Duration", "required": False},
        ],
        "title_template": "Task: {task_name} — {outcome}",
        "content_template": "Task: {task_name}\nOutcome: {outcome}\nDetails: {details}\nDuration: {duration}",
        "default_type": "workflow",
        "default_tags": ["task", "result"],
    },
    {
        "id": "tpl-learning-insight",
        "name": "Learning Insight",
        "icon": "💡",
        "description": "Capture a learning or insight",
        "builtin": True,
        "fields": [
            {"name": "insight", "type": "text", "label": "Insight", "required": True},
            {"name": "source", "type": "text", "label": "Source", "required": False},
            {"name": "domain", "type": "select", "label": "Domain", "options": ["Programming", "Design", "Architecture", "DevOps", "Business", "Other"], "required": False},
            {"name": "confidence", "type": "number", "label": "Confidence (1-10)", "min": 1, "max": 10, "required": False},
            {"name": "related_topics", "type": "tags", "label": "Related Topics", "required": False},
        ],
        "title_template": "Insight: {insight}",
        "content_template": "Insight: {insight}\nSource: {source}\nDomain: {domain}\nConfidence: {confidence}/10",
        "default_type": "pattern",
        "default_tags": ["learning", "insight"],
    },
    {
        "id": "tpl-error-failure",
        "name": "Error/Failure",
        "icon": "🐛",
        "description": "Record an error or failure for future reference",
        "builtin": True,
        "fields": [
            {"name": "error_message", "type": "text", "label": "Error Message", "required": True},
            {"name": "context", "type": "text", "label": "Context/Stack Trace", "required": False},
            {"name": "root_cause", "type": "text", "label": "Root Cause", "required": False},
            {"name": "resolution", "type": "text", "label": "Resolution", "required": False},
            {"name": "severity", "type": "select", "label": "Severity", "options": ["Low", "Medium", "High", "Critical"], "required": False},
            {"name": "tags", "type": "tags", "label": "Tags", "required": False},
        ],
        "title_template": "Error: {error_message}",
        "content_template": "Error: {error_message}\nContext: {context}\nRoot Cause: {root_cause}\nResolution: {resolution}\nSeverity: {severity}",
        "default_type": "bug",
        "default_tags": ["error", "debugging"],
    },
]


def _load_templates() -> dict:
    """Load templates from disk."""
    try:
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"custom_templates": []}


def _save_templates(data: dict) -> None:
    """Save templates to disk."""
    os.makedirs(os.path.dirname(TEMPLATES_PATH), exist_ok=True)
    _atomic_write_json(TEMPLATES_PATH, data)


def get_all_templates() -> list[dict]:
    """Get all templates (built-in + custom)."""
    data = _load_templates()
    custom = data.get("custom_templates", [])
    return BUILTIN_TEMPLATES + custom


def get_template(template_id: str) -> Optional[dict]:
    """Get a specific template by ID."""
    for t in BUILTIN_TEMPLATES:
        if t["id"] == template_id:
            return t
    data = _load_templates()
    for t in data.get("custom_templates", []):
        if t["id"] == template_id:
            return t
    return None


def create_template(name: str, description: str, fields: list[dict],
                    title_template: str, content_template: str,
                    default_type: str = "fact", default_tags: list[str] = None,
                    icon: str = "📝") -> dict:
    """Create a custom template."""
    template_id = f"tpl-{hashlib.md5(f'{name}:{time.time()}'.encode()).hexdigest()[:10]}"
    template = {
        "id": template_id,
        "name": name,
        "icon": icon,
        "description": description,
        "builtin": False,
        "fields": fields,
        "title_template": title_template,
        "content_template": content_template,
        "default_type": default_type,
        "default_tags": default_tags or [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    data = _load_templates()
    data.setdefault("custom_templates", []).append(template)
    _save_templates(data)
    return template


def update_template(template_id: str, **kwargs) -> Optional[dict]:
    """Update a custom template."""
    data = _load_templates()
    templates = data.get("custom_templates", [])
    for i, t in enumerate(templates):
        if t["id"] == template_id:
            for key, value in kwargs.items():
                if value is not None and key in ("name", "description", "fields", "title_template", "content_template", "default_type", "default_tags", "icon"):
                    t[key] = value
            t["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            templates[i] = t
            data["custom_templates"] = templates
            _save_templates(data)
            return t
    return None


def delete_template(template_id: str) -> bool:
    """Delete a custom template (cannot delete built-in)."""
    data = _load_templates()
    templates = data.get("custom_templates", [])
    original_len = len(templates)
    data["custom_templates"] = [t for t in templates if t["id"] != template_id]
    if len(data["custom_templates"]) < original_len:
        _save_templates(data)
        return True
    return False


def validate_template_fields(template: dict, values: dict) -> list[str]:
    """Validate field values against template schema. Returns list of errors."""
    errors = []
    for field in template.get("fields", []):
        name = field["name"]
        required = field.get("required", False)
        if required and (name not in values or not values[name]):
            errors.append(f"Field '{field['label']}' is required")
        if name in values and values[name]:
            ftype = field.get("type", "text")
            val = values[name]
            if ftype == "number":
                try:
                    num = float(val)
                    if "min" in field and num < field["min"]:
                        errors.append(f"Field '{field['label']}' must be >= {field['min']}")
                    if "max" in field and num > field["max"]:
                        errors.append(f"Field '{field['label']}' must be <= {field['max']}")
                except (ValueError, TypeError):
                    errors.append(f"Field '{field['label']}' must be a number")
    return errors


def create_memory_from_template(template_id: str, values: dict) -> dict:
    """Create a memory using a template and provided values.

    AC-F52-5: Use Template button creates memory from template.
    """
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    errors = validate_template_fields(template, values)
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")

    # Render title and content from templates
    title = template["title_template"]
    content = template["content_template"]
    for field in template.get("fields", []):
        name = field["name"]
        val = values.get(name, "")
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        title = title.replace(f"{{{name}}}", str(val))
        content = content.replace(f"{{{name}}}", str(val))

    # Collect tags from tags-type fields
    tags = list(template.get("default_tags", []))
    for field in template.get("fields", []):
        if field.get("type") == "tags" and field["name"] in values:
            v = values[field["name"]]
            if isinstance(v, list):
                tags.extend(v)
            elif isinstance(v, str):
                tags.extend([t.strip() for t in v.split(",") if t.strip()])

    memory = create_memory(
        title=title,
        content=content,
        memory_type=template.get("default_type", "fact"),
        tags=tags,
    )
    return memory
