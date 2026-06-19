"""Graph API router (F-18)."""

from fastapi import APIRouter

from app.services.graph import build_graph

router = APIRouter()


@router.get("/graph")
async def get_graph():
    """Get memory relationship graph based on concept co-occurrence."""
    return await build_graph(provider="agentmemory")
