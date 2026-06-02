"""PII Redaction API router (F-41)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.redaction_service import (
    detect_pii,
    mask_text,
    scan_memories,
    has_pii,
    get_detector_config,
    set_detector_enabled,
)
from app.services.agentmemory import get_all_memories, get_memory_by_id

router = APIRouter()


class RedactResponse(BaseModel):
    memory_id: str
    original_length: int
    masked_content: str
    pii_found: int
    pii_types: list[str]
    matches: list[dict]


class PIIMatchInfo(BaseModel):
    memory_id: str
    memory_title: str
    pii_count: int
    pii_types: list[str]


class PIIScanResponse(BaseModel):
    total_memories: int
    memories_with_pii: int
    total_pii_count: int
    affected_memories: list[PIIMatchInfo]


class PIIReportResponse(BaseModel):
    total_memories: int
    memories_with_pii: int
    total_pii_count: int
    by_type: dict[str, int]
    memories: list[dict]


class DetectorConfigRequest(BaseModel):
    detector: str
    enabled: bool


@router.post("/memories/{memory_id}/redact", response_model=RedactResponse)
def redact_memory(memory_id: str):
    """Redact PII from a single memory. Returns masked content without modifying original.
    
    AC-F41-1: API keys are auto-detected and marked.
    AC-F41-2: Emails are detected and partially masked.
    AC-F41-6: Masking doesn't affect original data storage.
    """
    mem = get_memory_by_id(memory_id)
    if not mem:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")

    text = f"{mem.get('title', '')}\n{mem.get('content', '')}"
    matches = detect_pii(text)
    masked = mask_text(text, matches)
    pii_types = list(set(m.pii_type for m in matches))

    return RedactResponse(
        memory_id=memory_id,
        original_length=len(text),
        masked_content=masked,
        pii_found=len(matches),
        pii_types=pii_types,
        matches=[
            {
                "type": m.pii_type,
                "masked": m.masked,
                "start": m.start,
                "end": m.end,
                "confidence": m.confidence,
            }
            for m in matches
        ],
    )


@router.post("/memories/scan-pii", response_model=PIIScanResponse)
def scan_all_pii():
    """Scan all memories for PII.
    
    AC-F41-3: PII scan report lists all memories containing sensitive info.
    """
    memories = get_all_memories()
    report = scan_memories(memories)

    return PIIScanResponse(
        total_memories=report.total_memories,
        memories_with_pii=report.memories_with_pii,
        total_pii_count=report.total_pii_count,
        affected_memories=[
            PIIMatchInfo(
                memory_id=r.memory_id,
                memory_title=r.memory_title,
                pii_count=r.pii_count,
                pii_types=r.pii_types,
            )
            for r in report.by_memory
        ],
    )


@router.get("/memories/pii-report", response_model=PIIReportResponse)
def pii_report():
    """Get PII statistics report.
    
    AC-F41-3: PII scan report lists all memories containing sensitive info.
    """
    memories = get_all_memories()
    report = scan_memories(memories)

    return PIIReportResponse(
        total_memories=report.total_memories,
        memories_with_pii=report.memories_with_pii,
        total_pii_count=report.total_pii_count,
        by_type=report.by_type,
        memories=[
            {
                "id": r.memory_id,
                "title": r.memory_title,
                "pii_count": r.pii_count,
                "pii_types": r.pii_types,
            }
            for r in report.by_memory
        ],
    )


@router.get("/memories/pii-detectors")
def get_pii_detectors():
    """Get available PII detectors and their enabled/disabled state."""
    return {"detectors": get_detector_config()}


@router.put("/memories/pii-detectors")
def update_pii_detector(req: DetectorConfigRequest):
    """Enable or disable a specific PII detector."""
    success = set_detector_enabled(req.detector, req.enabled)
    if not success:
        raise HTTPException(status_code=404, detail=f"Detector '{req.detector}' not found")
    return {"success": True, "detector": req.detector, "enabled": req.enabled}
