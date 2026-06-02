"""Changelog API router — F-12 version update notes."""

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

_CHANGELOG_PATH = Path(__file__).resolve().parent.parent / "CHANGELOG.json"


def _load_changelog() -> list[dict]:
    """Load and return changelog entries from CHANGELOG.json."""
    try:
        with open(_CHANGELOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


@router.get("")
def get_changelog():
    """Get changelog entries sorted by version descending."""
    entries = _load_changelog()
    # Sort by version descending (e.g. "2.1.0" > "2.0.0")
    entries.sort(key=lambda e: e.get("version", "0"), reverse=True)
    return {"changelog": entries}
