"""Memory Lineage & Provenance API router (F-48)."""

from fastapi import APIRouter, HTTPException, Query

from app.services.lineage_service import (
    get_lineage,
    get_lineage_graph,
    backfill_all,
    record_creation,
    record_transformation,
    record_merge,
)

router = APIRouter()


@router.get("/{memory_id}/lineage")
def memory_lineage(memory_id: str):
    """Get the full provenance chain for a memory.
    
    AC-F48-1: New memories automatically get lineage metadata.
    AC-F48-5: Source type displayed with appropriate icon.
    AC-F48-6: Backfilled legacy memories show "legacy" source.
    """
    lineage = get_lineage(memory_id)
    if not lineage:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
    return lineage


@router.get("/graph")
def lineage_graph():
    """Get DAG visualization data of all memory derivations.
    
    AC-F48-4: Lineage graph renders correctly with force-graph.
    AC-F48-5: Source type displayed with appropriate icon.
    """
    return get_lineage_graph()


@router.post("/backfill")
def backfill_lineage():
    """Backfill lineage for all legacy memories.
    
    AC-F48-6: Backfilled legacy memories show "legacy" source.
    """
    result = backfill_all()
    return {"success": True, **result}


class LineageRecordRequest:
    pass


from pydantic import BaseModel
from typing import Optional


class RecordCreationReq(BaseModel):
    source: str = "manual"
    parent_ids: list[str] = []


class RecordTransformReq(BaseModel):
    transform_type: str
    detail: str = ""


class RecordMergeReq(BaseModel):
    parent_ids: list[str]


@router.post("/{memory_id}/lineage/creation")
def create_lineage(memory_id: str, req: RecordCreationReq):
    """Record creation lineage for a memory."""
    lineage = record_creation(memory_id, source=req.source, parent_ids=req.parent_ids)
    return lineage


@router.post("/{memory_id}/lineage/transform")
def add_transformation(memory_id: str, req: RecordTransformReq):
    """Record a transformation on a memory."""
    lineage = record_transformation(memory_id, req.transform_type, req.detail)
    if not lineage:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
    return lineage


@router.post("/{memory_id}/lineage/merge")
def add_merge(memory_id: str, req: RecordMergeReq):
    """Record a merge operation."""
    lineage = record_merge(memory_id, req.parent_ids)
    return lineage
