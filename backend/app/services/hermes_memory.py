"""Service layer for hermes memory file operations."""

import os
from app.config import settings
from app.utils.markdown import parse_section_entries
from app.utils.text import read_text_file_safe


def _read_file_safe(path: str) -> str:
    """Read file content with UTF-8 first and legacy encoding fallback."""
    return read_text_file_safe(path)


def _parse_section_entries(content: str) -> list[str]:
    """Split content by § delimiter, strip whitespace, filter empty."""
    return parse_section_entries(content)


def _discover_profiles() -> list[str]:
    """Discover profile directories under HERMES_PROFILES_DIR."""
    profiles = []
    if not os.path.isdir(settings.HERMES_PROFILES_DIR):
        return profiles
    for entry in sorted(os.listdir(settings.HERMES_PROFILES_DIR)):
        full = os.path.join(settings.HERMES_PROFILES_DIR, entry)
        if os.path.isdir(full):
            profiles.append(entry)
    return profiles


def get_hermes_memory() -> dict:
    """Read hermes built-in memory files (global + per-profile)."""
    result = {
        "global": {"memory": [], "user": []},
        "profiles": {},
    }

    # Global memory
    global_memory_path = os.path.join(settings.HERMES_MEMORIES_DIR, "MEMORY.md")
    global_user_path = os.path.join(settings.HERMES_MEMORIES_DIR, "USER.md")
    result["global"]["memory"] = _parse_section_entries(_read_file_safe(global_memory_path))
    result["global"]["user"] = _parse_section_entries(_read_file_safe(global_user_path))

    # Per-profile memory
    for profile in _discover_profiles():
        mem_dir = os.path.join(settings.HERMES_PROFILES_DIR, profile, "memories")
        if not os.path.isdir(mem_dir):
            continue
        memory_path = os.path.join(mem_dir, "MEMORY.md")
        user_path = os.path.join(mem_dir, "USER.md")
        memory_entries = _parse_section_entries(_read_file_safe(memory_path))
        user_entries = _parse_section_entries(_read_file_safe(user_path))
        if memory_entries or user_entries:
            result["profiles"][profile] = {
                "memory": memory_entries,
                "user": user_entries,
            }

    return result


def get_profiles() -> list[str]:
    """Return list of known profile names."""
    return _discover_profiles()


def get_hermes_memory_count() -> int:
    """Get total count of hermes memory entries."""
    data = get_hermes_memory()
    count = len(data["global"]["memory"]) + len(data["global"]["user"])
    for profile_data in data.get("profiles", {}).values():
        count += len(profile_data.get("memory", [])) + len(profile_data.get("user", []))
    return count
