"""Natural Language Query API router (F-39)."""

from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.services.nlq_service import process_nlq
from app.services.search import search_memories

router = APIRouter()


class NLQRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural language query")


class NLQResponse(BaseModel):
    question: str
    parsed_conditions: dict
    explanation: str
    parse_method: str
    confidence: float
    results: dict


@router.post("/search/nlq", response_model=NLQResponse)
def nlq_search(req: NLQRequest):
    """Natural language query endpoint.
    
    Converts natural language to structured query, executes it, and returns results.
    
    AC-F39-1: Input Chinese/English NL query returns correct filtered results.
    AC-F39-2: Displays parsed structured query conditions.
    AC-F39-4: When LLM not configured, NLQ still works with pattern matching.
    AC-F39-5: Query response time <5s.
    """
    # Parse natural language to conditions
    nlq_result = process_nlq(req.question)
    conditions = nlq_result.get("conditions", {})

    # Execute search with parsed conditions
    type_filter = conditions.get("type")
    if isinstance(type_filter, str):
        type_filter = [type_filter]

    results = search_memories(
        query=conditions.get("query", ""),
        type_filter=type_filter,
        strength_min=conditions.get("strength_min"),
        strength_max=conditions.get("strength_max"),
        date_from=conditions.get("date_from"),
        date_to=conditions.get("date_to"),
    )

    # Sort results if specified
    sort_by = conditions.get("sort_by")
    if sort_by and results.get("results"):
        sort_map = {
            "newest": lambda r: r.get("updatedAt", ""),
            "oldest": lambda r: r.get("updatedAt", ""),
            "strongest": lambda r: r.get("strength", 0),
            "weakest": lambda r: r.get("strength", 0),
        }
        reverse = sort_by in ("newest", "strongest")
        if sort_by in sort_map:
            results["results"].sort(key=sort_map[sort_by], reverse=reverse)

    return NLQResponse(
        question=req.question,
        parsed_conditions=conditions,
        explanation=nlq_result.get("explanation", ""),
        parse_method=nlq_result.get("parse_method", "pattern"),
        confidence=nlq_result.get("confidence", 0.5),
        results=results,
    )
