"""Anomaly Detection & Alerts API router (F-43)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.anomaly_service import (
    run_detection,
    get_anomalies,
    get_health_score,
    get_thresholds,
    update_threshold,
)

router = APIRouter()


@router.get("")
def list_anomalies(
    limit: int = Query(default=50, ge=1, le=200),
    severity: Optional[str] = Query(default=None, pattern="^(info|warning|critical)$"),
    anomaly_type: Optional[str] = Query(default=None),
    resolved: Optional[bool] = Query(default=None),
):
    """Get detected anomaly list.
    
    AC-F43-5: Anomaly history is traceable (30-day retention).
    """
    anomalies = get_anomalies(
        limit=limit,
        severity=severity,
        anomaly_type=anomaly_type,
        resolved=resolved,
    )
    return {"anomalies": anomalies, "total": len(anomalies)}


@router.get("/health")
def health_score():
    """Get overall system health score (0-100).
    
    AC-F43-2: Health score correctly reflects system state.
    AC-F43-6: Dashboard displays current health score.
    """
    return get_health_score()


@router.post("/check")
def trigger_check():
    """Manually trigger anomaly detection.
    
    AC-F43-1: Memory count sudden change triggers anomaly.
    AC-F43-3: Anomalies trigger webhook alerts.
    """
    new_anomalies = run_detection()

    # Send webhook notifications for critical anomalies
    for anomaly in new_anomalies:
        if anomaly.get("severity") in ("warning", "critical"):
            try:
                from app.services.notification import send_notification_sync
                send_notification_sync(
                    operation="anomaly",
                    title=anomaly.get("title", "Unknown anomaly"),
                    memory_id=anomaly.get("id", ""),
                    details=anomaly.get("description", ""),
                )
            except Exception as e:
                # Non-blocking: don't fail the check if notification fails
                pass

    return {
        "success": True,
        "new_anomalies": len(new_anomalies),
        "anomalies": new_anomalies,
    }


@router.get("/thresholds")
def get_config():
    """Get current anomaly detection thresholds.
    
    AC-F43-4: Alert thresholds are configurable.
    """
    return {"thresholds": get_thresholds()}


class ThresholdUpdate(BaseModel):
    key: str
    value: float


@router.put("/thresholds")
def update_config(req: ThresholdUpdate):
    """Update an anomaly detection threshold.
    
    AC-F43-4: Alert thresholds are configurable.
    """
    success = update_threshold(req.key, req.value)
    if not success:
        raise HTTPException(status_code=404, detail=f"Threshold '{req.key}' not found")
    return {"success": True, "key": req.key, "value": req.value}
