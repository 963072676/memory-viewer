"""Memory Clustering service (F-40) — Automatic topic grouping via embedding similarity.

Uses TF-IDF vectors from the semantic search service for clustering.
K-Means with auto-K selection via silhouette score.
"""

import logging
import math
import time
import hashlib
import json
import os
import random
from collections import Counter
from typing import Optional

from app.config import settings
from app.services.agentmemory import get_all_memories
from app.services.semantic_search import _tokenize, _compute_tf

logger = logging.getLogger(__name__)

# Cache for cluster results
_cluster_cache: Optional[dict] = None
_cluster_cache_time: float = 0
_CACHE_TTL = 3600  # 1 hour


def _build_tfidf_vectors(memories: list[dict]) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """Build TF-IDF vectors for all memories."""
    # Tokenize all documents
    doc_tokens: dict[str, list[str]] = {}
    for mem in memories:
        mid = mem.get("id", "")
        text = f"{mem.get('title', '')} {mem.get('content', '')} {' '.join(mem.get('concepts', []))}"
        doc_tokens[mid] = _tokenize(text)

    # Compute document frequency
    doc_freq: dict[str, int] = {}
    n_docs = len(doc_tokens)
    for tokens in doc_tokens.values():
        unique = set(tokens)
        for term in unique:
            doc_freq[term] = doc_freq.get(term, 0) + 1

    # Compute TF-IDF vectors
    tfidf_vectors: dict[str, dict[str, float]] = {}
    for doc_id, tokens in doc_tokens.items():
        tf = _compute_tf(tokens)
        tfidf: dict[str, float] = {}
        for term, tf_val in tf.items():
            df = doc_freq.get(term, 1)
            idf = math.log(n_docs / df) if df > 0 else 0
            tfidf[term] = tf_val * idf
        tfidf_vectors[doc_id] = tfidf

    return tfidf_vectors, doc_freq


def _cosine_sim(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(a.keys()) & set(b.keys())
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _kmeans(vectors: list[dict[str, float]], k: int, max_iter: int = 30) -> list[int]:
    """Simple K-Means clustering. Returns cluster assignment per vector."""
    n = len(vectors)
    if n == 0:
        return []
    if k >= n:
        return list(range(n))

    # Initialize centroids using k-means++ style
    random.seed(42)
    centroids_idx = [random.randint(0, n - 1)]
    for _ in range(k - 1):
        # Choose next centroid proportional to distance
        distances = []
        for i, v in enumerate(vectors):
            min_sim = max(_cosine_sim(v, vectors[c]) for c in centroids_idx)
            distances.append(1 - min_sim)  # Distance = 1 - similarity
        total = sum(distances) or 1
        probs = [d / total for d in distances]
        r = random.random()
        cumsum = 0
        chosen = n - 1
        for i, p in enumerate(probs):
            cumsum += p
            if cumsum >= r:
                chosen = i
                break
        centroids_idx.append(chosen)

    centroids = [vectors[i] for i in centroids_idx]
    assignments = [0] * n

    for iteration in range(max_iter):
        # Assign to nearest centroid
        new_assignments = []
        for v in vectors:
            best_cluster = 0
            best_sim = -1
            for c_idx, c in enumerate(centroids):
                sim = _cosine_sim(v, c)
                if sim > best_sim:
                    best_sim = sim
                    best_cluster = c_idx
            new_assignments.append(best_cluster)

        # Check convergence
        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Update centroids (average of assigned vectors)
        for c_idx in range(k):
            members = [vectors[i] for i in range(n) if assignments[i] == c_idx]
            if not members:
                continue
            # Average the sparse vectors
            all_terms: set[str] = set()
            for m in members:
                all_terms.update(m.keys())
            new_centroid: dict[str, float] = {}
            for term in all_terms:
                new_centroid[term] = sum(m.get(term, 0) for m in members) / len(members)
            centroids[c_idx] = new_centroid

    return assignments


def _silhouette_score(vectors: list[dict[str, float]], assignments: list[int]) -> float:
    """Compute average silhouette score for clustering quality."""
    n = len(vectors)
    if n <= 1 or len(set(assignments)) <= 1:
        return 0.0

    # Sample for performance (max 200 points)
    sample_indices = list(range(min(n, 200)))
    scores = []

    for i in sample_indices:
        same_cluster = [j for j in range(n) if assignments[j] == assignments[i] and j != i]
        if not same_cluster:
            scores.append(0)
            continue

        # a(i): average distance to same cluster
        a_i = 1 - sum(_cosine_sim(vectors[i], vectors[j]) for j in same_cluster) / len(same_cluster)

        # b(i): min average distance to other clusters
        other_clusters = set(assignments) - {assignments[i]}
        b_i = float("inf")
        for c in other_clusters:
            members = [j for j in range(n) if assignments[j] == c]
            if not members:
                continue
            avg_dist = 1 - sum(_cosine_sim(vectors[i], vectors[j]) for j in members) / len(members)
            b_i = min(b_i, avg_dist)

        if max(a_i, b_i) == 0:
            scores.append(0)
        else:
            scores.append((b_i - a_i) / max(a_i, b_i))

    return sum(scores) / len(scores) if scores else 0.0


def _extract_cluster_concepts(memories: list[dict], top_n: int = 5) -> list[str]:
    """Extract top TF-IDF concepts from a cluster of memories."""
    all_tokens: list[str] = []
    for mem in memories:
        text = f"{mem.get('title', '')} {mem.get('content', '')}"
        all_tokens.extend(_tokenize(text))

    counter = Counter(all_tokens)
    return [term for term, _ in counter.most_common(top_n)]


def _generate_cluster_name(concepts: list[str]) -> str:
    """Generate a human-readable cluster name from concepts."""
    if not concepts:
        return "未分类"
    # Take top 3 concepts and join
    return " / ".join(concepts[:3]).title()


def compute_clusters(force_refresh: bool = False) -> list[dict]:
    """Compute memory clusters. Results are cached for 1 hour.
    
    AC-F40-1: Returns >=3 meaningful clusters (when enough memories).
    AC-F40-2: Each cluster has an understandable name.
    AC-F40-6: Cache invalidation on memory changes.
    """
    global _cluster_cache, _cluster_cache_time

    now = time.time()
    if not force_refresh and _cluster_cache and (now - _cluster_cache_time) < _CACHE_TTL:
        return _cluster_cache["clusters"]

    memories = get_all_memories()
    if len(memories) < 5:
        return [{
            "id": "cluster-0",
            "name": "所有记忆",
            "count": len(memories),
            "memory_ids": [m.get("id") for m in memories],
            "centroid_concepts": [],
        }]

    # Build TF-IDF vectors
    tfidf_vectors, doc_freq = _build_tfidf_vectors(memories)

    # Get vectors in order
    doc_ids = [m.get("id") for m in memories]
    vectors = [tfidf_vectors.get(did, {}) for did in doc_ids]

    # Try different K values and pick best silhouette score
    best_k = 3
    best_score = -1
    best_assignments: list[int] = []

    max_k = min(8, len(memories) // 3)
    for k in range(3, max_k + 1):
        assignments = _kmeans(vectors, k)
        score = _silhouette_score(vectors, assignments)
        if score > best_score:
            best_score = score
            best_k = k
            best_assignments = assignments

    # Build cluster results
    clusters: list[dict] = []
    for c_id in range(best_k):
        member_indices = [i for i, a in enumerate(best_assignments) if a == c_id]
        cluster_mems = [memories[i] for i in member_indices]
        concepts = _extract_cluster_concepts(cluster_mems)
        name = _generate_cluster_name(concepts)

        # Type distribution for this cluster
        type_dist = Counter(m.get("type", "unknown") for m in cluster_mems)

        clusters.append({
            "id": f"cluster-{c_id}",
            "name": name,
            "count": len(member_indices),
            "memory_ids": [doc_ids[i] for i in member_indices],
            "centroid_concepts": concepts,
            "type_distribution": dict(type_dist),
        })

    # Sort by count descending
    clusters.sort(key=lambda c: c["count"], reverse=True)

    _cluster_cache = {"clusters": clusters}
    _cluster_cache_time = now

    return clusters


def get_cluster_detail(cluster_id: str) -> Optional[dict]:
    """Get detailed info about a specific cluster."""
    clusters = compute_clusters()
    for cluster in clusters:
        if cluster["id"] == cluster_id:
            # Fetch full memory objects
            all_mems = {m.get("id"): m for m in get_all_memories()}
            cluster["memories"] = [
                all_mems[mid] for mid in cluster.get("memory_ids", [])
                if mid in all_mems
            ]
            return cluster
    return None


def invalidate_cache():
    """Invalidate cluster cache (call when memories change)."""
    global _cluster_cache, _cluster_cache_time
    _cluster_cache = None
    _cluster_cache_time = 0
