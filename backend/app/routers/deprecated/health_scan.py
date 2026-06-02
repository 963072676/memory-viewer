"""Health Scanner router (F-68).

Endpoints:
  POST /         -> run a new scan (adapts to frontend HealthScanResult format)
  GET  /summary  -> score + issue count + issues by severity
  GET  /last     -> most recent scan result (adapts to frontend format)
"""

from fastapi import APIRouter, HTTPException

from app.services.health_scanner_service import (
    run_full_scan,
    get_scan_summary,
    get_latest_scan,
)


def _build_breakdown(issues: list[dict]) -> dict:
    high = sum(1 for i in issues if i.get("severity") == "high")
    medium = sum(1 for i in issues if i.get("severity") == "medium")
    return {
        "strength_avg": 0,
        "stale_count": sum(1 for i in issues if i.get("check") == "stale"),
        "duplicate_count": sum(1 for i in issues if i.get("check") == "duplicate"),
        "missing_concepts_count": sum(1 for i in issues if i.get("check") == "empty_metadata"),
        "missing_tags_count": 0,
        "low_health_count": high + medium,
        "orphan_count": sum(1 for i in issues if i.get("check") == "orphaned_concept"),
    }


def _adapt_result(result: dict) -> dict:
    """Adapt backend scan result to frontend HealthScanResult format."""
    issues = result.get("issues", [])
    adapted_issues = []
    for idx, issue in enumerate(issues):
        adapted_issues.append({
            "id": f"issue_{idx}",
            "severity": issue.get("severity", "info"),
            "category": issue.get("check", "unknown"),
            "title": issue.get("message", ""),
            "description": "",
            "affected_count": 1,
            "suggestion": None,
        })
    adapted = {
        "overall_score": result.get("score", 0),
        "total_memories": result.get("memory_count", 0),
        "scanned_at": result.get("scanned_at", ""),
        "issues": adapted_issues,
        "breakdown": _build_breakdown(issues),
    }
    return adapted


router = APIRouter()


@router.post("")
def full_scan():
    """Run a full health scan and return results adapted to frontend format."""
    try:
        result = run_full_scan()
        return _adapt_result(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health scan failed: {e}")


@router.get("/summary")
def summary():
    """Get health scan summary.

    If no scan has been run yet, runs one automatically.
    """
    try:
        result = get_latest_scan()
        if not result:
            result = run_full_scan()
        return get_scan_summary(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health summary failed: {e}")


@router.get("/last")
def last_scan():
    """Get the most recent scan result, adapted to frontend format."""
    try:
        result = get_latest_scan()
        if not result:
            result = run_full_scan()
        return _adapt_result(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get last scan: {e}")