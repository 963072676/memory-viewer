"""Feishu summary API router (F-25)."""

from fastapi import APIRouter

from app.services.feishu_summary import generate_summary, send_summary_to_feishu

router = APIRouter()


@router.get("/summary")
def api_get_summary():
    """Get memory summary."""
    return generate_summary()


@router.post("/summary/send-to-feishu")
def api_send_summary():
    """Send memory summary to Feishu webhook."""
    result = send_summary_to_feishu()
    return result
