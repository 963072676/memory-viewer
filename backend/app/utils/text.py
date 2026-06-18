"""Text file decoding helpers."""

from __future__ import annotations

import locale
import logging

logger = logging.getLogger(__name__)


def candidate_text_encodings() -> list[str]:
    """Return preferred text encodings in deterministic fallback order."""
    encodings = ["utf-8-sig", "utf-8", locale.getpreferredencoding(False), "gb18030", "gbk"]
    result: list[str] = []
    for encoding in encodings:
        normalized = encoding.lower()
        if normalized not in result:
            result.append(normalized)
    return result


def read_text_file_safe(path: str) -> str:
    """Read text with UTF-8 first and legacy encoding fallback."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except (FileNotFoundError, PermissionError, OSError):
        return ""

    for encoding in candidate_text_encodings():
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    logger.warning("Failed to decode text file cleanly: %s", path)
    return raw.decode("utf-8", errors="replace")
