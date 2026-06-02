"""Semantic search API router (F-33)."""

from fastapi import APIRouter, Query

from app.services.semantic_search import semantic_search, invalidate_index
from app.services.agentmemory import quick_search

router = APIRouter()


@router.get("")
def search_semantic(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=50),
    mode: str = Query(default="semantic", pattern="^(semantic|keyword)$"),
):
    """Semantic search using TF-IDF cosine similarity.

    Falls back to keyword search if no semantic results found.
    Returns results with similarity scores as percentages.
    """
    if mode == "keyword":
        # Use keyword-based quick search
        results = quick_search(query=q, limit=limit)
        return {
            "query": q,
            "mode": "keyword",
            "results": [
                {**r, "similarity": 100.0, "match_type": "keyword"}
                for r in results
            ],
        }

    # Semantic search
    results = semantic_search(query=q, limit=limit)

    if not results:
        # Fallback to keyword search
        kw_results = quick_search(query=q, limit=limit)
        return {
            "query": q,
            "mode": "keyword_fallback",
            "results": [
                {**r, "similarity": 100.0, "match_type": "keyword"}
                for r in kw_results
            ],
        }

    return {
        "query": q,
        "mode": "semantic",
        "results": results,
    }


@router.post("/reindex")
def reindex():
    """Force rebuild the semantic search index."""
    invalidate_index()
    return {"success": True, "message": "Semantic index invalidated, will rebuild on next search."}
