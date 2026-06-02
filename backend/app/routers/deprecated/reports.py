"""Advanced Reports API router (F-67)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.report_service import (
    get_report_templates,
    generate_report,
    get_report_history,
    get_report_by_id,
    get_report_content,
)

router = APIRouter()


@router.get("/templates")
def list_templates():
    """Get available report templates.

    AC-F67-1: Template selector in frontend.
    """
    templates = get_report_templates()
    return {"templates": templates, "total": len(templates)}


class GenerateReportReq(BaseModel):
    template_id: str
    filters: Optional[dict] = None
    format_: str = "html"


@router.post("/generate")
def generate(req: GenerateReportReq):
    """Generate a new report.

    AC-F67-1: HTML report generation
    AC-F67-2: PDF report generation (optional)
    AC-F67-3: Charts and statistics included
    AC-F67-4: Custom filters applied
    AC-F67-6: <15s for 200 memories
    """
    if req.format_ not in ("html", "pdf"):
        raise HTTPException(status_code=400, detail="Format must be 'html' or 'pdf'")

    try:
        result = generate_report(
            template_id=req.template_id,
            filters=req.filters,
            format_=req.format_,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
def history(limit: int = 50):
    """Get report generation history.

    AC-F67-5: Downloadable from history.
    """
    reports = get_report_history(limit=limit)
    return {"reports": reports, "total": len(reports)}


@router.get("/{report_id}")
def get_one(report_id: str):
    """Get a specific report by ID."""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return {"report": report}


@router.get("/{report_id}/download")
def download(report_id: str, format_: str = "html"):
    """Download a report's content.

    AC-F67-5: Downloadable from history.
    """
    content = get_report_content(report_id)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found or content unavailable")

    report_info = get_report_by_id(report_id)
    filename = f"report_{report_id}.{format_}"

    if format_ == "html":
        return Response(content=content, media_type="text/html", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported download format: {format_}")


@router.get("/{report_id}/content")
def content(report_id: str):
    """Get the raw content of a report."""
    content = get_report_content(report_id)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found or content unavailable")
    return Response(content=content, media_type="text/html")