"""Memory Links router (F-65).

Endpoints:
  GET    /       -> list all links (with filters)
  POST   /       -> create link
  DELETE /{id}   -> remove link
  GET    /graph  -> graph for visualization
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.services.linking_service import (
    get_links,
    get_link,
    create_link,
    delete_link,
    get_graph,
    VALID_RELATION_TYPES,
)

router = APIRouter()


class CreateLinkReq(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = "related_to"
    label: str = ""


@router.get("")
def list_links(
    source_id: Optional[str] = Query(None, description="Filter by source memory ID"),
    target_id: Optional[str] = Query(None, description="Filter by target memory ID"),
    type: Optional[str] = Query(None, alias="type", description="Filter by relation type"),
):
    """List all links with optional filters."""
    try:
        links = get_links(source_id=source_id, target_id=target_id, relation_type=type)
        return {"links": links, "total": len(links)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list links: {e}")


@router.post("")
def create(req: CreateLinkReq):
    """Create a new memory link."""
    try:
        if req.source_id == req.target_id:
            raise HTTPException(status_code=400, detail="Cannot link a memory to itself")
        if req.relation_type not in VALID_RELATION_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid relation_type: {req.relation_type}. Must be one of: {VALID_RELATION_TYPES}",
            )
        link = create_link(req.model_dump())
        return {"success": True, "link": link}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create link: {e}")


@router.delete("/{link_id}")
def delete(link_id: str):
    """Remove a memory link."""
    try:
        if not delete_link(link_id):
            raise HTTPException(status_code=404, detail=f"Link {link_id} not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete link: {e}")


@router.get("/graph")
def graph():
    """Get graph structure for visualization.

    Returns nodes and edges suitable for rendering in a graph view.
    """
    try:
        data = get_graph()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build graph: {e}")
