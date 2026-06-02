"""Auto-translate plugin — flags non-English content.

This is an example plugin that detects non-English text in memory
content and adds a 'needs-translation' tag automatically.
"""

import re


def _has_cjk(text: str) -> bool:
    """Check if text contains CJK (Chinese/Japanese/Korean) characters."""
    return bool(re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text))


def _has_cyrillic(text: str) -> bool:
    """Check if text contains Cyrillic characters."""
    return bool(re.search(r'[\u0400-\u04ff]', text))


def _is_likely_english(text: str) -> bool:
    """Simple heuristic to check if text is likely English."""
    # If text has CJK or Cyrillic, it's not English
    if _has_cjk(text) or _has_cyrillic(text):
        return False
    # If text is mostly ASCII letters, likely English
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    total_letters = sum(1 for c in text if c.isalpha())
    if total_letters == 0:
        return True
    return ascii_letters / total_letters > 0.85


def on_memory_create(data: dict) -> dict:
    """Hook fired when a new memory is created.

    Checks if content is non-English and flags it.
    """
    content = data.get("content", "")
    title = data.get("title", "")
    text = f"{title} {content}"

    if text.strip() and not _is_likely_english(text):
        return {
            "action": "add_tag",
            "tag": "needs-translation",
            "reason": "Non-English content detected",
        }
    return {"action": "none"}


def on_memory_update(data: dict) -> dict:
    """Hook fired when a memory is updated.

    Same logic as on_memory_create.
    """
    content = data.get("content", "")
    title = data.get("title", "")
    text = f"{title} {content}"

    if text.strip() and not _is_likely_english(text):
        return {
            "action": "add_tag",
            "tag": "needs-translation",
            "reason": "Non-English content detected on update",
        }
    return {"action": "none"}
