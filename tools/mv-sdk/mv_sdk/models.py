"""Typed data models for Memory Viewer SDK."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Memory(BaseModel):
    """Memory data model."""
    id: str
    type: str = "fact"
    title: str = ""
    content: str = ""
    concepts: list[str] = []
    files: list[str] = []
    createdAt: str = ""
    updatedAt: str = ""
    strength: int = 100
    version: int = 1
    isLatest: bool = True
    sessionIds: list[str] = []
    archived: bool = False
    tags: list[str] = []
    health_score: Optional[float] = None
    health_color: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model."""
    id: str
    title: str
    type: str
    snippet: str
    tags: list[str] = []
    similarity: float = 0.0
    match_type: str = "keyword"


class RagResponse(BaseModel):
    """RAG search response."""
    query: str
    answer: str
    sources: list[SearchResult] = []
    confidence: float = 0.0
    follow_up_questions: list[str] = []
    total_sources: int = 0


class DigestSection(BaseModel):
    """Digest section."""
    new_memories: list[dict] = []
    top_changes: list[dict] = []
    emerging_themes: list[dict] = []
    health_alerts: list[dict] = []


class Digest(BaseModel):
    """Memory digest model."""
    id: str
    type: str
    generated_at: str
    period: dict = {}
    summary: str = ""
    sections: DigestSection = DigestSection()
    stats: dict = {}


class TemplateField(BaseModel):
    """Template field definition."""
    name: str
    type: str = "text"
    label: str = ""
    required: bool = False
    options: list[str] = []
    min: Optional[float] = None
    max: Optional[float] = None


class Template(BaseModel):
    """Memory template model."""
    id: str
    name: str
    icon: str = "📝"
    description: str = ""
    builtin: bool = False
    fields: list[TemplateField] = []
    title_template: str = ""
    content_template: str = ""
    default_type: str = "fact"
    default_tags: list[str] = []


class Workspace(BaseModel):
    """Workspace model."""
    id: str
    name: str
    description: str = ""
    created_at: str = ""
    created_by: str = ""
    is_default: bool = False


class Member(BaseModel):
    """Workspace member model."""
    user_id: str
    role: str = "viewer"
    workspace_id: str = ""
    joined_at: str = ""


class ImportResult(BaseModel):
    """Import result model."""
    success: bool
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = []


class Stats(BaseModel):
    """Memory statistics."""
    total: int = 0
    by_type: dict = {}
    avg_strength: float = 0.0
    archived_count: int = 0
    tags_count: int = 0
