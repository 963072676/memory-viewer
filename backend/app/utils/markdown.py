"""Markdown and § delimiter parsing utilities."""

import re


_FRONTMATTER_RE = re.compile(r"^---\s*\r?\n.*?\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def parse_section_entries(content: str) -> list[str]:
    """Split content by § delimiter, strip whitespace, filter empty."""
    if not content:
        return []
    content = _FRONTMATTER_RE.sub("", content, count=1)
    entries = content.split("§")
    return [e.strip() for e in entries if e.strip()]


def format_memory_markdown(memory: dict) -> str:
    """Format a memory dict as markdown."""
    title = memory.get("title", "Untitled")
    content = memory.get("content", "")
    type_ = memory.get("type", "pattern")
    strength = memory.get("strength", 5)
    concepts = ", ".join(memory.get("concepts", []))

    lines = [f"## {title}\n", content]
    lines.append(f"\n**type**: {type_} | **strength**: {strength * 10}%")
    if concepts:
        lines.append(f"**concepts**: {concepts}")

    return "\n".join(lines)
