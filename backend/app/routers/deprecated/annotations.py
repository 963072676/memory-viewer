"""Collaborative Annotations API router (F-46)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.annotation_service import (
    get_annotations,
    add_annotation,
    update_annotation,
    delete_annotation,
    resolve_annotation,
    get_annotation_stats,
    get_all_annotation_stats,
    get_flagged_memories,
)

router = APIRouter()


class AddAnnotationReq(BaseModel):
    author: str = "anonymous"
    content: str
    type: str = "comment"  # comment, flag_for_review, suggest_edit, tag_suggestion
    parent_id: Optional[str] = None


@router.get("/memories/{memory_id}/annotations")
def list_annotations(memory_id: str):
    """Get annotations for a memory.
    
    AC-F46-1: Can add comment to any memory.
    AC-F46-2: Comments support threading (reply to comment).
    """
    annotations = get_annotations(memory_id)
    return {"annotations": annotations, "total": len(annotations)}


@router.post("/memories/{memory_id}/annotations")
def create_annotation(memory_id: str, req: AddAnnotationReq):
    """Add an annotation to a memory.
    
    AC-F46-1: Can add comment to any memory.
    AC-F46-2: Comments support threading (reply to comment).
    AC-F46-3: Flag for review shows badge on memory card.
    """
    if req.type not in ("comment", "flag_for_review", "suggest_edit", "tag_suggestion"):
        raise HTTPException(status_code=400, detail=f"Invalid annotation type: {req.type}")
    annotation = add_annotation(memory_id, req.author, req.content, req.type, req.parent_id)
    return {"success": True, "annotation": annotation}


@router.get("/memories/{memory_id}/annotations/stats")
def annotation_stats(memory_id: str):
    """Get annotation stats for a memory card.
    
    AC-F46-6: Annotation count visible on collapsed memory cards.
    """
    return get_annotation_stats(memory_id)


class UpdateAnnotationReq(BaseModel):
    content: Optional[str] = None
    author: Optional[str] = None


@router.put("/annotations/{annotation_id}")
def update(annotation_id: str, req: UpdateAnnotationReq):
    """Edit an annotation."""
    result = update_annotation(annotation_id, req.content, req.author)
    if not result:
        raise HTTPException(status_code=404, detail=f"Annotation {annotation_id} not found")
    return {"success": True, "annotation": result}


@router.delete("/annotations/{annotation_id}")
def delete(annotation_id: str):
    """Delete an annotation."""
    if not delete_annotation(annotation_id):
        raise HTTPException(status_code=404, detail=f"Annotation {annotation_id} not found")
    return {"success": True}


class ResolveReq(BaseModel):
    resolved_by: str = "system"


@router.post("/annotations/{annotation_id}/resolve")
def resolve(annotation_id: str, req: ResolveReq):
    """Resolve a flag/suggestion annotation.
    
    AC-F46-3: Flag for review shows badge on memory card.
    """
    result = resolve_annotation(annotation_id, req.resolved_by)
    if not result:
        raise HTTPException(status_code=404, detail=f"Annotation {annotation_id} not found")
    return {"success": True, "annotation": result}


@router.get("/annotations/stats/all")
def all_stats():
    """Get annotation stats for all memories."""
    return {"stats": get_all_annotation_stats()}


@router.get("/annotations/flagged")
def flagged_memories():
    """Get all memories with unresolved flags.
    
    AC-F46-5: Can filter memories by "has flags" or "has suggestions".
    """
    return {"flagged": get_flagged_memories()}
