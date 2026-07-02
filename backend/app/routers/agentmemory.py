"""Agentmemory API router."""

from typing import Optional

from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import Response

from app.models.agentmemory import (
    AgentMemoryResponse,
    AgentMemoryPaginatedResponse,
    AgentMemoryCreateRequest,
    AgentMemoryCreateResponse,
    AgentMemoryUpdateRequest,
    AgentMemoryUpdateResponse,
    AgentMemoryDeleteResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
    ImportResult,
    BatchActionRequest,
    BatchActionResponse,
    TagsResponse,
    SetTagsRequest,
    SetTagsResponse,
    CollectionsResponse,
    TemplatesResponse,
)
from app.services import agentmemory as service
from app.services.feishu_webhook import send_notification as feishu_send
from app.services.notification import send_notification_sync

router = APIRouter()


@router.get("", response_model=AgentMemoryResponse)
def get_agentmemory():
    """Get all agentmemory entries (v1 compatible)."""
    memories = service.get_all_memories()
    return {"memories": memories}


@router.get("/paginated", response_model=AgentMemoryPaginatedResponse)
def get_agentmemory_paginated(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="updatedAt", pattern="^(updatedAt|createdAt|strength|type)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    type: Optional[str] = Query(default=None),
    include_archived: bool = Query(default=False),
    tag: Optional[str] = Query(default=None),
):
    """Get paginated agentmemory entries with sorting and filtering."""
    return service.get_paginated_memories(
        limit=limit, offset=offset, sort=sort, order=order,
        type_filter=type, include_archived=include_archived,
        tag_filter=tag,
    )


@router.post("", response_model=AgentMemoryCreateResponse)
def create_agentmemory(req: AgentMemoryCreateRequest):
    """Create a new agentmemory entry."""
    memory = service.create_memory(
        title=req.title,
        content=req.content,
        type_=req.type,
        concepts=req.concepts,
        strength=req.strength,
        tags=req.tags,
    )
    # F-17: Send Feishu webhook notification
    feishu_send("🆕 New Memory", f"**Title**: {req.title}\n**ID**: `{memory.get('id', '')}`", msg_type="success")
    # F-17: Legacy notification
    try:
        send_notification_sync("create", memory.get("title", ""), memory.get("id", ""))
    except Exception:
        pass
    return {"success": True, "memory": memory}


@router.put("/{memory_id}", response_model=AgentMemoryUpdateResponse)
def update_agentmemory(memory_id: str, req: AgentMemoryUpdateRequest):
    """Update an existing agentmemory entry (F-08)."""
    memory = service.update_memory(
        memory_id=memory_id,
        content=req.content,
        concepts=req.concepts,
        strength=req.strength,
        tags=req.tags,
    )
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    # F-17: Send Feishu webhook notification
    feishu_send("✏️ Updated Memory", f"**Title**: {memory.get('title', '')}\n**ID**: `{memory_id}`", msg_type="warning")
    # F-17: Legacy notification
    try:
        send_notification_sync("update", memory.get("title", ""), memory_id)
    except Exception:
        pass
    return {"success": True, "memory": memory}


@router.delete("/{memory_id}", response_model=AgentMemoryDeleteResponse)
def delete_agentmemory(memory_id: str):
    """Delete a single agentmemory entry (F-09)."""
    # Get title before deletion for notification
    memory = service.get_memory_by_id(memory_id)
    title = memory.get("title", "") if memory else ""
    deleted = service.delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    # F-17: Send Feishu webhook notification
    feishu_send("🗑️ Deleted Memory", f"**Title**: {title}\n**ID**: `{memory_id}`", msg_type="danger")
    # F-17: Legacy notification
    try:
        send_notification_sync("delete", title, memory_id)
    except Exception:
        pass
    return {"success": True, "deleted_id": memory_id}


@router.post("/batch/delete", response_model=BatchDeleteResponse)
def batch_delete_agentmemory(req: BatchDeleteRequest):
    """Batch delete agentmemory entries (F-09)."""
    if not req.ids:
        return {"success": True, "deleted_count": 0, "deleted_ids": [], "not_found_ids": []}
    result = service.delete_memories_batch(req.ids)
    return {"success": True, **result}


@router.post("/batch", response_model=BatchActionResponse)
def batch_action(req: BatchActionRequest):
    """Unified batch action endpoint (F45). Supports: delete, archive, unarchive."""
    if not req.ids:
        return {"success": True, "action": req.action, "affected_count": 0, "affected_ids": [], "not_found_ids": []}

    if req.action == "delete":
        result = service.delete_memories_batch(req.ids)
        return {
            "success": True,
            "action": "delete",
            "affected_count": result["deleted_count"],
            "affected_ids": result["deleted_ids"],
            "not_found_ids": result["not_found_ids"],
        }
    elif req.action == "archive":
        result = service.batch_archive_memories(req.ids)
        return {"success": True, "action": "archive", **result}
    elif req.action == "unarchive":
        result = service.batch_unarchive_memories(req.ids)
        return {"success": True, "action": "unarchive", **result}
    elif req.action == "add_tags":
        tags = req.params.get("tags", []) if req.params else []
        result = service.batch_add_tags(req.ids, tags)
        return {"success": True, "action": "add_tags", **result}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}. Supported: delete, archive, unarchive, add_tags")


@router.get("/stats")
def get_agentmemory_stats():
    """Get detailed agentmemory statistics (F-10)."""
    return service.get_stats()


@router.post("/import", response_model=ImportResult)
async def import_agentmemory(file: UploadFile = File(...)):
    """Import memories from a JSON or Markdown file."""
    content = await file.read()
    text = content.decode("utf-8")
    return service.import_memories(text, file.filename or "unknown.json")


@router.get("/export")
def export_agentmemory(
    format: str = Query(default="json", pattern="^(json|markdown)$"),
    ids: Optional[str] = Query(default=None),
):
    """Export memories as JSON or Markdown."""
    content, media_type, filename = service.export_memories(format_=format, ids=ids)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch("/{memory_id}/archive")
def archive_agentmemory(memory_id: str):
    """Archive a memory entry (F-15). Sets archived=true."""
    memory = service.set_archive_status(memory_id, archived=True)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    # F-17: Send notification asynchronously
    try:
        send_notification_sync("archive", memory.get("title", ""), memory_id)
    except Exception:
        pass
    return {"success": True, "memory": memory}


@router.patch("/{memory_id}/unarchive")
def unarchive_agentmemory(memory_id: str):
    """Unarchive a memory entry (F-15). Sets archived=false."""
    memory = service.set_archive_status(memory_id, archived=False)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    # F-17: Send notification asynchronously
    try:
        send_notification_sync("unarchive", memory.get("title", ""), memory_id)
    except Exception:
        pass
    return {"success": True, "memory": memory}


# F46: Tag endpoints
@router.put("/{memory_id}/tags", response_model=SetTagsResponse)
def set_memory_tags(memory_id: str, req: SetTagsRequest):
    """Set tags on a memory (replaces existing tags)."""
    memory = service.set_memory_tags(memory_id, req.tags)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    return {"success": True, "memory": memory}


# F48: Smart Collections endpoints
@router.get("/collections", response_model=CollectionsResponse)
def get_smart_collections():
    """Get smart collections with rule-based filtering (F48)."""
    collections = service.get_smart_collections()
    return {"collections": collections}


# F46: Tags endpoint
@router.get("/tags", response_model=TagsResponse)
def get_all_tags():
    """Get all unique tags with usage counts."""
    tags = service.get_all_tags()
    return {"tags": tags}


# F49: Memory Templates (MUST be before /{memory_id} to avoid route collision)
MEMORY_TEMPLATES = [
    {
        "id": "bug-report",
        "name": "Bug Report",
        "icon": "🐛",
        "type": "bug",
        "title_template": "Bug: [description]",
        "content_template": (
            "## Steps to Reproduce\n"
            "1. \n"
            "2. \n"
            "3. \n\n"
            "## Expected Behavior\n"
            "\n\n"
            "## Actual Behavior\n"
            "\n\n"
            "## Suggested Fix\n"
            "\n"
        ),
        "suggested_concepts": ["bug", "debugging"],
    },
    {
        "id": "code-pattern",
        "name": "Code Pattern",
        "icon": "🧩",
        "type": "pattern",
        "title_template": "Pattern: [name]",
        "content_template": (
            "## Context\n"
            "\n\n"
            "## Solution\n"
            "\n\n"
            "## Example\n"
            "```\n"
            "```\n"
        ),
        "suggested_concepts": ["pattern", "best-practice"],
    },
    {
        "id": "architecture-decision",
        "name": "Architecture Decision",
        "icon": "🏗️",
        "type": "architecture",
        "title_template": "ADR: [decision]",
        "content_template": (
            "## Context\n"
            "\n\n"
            "## Decision\n"
            "\n\n"
            "## Consequences\n"
            "\n"
        ),
        "suggested_concepts": ["architecture", "decision"],
    },
    {
        "id": "meeting-note",
        "name": "Meeting Note",
        "icon": "📝",
        "type": "fact",
        "title_template": "Meeting: [topic]",
        "content_template": (
            "## Attendees\n"
            "\n\n"
            "## Agenda\n"
            "\n\n"
            "## Decisions\n"
            "\n\n"
            "## Action Items\n"
            "- [ ] \n"
        ),
        "suggested_concepts": ["meeting", "notes"],
    },
    {
        "id": "workflow",
        "name": "Workflow",
        "icon": "⚙️",
        "type": "workflow",
        "title_template": "Workflow: [process]",
        "content_template": (
            "## Trigger\n"
            "\n\n"
            "## Steps\n"
            "1. \n"
            "2. \n"
            "3. \n\n"
            "## Output\n"
            "\n"
        ),
        "suggested_concepts": ["workflow", "automation"],
    },
]


@router.get("/templates", response_model=TemplatesResponse)
def get_templates():
    """Get predefined memory creation templates (F49)."""
    return {"templates": MEMORY_TEMPLATES}


# P21-T1: Memory Detail endpoint (MUST be last to avoid route conflict with /collections, /tags, /templates)
@router.get("/{memory_id}", response_model=AgentMemoryResponse)
def get_agentmemory_by_id(memory_id: str):
    """Get a single agentmemory entry by ID (P21-T1)."""
    memory = service.get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    return {"memories": [memory]}