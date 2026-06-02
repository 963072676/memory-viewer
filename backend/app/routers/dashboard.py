"""Custom Dashboard API router (F-44) — Save/read layout configuration."""

import json
import os
import tempfile
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter()

_LAYOUT_PATH = os.path.join(settings.cache_dir, "dashboard_layout.json")


# --- Preset Templates ---

PRESET_TEMPLATES = {
    "default": {
        "name": "默认视图",
        "description": "标准仪表盘布局，适合所有用户",
        "widgets": [
            {"id": "w-total", "type": "memory-count", "x": 0, "y": 0, "w": 3, "h": 2, "config": {}},
            {"id": "w-types", "type": "type-distribution", "x": 3, "y": 0, "w": 5, "h": 4, "config": {}},
            {"id": "w-strength", "type": "strength-histogram", "x": 8, "y": 0, "w": 4, "h": 4, "config": {}},
            {"id": "w-heatmap", "type": "activity-heatmap", "x": 0, "y": 2, "w": 12, "h": 3, "config": {}},
            {"id": "w-recent", "type": "recent-memories", "x": 0, "y": 5, "w": 6, "h": 4, "config": {}},
            {"id": "w-quick", "type": "quick-actions", "x": 6, "y": 5, "w": 6, "h": 4, "config": {}},
        ],
    },
    "developer": {
        "name": "开发者视图",
        "description": "聚焦代码相关记忆和Bug追踪",
        "widgets": [
            {"id": "w-total", "type": "memory-count", "x": 0, "y": 0, "w": 3, "h": 2, "config": {}},
            {"id": "w-health", "type": "health-score", "x": 3, "y": 0, "w": 3, "h": 2, "config": {}},
            {"id": "w-pii", "type": "pii-alerts", "x": 6, "y": 0, "w": 3, "h": 2, "config": {}},
            {"id": "w-clusters", "type": "cluster-overview", "x": 9, "y": 0, "w": 3, "h": 2, "config": {}},
            {"id": "w-types", "type": "type-distribution", "x": 0, "y": 2, "w": 6, "h": 4, "config": {}},
            {"id": "w-anomalies", "type": "anomaly-timeline", "x": 6, "y": 2, "w": 6, "h": 4, "config": {}},
            {"id": "w-recent", "type": "recent-memories", "x": 0, "y": 6, "w": 12, "h": 4, "config": {}},
        ],
    },
    "ops": {
        "name": "运维视图",
        "description": "聚焦系统健康、异常监控和性能指标",
        "widgets": [
            {"id": "w-health", "type": "health-score", "x": 0, "y": 0, "w": 4, "h": 3, "config": {}},
            {"id": "w-anomalies", "type": "anomaly-timeline", "x": 4, "y": 0, "w": 8, "h": 3, "config": {}},
            {"id": "w-heatmap", "type": "activity-heatmap", "x": 0, "y": 3, "w": 12, "h": 3, "config": {}},
            {"id": "w-pii", "type": "pii-alerts", "x": 0, "y": 6, "w": 4, "h": 3, "config": {}},
            {"id": "w-total", "type": "memory-count", "x": 4, "y": 6, "w": 4, "h": 3, "config": {}},
            {"id": "w-decay", "type": "decay-curve", "x": 8, "y": 6, "w": 4, "h": 3, "config": {}},
        ],
    },
    "pm": {
        "name": "PM 视图",
        "description": "聚焦产品决策相关记忆和趋势分析",
        "widgets": [
            {"id": "w-total", "type": "memory-count", "x": 0, "y": 0, "w": 4, "h": 2, "config": {}},
            {"id": "w-clusters", "type": "cluster-overview", "x": 4, "y": 0, "w": 8, "h": 4, "config": {}},
            {"id": "w-types", "type": "type-distribution", "x": 0, "y": 2, "w": 4, "h": 4, "config": {}},
            {"id": "w-heatmap", "type": "activity-heatmap", "x": 0, "y": 6, "w": 12, "h": 3, "config": {}},
            {"id": "w-recent", "type": "recent-memories", "x": 0, "y": 9, "w": 12, "h": 4, "config": {}},
        ],
    },
}


def _load_layout() -> dict:
    """Load saved layout from file."""
    try:
        with open(_LAYOUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"preset": "default", "widgets": PRESET_TEMPLATES["default"]["widgets"]}


def _save_layout(layout: dict) -> None:
    """Save layout to file."""
    os.makedirs(os.path.dirname(_LAYOUT_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(_LAYOUT_PATH), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(layout, f, indent=2, ensure_ascii=False)
        os.replace(tmp, _LAYOUT_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


class WidgetConfig(BaseModel):
    id: str
    type: str
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 3
    config: dict = Field(default_factory=dict)


class LayoutRequest(BaseModel):
    widgets: list[WidgetConfig]
    preset: Optional[str] = None


@router.get("/dashboard/layout")
def get_layout():
    """Retrieve saved dashboard layout.
    
    AC-F44-3: Layout persists after refresh.
    """
    layout = _load_layout()
    return {
        "widgets": layout.get("widgets", []),
        "preset": layout.get("preset", "default"),
        "available_presets": {
            k: {"name": v["name"], "description": v["description"]}
            for k, v in PRESET_TEMPLATES.items()
        },
    }


@router.put("/dashboard/layout")
def save_layout(req: LayoutRequest):
    """Save dashboard layout configuration.
    
    AC-F44-3: Layout persists after refresh.
    """
    layout = {
        "widgets": [w.model_dump() for w in req.widgets],
        "preset": req.preset or "custom",
    }
    _save_layout(layout)
    return {"success": True, "widget_count": len(req.widgets)}


@router.get("/dashboard/presets")
def list_presets():
    """List available preset templates.
    
    AC-F44-4: Provides >=3 preset layout templates.
    """
    return {
        "presets": {
            k: {"name": v["name"], "description": v["description"], "widgets": v["widgets"]}
            for k, v in PRESET_TEMPLATES.items()
        }
    }


@router.get("/dashboard/presets/{preset_id}")
def get_preset(preset_id: str):
    """Get a specific preset template."""
    if preset_id not in PRESET_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
    preset = PRESET_TEMPLATES[preset_id]
    return {
        "id": preset_id,
        "name": preset["name"],
        "description": preset["description"],
        "widgets": preset["widgets"],
    }


@router.post("/dashboard/presets/{preset_id}/apply")
def apply_preset(preset_id: str):
    """Apply a preset template as the current layout."""
    if preset_id not in PRESET_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")

    preset = PRESET_TEMPLATES[preset_id]
    layout = {"preset": preset_id, "widgets": preset["widgets"]}
    _save_layout(layout)

    return {"success": True, "preset": preset_id, "widget_count": len(preset["widgets"])}
