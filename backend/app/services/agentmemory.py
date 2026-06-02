"""Service layer for agentmemory data operations."""

import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.agentmemory import AgentMemoryItem


def _read_json_cache(path: str) -> dict:
    """Read the agentmemory JSON cache file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "memories" in data:
                return data
            if isinstance(data, list):
                return {"memories": data}
            return {"memories": []}
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return {"memories": []}


def _atomic_write_json(path: str, data: dict) -> None:
    """Write JSON to file atomically (tmp + rename)."""
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _append_audit(entry: dict) -> None:
    """Append an entry to the audit log."""
    audit_path = settings.AUDIT_LOG
    dir_name = os.path.dirname(audit_path)
    os.makedirs(dir_name, exist_ok=True)
    try:
        entries = []
        try:
            with open(audit_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Handle both formats: list or {"entries": [...]}
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict) and "entries" in data:
                entries = data["entries"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        entries.append(entry)
        _atomic_write_json(audit_path, {"entries": entries})
    except Exception:
        # Don't let audit failures break the main operation
        pass


def _audit_log(operation: str, memory_id: str, title: str = "", details: dict = None) -> None:
    """Write an audit log entry."""
    entry = {
        "operation": operation,
        "memory_id": memory_id,
        "title": title,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if details:
        entry.update(details)
    _append_audit(entry)


def get_all_memories() -> list[dict]:
    """Get all agentmemory entries."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    # F43: Attach lightweight health scores to all memories
    _attach_health_scores(memories)
    return memories


def get_paginated_memories(
    limit: int = 50,
    offset: int = 0,
    sort: str = "updatedAt",
    order: str = "desc",
    type_filter: Optional[str] = None,
    include_archived: bool = False,
    tag_filter: Optional[str] = None,
) -> dict:
    """Get paginated agentmemory entries with sorting and filtering."""
    memories = get_all_memories()

    # Filter archived
    if not include_archived:
        memories = [m for m in memories if not m.get("archived", False)]

    # Filter by type
    if type_filter:
        memories = [m for m in memories if m.get("type") == type_filter]

    # F46: Filter by tag
    if tag_filter:
        tag_lower = tag_filter.strip().lower()
        memories = [m for m in memories if tag_lower in [t.lower() for t in m.get("tags", [])]]

    # Sort
    reverse = order == "desc"
    if sort in ("updatedAt", "createdAt"):
        memories.sort(key=lambda m: m.get(sort, ""), reverse=reverse)
    elif sort == "strength":
        memories.sort(key=lambda m: m.get("strength", 0), reverse=reverse)
    elif sort == "type":
        memories.sort(key=lambda m: m.get("type", ""), reverse=reverse)

    total = len(memories)
    paginated = memories[offset : offset + limit]

    # F43: Attach lightweight health_score to each memory in paginated result
    _attach_health_scores(paginated)

    return {"total": total, "limit": limit, "offset": offset, "memories": paginated}


def _attach_health_scores(memories: list[dict]) -> None:
    """Batch-compute simplified health scores (no recommendation lookup)."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    for m in memories:
        strength = m.get("strength", 5)
        concepts = m.get("concepts", [])
        created_at = m.get("createdAt") or m.get("updatedAt") or ""

        # Parse days since created
        days = 0
        if created_at:
            try:
                dt_str = created_at.replace("Z", "+00:00")
                created = datetime.fromisoformat(dt_str)
                days = max(0, (now - created).days)
            except (ValueError, TypeError):
                pass

        # Dimension scores (0-100)
        strength_score = min(100, max(0, (strength / 10) * 100))
        age_score = max(0, 100 - (days / 30) * 100)
        concepts_score = min(100, (len(concepts) / 5) * 100)
        # Skip recommendation_score for batch (set to 0)
        total_score = (
            strength_score * 0.40
            + age_score * 0.30
            + concepts_score * 0.15
            + 0 * 0.15
        )

        if total_score > 70:
            color = "green"
        elif total_score >= 40:
            color = "yellow"
        else:
            color = "red"

        m["health_score"] = round(total_score)
        m["health_color"] = color


def get_memory_by_id(memory_id: str) -> Optional[dict]:
    """Get a single memory by ID."""
    memories = get_all_memories()
    for m in memories:
        if m.get("id") == memory_id:
            return m
    return None


def update_memory(memory_id: str, content: Optional[str] = None, concepts: Optional[list[str]] = None, strength: Optional[int] = None, tags: Optional[list[str]] = None) -> Optional[dict]:
    """Update an existing memory entry (F-08)."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    updated = False

    # Find current state before update (for version snapshot)
    current = None
    for m in memories:
        if m.get("id") == memory_id:
            current = dict(m)
            break

    for m in memories:
        if m.get("id") == memory_id:
            if content is not None:
                m["content"] = content
            if concepts is not None:
                m["concepts"] = concepts
            if strength is not None:
                m["strength"] = strength
            if tags is not None:
                m["tags"] = _normalize_tags(tags)
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            m["version"] = m.get("version", 1) + 1
            updated = True
            break

    if not updated:
        return None

    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    # F-24: Save version snapshot before update
    if current:
        try:
            from app.services.versioning import save_snapshot
            save_snapshot(current)
        except Exception:
            pass

    _audit_log("update", memory_id, details={
        "updated_fields": {
            k: v for k, v in {"content": content, "concepts": concepts, "strength": strength}.items()
            if v is not None
        }
    })

    # F-26: Notify webhook subscribers
    try:
        from app.services.subscriptions import notify_subscribers
        updated_mem = next((m for m in memories if m.get("id") == memory_id), None)
        if updated_mem:
            notify_subscribers("update", updated_mem.get("title", ""), memory_id)
    except Exception:
        pass

    return next((m for m in memories if m.get("id") == memory_id), None)


def delete_memory(memory_id: str) -> bool:
    """Delete a single memory entry (F-09). Returns True if found and deleted."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    target = None

    for m in memories:
        if m.get("id") == memory_id:
            target = m
            break

    if not target:
        return False

    data["memories"] = [m for m in memories if m.get("id") != memory_id]
    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)
    _audit_log("delete", memory_id, target.get("title", ""))

    # F-26: Notify webhook subscribers
    try:
        from app.services.subscriptions import notify_subscribers
        notify_subscribers("delete", target.get("title", ""), memory_id)
    except Exception:
        pass

    return True


def delete_memories_batch(ids: list[str]) -> dict:
    """Delete multiple memory entries (F-09). Returns summary."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    id_set = set(ids)

    found = {m.get("id") for m in memories if m.get("id") in id_set}
    not_found = id_set - found

    data["memories"] = [m for m in memories if m.get("id") not in found]
    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    for mid in found:
        title = next((m.get("title", "") for m in memories if m.get("id") == mid), "")
        _audit_log("batch_delete", mid, title)

    return {
        "deleted_count": len(found),
        "deleted_ids": list(found),
        "not_found_ids": list(not_found),
    }


def create_memory(
    title: str,
    content: str,
    type_: str = "pattern",
    concepts: Optional[list[str]] = None,
    strength: int = 5,
    tags: Optional[list[str]] = None,
) -> dict:
    """Create a new agentmemory entry."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    mem_id = f"mem_{hashlib.md5(f'{title}{content}{now}'.encode()).hexdigest()[:16]}"
    # Normalize tags: lowercase, strip, deduplicate
    normalized_tags = _normalize_tags(tags) if tags else []

    new_memory = {
        "id": mem_id,
        "type": type_,
        "title": title,
        "content": content,
        "concepts": concepts or [],
        "files": [],
        "createdAt": now,
        "updatedAt": now,
        "strength": strength,
        "version": 1,
        "isLatest": True,
        "sessionIds": [],
        "tags": normalized_tags,
    }

    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    data.setdefault("memories", []).append(new_memory)
    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    # F-38: Save initial version snapshot (v1) on creation
    try:
        from app.services.versioning import save_snapshot
        save_snapshot(new_memory)
    except Exception:
        pass

    # F-26: Notify webhook subscribers
    try:
        from app.services.subscriptions import notify_subscribers
        notify_subscribers("create", title, mem_id)
    except Exception:
        pass

    return new_memory


def import_memories(file_content: str, filename: str) -> dict:
    """Import memories from JSON or Markdown content."""
    imported = 0
    skipped = 0
    failed = 0
    errors = []

    existing = get_all_memories()
    existing_hashes = set()
    for m in existing:
        h = hashlib.md5(f"{m.get('title', '')}{m.get('content', '')}".encode()).hexdigest()
        existing_hashes.add(h)

    new_memories = []

    if filename.endswith(".json"):
        try:
            data = json.loads(file_content)
            if isinstance(data, dict) and "memories" in data:
                items = data["memories"]
            elif isinstance(data, list):
                items = data
            else:
                return {"success": False, "imported": 0, "skipped": 0, "failed": 1, "errors": ["Invalid JSON format"]}

            for item in items:
                try:
                    h = hashlib.md5(f"{item.get('title', '')}{item.get('content', '')}".encode()).hexdigest()
                    if h in existing_hashes:
                        skipped += 1
                        continue
                    new_memories.append(item)
                    existing_hashes.add(h)
                    imported += 1
                except Exception as e:
                    failed += 1
                    errors.append(str(e))
        except json.JSONDecodeError as e:
            return {"success": False, "imported": 0, "skipped": 0, "failed": 1, "errors": [f"JSON parse error: {e}"]}
    elif filename.endswith(".md"):
        # Parse markdown: ## title\n\ncontent\n\n---\n
        sections = file_content.split("---")
        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split("\n")
            title = ""
            content_lines = []
            in_content = False
            for line in lines:
                if line.startswith("## "):
                    title = line[3:].strip()
                    in_content = True
                elif in_content:
                    content_lines.append(line)
            if title and content_lines:
                content = "\n".join(content_lines).strip()
                h = hashlib.md5(f"{title}{content}".encode()).hexdigest()
                if h in existing_hashes:
                    skipped += 1
                    continue
                new_memories.append({
                    "title": title,
                    "content": content,
                    "type": "pattern",
                    "concepts": [],
                    "strength": 5,
                    "tags": [],
                })
                imported += 1
    else:
        return {"success": False, "imported": 0, "skipped": 0, "failed": 1, "errors": [f"Unsupported file format: {filename}"]}

    # Write new memories
    if new_memories:
        data = _read_json_cache(settings.AGENTMEMORY_CACHE)
        data.setdefault("memories", []).extend(new_memories)
        _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    return {"success": True, "imported": imported, "skipped": skipped, "failed": failed, "errors": errors}


def export_memories(format_: str = "json", ids: Optional[str] = None) -> tuple[str, str, str]:
    """Export memories. Returns (content, media_type, filename)."""
    memories = get_all_memories()

    if ids:
        id_set = set(ids.split(","))
        memories = [m for m in memories if m.get("id") in id_set]

    if format_ == "markdown":
        lines = []
        for m in memories:
            title = m.get("title", "Untitled")
            content = m.get("content", "")
            type_ = m.get("type", "pattern")
            strength = m.get("strength", 5)
            concepts = ", ".join(m.get("concepts", []))
            lines.append(f"## {title}\n")
            lines.append(content)
            lines.append(f"\n**type**: {type_} | **strength**: {strength * 10}%")
            if concepts:
                lines.append(f"**concepts**: {concepts}")
            lines.append("\n---\n")
        return "\n".join(lines), "text/markdown", "memories.md"
    else:
        return json.dumps({"memories": memories}, indent=2, ensure_ascii=False), "application/json", "memories.json"


def get_cache_age() -> float:
    """Get cache file age in seconds."""
    try:
        mtime = os.path.getmtime(settings.AGENTMEMORY_CACHE)
        return time.time() - mtime
    except (FileNotFoundError, OSError):
        return -1


def get_stats() -> dict:
    """Get detailed statistics for the dashboard (F-10)."""
    # Use cached health scores to avoid duplicate computation
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    cached = data.get("_cached_health_scores")
    now_ts = time.time()
    cache_valid = cached and (now_ts - cached.get("_ts", 0)) < 60  # 60s cache

    if cache_valid:
        # Use pre-computed scores from cache
        score_map = cached.get("_scores", {})
        by_type = {}
        strength_dist = {str(i): 0 for i in range(11)}
        by_month = {}

        for m in memories:
            t = m.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            s = min(10, max(0, m.get("strength", 0)))
            strength_dist[str(s)] = strength_dist.get(str(s), 0) + 1
            dt_str = m.get("createdAt") or m.get("updatedAt") or ""
            if len(dt_str) >= 7:
                by_month[dt_str[:7]] = by_month.get(dt_str[:7], 0) + 1

        total = len(memories)
        strengths = [m.get("strength", 0) for m in memories]
        avg_strength = round(sum(strengths) / len(strengths), 1) if strengths else 0

        by_month = dict(sorted(by_month.items()))
        return {
            "total": total,
            "avg_strength": avg_strength,
            "by_type": by_type,
            "strength_distribution": strength_dist,
            "by_month": by_month,
        }

    # Full computation (cache miss or stale)
    by_type = {}
    for m in memories:
        t = m.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    strength_dist = {str(i): 0 for i in range(11)}
    for m in memories:
        s = min(10, max(0, m.get("strength", 0)))
        strength_dist[str(s)] = strength_dist.get(str(s), 0) + 1

    by_month = {}
    for m in memories:
        dt_str = m.get("createdAt") or m.get("updatedAt") or ""
        if len(dt_str) >= 7:
            month = dt_str[:7]
            by_month[month] = by_month.get(month, 0) + 1

    by_month = dict(sorted(by_month.items()))
    total = len(memories)
    strengths = [m.get("strength", 0) for m in memories]
    avg_strength = round(sum(strengths) / len(strengths), 1) if strengths else 0

    return {
        "total": total,
        "avg_strength": avg_strength,
        "by_type": by_type,
        "strength_distribution": strength_dist,
        "by_month": by_month,
    }


def set_archive_status(memory_id: str, archived: bool) -> Optional[dict]:
    """Set the archived status of a memory entry (F-15). Returns the updated memory or None."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    updated = False

    for m in memories:
        if m.get("id") == memory_id:
            m["archived"] = archived
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            updated = True
            break

    if not updated:
        return None

    _atomic_write_json(settings.AGENTMEMORY_CACHE, data)
    _audit_log(
        "archive" if archived else "unarchive",
        memory_id,
        details={"archived": archived},
    )
    return next((m for m in memories if m.get("id") == memory_id), None)


def batch_archive_memories(ids: list[str]) -> dict:
    """Batch archive memories (F45)."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    id_set = set(ids)
    found = []
    not_found = []

    for m in memories:
        if m.get("id") in id_set:
            m["archived"] = True
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            found.append(m.get("id"))
            _audit_log("batch_archive", m.get("id"), m.get("title", ""))

    not_found = list(id_set - set(found))

    if found:
        _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    return {"affected_count": len(found), "affected_ids": found, "not_found_ids": not_found}


def batch_unarchive_memories(ids: list[str]) -> dict:
    """Batch unarchive memories (F45)."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    id_set = set(ids)
    found = []
    not_found = []

    for m in memories:
        if m.get("id") in id_set:
            m["archived"] = False
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            found.append(m.get("id"))
            _audit_log("batch_unarchive", m.get("id"), m.get("title", ""))

    not_found = list(id_set - set(found))

    if found:
        _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    return {"affected_count": len(found), "affected_ids": found, "not_found_ids": not_found}


def _normalize_tags(tags: list[str]) -> list[str]:
    """Normalize tags: lowercase, strip whitespace, deduplicate, remove empty."""
    seen = set()
    result = []
    for t in tags:
        normalized = t.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def set_memory_tags(memory_id: str, tags: list[str]) -> Optional[dict]:
    """Set tags on a memory (replaces existing tags). Returns updated memory or None."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    normalized = _normalize_tags(tags)

    for m in memories:
        if m.get("id") == memory_id:
            m["tags"] = normalized
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            _atomic_write_json(settings.AGENTMEMORY_CACHE, data)
            _audit_log("set_tags", memory_id, details={"tags": normalized})
            return m
    return None


def get_all_tags() -> list[dict]:
    """Get all unique tags with counts across all memories."""
    memories = get_all_memories()
    tag_counts: dict[str, int] = {}
    for m in memories:
        for t in m.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    result = [{"tag": t, "count": c} for t, c in tag_counts.items()]
    result.sort(key=lambda x: (-x["count"], x["tag"]))
    return result


def batch_add_tags(ids: list[str], tags: list[str]) -> dict:
    """Add tags to specified memories (merge, not replace)."""
    data = _read_json_cache(settings.AGENTMEMORY_CACHE)
    memories = data.get("memories", [])
    id_set = set(ids)
    normalized = _normalize_tags(tags)
    found = []

    for m in memories:
        if m.get("id") in id_set:
            existing = set(m.get("tags", []))
            existing.update(normalized)
            m["tags"] = sorted(existing)
            m["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            found.append(m.get("id"))

    not_found = list(id_set - set(found))

    if found:
        _atomic_write_json(settings.AGENTMEMORY_CACHE, data)

    return {"affected_count": len(found), "affected_ids": found, "not_found_ids": not_found}


def get_smart_collections() -> list[dict]:
    """Evaluate predefined smart collection rules against all memories (F48)."""
    memories = get_all_memories()
    now = datetime.now(timezone.utc)

    def _parse_dt(dt_str: str):
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    recent_7d = 0
    high_strength = 0
    low_health = 0
    untagged = 0
    stale = 0
    archived_count = 0

    for m in memories:
        updated = _parse_dt(m.get("updatedAt", ""))
        strength = m.get("strength", 0)
        health = m.get("health_score")
        tags = m.get("tags", [])
        is_archived = m.get("archived", False)

        if updated and (now - updated).days <= 7:
            recent_7d += 1
        if strength >= 8:
            high_strength += 1
        if health is not None and health < 40:
            low_health += 1
        if not tags:
            untagged += 1
        if updated and (now - updated).days > 30:
            stale += 1
        if is_archived:
            archived_count += 1

    return [
        {"id": "recent_7d", "name": "最近 7 天", "description": "Memories updated in the last 7 days", "count": recent_7d, "icon": "🕐"},
        {"id": "high_strength", "name": "高强度", "description": "Strength >= 8", "count": high_strength, "icon": "⚡"},
        {"id": "low_health", "name": "低健康度", "description": "Health score < 40", "count": low_health, "icon": "❤️"},
        {"id": "untagged", "name": "无标签", "description": "Memories with no tags", "count": untagged, "icon": "🏷️"},
        {"id": "stale", "name": "待更新", "description": "Not updated in over 30 days", "count": stale, "icon": "🔄"},
        {"id": "archived", "name": "已归档", "description": "Archived memories", "count": archived_count, "icon": "📦"},
    ]


def quick_search(query: str, limit: int = 10) -> list[dict]:
    """Quick search across memory titles and content (F47).

    Returns minimal fields: id, title, type, snippet (first 80 chars), tags.
    Sorted by relevance: exact title match > title contains > content contains.
    """
    if not query:
        return []

    memories = get_all_memories()
    query_lower = query.lower()
    scored: list[tuple[int, dict]] = []

    for m in memories:
        title = m.get("title", "")
        content = m.get("content", "")
        title_lower = title.lower()
        content_lower = content.lower()

        # Score: 3 = exact title, 2 = title contains, 1 = content contains
        if title_lower == query_lower:
            score = 3
        elif query_lower in title_lower:
            score = 2
        elif query_lower in content_lower:
            score = 1
        else:
            continue

        snippet = content[:80]
        scored.append((score, {
            "id": m.get("id"),
            "title": title,
            "type": m.get("type"),
            "snippet": snippet,
            "tags": m.get("tags", []),
        }))

    # Sort by score descending (highest relevance first)
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]
