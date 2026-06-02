"""Hermes memory adapter — reads *.md files with frontmatter from memories_dir."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from app.adapters.base import MemoryItem, MemorySource

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

    def _read_file(self, path: str) -> MemoryItem | None:
        """Read a single .md file and convert to MemoryItem."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except (FileNotFoundError, PermissionError, OSError):
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
        files = self._scan_files()
        sliced = files[offset : offset + limit]
        results: list[MemoryItem] = []
        for fp in sliced:
            item = self._read_file(fp)
            if item:
                results.append(item)
        return results

    async def get(self, id: str) -> Optional[MemoryItem]:
        md = self._resolve_path(self.memories_dir)
        path = os.path.join(md, f"{id}.md")
        if not os.path.isfile(path):
            return None
        return self._read_file(path)

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        query_lower = query.lower()
        results: list[MemoryItem] = []
        for fp in self._scan_files():
            item = self._read_file(fp)
            if not item:
                continue
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
