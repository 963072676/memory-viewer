"""Plugin manager for the Memory Viewer plugin system (F-38).

Scans the plugins/ directory for Python modules with plugin.json manifests.
Each plugin defines hooks that fire on memory lifecycle events.
Plugins run in isolated async tasks with timeout protection.
"""

import asyncio
import importlib.util
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Plugin directory
PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")
PLUGINS_DIR = os.path.normpath(PLUGINS_DIR)

# Supported hooks
SUPPORTED_HOOKS = {
    "on_memory_create",
    "on_memory_update",
    "on_memory_delete",
    "on_search",
    "on_export",
}

# Plugin execution timeout (seconds)
PLUGIN_TIMEOUT = 5.0

# Execution log buffer (ring buffer, max 100 entries)
_execution_log: list[dict] = []
_MAX_LOG_ENTRIES = 100


class PluginInfo:
    """Represents a loaded plugin."""

    def __init__(self, name: str, version: str, description: str,
                 hooks: list[str], module: Any, path: str,
                 capabilities: list[dict] | None = None,
                 permissions: list[str] | None = None,
                 entry_points: dict | None = None,
                 author: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.hooks = hooks
        self.module = module
        self.path = path
        self.capabilities = capabilities or []
        self.permissions = permissions or []
        self.entry_points = entry_points or {}
        self.author = author
        self.enabled = True
        self.loaded_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "hooks": self.hooks,
            "capabilities": self.capabilities,
            "permissions": self.permissions,
            "entryPoints": self.entry_points,
            "author": self.author,
            "enabled": self.enabled,
            "loaded_at": self.loaded_at,
            "path": self.path,
        }


# Loaded plugins registry
_plugins: dict[str, PluginInfo] = {}
_initialized = False


def _normalize_capabilities(manifest: dict, hooks: list[str]) -> list[dict]:
    """Return stable plugin capability records for API and UI surfaces."""
    raw_capabilities = manifest.get("capabilities", [])
    capabilities: list[dict] = []

    if isinstance(raw_capabilities, list):
        for raw in raw_capabilities:
            if isinstance(raw, str):
                name = raw.strip()
                if name:
                    capabilities.append(
                        {
                            "name": name,
                            "category": "extension",
                            "description": "",
                            "hooks": [],
                        }
                    )
            elif isinstance(raw, dict):
                name = str(raw.get("name", "")).strip()
                if not name:
                    continue
                capability_hooks = raw.get("hooks", [])
                if not isinstance(capability_hooks, list):
                    capability_hooks = []
                capabilities.append(
                    {
                        "name": name,
                        "category": str(raw.get("category", "extension")),
                        "description": str(raw.get("description", "")),
                        "hooks": [h for h in capability_hooks if h in SUPPORTED_HOOKS],
                    }
                )

    if capabilities:
        return capabilities

    return [
        {
            "name": hook,
            "category": "hook",
            "description": f"Runs on {hook}",
            "hooks": [hook],
        }
        for hook in hooks
    ]


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _log_execution(plugin_name: str, hook: str, success: bool,
                   duration_ms: float, error: str = "") -> None:
    """Log plugin execution for the log viewer."""
    entry = {
        "plugin": plugin_name,
        "hook": hook,
        "success": success,
        "duration_ms": round(duration_ms, 2),
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    _execution_log.append(entry)
    if len(_execution_log) > _MAX_LOG_ENTRIES:
        _execution_log.pop(0)


def discover_plugins() -> None:
    """Scan the plugins/ directory and load valid plugins."""
    global _initialized

    if not os.path.exists(PLUGINS_DIR):
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        _initialized = True
        return

    for entry in os.listdir(PLUGINS_DIR):
        plugin_dir = os.path.join(PLUGINS_DIR, entry)
        if not os.path.isdir(plugin_dir):
            continue

        manifest_path = os.path.join(plugin_dir, "plugin.json")
        main_path = os.path.join(plugin_dir, "main.py")

        if not os.path.exists(manifest_path) or not os.path.exists(main_path):
            continue

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load plugin manifest for {entry}: {e}")
            continue

        name = manifest.get("name", entry)
        version = manifest.get("version", "0.0.1")
        description = manifest.get("description", "")
        hooks = [h for h in manifest.get("hooks", []) if h in SUPPORTED_HOOKS]
        capabilities = _normalize_capabilities(manifest, hooks)
        permissions = _normalize_string_list(manifest.get("permissions", []))
        entry_points = manifest.get("entryPoints", {})
        if not isinstance(entry_points, dict):
            entry_points = {}
        author = str(manifest.get("author", ""))

        if not hooks:
            logger.info(f"Plugin {name} has no valid hooks, skipping")
            continue

        # Load the Python module
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugin_{name}", main_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{name}"] = module
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error(f"Failed to load plugin {name}: {e}")
            _log_execution(name, "load", False, 0, str(e))
            continue

        plugin = PluginInfo(
            name=name,
            version=version,
            description=description,
            hooks=hooks,
            module=module,
            path=plugin_dir,
            capabilities=capabilities,
            permissions=permissions,
            entry_points=entry_points,
            author=author,
        )
        _plugins[name] = plugin
        logger.info(f"Loaded plugin: {name} v{version} (hooks: {hooks})")

    _initialized = True


def get_all_plugins() -> list[dict]:
    """Get all loaded plugins with their status."""
    if not _initialized:
        discover_plugins()
    return [p.to_dict() for p in _plugins.values()]


def get_capability_manifest() -> dict:
    """Return aggregate plugin capability inventory."""
    if not _initialized:
        discover_plugins()

    capability_index: dict[str, dict] = {}
    for plugin in _plugins.values():
        for capability in plugin.capabilities:
            name = capability["name"]
            record = capability_index.setdefault(
                name,
                {
                    "name": name,
                    "category": capability.get("category", "extension"),
                    "description": capability.get("description", ""),
                    "hooks": set(),
                    "plugins": [],
                },
            )
            record["hooks"].update(capability.get("hooks", []))
            record["plugins"].append(plugin.name)

    capabilities = [
        {
            **record,
            "hooks": sorted(record["hooks"]),
            "plugins": sorted(record["plugins"]),
        }
        for record in capability_index.values()
    ]

    return {
        "plugins": [p.to_dict() for p in _plugins.values()],
        "total": len(_plugins),
        "capabilities": sorted(capabilities, key=lambda item: item["name"]),
        "supportedHooks": sorted(SUPPORTED_HOOKS),
    }


def get_plugin(name: str) -> Optional[PluginInfo]:
    """Get a specific plugin by name."""
    if not _initialized:
        discover_plugins()
    return _plugins.get(name)


def enable_plugin(name: str) -> bool:
    """Enable a plugin. Returns True if found."""
    plugin = _plugins.get(name)
    if plugin:
        plugin.enabled = True
        return True
    return False


def disable_plugin(name: str) -> bool:
    """Disable a plugin. Returns True if found."""
    plugin = _plugins.get(name)
    if plugin:
        plugin.enabled = False
        return True
    return False


def get_execution_log(limit: int = 50) -> list[dict]:
    """Get recent plugin execution log entries."""
    return list(reversed(_execution_log[-limit:]))


async def fire_hook(hook_name: str, data: dict) -> list[dict]:
    """Fire a hook across all enabled plugins that subscribe to it.

    Each plugin runs in an isolated async task with a timeout.
    Returns list of {plugin, success, result, duration_ms, error}.
    """
    if not _initialized:
        discover_plugins()

    results = []
    tasks = []

    for name, plugin in _plugins.items():
        if not plugin.enabled or hook_name not in plugin.hooks:
            continue

        # Check if the module has the hook function
        hook_fn = getattr(plugin.module, hook_name, None)
        if not hook_fn or not callable(hook_fn):
            continue

        tasks.append((_run_plugin_hook(plugin, hook_name, hook_fn, data)))

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return [r for r in results if isinstance(r, dict)]


async def _run_plugin_hook(plugin: PluginInfo, hook_name: str,
                           hook_fn: Callable, data: dict) -> dict:
    """Run a single plugin hook with timeout protection."""
    start = time.monotonic()
    try:
        # Run in thread pool with timeout to avoid blocking
        if asyncio.iscoroutinefunction(hook_fn):
            result = await asyncio.wait_for(hook_fn(data), timeout=PLUGIN_TIMEOUT)
        else:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, hook_fn, data),
                timeout=PLUGIN_TIMEOUT,
            )

        duration_ms = (time.monotonic() - start) * 1000
        _log_execution(plugin.name, hook_name, True, duration_ms)
        return {
            "plugin": plugin.name,
            "success": True,
            "result": result,
            "duration_ms": round(duration_ms, 2),
            "error": "",
        }
    except asyncio.TimeoutError:
        duration_ms = (time.monotonic() - start) * 1000
        error = f"Plugin {plugin.name} timed out after {PLUGIN_TIMEOUT}s"
        logger.warning(error)
        _log_execution(plugin.name, hook_name, False, duration_ms, error)
        return {
            "plugin": plugin.name,
            "success": False,
            "result": None,
            "duration_ms": round(duration_ms, 2),
            "error": error,
        }
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        error = f"Plugin {plugin.name} error: {str(e)}"
        logger.error(error)
        _log_execution(plugin.name, hook_name, False, duration_ms, error)
        return {
            "plugin": plugin.name,
            "success": False,
            "result": None,
            "duration_ms": round(duration_ms, 2),
            "error": error,
        }


def fire_hook_sync(hook_name: str, data: dict) -> list[dict]:
    """Synchronous wrapper for fire_hook (for use in non-async contexts)."""
    try:
        loop = asyncio.get_running_loop()
        # We're inside an async context, schedule as task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, fire_hook(hook_name, data))
            return future.result(timeout=PLUGIN_TIMEOUT + 1)
    except RuntimeError:
        return asyncio.run(fire_hook(hook_name, data))
    except Exception as e:
        logger.error(f"Failed to fire hook {hook_name}: {e}")
        return []
