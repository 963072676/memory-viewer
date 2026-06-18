"""Hermes memory adapter — reads *.md files with frontmatter from memories_dir."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource
from app.utils.markdown import parse_section_entries
from app.utils.text import read_text_file_safe

# Frontmatter regex: matches YAML between --- delimiters at top of file
_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text.

    Returns (metadata_dict, body_text).
    Uses simple regex + line parsing to avoid hard yaml dependency in adapter.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    body = text[match.end():]

    meta: dict = {}
    current_key = None
    current_list: list[str] | None = None

    for line in raw_yaml.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- ") and current_key is not None:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip().strip("\"'"))
            meta[current_key] = current_list
            continue

        # Key: value
        if ":" in stripped:
            # Flush previous list
            current_list = None

            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip("\"'")
            current_key = key

            if val:
                # Try numeric
                try:
                    if "." in val:
                        meta[key] = float(val)
                    else:
                        meta[key] = int(val)
                except ValueError:
                    if val.lower() in ("true", "false"):
                        meta[key] = val.lower() == "true"
                    elif val.lower() == "null" or val == "":
                        meta[key] = None
                    else:
                        meta[key] = val
            else:
                # Empty value — may be a list key
                current_list = []

    return meta, body


class HermesAdapter(MemorySource):
    """Adapter for Hermes markdown memory files."""

    source_type = "hermes"

    def __init__(self, name: str = "hermes", config: dict | None = None):
        super().__init__(name=name, config=config)
        self.memories_dir: str = config.get("memories_dir", "") if config else ""
        self.profiles_dir: str = config.get("profiles_dir", "") if config else ""

    def _resolve_path(self, p: str) -> str:
        """Expand env vars and make relative paths absolute to project root."""
        from app.config import _PROJECT_ROOT
        p = os.path.expandvars(p)
        if not os.path.isabs(p):
            p = str(_PROJECT_ROOT / p)
        return p

    def _scan_files(self) -> list[str]:
        """Discover all .md files under memories_dir (non-recursive)."""
        md = self._resolve_path(self.memories_dir)
        if not os.path.isdir(md):
            return []
        return sorted(
            os.path.join(md, f)
            for f in os.listdir(md)
            if f.endswith(".md") and os.path.isfile(os.path.join(md, f))
        )

    def _scan_profile_files(self) -> list[tuple[str, str, str]]:
        """Discover profile MEMORY.md/USER.md files."""
        profiles_dir = self._resolve_path(self.profiles_dir)
        if not os.path.isdir(profiles_dir):
            return []

        files: list[tuple[str, str, str]] = []
        for profile in sorted(os.listdir(profiles_dir)):
            mem_dir = os.path.join(profiles_dir, profile, "memories")
            if not os.path.isdir(mem_dir):
                continue
            for file_name in ("MEMORY.md", "USER.md"):
                path = os.path.join(mem_dir, file_name)
                if os.path.isfile(path):
                    files.append((path, profile, file_name))
        return files

    def _read_entries_file(self, path: str, *, profile: str, file_name: str) -> list[MemoryItem]:
        """Read Hermes section-delimited files as individual memory items."""
        text = read_text_file_safe(path)
        if not text:
            return []

        meta, body = _parse_frontmatter(text)
        content = body.strip()
        entries = parse_section_entries(content)
        if not entries:
            entries = [content] if content else []

        results: list[MemoryItem] = []
        file_stem = Path(file_name).stem
        for index, entry in enumerate(entries):
            results.append(
                MemoryItem(
                    id=f"{profile}:{file_stem}:{index}",
                    title=str(meta.get("title", file_stem)),
                    content=entry,
                    type=str(meta.get("type", "fact")),
                    concepts=meta.get("concepts", []) or [],
                    strength=float(meta.get("strength", 5.0)),
                    created_at=str(meta.get("created_at", meta.get("createdAt", ""))),
                    updated_at=str(meta.get("updated_at", meta.get("updatedAt", ""))),
                    source=self.name,
                    metadata={
                        **meta,
                        "profile": profile,
                        "file": file_name,
                        "index": index,
                    },
                )
            )
        return results

    def _read_file(self, path: str) -> MemoryItem | None:
        """Read a single .md file and convert to MemoryItem."""
        text = read_text_file_safe(path)
        if not text:
            return None

        meta, body = _parse_frontmatter(text)
        file_id = Path(path).stem  # filename without .md
        title = meta.get("title", file_id)

        return MemoryItem(
            id=file_id,
            title=str(title),
            content=body.strip(),
            type=str(meta.get("type", "fact")),
            concepts=meta.get("concepts", []) or [],
            strength=float(meta.get("strength", 5.0)),
            created_at=str(meta.get("created_at", meta.get("createdAt", ""))),
            updated_at=str(meta.get("updated_at", meta.get("updatedAt", ""))),
            source=self.name,
            metadata=meta,
        )

    async def list(self, limit: int = 50, offset: int = 0) -> list[MemoryItem]:
        results: list[MemoryItem] = []
        for fp in self._scan_files():
            file_name = os.path.basename(fp)
            if file_name in ("MEMORY.md", "USER.md"):
                results.extend(self._read_entries_file(fp, profile="global", file_name=file_name))
                continue
            item = self._read_file(fp)
            if item:
                results.append(item)

        for fp, profile, file_name in self._scan_profile_files():
            results.extend(self._read_entries_file(fp, profile=profile, file_name=file_name))

        return results[offset : offset + limit]

    async def get(self, id: str) -> Optional[MemoryItem]:
        for item in await self.list(limit=999999):
            if item.id == id:
                return item
        return None

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        query_lower = query.lower()
        results: list[MemoryItem] = []
        for item in await self.list(limit=999999):
            if (
                query_lower in item.title.lower()
                or query_lower in item.content.lower()
                or any(query_lower in c.lower() for c in item.concepts)
            ):
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    async def health(self) -> bool:
        md = self._resolve_path(self.memories_dir)
        return os.path.isdir(md)
