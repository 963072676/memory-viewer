"""Multi-instance management API router (F-31, F-40)."""

import json
import os
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

_INSTANCES_FILE = Path(__file__).resolve().parent.parent.parent / "instances.json"

PROXY_TIMEOUT = 5.0


def _load_instances() -> list[dict]:
    if _INSTANCES_FILE.exists():
        with open(_INSTANCES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("instances", [])
    return []


def _find_instance(name: str) -> Optional[dict]:
    """Find instance by name (case-insensitive)."""
    for inst in _load_instances():
        if inst.get("name", "").lower() == name.lower() or inst.get("id", "").lower() == name.lower():
            return inst
    return None


@router.get("")
def get_instances():
    """List configured instances."""
    instances = _load_instances()
    return {"instances": instances}


@router.get("/{name}/proxy")
def proxy_instance_request(
    name: str,
    endpoint: str = Query(default="health", description="Target endpoint: 'health' or 'agentmemory'"),
):
    """Proxy a request to a target instance's API.

    F-40: Uses httpx to forward requests to /api/health or /api/agentmemory.
    Timeout 5s. Marks status=offline on failure.
    """
    inst = _find_instance(name)
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instance not found: {name}")

    base_url = inst.get("url", "").rstrip("/")
    if not base_url:
        raise HTTPException(status_code=400, detail="Instance URL is empty")

    # Validate endpoint
    allowed = {"health", "agentmemory"}
    if endpoint not in allowed:
        raise HTTPException(status_code=400, detail=f"endpoint must be one of: {allowed}")

    target_url = f"{base_url}/api/{endpoint}"

    try:
        with httpx.Client(timeout=PROXY_TIMEOUT) as client:
            resp = client.get(target_url)
            data = resp.json()
            return {
                "instance": inst.get("name", name),
                "endpoint": endpoint,
                "status": "online",
                "data": data,
            }
    except httpx.TimeoutException:
        return {
            "instance": inst.get("name", name),
            "endpoint": endpoint,
            "status": "offline",
            "error": "Connection timed out",
        }
    except httpx.ConnectError:
        return {
            "instance": inst.get("name", name),
            "endpoint": endpoint,
            "status": "offline",
            "error": "Connection refused",
        }
    except Exception as e:
        return {
            "instance": inst.get("name", name),
            "endpoint": endpoint,
            "status": "offline",
            "error": str(e),
        }
