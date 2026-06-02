"""Health Scanner service (F-68).

Quality checks for memory data integrity and health.
Storage: backend/cache/health_scans/
"""

import json
import os
import logging
from datetime import datetime, timezone, timedelta
from collections import Counter

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

SCANS_DIR = os.path.join(settings.cache_dir, "health_scans")

# Thresholds
STALE_DAYS = 90
STALE_STRENGTH_MAX = 3
SIMILARITY_THRESHOLD = 0.85
STRENGTH_ANOMALY_LOW = 1
STRENGTH_ANOMALY_HIGH = 10
ORPHAN_CONCEPT_THRESHOLD = 1


def _ensure_dir():
    os.makedirs(SCANS_DIR, exist_ok=True)


def _load_memories() -> list[dict]:
    """Load all memories."""
    try:
        cache_path = settings.AGENTMEMORY_CACHE
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("memories", data.get("agentmemory", []))
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ─── Health Checks ──────────────────────────────────────────────────────────

def check_empty_metadata(memories: list[dict]) -> list[dict]:
    """Check 1: Empty metadata (missing concepts, empty title)."""
    issues = []
    for mem in memories:
        mid = mem.get("id", "unknown")
        title = mem.get("title", "").strip()
        concepts = mem.get("concepts", mem.get("tags", []))

        if not title:
            issues.append({
                "check": "empty_metadata",
                "severity": "high",
                "memory_id": mid,
                "message": "Memory has empty title",
            })
        if not concepts:
            issues.append({
                "check": "empty_metadata",
                "severity": "medium",
                "memory_id": mid,
                "message": "Memory has no concepts/tags",
            })
    return issues


def check_stale_memories(memories: list[dict]) -> list[dict]:
    """Check 2: Stale memories (not updated in 90+ days, strength < 3)."""
    issues = []
    now = datetime.now(timezone.utc)

    for mem in memories:
        mid = mem.get("id", "unknown")
        strength = mem.get("strength", 0)
        updated = mem.get("updated_at", mem.get("created_at", ""))

        if not isinstance(strength, (int, float)):
            continue

        if strength < STALE_STRENGTH_MAX and updated:
            try:
                # Parse ISO date
                updated_str = updated.replace("Z", "+00:00")
                updated_dt = datetime.fromisoformat(updated_str)
                if (now - updated_dt) > timedelta(days=STALE_DAYS):
                    issues.append({
                        "check": "stale",
                        "severity": "low",
                        "memory_id": mid,
                        "message": f"Memory stale: {STALE_DAYS}+ days old, strength={strength}",
                        "days_since_update": (now - updated_dt).days,
                    })
            except (ValueError, TypeError):
                pass

    return issues


def check_duplicates(memories: list[dict]) -> list[dict]:
    """Check 3: Duplicate detection (similar content using substring matching)."""
    issues = []
    n = len(memories)

    # Simple duplicate detection: compare titles and content
    for i in range(n):
        for j in range(i + 1, n):
            title_i = memories[i].get("title", "").strip().lower()
            title_j = memories[j].get("title", "").strip().lower()

            if not title_i or not title_j:
                continue

            # Exact title match
            if title_i == title_j:
                issues.append({
                    "check": "duplicate",
                    "severity": "high",
                    "memory_id": memories[i].get("id", "unknown"),
                    "related_memory_id": memories[j].get("id", "unknown"),
                    "message": f"Exact duplicate title: '{title_i}'",
                })
                continue

            # Content similarity (simple substring check)
            content_i = memories[i].get("content", "").strip().lower()
            content_j = memories[j].get("content", "").strip().lower()

            if content_i and content_j and len(content_i) > 50 and len(content_j) > 50:
                # Check if one is a significant substring of the other
                shorter = min(content_i, content_j, key=len)
                longer = max(content_i, content_j, key=len)
                if shorter in longer and len(shorter) > 0.8 * len(longer):
                    issues.append({
                        "check": "duplicate",
                        "severity": "medium",
                        "memory_id": memories[i].get("id", "unknown"),
                        "related_memory_id": memories[j].get("id", "unknown"),
                        "message": "Potential duplicate: highly similar content",
                    })

    return issues


def check_orphaned_concepts(memories: list[dict]) -> list[dict]:
    """Check 4: Orphaned concepts (concepts used only once)."""
    issues = []
    concept_counts = Counter()

    for mem in memories:
        concepts = mem.get("concepts", mem.get("tags", []))
        for c in concepts:
            if isinstance(c, str):
                concept_counts[c.lower()] += 1

    orphaned = [c for c, count in concept_counts.items() if count <= ORPHAN_CONCEPT_THRESHOLD]

    for concept in orphaned:
        issues.append({
            "check": "orphaned_concept",
            "severity": "info",
            "concept": concept,
            "message": f"Concept '{concept}' used only once",
        })

    return issues


def check_strength_anomalies(memories: list[dict]) -> list[dict]:
    """Check 5: Strength anomalies."""
    issues = []

    for mem in memories:
        mid = mem.get("id", "unknown")
        strength = mem.get("strength")

        if strength is None:
            continue

        if isinstance(strength, (int, float)):
            if strength < STRENGTH_ANOMALY_LOW:
                issues.append({
                    "check": "strength_anomaly",
                    "severity": "medium",
                    "memory_id": mid,
                    "message": f"Very low strength: {strength}",
                    "strength": strength,
                })
            elif strength > STRENGTH_ANOMALY_HIGH:
                issues.append({
                    "check": "strength_anomaly",
                    "severity": "low",
                    "memory_id": mid,
                    "message": f"Unusually high strength: {strength}",
                    "strength": strength,
                })

    return issues


def run_full_scan() -> dict:
    """Run all health checks and compute health score."""
    memories = _load_memories()

    checks = {
        "empty_metadata": check_empty_metadata(memories),
        "stale": check_stale_memories(memories),
        "duplicates": check_duplicates(memories),
        "orphaned_concepts": check_orphaned_concepts(memories),
        "strength_anomalies": check_strength_anomalies(memories),
    }

    all_issues = []
    for check_name, issues in checks.items():
        all_issues.extend(issues)

    # Compute health score (0-100)
    total_memories = max(len(memories), 1)
    severity_weights = {"high": 3, "medium": 1.5, "low": 0.5, "info": 0.1}
    penalty = sum(severity_weights.get(issue.get("severity", "info"), 0) for issue in all_issues)
    # Normalize: ideal is 0 penalty, bad is heavily penalized
    score = max(0, min(100, 100 - (penalty / total_memories) * 10))

    result = {
        "scan_id": f"scan_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "scanned_at": _now_iso(),
        "memory_count": len(memories),
        "score": round(score, 1),
        "issues": all_issues,
        "issue_count": len(all_issues),
        "checks": {name: len(issues) for name, issues in checks.items()},
    }

    # Save scan result
    _save_scan(result)

    return result


def get_scan_summary(result: dict) -> dict:
    """Generate a summary from scan results."""
    issues_by_severity = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for issue in result.get("issues", []):
        sev = issue.get("severity", "info")
        issues_by_severity[sev] = issues_by_severity.get(sev, 0) + 1

    return {
        "score": result.get("score", 0),
        "issue_count": result.get("issue_count", 0),
        "issues_by_severity": issues_by_severity,
        "memory_count": result.get("memory_count", 0),
        "scanned_at": result.get("scanned_at"),
    }


def get_latest_scan() -> dict | None:
    """Get the most recent scan result."""
    _ensure_dir()
    scans = []
    for fname in os.listdir(SCANS_DIR):
        if fname.endswith(".json"):
            try:
                path = os.path.join(SCANS_DIR, fname)
                with open(path, "r", encoding="utf-8") as f:
                    scans.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue

    if not scans:
        return None

    scans.sort(key=lambda s: s.get("scanned_at", ""), reverse=True)
    return scans[0]


def _save_scan(result: dict) -> None:
    """Save a scan result to disk."""
    _ensure_dir()
    scan_file = os.path.join(SCANS_DIR, f"{result['scan_id']}.json")
    _atomic_write_json(scan_file, result)
    logger.info(f"Saved health scan {result['scan_id']}: score={result['score']}")

    # Clean up old scans (keep last 20)
    _cleanup_old_scans()


def _cleanup_old_scans(keep: int = 20) -> None:
    """Remove old scan files, keeping only the most recent."""
    _ensure_dir()
    files = []
    for fname in os.listdir(SCANS_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(SCANS_DIR, fname)
            files.append((fpath, os.path.getmtime(fpath)))

    files.sort(key=lambda x: x[1], reverse=True)
    for fpath, _ in files[keep:]:
        try:
            os.remove(fpath)
        except OSError:
            pass
