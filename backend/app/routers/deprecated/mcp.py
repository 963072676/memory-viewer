"""MCP Server (F-27) — JSON-RPC 2.0 over HTTP."""

import os
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services import agentmemory as am_service
from app.services.search import search_memories

router = APIRouter()

# F-35: MCP API Key authentication
_MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

def _check_mcp_auth(request: Request) -> Optional[JSONResponse]:
    """Check MCP API Key authentication. Returns JSON-RPC error response if auth fails."""
    if not _MCP_API_KEY:
        return None  # No key configured = no auth required
    
    provided_key = request.headers.get("X-API-Key", "")
    if provided_key != _MCP_API_KEY:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32001,
                    "message": "Authentication failed: invalid or missing API key",
                },
            },
            status_code=401,
        )
    return None

# Method dispatch table
_METHODS = {}


def _method(name: str):
    def decorator(func):
        _METHODS[name] = func
        return func
    return decorator


@_method("memory.list")
def _memory_list(params: dict) -> Any:
    """List all memories."""
    limit = params.get("limit", 50)
    offset = params.get("offset", 0)
    type_filter = params.get("type")
    result = am_service.get_paginated_memories(
        limit=limit, offset=offset, type_filter=type_filter,
    )
    return result


@_method("memory.get")
def _memory_get(params: dict) -> Any:
    """Get a single memory by ID."""
    memory_id = params.get("id", "")
    if not memory_id:
        return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
    memory = am_service.get_memory_by_id(memory_id)
    if not memory:
        return {"error": {"code": -32000, "message": f"Memory not found: {memory_id}"}}
    return {"memory": memory}


@_method("memory.search")
def _memory_search(params: dict) -> Any:
    """Search memories by query."""
    query = params.get("query", "")
    if not query:
        return {"error": {"code": -32602, "message": "Missing 'query' parameter"}}
    limit = params.get("limit", 10)
    result = search_memories(query, limit=limit)
    return {"results": result.get("results", []), "total": result.get("total", 0)}


@_method("memory.create")
def _memory_create(params: dict) -> Any:
    """Create a new memory."""
    title = params.get("title", "")
    content = params.get("content", "")
    if not title or not content:
        return {"error": {"code": -32602, "message": "Missing 'title' or 'content'"}}
    memory = am_service.create_memory(
        title=title,
        content=content,
        type_=params.get("type", "pattern"),
        concepts=params.get("concepts"),
        strength=params.get("strength", 5),
    )
    return {"memory": memory}


@_method("memory.update")
def _memory_update(params: dict) -> Any:
    """Update an existing memory."""
    memory_id = params.get("id", "")
    if not memory_id:
        return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
    memory = am_service.update_memory(
        memory_id=memory_id,
        content=params.get("content"),
        concepts=params.get("concepts"),
        strength=params.get("strength"),
        tags=params.get("tags"),
    )
    if not memory:
        return {"error": {"code": -32000, "message": f"Memory not found: {memory_id}"}}
    return {"memory": memory}


@_method("memory.delete")
def _memory_delete(params: dict) -> Any:
    """Delete a memory by ID."""
    memory_id = params.get("id", "")
    if not memory_id:
        return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
    deleted = am_service.delete_memory(memory_id)
    return {"deleted": deleted}


def _handle_jsonrpc(body: dict) -> dict:
    """Process a single JSON-RPC 2.0 request."""
    jsonrpc = body.get("jsonrpc")
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    if jsonrpc != "2.0":
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request: jsonrpc must be '2.0'"}}

    if not method:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request: missing method"}}

    handler = _METHODS.get(method)
    if not handler:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    try:
        result = handler(params if isinstance(params, dict) else {})
        if isinstance(result, dict) and "error" in result:
            return {"jsonrpc": "2.0", "id": req_id, "error": result["error"]}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    except Exception as e:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}


@router.post("/jsonrpc")
async def api_jsonrpc(request: Request):
    """Handle JSON-RPC 2.0 requests (single or batch)."""
    # F-35: Check MCP API Key authentication
    auth_error = _check_mcp_auth(request)
    if auth_error:
        return auth_error

    body = await request.json()

    # Batch request
    if isinstance(body, list):
        responses = [_handle_jsonrpc(item) for item in body]
        return JSONResponse(content=responses)

    # Single request
    response = _handle_jsonrpc(body)
    return JSONResponse(content=response)
