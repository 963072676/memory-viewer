"""Plugin ecosystem API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.plugin_manager import (
    disable_plugin,
    enable_plugin,
    get_all_plugins,
    get_capability_manifest,
    get_execution_log,
    get_plugin,
)

router = APIRouter()


@router.get("")
def list_plugins():
    """List installed plugins with manifest metadata."""
    plugins = get_all_plugins()
    return {
        "plugins": plugins,
        "total": len(plugins),
    }


@router.get("/manifest")
def plugin_capability_manifest():
    """Return aggregate plugin capability manifest."""
    return get_capability_manifest()


@router.get("/logs/recent")
def plugin_logs(limit: int = Query(default=50, ge=1, le=200)):
    """Return recent plugin execution log entries."""
    return {
        "logs": get_execution_log(limit=limit),
    }


@router.get("/{name}")
def get_plugin_detail(name: str):
    """Return one plugin manifest."""
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
