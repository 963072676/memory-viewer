"""Smart Collections router (F-64).

Endpoints:
  GET    /                -> list all collections
  POST   /                -> create collection
  PUT    /{id}            -> update collection
  DELETE /{id}            -> delete collection
  GET    /{id}/memories   -> evaluate and return matching memories
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.services.collections_service import (
    get_all_collections,
    get_collection,
    create_collection,
    update_collection,
    delete_collection,
    evaluate_collection,
)

router = APIRouter()


class CreateCollectionReq(BaseModel):
    name: str = "Untitled"
    description: str = ""
    query: dict = {}
    icon: str = "📁"
    color: str = "#6366f1"


class UpdateCollectionReq(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[dict] = None
    icon: Optional[str] = None
    color: Optional[str] = None


@router.get("")
def list_collections():
    """List all collections."""
    try:
        collections = get_all_collections()
        return {"collections": collections, "total": len(collections)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {e}")


@router.post("")
def create(req: CreateCollectionReq):
    """Create a new collection."""
    try:
        collection = create_collection(req.model_dump())
        return {"success": True, "collection": collection}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create collection: {e}")


@router.get("/{collection_id}")
def get_one(collection_id: str):
    """Get a single collection by ID."""
    collection = get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
    return {"collection": collection}


@router.put("/{collection_id}")
def update(collection_id: str, req: UpdateCollectionReq):
    """Update an existing collection."""
    try:
        updates = {k: v for k, v in req.model_dump().items() if v is not None}
        result = update_collection(collection_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        return {"success": True, "collection": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update collection: {e}")


@router.delete("/{collection_id}")
def delete(collection_id: str):
    """Delete a collection."""
    try:
        if not delete_collection(collection_id):
            raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete collection: {e}")


@router.get("/{collection_id}/memories")
def get_memories(collection_id: str):
    """Evaluate collection query and return matching memories."""
    try:
        collection = get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        memories = evaluate_collection(collection_id)
        return {"memories": memories, "total": len(memories), "collection_id": collection_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate collection: {e}")
