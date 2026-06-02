"""Application configuration via environment variables and YAML file."""

import os
from pathlib import Path
from typing import Optional

from app.config_loader import load_config

# Project root: <repo>/backend/app/config.py -> <repo>
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _project_path(*parts: str) -> str:
    """Return absolute path relative to project root."""
    return str(_PROJECT_ROOT.joinpath(*parts))


def _get_env(primary: str, legacy: str, default: str) -> str:
    """Read env var with MV_ prefix first, then legacy name, then default."""
    return os.environ.get(primary, os.environ.get(legacy, default))


class Settings:
    """Application settings loaded from YAML config + environment variables.

    Priority: MV_ prefixed env > legacy env > YAML config > built-in defaults.
    """

    def __init__(self):
        # Load YAML config file (returns {} if not found)
        yaml_cfg = load_config(_PROJECT_ROOT)

        # --- Port & Host ---
        self.MEMORY_VIEWER_PORT: int = int(
            _get_env("MV_PORT", "MEMORY_VIEWER_PORT",
                      str(yaml_cfg.get("port", 8501)))
        )
        self.MEMORY_VIEWER_HOST: str = _get_env(
            "MV_HOST", "MEMORY_VIEWER_HOST",
            str(yaml_cfg.get("host", "0.0.0.0"))
        )

        # --- Paths (all relative to project root by default) ---
        self.AGENTMEMORY_CACHE: str = _get_env(
            "MV_AGENTMEMORY_CACHE", "AGENTMEMORY_CACHE",
            yaml_cfg.get("agentmemory_cache",
                         _project_path("data", "cache", "agentmemory.json")),
        )
        self.HERMES_MEMORIES_DIR: str = _get_env(
            "MV_HERMES_MEMORIES_DIR", "HERMES_MEMORIES_DIR",
            yaml_cfg.get("hermes_memories_dir",
                         _project_path("data", "memories")),
        )
        self.HERMES_PROFILES_DIR: str = _get_env(
            "MV_HERMES_PROFILES_DIR", "HERMES_PROFILES_DIR",
            yaml_cfg.get("hermes_profiles_dir",
                         _project_path("data", "profiles")),
        )
        self.BACKUP_DIR: str = _get_env(
            "MV_BACKUP_DIR", "BACKUP_DIR",
            yaml_cfg.get("backup_dir",
                         _project_path("data", "backups")),
        )
        self.VERSIONS_DIR: str = _get_env(
            "MV_VERSIONS_DIR", "VERSIONS_DIR",
            yaml_cfg.get("versions_dir",
                         _project_path("data", "versions")),
        )

        # --- CORS ---
        self.CORS_ORIGINS: list[str] = _get_env(
            "MV_CORS_ORIGINS", "CORS_ORIGINS",
            yaml_cfg.get("cors_origins",
                         "http://localhost:8501,http://localhost:5173"),
        ).split(",")

        # --- Cache ---
        self.CACHE_REFRESH_INTERVAL: int = int(_get_env(
            "MV_CACHE_REFRESH_INTERVAL", "CACHE_REFRESH_INTERVAL",
            str(yaml_cfg.get("cache_refresh_interval", 30)),
        ))

        # --- Audit log ---
        self.AUDIT_LOG: str = _get_env(
            "MV_AUDIT_LOG", "AUDIT_LOG",
            yaml_cfg.get("audit_log",
                         _project_path("data", "cache", "audit.json")),
        )

        # --- Feishu webhook (F-17) ---
        self.FEISHU_WEBHOOK_URL: Optional[str] = os.environ.get("FEISHU_WEBHOOK_URL") or None

    @property
    def cache_dir(self) -> str:
        return str(Path(self.AGENTMEMORY_CACHE).parent)


settings = Settings()
