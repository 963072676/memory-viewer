"""Tests for plugin capability manifest API."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import plugin_manager
from app.routers import plugins as plugins_router


def _client() -> TestClient:
    plugin_manager._plugins.clear()
    plugin_manager._initialized = False
    app = FastAPI()
    app.include_router(plugins_router.router, prefix="/api/plugins")
    return TestClient(app)


def test_plugin_manifest_lists_capabilities():
    client = _client()

    resp = client.get("/api/plugins/manifest")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    capability = next(item for item in data["capabilities"] if item["name"] == "translation-awareness")
    assert capability["category"] == "memory_enrichment"
    assert capability["plugins"] == ["auto_translate"]
    assert "on_memory_create" in capability["hooks"]
    assert "on_memory_update" in capability["hooks"]
    assert "on_memory_delete" in data["supportedHooks"]


def test_plugins_api_exposes_manifest_metadata_and_logs_route():
    client = _client()

    plugins_resp = client.get("/api/plugins")
    logs_resp = client.get("/api/plugins/logs/recent?limit=5")

    assert plugins_resp.status_code == 200
    plugins = plugins_resp.json()["plugins"]
    auto_translate = next(item for item in plugins if item["name"] == "auto_translate")
    assert auto_translate["capabilities"][0]["name"] == "translation-awareness"
    assert auto_translate["permissions"] == ["memory:read", "memory:tag:suggest"]
    assert auto_translate["entryPoints"]["backend"] == "main.py"

    assert logs_resp.status_code == 200
    assert logs_resp.json()["logs"] == []
