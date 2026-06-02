"""Memory Workflow Automation API router (F-47)."""

from typing import Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.workflow_service import (
    list_workflows,
    get_workflow,
    create_workflow,
    update_workflow,
    delete_workflow,
    execute_workflow,
    get_workflow_logs,
    get_templates,
    create_from_template,
)

router = APIRouter()


@router.get("")
def list_all():
    """List all workflow rules.
    
    AC-F47-1: Can create a scheduled rule via UI.
    AC-F47-5: Rules can be enabled/disabled without deletion.
    """
    return {"workflows": list_workflows()}


@router.get("/templates")
def templates():
    """Get pre-built workflow templates.
    
    AC-F47-6: Pre-built templates work out of the box.
    """
    return {"templates": get_templates()}


class CreateWorkflowReq(BaseModel):
    name: str = "Untitled Rule"
    description: str = ""
    trigger: dict = {"type": "manual", "config": {}}
    conditions: list[dict] = []
    actions: list[dict] = []
    enabled: bool = True


@router.post("")
def create(req: CreateWorkflowReq):
    """Create a new workflow rule.
    
    AC-F47-1: Can create a scheduled rule via UI.
    AC-F47-3: Multiple conditions supported (AND logic).
    """
    workflow = create_workflow(req.model_dump())
    return {"success": True, "workflow": workflow}


@router.post("/templates/{template_index}")
def create_from_template(template_index: int):
    """Create a workflow from a pre-built template.
    
    AC-F47-6: Pre-built templates work out of the box.
    """
    workflow = create_from_template(template_index)
    if not workflow:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"success": True, "workflow": workflow}


@router.get("/{workflow_id}")
def get_one(workflow_id: str):
    """Get a specific workflow."""
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return workflow


class UpdateWorkflowReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger: Optional[dict] = None
    conditions: Optional[list[dict]] = None
    actions: Optional[list[dict]] = None
    enabled: Optional[bool] = None


@router.put("/{workflow_id}")
def update(workflow_id: str, req: UpdateWorkflowReq):
    """Update a workflow rule.
    
    AC-F47-5: Rules can be enabled/disabled without deletion.
    """
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    workflow = update_workflow(workflow_id, updates)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return {"success": True, "workflow": workflow}


@router.delete("/{workflow_id}")
def delete(workflow_id: str):
    """Delete a workflow rule."""
    if not delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return {"success": True}


@router.post("/{workflow_id}/execute")
def execute(workflow_id: str):
    """Manually trigger a workflow execution.
    
    AC-F47-2: Event-triggered rules fire on memory create/update.
    AC-F47-4: Execution logs show what was changed.
    """
    result = execute_workflow(workflow_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Execution failed"))
    return result


@router.get("/{workflow_id}/logs")
def logs(workflow_id: str, limit: int = Query(default=20, ge=1, le=100)):
    """Get execution history for a workflow.
    
    AC-F47-4: Execution logs show what was changed.
    """
    return {"logs": get_workflow_logs(workflow_id, limit)}
