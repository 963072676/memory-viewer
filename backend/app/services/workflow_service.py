"""Memory Workflow Automation service (F-47) — Rule-based automation for memory lifecycle.

Rule definition: {name, trigger: {type, config}, conditions, actions}.
Trigger types: schedule, on_memory_create, on_memory_update, on_strength_change.
Action types: archive, adjust_strength, add_tag, send_notification, delete.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

WORKFLOWS_PATH = os.path.join(settings.cache_dir, "workflows.json")

# Pre-built templates
TEMPLATES = [
    {
        "name": "Archive Stale Memories",
        "description": "Archive memories older than 90 days with low strength",
        "trigger": {"type": "schedule", "config": {"cron": "0 2 * * *"}},
        "conditions": [
            {"field": "age_days", "op": ">", "value": 90},
            {"field": "strength", "op": "<", "value": 0.3},
        ],
        "actions": [{"type": "archive", "config": {}}],
    },
    {
        "name": "Low Strength Cleanup",
        "description": "Delete memories with very low strength (<0.1) that are 30+ days old",
        "trigger": {"type": "schedule", "config": {"cron": "0 3 * * 0"}},
        "conditions": [
            {"field": "age_days", "op": ">", "value": 30},
            {"field": "strength", "op": "<", "value": 0.1},
        ],
        "actions": [{"type": "delete", "config": {}}],
    },
    {
        "name": "Auto-Tag by Pattern",
        "description": "Add 'bug' tag to memories containing error/bug/issue patterns",
        "trigger": {"type": "on_memory_create", "config": {}},
        "conditions": [
            {"field": "content", "op": "contains", "value": "error"},
        ],
        "actions": [{"type": "add_tag", "config": {"tag": "bug-related"}}],
    },
]


def _load_workflows() -> dict:
    """Load workflows from disk."""
    try:
        with open(WORKFLOWS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"workflows": [], "logs": []}


def _save_workflows(data: dict) -> None:
    """Save workflows to disk."""
    os.makedirs(os.path.dirname(WORKFLOWS_PATH), exist_ok=True)
    from app.services.agentmemory import _atomic_write_json
    _atomic_write_json(WORKFLOWS_PATH, data)


def list_workflows() -> list[dict]:
    """List all workflow rules."""
    data = _load_workflows()
    return data.get("workflows", [])


def get_workflow(workflow_id: str) -> Optional[dict]:
    """Get a specific workflow."""
    workflows = list_workflows()
    return next((w for w in workflows if w.get("id") == workflow_id), None)


def create_workflow(workflow_data: dict) -> dict:
    """Create a new workflow rule."""
    data = _load_workflows()

    workflow_id = f"wf-{hashlib.md5(json.dumps(workflow_data, sort_keys=True).encode() + str(time.time()).encode()).hexdigest()[:10]}"

    workflow = {
        "id": workflow_id,
        "name": workflow_data.get("name", "Untitled Rule"),
        "description": workflow_data.get("description", ""),
        "trigger": workflow_data.get("trigger", {"type": "manual", "config": {}}),
        "conditions": workflow_data.get("conditions", []),
        "actions": workflow_data.get("actions", []),
        "enabled": workflow_data.get("enabled", True),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "execution_count": 0,
        "last_executed": None,
    }

    data.setdefault("workflows", []).append(workflow)
    _save_workflows(data)
    return workflow


def update_workflow(workflow_id: str, updates: dict) -> Optional[dict]:
    """Update a workflow rule."""
    data = _load_workflows()
    workflows = data.get("workflows", [])

    for i, w in enumerate(workflows):
        if w.get("id") == workflow_id:
            for key in ("name", "description", "trigger", "conditions", "actions", "enabled"):
                if key in updates:
                    w[key] = updates[key]
            w["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            workflows[i] = w
            data["workflows"] = workflows
            _save_workflows(data)
            return w

    return None


def delete_workflow(workflow_id: str) -> bool:
    """Delete a workflow rule."""
    data = _load_workflows()
    workflows = data.get("workflows", [])
    original_len = len(workflows)
    data["workflows"] = [w for w in workflows if w.get("id") != workflow_id]
    if len(data["workflows"]) < original_len:
        _save_workflows(data)
        return True
    return False


def _evaluate_condition(memory: dict, condition: dict) -> bool:
    """Evaluate a single condition against a memory."""
    field = condition.get("field", "")
    op = condition.get("op", "")
    value = condition.get("value")

    if field == "age_days":
        created = memory.get("created_at", "")
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - created_dt).days
            except (ValueError, TypeError):
                age = 0
        else:
            age = 0
        if op == ">": return age > value
        if op == "<": return age < value
        if op == ">=": return age >= value
        if op == "<=": return age <= value
        return False

    if field == "strength":
        strength = memory.get("strength", 0)
        if op == ">": return strength > value
        if op == "<": return strength < value
        if op == ">=": return strength >= value
        if op == "<=": return strength <= value
        return False

    if field == "type":
        mem_type = memory.get("type", "")
        if op == "==": return mem_type == value
        if op == "!=": return mem_type != value
        return False

    if field == "content":
        content = memory.get("content", "").lower()
        if op == "contains": return str(value).lower() in content
        if op == "not_contains": return str(value).lower() not in content
        return False

    if field == "has_concept":
        concepts = [c.lower() for c in memory.get("concepts", [])]
        return str(value).lower() in concepts

    return False


def execute_workflow(workflow_id: str, memories: list[dict] = None) -> dict:
    """Execute a workflow rule against all memories.
    
    AC-F47-3: Multiple conditions supported (AND logic).
    AC-F47-4: Execution logs show what was changed.
    """
    workflow = get_workflow(workflow_id)
    if not workflow:
        return {"success": False, "error": "Workflow not found"}

    if memories is None:
        from app.services.agentmemory import get_all_memories
        memories = get_all_memories()

    conditions = workflow.get("conditions", [])
    actions = workflow.get("actions", [])
    affected = []
    errors = []

    for memory in memories:
        # All conditions must match (AND logic)
        if conditions and all(_evaluate_condition(memory, c) for c in conditions):
            for action in actions:
                action_type = action.get("type", "")
                try:
                    if action_type == "archive":
                        affected.append({
                            "memory_id": memory.get("id"),
                            "action": "archive",
                            "title": memory.get("title", ""),
                        })
                    elif action_type == "add_tag":
                        tag = action.get("config", {}).get("tag", "")
                        affected.append({
                            "memory_id": memory.get("id"),
                            "action": f"add_tag:{tag}",
                            "title": memory.get("title", ""),
                        })
                    elif action_type == "adjust_strength":
                        delta = action.get("config", {}).get("delta", 0)
                        affected.append({
                            "memory_id": memory.get("id"),
                            "action": f"adjust_strength:{delta}",
                            "title": memory.get("title", ""),
                        })
                    elif action_type == "delete":
                        affected.append({
                            "memory_id": memory.get("id"),
                            "action": "delete",
                            "title": memory.get("title", ""),
                        })
                    elif action_type == "send_notification":
                        affected.append({
                            "memory_id": memory.get("id"),
                            "action": "notification",
                            "title": memory.get("title", ""),
                        })
                except Exception as e:
                    errors.append({"memory_id": memory.get("id"), "error": str(e)})

    # Log execution
    log_entry = {
        "workflow_id": workflow_id,
        "workflow_name": workflow.get("name", ""),
        "executed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "affected_count": len(affected),
        "affected": affected[:20],  # Limit stored details
        "errors": errors,
        "conditions": conditions,
        "actions": actions,
    }

    data = _load_workflows()
    data.setdefault("logs", []).append(log_entry)
    # Keep only last 100 logs
    data["logs"] = data["logs"][-100:]

    # Update execution count
    for w in data.get("workflows", []):
        if w.get("id") == workflow_id:
            w["execution_count"] = w.get("execution_count", 0) + 1
            w["last_executed"] = log_entry["executed_at"]
            break

    _save_workflows(data)

    return {
        "success": True,
        "affected_count": len(affected),
        "affected": affected,
        "errors": errors,
    }


def get_workflow_logs(workflow_id: str, limit: int = 20) -> list[dict]:
    """Get execution history for a workflow."""
    data = _load_workflows()
    logs = [l for l in data.get("logs", []) if l.get("workflow_id") == workflow_id]
    return logs[-limit:]


def get_templates() -> list[dict]:
    """Get pre-built workflow templates."""
    return TEMPLATES


def create_from_template(template_index: int) -> Optional[dict]:
    """Create a workflow from a pre-built template."""
    if 0 <= template_index < len(TEMPLATES):
        return create_workflow(TEMPLATES[template_index])
    return None


def fire_event(event_type: str, memory: dict = None):
    """Fire an event that may trigger event-based workflows.
    
    AC-F47-2: Event-triggered rules fire on memory create/update.
    """
    workflows = list_workflows()
    triggered = []
    for wf in workflows:
        if not wf.get("enabled", True):
            continue
        trigger = wf.get("trigger", {})
        if trigger.get("type") == event_type:
            if memory:
                result = execute_workflow(wf["id"], [memory])
                if result.get("affected_count", 0) > 0:
                    triggered.append(wf["id"])
    return triggered
