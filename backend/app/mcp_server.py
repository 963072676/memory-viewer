"""MCP Server stdio transport (F-27).

This module implements the MCP (Model Context Protocol) stdio transport,
allowing Memory Viewer to act as an MCP server accessed via stdin/stdout.

Usage:
    python -m app.mcp_server
"""

import json
import sys
from typing import Any, Optional

# MCP protocol version
MCP_PROTOCOL_VERSION = "2024-11-05"

# Import existing MCP router methods
from app.services import agentmemory as am_service
from app.services.search import search_memories


def _check_api_key(api_key: Optional[str]) -> bool:
    """Validate API key if required."""
    import os
    required_key = os.environ.get("MCP_API_KEY", "")
    if not required_key:
        return True  # No auth required
    return api_key == required_key


def _parse_header(line: str) -> tuple[Optional[str], Optional[str]]:
    """Parse a single MCP protocol header line.
    
    Returns: (key, value) or (None, None) if not a header line.
    """
    line = line.strip()
    if not line or ":" not in line:
        return None, None
    key, value = line.split(":", 1)
    return key.strip().lower(), value.strip()


def _read_jsonrpc_message() -> Optional[dict]:
    """Read and parse a JSON-RPC 2.0 message from stdin.
    
    Handles:
    - Single JSON-RPC request
    - Batch requests (array)
    - MCP protocol headers before JSON body
    
    Returns None on EOF.
    """
    api_key: Optional[str] = None
    
    # Read lines until we get a blank line (end of headers) or JSON
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None  # EOF
        
        line = line.rstrip("\n\r")
        
        # Blank line signals end of headers, next thing is JSON
        if not line:
            break
        
        # Parse header
        key, value = _parse_header(line)
        if key:
            headers[key] = value
    
    # Read the JSON body
    json_line = sys.stdin.readline()
    if not json_line:
        return None
    
    try:
        body = json.loads(json_line.strip())
    except json.JSONDecodeError as e:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": f"Invalid JSON: {e}"},
        }
    
    # Store API key from headers for auth
    if "x-api-key" in headers:
        api_key = headers["x-api-key"]
    body["_api_key"] = api_key
    
    return body


def _build_response(req_id: Any, result: Any = None, error: dict = None) -> dict:
    """Build a JSON-RPC 2.0 response."""
    resp = {"jsonrpc": "2.0", "id": req_id}
    if error:
        resp["error"] = error
    else:
        resp["result"] = result
    return resp


def _handle_initialize(params: dict) -> dict:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "memory-viewer",
            "version": "2.0.0",
        },
    }


def _handle_tools_list() -> dict:
    """Handle MCP tools/list request - return tool manifest."""
    return {
        "tools": [
            {
                "name": "memory_list",
                "description": "List all memories with pagination and filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max results (default 50)"},
                        "offset": {"type": "integer", "description": "Skip count (default 0)"},
                        "type": {"type": "string", "description": "Filter by memory type"},
                    },
                },
            },
            {
                "name": "memory_get",
                "description": "Get a single memory by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Memory ID"},
                    },
                    "required": ["id"],
                },
            },
            {
                "name": "memory_search",
                "description": "Search memories by query string",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Max results (default 10)"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "memory_create",
                "description": "Create a new memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Memory title"},
                        "content": {"type": "string", "description": "Memory content"},
                        "type": {"type": "string", "description": "Memory type (default: pattern)"},
                        "concepts": {"type": "array", "items": {"type": "string"}, "description": "Concept tags"},
                        "strength": {"type": "integer", "description": "Strength 1-10 (default 5)"},
                    },
                    "required": ["title", "content"],
                },
            },
            {
                "name": "memory_update",
                "description": "Update an existing memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Memory ID"},
                        "content": {"type": "string", "description": "New content"},
                        "concepts": {"type": "array", "items": {"type": "string"}, "description": "Concept tags"},
                        "strength": {"type": "integer", "description": "Strength 1-10"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
                    },
                    "required": ["id"],
                },
            },
            {
                "name": "memory_delete",
                "description": "Delete a memory by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Memory ID"},
                    },
                    "required": ["id"],
                },
            },
            {
                "name": "health_check",
                "description": "Health check for the MCP server",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]
    }


def _handle_tools_call(name: str, arguments: dict, api_key: Optional[str]) -> dict:
    """Handle MCP tools/call request - dispatch to appropriate method."""
    import os
    
    # Check auth
    required_key = os.environ.get("MCP_API_KEY", "")
    if required_key and api_key != required_key:
        return {"error": {"code": -32001, "message": "Authentication failed"}}
    
    # Dispatch
    if name == "memory_list":
        limit = arguments.get("limit", 50)
        offset = arguments.get("offset", 0)
        type_filter = arguments.get("type")
        result = am_service.get_paginated_memories(limit=limit, offset=offset, type_filter=type_filter)
        return result
    
    elif name == "memory_get":
        memory_id = arguments.get("id", "")
        if not memory_id:
            return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
        memory = am_service.get_memory_by_id(memory_id)
        if not memory:
            return {"error": {"code": -32000, "message": f"Memory not found: {memory_id}"}}
        return {"memory": memory}
    
    elif name == "memory_search":
        query = arguments.get("query", "")
        if not query:
            return {"error": {"code": -32602, "message": "Missing 'query' parameter"}}
        limit = arguments.get("limit", 10)
        result = search_memories(query, limit=limit)
        return {"results": result.get("results", []), "total": result.get("total", 0)}
    
    elif name == "memory_create":
        title = arguments.get("title", "")
        content = arguments.get("content", "")
        if not title or not content:
            return {"error": {"code": -32602, "message": "Missing 'title' or 'content'"}}
        memory = am_service.create_memory(
            title=title,
            content=content,
            type_=arguments.get("type", "pattern"),
            concepts=arguments.get("concepts"),
            strength=arguments.get("strength", 5),
        )
        return {"memory": memory}
    
    elif name == "memory_update":
        memory_id = arguments.get("id", "")
        if not memory_id:
            return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
        memory = am_service.update_memory(
            memory_id=memory_id,
            content=arguments.get("content"),
            concepts=arguments.get("concepts"),
            strength=arguments.get("strength"),
            tags=arguments.get("tags"),
        )
        if not memory:
            return {"error": {"code": -32000, "message": f"Memory not found: {memory_id}"}}
        return {"memory": memory}
    
    elif name == "memory_delete":
        memory_id = arguments.get("id", "")
        if not memory_id:
            return {"error": {"code": -32602, "message": "Missing 'id' parameter"}}
        deleted = am_service.delete_memory(memory_id)
        return {"deleted": deleted}
    
    elif name == "health_check":
        return {"status": "ok", "server": "memory-viewer", "version": "2.0.0"}
    
    else:
        return {"error": {"code": -32601, "message": f"Unknown tool: {name}"}}


def _handle_request(body: dict) -> dict:
    """Handle a single JSON-RPC 2.0 request."""
    jsonrpc = body.get("jsonrpc")
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")
    api_key = body.pop("_api_key", None) if isinstance(body, dict) else None
    
    if jsonrpc != "2.0":
        return _build_response(req_id, error={"code": -32600, "message": "Invalid Request: jsonrpc must be '2.0'"})
    
    if not method:
        return _build_response(req_id, error={"code": -32600, "message": "Invalid Request: missing method"})
    
    # MCP protocol methods
    if method == "initialize":
        result = _handle_initialize(params)
        return _build_response(req_id, result=result)
    
    elif method == "tools/list":
        result = _handle_tools_list()
        return _build_response(req_id, result=result)
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = _handle_tools_call(tool_name, arguments, api_key)
        if isinstance(result, dict) and "error" in result:
            return _build_response(req_id, error=result["error"])
        return _build_response(req_id, result=result)
    
    elif method == "health.check":
        result = {"status": "ok", "server": "memory-viewer", "version": "2.0.0"}
        return _build_response(req_id, result=result)
    
    # Backward compatibility: direct memory methods
    elif method == "memory.list":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        type_filter = params.get("type")
        result = am_service.get_paginated_memories(limit=limit, offset=offset, type_filter=type_filter)
        return _build_response(req_id, result=result)
    
    elif method == "memory.get":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        memory_id = params.get("id", "")
        if not memory_id:
            return _build_response(req_id, error={"code": -32602, "message": "Missing 'id' parameter"})
        memory = am_service.get_memory_by_id(memory_id)
        if not memory:
            return _build_response(req_id, error={"code": -32000, "message": f"Memory not found: {memory_id}"})
        return _build_response(req_id, result={"memory": memory})
    
    elif method == "memory.search":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        query = params.get("query", "")
        if not query:
            return _build_response(req_id, error={"code": -32602, "message": "Missing 'query' parameter"})
        limit = params.get("limit", 10)
        result = search_memories(query, limit=limit)
        return _build_response(req_id, result={"results": result.get("results", []), "total": result.get("total", 0)})
    
    elif method == "memory.create":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        title = params.get("title", "")
        content = params.get("content", "")
        if not title or not content:
            return _build_response(req_id, error={"code": -32602, "message": "Missing 'title' or 'content'"})
        memory = am_service.create_memory(
            title=title,
            content=content,
            type_=params.get("type", "pattern"),
            concepts=params.get("concepts"),
            strength=params.get("strength", 5),
        )
        return _build_response(req_id, result={"memory": memory})
    
    elif method == "memory.update":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        memory_id = params.get("id", "")
        if not memory_id:
            return _build_response(req_id, error={"code": -32602, "message": "Missing 'id' parameter"})
        memory = am_service.update_memory(
            memory_id=memory_id,
            content=params.get("content"),
            concepts=params.get("concepts"),
            strength=params.get("strength"),
            tags=params.get("tags"),
        )
        if not memory:
            return _build_response(req_id, error={"code": -32000, "message": f"Memory not found: {memory_id}"})
        return _build_response(req_id, result={"memory": memory})
    
    elif method == "memory.delete":
        if not _check_api_key(api_key):
            return _build_response(req_id, error={"code": -32001, "message": "Authentication failed"})
        memory_id = params.get("id", "")
        if not memory_id:
            return _build_response(req_id, error={"code": -32602, "message": "Missing 'id' parameter"})
        deleted = am_service.delete_memory(memory_id)
        return _build_response(req_id, result={"deleted": deleted})
    
    else:
        return _build_response(req_id, error={"code": -32601, "message": f"Method not found: {method}"})


def run_stdio_server():
    """Main stdio server loop.
    
    Reads JSON-RPC requests from stdin and writes responses to stdout.
    This is a blocking call that runs until EOF.
    """
    while True:
        try:
            body = _read_jsonrpc_message()
            if body is None:
                break  # EOF
            
            # Handle batch requests
            if isinstance(body, list):
                responses = [_handle_request(item) for item in body]
                for resp in responses:
                    sys.stdout.write(json.dumps(resp) + "\n")
            else:
                response = _handle_request(body)
                sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        
        except Exception as e:
            # Write error response
            error_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)},
            }
            try:
                sys.stdout.write(json.dumps(error_resp) + "\n")
                sys.stdout.flush()
            except Exception:
                pass


if __name__ == "__main__":
    run_stdio_server()