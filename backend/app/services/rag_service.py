"""RAG-Powered Search service (F-53) — Retrieval-Augmented Generation for memory search.

Pipeline: query → semantic search (top-K=10) → LLM synthesis with citations.
Response: answer, sources, confidence, follow_up_questions.
SSE streaming support.
"""

import json
import logging
import re
from typing import AsyncGenerator, Optional

from app.services.semantic_search import semantic_search
from app.services.agentmemory import get_all_memories

logger = logging.getLogger(__name__)


def _build_context_block(memories: list[dict]) -> str:
    """Build context block from retrieved memories for LLM prompt."""
    blocks = []
    for i, m in enumerate(memories, 1):
        title = m.get("title", "Untitled")
        content = m.get("content", "")[:500]
        tags = ", ".join(m.get("tags", []))
        blocks.append(f"[{i}] {title}\nTags: {tags}\nContent: {content}")
    return "\n\n".join(blocks)


def _generate_answer(query: str, context: str, sources: list[dict]) -> dict:
    """Generate an answer from query and context.

    In production this would call an LLM API.
    For now, we synthesize a structured answer from the search results.
    """
    if not sources:
        return {
            "answer": f"No relevant memories found for: '{query}'. Try rephrasing your query or broadening your search.",
            "confidence": 0.0,
            "follow_up_questions": [
                "Would you like to search with different keywords?",
                "Should I create a new memory for this topic?",
            ],
        }

    # Build answer from top results
    answer_parts = [f"Based on your memory collection, here's what I found about \"{query}\":\n"]

    for i, src in enumerate(sources[:5], 1):
        title = src.get("title", "Untitled")
        snippet = src.get("snippet", "")
        similarity = src.get("similarity", 0)
        answer_parts.append(f"**[{i}] {title}** (relevance: {similarity}%)\n{snippet}\n")

    # Calculate confidence from top similarities
    top_sim = sources[0].get("similarity", 0) if sources else 0
    avg_sim = sum(s.get("similarity", 0) for s in sources[:5]) / min(len(sources), 5) if sources else 0
    confidence = min(0.95, (top_sim * 0.6 + avg_sim * 0.4) / 100)

    # Generate follow-up questions based on found topics
    follow_ups = []
    tags_seen = set()
    for src in sources[:3]:
        for tag in src.get("tags", []):
            if tag not in tags_seen:
                tags_seen.add(tag)
                follow_ups.append(f"Tell me more about '{tag}'")
    if len(sources) > 3:
        follow_ups.append("Show me more related memories")
    follow_ups = follow_ups[:4]

    return {
        "answer": "\n".join(answer_parts),
        "confidence": round(confidence, 2),
        "follow_up_questions": follow_ups,
    }


def rag_search(query: str, top_k: int = 10) -> dict:
    """Perform RAG-powered search: semantic retrieval + synthesis.

    AC-F53-1: Pipeline query → semantic search → synthesis with citations.
    AC-F53-2: Response includes answer, sources, confidence, follow_up_questions.
    """
    # Step 1: Semantic retrieval
    raw_results = semantic_search(query, limit=top_k)

    # Step 2: Enrich with full content
    memory_ids = {r["id"] for r in raw_results}
    all_memories = get_all_memories()
    memory_map = {m.get("id"): m for m in all_memories}

    sources = []
    for r in raw_results:
        full = memory_map.get(r["id"], {})
        sources.append({
            "id": r["id"],
            "title": r.get("title", ""),
            "snippet": full.get("content", r.get("snippet", ""))[:300],
            "type": r.get("type", ""),
            "tags": r.get("tags", []),
            "similarity": r.get("similarity", 0),
        })

    # Step 3: Build context and generate answer
    context = _build_context_block([memory_map.get(s["id"], {}) for s in sources])
    result = _generate_answer(query, context, sources)

    return {
        "query": query,
        "answer": result["answer"],
        "sources": sources,
        "confidence": result["confidence"],
        "follow_up_questions": result["follow_up_questions"],
        "total_sources": len(sources),
    }


async def rag_search_stream(query: str, top_k: int = 10) -> AsyncGenerator[str, None]:
    """Streaming RAG search via SSE.

    AC-F53-3: SSE streaming support.
    """
    # Step 1: Emit progress
    yield json.dumps({"type": "progress", "message": "Searching memories..."}) + "\n"

    raw_results = semantic_search(query, limit=top_k)

    yield json.dumps({"type": "progress", "message": f"Found {len(raw_results)} relevant memories. Synthesizing..."}) + "\n"

    # Step 2: Enrich
    memory_ids = {r["id"] for r in raw_results}
    all_memories = get_all_memories()
    memory_map = {m.get("id"): m for m in all_memories}

    sources = []
    for r in raw_results:
        full = memory_map.get(r["id"], {})
        sources.append({
            "id": r["id"],
            "title": r.get("title", ""),
            "snippet": full.get("content", r.get("snippet", ""))[:300],
            "type": r.get("type", ""),
            "tags": r.get("tags", []),
            "similarity": r.get("similarity", 0),
        })

    # Step 3: Stream sources
    for src in sources:
        yield json.dumps({"type": "source", "data": src}) + "\n"

    # Step 4: Generate and stream answer
    context = _build_context_block([memory_map.get(s["id"], {}) for s in sources])
    result = _generate_answer(query, context, sources)

    # Stream answer in chunks
    answer = result["answer"]
    chunk_size = 50
    for i in range(0, len(answer), chunk_size):
        chunk = answer[i:i + chunk_size]
        yield json.dumps({"type": "chunk", "data": chunk}) + "\n"

    # Step 5: Final metadata
    yield json.dumps({
        "type": "done",
        "confidence": result["confidence"],
        "follow_up_questions": result["follow_up_questions"],
        "total_sources": len(sources),
    }) + "\n"
