"""Cross-Agent Knowledge Insights service (F-62).

Compare memories across agent profiles.
Find overlap, gaps, complementary knowledge, and shared themes.
"""

import json
import logging
import math
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.services.agentmemory import _atomic_write_json

logger = logging.getLogger(__name__)

INSIGHTS_CACHE_PATH = os.path.join(settings.cache_dir, "cross_agent_insights.json")
CACHE_TTL_SECONDS = 4 * 3600  # 4 hours


def _load_insights_cache() -> dict:
    try:
        with open(INSIGHTS_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Check TTL
            if time.time() - data.get("_cached_at", 0) < CACHE_TTL_SECONDS:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}


def _save_insights_cache(data: dict) -> None:
    data["_cached_at"] = time.time()
    os.makedirs(os.path.dirname(INSIGHTS_CACHE_PATH), exist_ok=True)
    _atomic_write_json(INSIGHTS_CACHE_PATH, data)


def invalidate_cache() -> None:
    """Invalidate the insights cache."""
    try:
        os.remove(INSIGHTS_CACHE_PATH)
    except FileNotFoundError:
        pass


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


def _get_profiles() -> list[str]:
    """Get available agent profiles."""
    try:
        profiles_dir = settings.HERMES_PROFILES_DIR
        if os.path.isdir(profiles_dir):
            return [d for d in os.listdir(profiles_dir) if os.path.isdir(os.path.join(profiles_dir, d))]
    except Exception:
        pass
    return ["chief-agent", "daily", "dev-worker", "pm-orchestrator", "qa-worker"]


def _group_memories_by_profile(memories: list[dict]) -> dict[str, list[dict]]:
    """Group memories by their agent profile."""
    grouped = defaultdict(list)
    for mem in memories:
        profile = mem.get("profile", mem.get("agent", "unknown"))
        grouped[profile].append(mem)
    return dict(grouped)


def _tokenize(text: str) -> list[str]:
    """Simple tokenization: lowercase, split, remove short words."""
    import re
    text = text.lower()
    words = re.findall(r'\b[a-z0-9]{3,}\b', text)
    # Remove common stop words
    stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "has", "this", "that", "with", "have", "from", "they", "been", "said", "each", "which", "their", "will", "other", "about", "many", "then", "them", "would", "like", "more", "some", "these", "what"}
    return [w for w in words if w not in stop_words]


def _compute_tf(text: str) -> dict[str, float]:
    """Compute term frequency for a text."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {term: count / total for term, count in counts.items()}


def _cosine_similarity(tf1: dict[str, float], tf2: dict[str, float]) -> float:
    """Compute cosine similarity between two TF vectors."""
    if not tf1 or not tf2:
        return 0.0

    all_terms = set(tf1.keys()) | set(tf2.keys())
    dot_product = sum(tf1.get(t, 0) * tf2.get(t, 0) for t in all_terms)
    norm1 = math.sqrt(sum(v * v for v in tf1.values()))
    norm2 = math.sqrt(sum(v * v for v in tf2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def _memory_text(memory: dict) -> str:
    """Extract text content from a memory for analysis."""
    parts = []
    if memory.get("title"):
        parts.append(memory["title"])
    if memory.get("content"):
        parts.append(memory["content"])
    if memory.get("summary"):
        parts.append(memory["summary"])
    concepts = memory.get("concepts", [])
    if concepts:
        parts.extend(concepts)
    tags = memory.get("tags", [])
    if tags:
        parts.extend(tags)
    return " ".join(parts)


# ─── Analysis Functions ──────────────────────────────────────────────────────

def compute_overlap(threshold: float = 0.85, use_cache: bool = True) -> dict:
    """Find knowledge overlap across agent profiles."""
    if use_cache:
        cache = _load_insights_cache()
        if "overlap" in cache:
            return cache["overlap"]

    memories = _load_memories()
    grouped = _group_memories_by_profile(memories)
    profiles = sorted(grouped.keys())

    # Pre-compute TF vectors for all memories
    memory_vectors = {}
    for mem in memories:
        mid = mem.get("id", "")
        memory_vectors[mid] = _compute_tf(_memory_text(mem))

    # Compare across profiles
    overlaps = []
    profile_overlap_matrix = {}

    for i, p1 in enumerate(profiles):
        for j, p2 in enumerate(profiles):
            if j <= i:
                continue

            pair_key = f"{p1}|{p2}"
            pair_overlaps = []

            for m1 in grouped[p1]:
                for m2 in grouped[p2]:
                    v1 = memory_vectors.get(m1.get("id", ""), {})
                    v2 = memory_vectors.get(m2.get("id", ""), {})
                    sim = _cosine_similarity(v1, v2)

                    if sim >= threshold:
                        pair_overlaps.append({
                            "memory_1": {"id": m1.get("id"), "title": m1.get("title", "")[:50], "profile": p1},
                            "memory_2": {"id": m2.get("id"), "title": m2.get("title", "")[:50], "profile": p2},
                            "similarity": round(sim, 4),
                        })

            profile_overlap_matrix[pair_key] = len(pair_overlaps)
            overlaps.extend(pair_overlaps)

    # Build matrix for visualization
    matrix = {}
    for p1 in profiles:
        matrix[p1] = {}
        for p2 in profiles:
            if p1 == p2:
                matrix[p1][p2] = len(grouped.get(p1, []))
            else:
                key1 = f"{p1}|{p2}"
                key2 = f"{p2}|{p1}"
                matrix[p1][p2] = profile_overlap_matrix.get(key1, profile_overlap_matrix.get(key2, 0))

    result = {
        "total_overlap_pairs": len(overlaps),
        "threshold": threshold,
        "profiles": profiles,
        "matrix": matrix,
        "overlaps": overlaps[:100],  # Limit for API response
    }

    # Cache
    cache = _load_insights_cache()
    cache["overlap"] = result
    _save_insights_cache(cache)

    return result


def compute_gaps(use_cache: bool = True) -> dict:
    """Analyze knowledge gaps per profile."""
    if use_cache:
        cache = _load_insights_cache()
        if "gaps" in cache:
            return cache["gaps"]

    memories = _load_memories()
    grouped = _group_memories_by_profile(memories)
    profiles = sorted(grouped.keys())

    # Extract topics per profile using TF-IDF-like approach
    profile_topics = {}
    for profile, mems in grouped.items():
        all_text = " ".join(_memory_text(m) for m in mems)
        tf = _compute_tf(all_text)
        # Top 20 terms as "topics"
        top_terms = sorted(tf.items(), key=lambda x: x[1], reverse=True)[:20]
        profile_topics[profile] = {term: score for term, score in top_terms}

    # Find gaps: topics present in other profiles but missing in each
    gaps = {}
    for profile in profiles:
        my_topics = set(profile_topics.get(profile, {}).keys())
        other_topics = set()
        for p, topics in profile_topics.items():
            if p != profile:
                other_topics.update(topics.keys())

        missing = other_topics - my_topics
        # Rank by frequency in other profiles
        topic_importance = {}
        for term in missing:
            count = sum(1 for p, topics in profile_topics.items() if p != profile and term in topics)
            topic_importance[term] = count

        sorted_gaps = sorted(topic_importance.items(), key=lambda x: x[1], reverse=True)[:10]

        # Find example memories from other profiles for each gap topic
        gap_details = []
        for term, count in sorted_gaps:
            examples = []
            for p, mems in grouped.items():
                if p != profile:
                    for m in mems[:3]:
                        if term in _memory_text(m).lower():
                            examples.append({"profile": p, "id": m.get("id"), "title": m.get("title", "")[:50]})
                            break
            gap_details.append({
                "topic": term,
                "present_in_profiles": count,
                "examples": examples[:3],
            })

        gaps[profile] = {
            "missing_topics_count": len(missing),
            "gaps": gap_details,
        }

    result = {
        "profiles": profiles,
        "gaps": gaps,
    }

    cache = _load_insights_cache()
    cache["gaps"] = result
    _save_insights_cache(cache)

    return result


def compute_themes(use_cache: bool = True) -> dict:
    """Identify collective themes across all profiles."""
    if use_cache:
        cache = _load_insights_cache()
        if "themes" in cache:
            return cache["themes"]

    memories = _load_memories()
    grouped = _group_memories_by_profile(memories)
    profiles = sorted(grouped.keys())

    # Compute TF per profile
    profile_tfs = {}
    for profile, mems in grouped.items():
        all_text = " ".join(_memory_text(m) for m in mems)
        profile_tfs[profile] = _compute_tf(all_text)

    # Find themes: terms appearing in multiple profiles
    all_terms = set()
    for tf in profile_tfs.values():
        all_terms.update(tf.keys())

    theme_scores = []
    for term in all_terms:
        # How many profiles mention this term
        contributing_profiles = []
        for profile, tf in profile_tfs.items():
            if term in tf:
                contributing_profiles.append(profile)

        if len(contributing_profiles) >= 2:
            # Score: number of profiles * average TF
            avg_tf = sum(profile_tfs[p].get(term, 0) for p in contributing_profiles) / len(contributing_profiles)
            score = len(contributing_profiles) * avg_tf

            theme_scores.append({
                "term": term,
                "score": round(score, 6),
                "profile_count": len(contributing_profiles),
                "profiles": contributing_profiles,
            })

    theme_scores.sort(key=lambda x: x["score"], reverse=True)
    top_themes = theme_scores[:30]

    result = {
        "total_themes": len(theme_scores),
        "profiles": profiles,
        "themes": top_themes,
    }

    cache = _load_insights_cache()
    cache["themes"] = result
    _save_insights_cache(cache)

    return result


def compute_specialization(use_cache: bool = True) -> dict:
    """Compute specialization scores per profile.

    Score: 0 = diverse knowledge, 1 = highly focused.
    Based on entropy of topic distribution.
    """
    if use_cache:
        cache = _load_insights_cache()
        if "specialization" in cache:
            return cache["specialization"]

    memories = _load_memories()
    grouped = _group_memories_by_profile(memories)

    # Extract topic concepts per profile
    profile_topic_dist = {}
    for profile, mems in grouped.items():
        topic_counter = Counter()
        for m in mems:
            # Use concepts, tags, and extracted terms
            for concept in m.get("concepts", []):
                topic_counter[concept.lower()] += 1
            for tag in m.get("tags", []):
                topic_counter[tag.lower()] += 1

            # Extract terms from content
            terms = _tokenize(_memory_text(m))
            for t in terms[:10]:  # Top terms per memory
                topic_counter[t] += 1

        total = sum(topic_counter.values())
        if total > 0:
            profile_topic_dist[profile] = {t: c / total for t, c in topic_counter.items()}
        else:
            profile_topic_dist[profile] = {}

    # Compute entropy and specialization
    specializations = {}
    for profile, dist in profile_topic_dist.items():
        if not dist:
            specializations[profile] = {
                "specialization_score": 0,
                "entropy": 0,
                "memory_count": len(grouped.get(profile, [])),
                "top_topics": [],
                "topic_count": 0,
            }
            continue

        # Entropy: -sum(p * log2(p))
        entropy = -sum(p * math.log2(p) for p in dist.values() if p > 0)

        # Normalize entropy: max entropy = log2(n) where n = number of distinct topics
        max_entropy = math.log2(max(len(dist), 1))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Specialization = 1 - normalized_entropy
        specialization = 1 - normalized_entropy

        top_topics = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:10]

        specializations[profile] = {
            "specialization_score": round(specialization, 4),
            "entropy": round(entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "memory_count": len(grouped.get(profile, [])),
            "top_topics": [{"term": t, "weight": round(w, 4)} for t, w in top_topics],
            "topic_count": len(dist),
        }

    result = {
        "profiles": sorted(specializations.keys()),
        "specializations": specializations,
    }

    cache = _load_insights_cache()
    cache["specialization"] = result
    _save_insights_cache(cache)

    return result


def refresh_all() -> dict:
    """Force recalculation of all insights."""
    invalidate_cache()
    overlap = compute_overlap(use_cache=False)
    gaps = compute_gaps(use_cache=False)
    themes = compute_themes(use_cache=False)
    specialization = compute_specialization(use_cache=False)

    return {
        "status": "refreshed",
        "overlap_pairs": overlap.get("total_overlap_pairs", 0),
        "gap_profiles": len(gaps.get("gaps", {})),
        "themes_count": themes.get("total_themes", 0),
        "profiles_analyzed": len(specialization.get("profiles", [])),
        "refreshed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
