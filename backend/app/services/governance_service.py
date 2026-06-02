"""Memory Governance Policies service (F-58).

Policy types: retention, quality, tagging, access.
Policy evaluation engine with violation tracking.
Storage: governance_policies.json, governance_violations.jsonl.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

POLICIES_PATH = os.path.join(settings.cache_dir, "governance_policies.json")
VIOLATIONS_PATH = os.path.join(settings.cache_dir, "governance_violations.jsonl")

VALID_POLICY_TYPES = {"retention", "quality", "tagging", "access"}
VALID_OPERATORS = {"gt", "lt", "gte", "lte", "eq", "neq", "contains", "not_contains", "exists", "not_exists"}
VALID_ACTIONS = {"archive", "flag", "delete", "notify", "require_approval"}
VALID_SEVERITIES = {"info", "warning", "error", "critical"}


def _load_policies() -> dict:
    try:
        with open(POLICIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"policies": []}


def _save_policies(data: dict) -> None:
    os.makedirs(os.path.dirname(POLICIES_PATH), exist_ok=True)
    _atomic_write_json(POLICIES_PATH, data)


def _append_violation(violation: dict) -> None:
    os.makedirs(os.path.dirname(VIOLATIONS_PATH), exist_ok=True)
    with open(VIOLATIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(violation, ensure_ascii=False) + "\n")


def _load_violations() -> list[dict]:
    violations = []
    try:
        with open(VIOLATIONS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    violations.append(json.loads(line))
    except FileNotFoundError:
        pass
    return violations


# ─── Policy CRUD ─────────────────────────────────────────────────────────────

def get_all_policies() -> list[dict]:
    """Get all governance policies."""
    data = _load_policies()
    return data.get("policies", [])


def get_policy(policy_id: str) -> Optional[dict]:
    """Get a specific policy."""
    for p in get_all_policies():
        if p["id"] == policy_id:
            return p
    return None


def create_policy(policy: dict) -> dict:
    """Create a new governance policy."""
    import hashlib

    if not policy.get("id"):
        pol_name = policy.get("name", "")
        policy["id"] = f"pol_{hashlib.md5(f'{pol_name}:{time.time()}'.encode()).hexdigest()[:10]}"

    policy.setdefault("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    policy.setdefault("enabled", True)
    policy.setdefault("severity", "warning")

    # Validate
    if policy.get("type") not in VALID_POLICY_TYPES:
        raise ValueError(f"Invalid policy type: {policy.get('type')}. Must be one of {VALID_POLICY_TYPES}")

    data = _load_policies()
    data["policies"].append(policy)
    _save_policies(data)
    return policy


def update_policy(policy_id: str, updates: dict) -> Optional[dict]:
    """Update an existing policy."""
    data = _load_policies()
    for i, p in enumerate(data["policies"]):
        if p["id"] == policy_id:
            p.update(updates)
            p["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            data["policies"][i] = p
            _save_policies(data)
            return p
    return None


def delete_policy(policy_id: str) -> bool:
    """Delete a policy."""
    data = _load_policies()
    original_len = len(data["policies"])
    data["policies"] = [p for p in data["policies"] if p["id"] != policy_id]
    if len(data["policies"]) < original_len:
        _save_policies(data)
        return True
    return False


def toggle_policy(policy_id: str) -> Optional[dict]:
    """Toggle a policy's enabled state."""
    data = _load_policies()
    for i, p in enumerate(data["policies"]):
        if p["id"] == policy_id:
            p["enabled"] = not p.get("enabled", True)
            p["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            data["policies"][i] = p
            _save_policies(data)
            return p
    return None


# ─── Policy Evaluation Engine ────────────────────────────────────────────────

def _get_field_value(memory: dict, field: str):
    """Get a field value from memory, supporting nested fields."""
    if field == "age_days":
        created = memory.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                delta = datetime.now(timezone.utc) - dt
                return delta.days
            except ValueError:
                return 0
        return 0
    elif field == "strength":
        return memory.get("strength", 0)
    elif field == "title_length":
        return len(memory.get("title", memory.get("content", "")))
    elif field == "concepts_count":
        return len(memory.get("concepts", []))
    elif field == "tags_count":
        return len(memory.get("tags", []))
    elif field == "has_title":
        return bool(memory.get("title"))
    elif field == "type":
        return memory.get("type", "")
    elif field == "tags":
        return memory.get("tags", [])
    else:
        return memory.get(field)


def _evaluate_condition(memory: dict, condition: dict) -> bool:
    """Evaluate a single condition against a memory."""
    field = condition.get("field", "")
    operator = condition.get("operator", "")
    value = condition.get("value")

    actual = _get_field_value(memory, field)

    if operator == "gt":
        return actual is not None and actual > value
    elif operator == "lt":
        return actual is not None and actual < value
    elif operator == "gte":
        return actual is not None and actual >= value
    elif operator == "lte":
        return actual is not None and actual <= value
    elif operator == "eq":
        return actual == value
    elif operator == "neq":
        return actual != value
    elif operator == "contains":
        if isinstance(actual, list):
            return value in actual
        return value in str(actual) if actual else False
    elif operator == "not_contains":
        if isinstance(actual, list):
            return value not in actual
        return value not in str(actual) if actual else True
    elif operator == "exists":
        return actual is not None and actual != "" and actual != []
    elif operator == "not_exists":
        return actual is None or actual == "" or actual == []
    return False


def evaluate_policy(policy: dict, memories: list[dict]) -> list[dict]:
    """Evaluate a policy against a list of memories. Returns violations."""
    if not policy.get("enabled", True):
        return []

    violations = []
    conditions = policy.get("conditions", [])

    for memory in memories:
        # All conditions must match (AND logic)
        all_match = True
        for condition in conditions:
            if not _evaluate_condition(memory, condition):
                all_match = False
                break

        if all_match and conditions:
            violation = {
                "policy_id": policy["id"],
                "policy_name": policy.get("name", ""),
                "policy_type": policy.get("type", ""),
                "memory_id": memory.get("id", ""),
                "memory_title": memory.get("title", memory.get("content", "")[:50]),
                "action": policy.get("action", "flag"),
                "severity": policy.get("severity", "warning"),
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "conditions_matched": conditions,
            }
            violations.append(violation)

    return violations


def run_evaluation(memories: list[dict], policy_id: Optional[str] = None) -> dict:
    """Run policy evaluation. If policy_id is given, evaluate only that policy."""
    policies = get_all_policies()

    if policy_id:
        policies = [p for p in policies if p["id"] == policy_id]
        if not policies:
            return {"error": f"Policy {policy_id} not found"}

    all_violations = []
    for policy in policies:
        violations = evaluate_policy(policy, memories)
        all_violations.extend(violations)

    # Record violations
    for v in all_violations:
        _append_violation(v)

    return {
        "policies_evaluated": len(policies),
        "memories_checked": len(memories),
        "violations_found": len(all_violations),
        "violations": all_violations,
        "evaluated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def get_violations(policy_id: Optional[str] = None, limit: int = 100) -> list[dict]:
    """Get recorded violations, optionally filtered by policy."""
    violations = _load_violations()
    if policy_id:
        violations = [v for v in violations if v.get("policy_id") == policy_id]
    return violations[-limit:]


def get_compliance_report(memories: list[dict]) -> dict:
    """Generate a compliance report."""
    policies = get_all_policies()
    enabled_policies = [p for p in policies if p.get("enabled", True)]

    all_violations = []
    for policy in enabled_policies:
        violations = evaluate_policy(policy, memories)
        all_violations.extend(violations)

    violating_ids = set(v["memory_id"] for v in all_violations)
    compliant_count = len(memories) - len(violating_ids)

    return {
        "total_memories": len(memories),
        "total_policies": len(policies),
        "enabled_policies": len(enabled_policies),
        "compliant_memories": compliant_count,
        "violating_memories": len(violating_ids),
        "compliance_rate": round(compliant_count / max(len(memories), 1) * 100, 1),
        "violations_by_type": _group_violations_by_type(all_violations),
        "violations_by_severity": _group_violations_by_severity(all_violations),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _group_violations_by_type(violations: list[dict]) -> dict:
    groups = {}
    for v in violations:
        t = v.get("policy_type", "unknown")
        groups[t] = groups.get(t, 0) + 1
    return groups


def _group_violations_by_severity(violations: list[dict]) -> dict:
    groups = {}
    for v in violations:
        s = v.get("severity", "unknown")
        groups[s] = groups.get(s, 0) + 1
    return groups
