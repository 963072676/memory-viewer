"""Favorites router (F-63).

Endpoints:
  PUT /{memory_id}/favorite -> toggle favorite
  GET /favorites            -> list favorited memory IDs
"""

from fastapi import APIRouter, HTTPException

from app.services.favorites_service import (
    toggle_favorite,
    get_favorites,
    is_favorited,
)

router = APIRouter()


@router.put("/{memory_id}/favorite")
def toggle(memory_id: str):
    """Toggle favorite status for a memory."""
    try:
        favorited = toggle_favorite(memory_id)
        return {"memory_id": memory_id, "favorited": favorited}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {e}")


@router.get("/favorites")
def list_favorites():
    """List all favorited memory IDs."""
    try:
        favorites = get_favorites()
        return {"favorites": favorites, "count": len(favorites)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list favorites: {e}")
