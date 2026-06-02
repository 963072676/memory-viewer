"""Plugin system API router (F-38)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.plugin_manager import (
    get_all_plugins,
    get_plugin,
    enable_plugin,
    disable_plugin,
    get_execution_log,
    discover_plugins,
)

router = APIRouter()


class PluginToggleRequest(BaseModel):
    enabled: bool


@router.get("")
def list_plugins():
    """List all installed plugins with status."""
    plugins = get_all_plugins()
    return {
        "plugins": plugins,
        "total": len(plugins),
    }


@router.get("/{name}")
def get_plugin_detail(name: str):
    """Get detailed info about a specific plugin."""
    plugin = get_plugin(name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {name}")
    return plugin.to_dict()


@router.post("/{name}/enable")
def api_enable_plugin(name: str):
    """Enable a plugin."""
    if not enable_plugin(name):
        raise HTTPException(status_code=404, detail=f"Plugin not found: {name}")
    return {"success": True, "name": name, "enabled": True}


@router.post("/{name}/disable")
def api_disable_plugin(name: str):
    """Disable a plugin."""
    if not disable_plugin(name):
        raise HTTPException(status_code=404, detail=f"Plugin not found: {name}")
    return {"success": True, "name": name, "enabled": False}


@router.get("/logs/recent")
def plugin_logs(limit: int = 50):
    """Get recent plugin execution logs."""
    return {
        "logs": get_execution_log(limit=limit),
    }
