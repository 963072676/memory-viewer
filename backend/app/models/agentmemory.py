"""Pydantic models for agentmemory data."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentMemoryItem(BaseModel):
    """Single agentmemory entry."""
    id: str
    type: str = "pattern"
    title: str
    content: str
    concepts: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    strength: int = 5
    version: int = 1
    isLatest: bool = True
    sessionIds: list[str] = Field(default_factory=list)
    archived: bool = False
    health_score: Optional[int] = None
    health_color: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class AgentMemoryResponse(BaseModel):
    """Response for GET /api/agentmemory."""
    memories: list[AgentMemoryItem]


class AgentMemoryPaginatedResponse(BaseModel):
    """Response for GET /api/agentmemory/paginated."""
    total: int
    limit: int
    offset: int
    memories: list[AgentMemoryItem]


class AgentMemoryCreateRequest(BaseModel):
    """Request body for POST /api/agentmemory."""
    title: str
    content: str
    type: str = "pattern"
    concepts: list[str] = Field(default_factory=list)
    strength: int = 5
    tags: list[str] = Field(default_factory=list)


class AgentMemoryCreateResponse(BaseModel):
    """Response for POST /api/agentmemory."""
    success: bool
    memory: AgentMemoryItem


class AgentMemoryUpdateRequest(BaseModel):
    """Request body for PUT /api/agentmemory/{id} (F-08)."""
    content: Optional[str] = None
    concepts: Optional[list[str]] = None
    strength: Optional[int] = Field(default=None, ge=0, le=10)
    tags: Optional[list[str]] = None


class AgentMemoryUpdateResponse(BaseModel):
    """Response for PUT /api/agentmemory/{id}."""
    success: bool
    memory: AgentMemoryItem


class AgentMemoryDeleteResponse(BaseModel):
    """Response for DELETE /api/agentmemory/{id} (F-09)."""
    success: bool
    deleted_id: str


class BatchDeleteRequest(BaseModel):
    """Request body for POST /api/agentmemory/batch/delete."""
    ids: list[str]


class BatchDeleteResponse(BaseModel):
    """Response for batch delete."""
    success: bool
    deleted_count: int
    deleted_ids: list[str]
    not_found_ids: list[str] = Field(default_factory=list)


class ImportResult(BaseModel):
    """Result of memory import operation."""
    success: bool
    imported: int
    skipped: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class BatchActionRequest(BaseModel):
    """Request body for POST /api/agentmemory/batch (F45)."""
    action: str = Field(description="Action: delete, archive, unarchive")
    ids: list[str]
    params: Optional[dict] = None


class BatchActionResponse(BaseModel):
    """Response for POST /api/agentmemory/batch (F45)."""
    success: bool
    action: str
    affected_count: int
    affected_ids: list[str] = Field(default_factory=list)
    not_found_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class TagInfo(BaseModel):
    """Tag with usage count."""
    tag: str
    count: int


class TagsResponse(BaseModel):
    """Response for GET /api/tags."""
    tags: list[TagInfo]


class SetTagsRequest(BaseModel):
    """Request body for PUT /api/agentmemory/{id}/tags."""
    tags: list[str]


class SetTagsResponse(BaseModel):
    """Response for PUT /api/agentmemory/{id}/tags."""
    success: bool
    memory: AgentMemoryItem


class QuickSearchResult(BaseModel):
    """Single result from quick search (F47)."""
    id: str
    title: str
    type: str
    snippet: str
    tags: list[str] = Field(default_factory=list)


class QuickSearchResponse(BaseModel):
    """Response for GET /api/search/quick (F47)."""
    results: list[QuickSearchResult]
    total: int


class SmartCollection(BaseModel):
    """Smart collection with rule-based filtering (F48)."""
    id: str
    name: str
    description: str
    count: int
    icon: str


class CollectionsResponse(BaseModel):
    """Response for GET /api/agentmemory/collections (F48)."""
    collections: list[SmartCollection]
class MemoryTemplate(BaseModel):
    """Memory creation template (F49)."""
    id: str
    name: str
    icon: str
    type: str
    title_template: str
    content_template: str
    suggested_concepts: list[str] = Field(default_factory=list)


class TemplatesResponse(BaseModel):
    """Response for GET /api/agentmemory/templates (F49)."""
    templates: list[MemoryTemplate]
