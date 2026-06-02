"""Diagnostics API router (F-28)."""

from fastapi import APIRouter

from app.services.diagnostics import run_diagnostics

router = APIRouter()


@router.get("")
def get_diagnostics():
    """Run memory system diagnostics and return results."""
    return run_diagnostics()
