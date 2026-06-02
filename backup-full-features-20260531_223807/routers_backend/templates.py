"""Memory Templates API router (F-52)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.template_service import (
    get_all_templates,
    get_template,
    create_template,
    update_template,
    delete_template,
    create_memory_from_template,
)

router = APIRouter()


@router.get("")
def list_templates():
    """Get all templates (built-in + custom)."""
    return {"templates": get_all_templates(), "total": len(get_all_templates())}


@router.get("/{template_id}")
def get_one(template_id: str):
    """Get a specific template."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    return {"template": template}


class CreateTemplateReq(BaseModel):
    name: str
    description: str = ""
    fields: list[dict] = []
    title_template: str = ""
    content_template: str = ""
    default_type: str = "fact"
    default_tags: list[str] = []
    icon: str = "📝"


@router.post("")
def create(req: CreateTemplateReq):
    """Create a custom template.

    AC-F52-3: Custom template CRUD.
    """
    template = create_template(
        name=req.name,
        description=req.description,
        fields=req.fields,
        title_template=req.title_template,
        content_template=req.content_template,
        default_type=req.default_type,
        default_tags=req.default_tags,
        icon=req.icon,
    )
    return {"success": True, "template": template}


class UpdateTemplateReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list[dict]] = None
    title_template: Optional[str] = None
    content_template: Optional[str] = None
    default_type: Optional[str] = None
    default_tags: Optional[list[str]] = None
    icon: Optional[str] = None


@router.put("/{template_id}")
def update(template_id: str, req: UpdateTemplateReq):
    """Update a custom template."""
    result = update_template(template_id, **req.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found or is built-in")
    return {"success": True, "template": result}


@router.delete("/{template_id}")
def delete(template_id: str):
    """Delete a custom template."""
    if not delete_template(template_id):
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found or is built-in")
    return {"success": True}


class CreateMemoryReq(BaseModel):
    values: dict


@router.post("/{template_id}/create-memory")
def create_from_template(template_id: str, req: CreateMemoryReq):
    """Create a memory from a template.

    AC-F52-5: Use Template button creates memory.
    """
    try:
        memory = create_memory_from_template(template_id, req.values)
        return {"success": True, "memory": memory}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
