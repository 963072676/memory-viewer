"""RAG-Powered Search API router (F-53)."""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.services.rag_service import rag_search, rag_search_stream

router = APIRouter()


class RagSearchReq(BaseModel):
    query: str
    top_k: int = 10


@router.post("/rag")
def rag_search_endpoint(req: RagSearchReq):
    """Perform RAG-powered search.

    AC-F53-1: Pipeline query → semantic search → synthesis with citations.
    AC-F53-2: Response includes answer, sources, confidence, follow_up_questions.
    """
    if not req.query.strip():
        return {"query": req.query, "answer": "Please enter a search query.", "sources": [], "confidence": 0, "follow_up_questions": []}
    result = rag_search(req.query, req.top_k)
    return result


@router.get("/rag/stream")
async def rag_stream(q: str = Query(...), top_k: int = Query(default=10)):
    """SSE streaming RAG search.

    AC-F53-3: SSE streaming support.
    """
    return StreamingResponse(
        rag_search_stream(q, top_k),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
