"""AI Auto-Tagging & Summarization API router (F-34)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.auto_tag import suggest_tags, summarize_memory, bulk_auto_tag
from app.services.agentmemory import get_memory_by_id, get_all_memories

router = APIRouter()


class SuggestTagsResponse(BaseModel):
    memory_id: str
    title: str
    suggested_tags: list[str]


class SummarizeResponse(BaseModel):
    memory_id: str
    title: str
    summary: str


class BulkAutoTagRequest(BaseModel):
    ids: Optional[list[str]] = None  # None = all untagged
    max_tags: int = Field(default=5, ge=1, le=10)


class BulkAutoTagResponse(BaseModel):
    success: bool
    processed: int
    results: list[dict]


@router.post("/{memory_id}/suggest-tags", response_model=SuggestTagsResponse)
def api_suggest_tags(memory_id: str):
    """Suggest tags for a specific memory based on content analysis."""
    memory = get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")

    tags = suggest_tags(
        title=memory.get("title", ""),
        content=memory.get("content", ""),
        concepts=memory.get("concepts", []),
        existing_tags=memory.get("tags", []),
    )

    return {
        "memory_id": memory_id,
        "title": memory.get("title", ""),
        "suggested_tags": tags,
    }


@router.post("/{memory_id}/summarize", response_model=SummarizeResponse)
def api_summarize(memory_id: str):
    """Generate a 1-2 sentence summary of a memory."""
    memory = get_memory_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")

    summary = summarize_memory(
        title=memory.get("title", ""),
        content=memory.get("content", ""),
    )

    return {
        "memory_id": memory_id,
        "title": memory.get("title", ""),
        "summary": summary,
    }


@router.post("/bulk-auto-tag", response_model=BulkAutoTagResponse)
def api_bulk_auto_tag(req: BulkAutoTagRequest):
    """Auto-tag multiple memories (or all untagged ones)."""
    memories = get_all_memories()

    if req.ids:
        id_set = set(req.ids)
        memories = [m for m in memories if m.get("id") in id_set]
    else:
        # Auto-tag untagged memories
        memories = [m for m in memories if not m.get("tags")]

    results = bulk_auto_tag(memories, max_tags_per_memory=req.max_tags)

    return {
        "success": True,
        "processed": len(results),
        "results": results,
    }
