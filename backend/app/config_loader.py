"""YAML configuration loader for Memory Viewer.

Reads ``memory-viewer.yaml`` from the project root (if present) and
resolves ``${ENV_VAR}`` placeholders inside string values.

Environment variables always take precedence over YAML values — the
caller (config.py) handles that layering.
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml  # PyYAML (add pyyaml to requirements.txt)


_CONFIG_FILENAMES = ("memory-viewer.yaml", "memory-viewer.yml")

_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")


def _resolve_env_vars(value: Any) -> Any:
    """Recursively expand ``${VAR}`` / ``${VAR:default}`` in strings."""
    if isinstance(value, str):
        def _replace(m: re.Match) -> str:
            var_name = m.group(1)
            default = m.group(2)  # may be None
            return os.environ.get(var_name, default if default is not None else m.group(0))
        return _ENV_PATTERN.sub(_replace, value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


def load_config(project_root: Path) -> dict[str, Any]:
    """Load and return the YAML configuration dict.

    Searches for *memory-viewer.yaml* (or *.yml*) in *project_root*.
    Returns an empty dict when no config file is found.
    """
    for name in _CONFIG_FILENAMES:
        config_path = project_root / name
        if config_path.is_file():
            with open(config_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            return _resolve_env_vars(raw)
    return {}
