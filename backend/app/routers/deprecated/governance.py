"""Memory Governance Policies router (F-58)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.governance_service import (
    get_all_policies,
    get_policy,
    create_policy,
    update_policy,
    delete_policy,
    toggle_policy,
    run_evaluation,
    get_violations,
    get_compliance_report,
)
from app.services.agentmemory import get_all_memories

router = APIRouter()


# ─── Policy CRUD ─────────────────────────────────────────────────────────────

@router.get("/policies")
def list_policies():
    """List all governance policies."""
    policies = get_all_policies()
    return {"policies": policies, "total": len(policies)}


class CreatePolicyReq(BaseModel):
    name: str
    description: str = ""
    type: str  # retention, quality, tagging, access
    conditions: list[dict] = []
    action: str = "flag"
    enabled: bool = True
    severity: str = "warning"
    schedule: str = ""


@router.post("/policies")
def create(req: CreatePolicyReq):
    """Create a new governance policy."""
    try:
        policy = create_policy(req.model_dump())
        return {"success": True, "policy": policy}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies/{policy_id}")
def get_one(policy_id: str):
    """Get a specific policy."""
    policy = get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"policy": policy}


class UpdatePolicyReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[list[dict]] = None
    action: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None
    schedule: Optional[str] = None


@router.put("/policies/{policy_id}")
def update(policy_id: str, req: UpdatePolicyReq):
    """Update a policy."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    policy = update_policy(policy_id, updates)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"success": True, "policy": policy}


@router.delete("/policies/{policy_id}")
def delete(policy_id: str):
    """Delete a policy."""
    if not delete_policy(policy_id):
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"success": True}


@router.post("/policies/{policy_id}/toggle")
def toggle(policy_id: str):
    """Toggle a policy's enabled state."""
    policy = toggle_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return {"success": True, "policy": policy}


# ─── Evaluation ──────────────────────────────────────────────────────────────

@router.post("/policies/{policy_id}/evaluate")
def evaluate_single(policy_id: str):
    """Manually trigger evaluation for a specific policy."""
    memories = _get_all_memories()
    result = run_evaluation(memories, policy_id=policy_id)
    return result


@router.post("/evaluate")
def evaluate_all():
    """Evaluate all enabled policies against all memories."""
    memories = _get_all_memories()
    result = run_evaluation(memories)
    return result


# ─── Violations & Reports ────────────────────────────────────────────────────

@router.get("/violations")
def list_violations(policy_id: str = Query(""), limit: int = Query(100)):
    """List policy violations."""
    violations = get_violations(policy_id=policy_id or None, limit=limit)
    return {"violations": violations, "total": len(violations)}


@router.get("/compliance-report")
def compliance_report():
    """Generate compliance report."""
    memories = _get_all_memories()
    report = get_compliance_report(memories)
    return report


def _get_all_memories() -> list[dict]:
    """Helper to load all memories."""
    try:
        return get_all_memories()
    except Exception:
        return []
