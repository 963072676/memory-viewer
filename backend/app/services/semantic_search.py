"""Semantic search service using TF-IDF + cosine similarity (F-33).

Lightweight implementation without external dependencies.
Uses scikit-learn style TF-IDF approach but implemented with pure Python
so it works without installing heavy packages.
"""

import json
import math
import os
import re
import hashlib
from collections import Counter
from typing import Optional

from app.config import settings

# Path to store TF-IDF vectors
_VECTORS_PATH = os.path.join(settings.cache_dir, "semantic_vectors.json")

# Stopwords (English + common programming terms)
_STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "and", "but", "or",
    "nor", "not", "so", "if", "that", "this", "these", "those", "it",
    "its", "i", "me", "my", "we", "our", "you", "your", "he", "him",
    "his", "she", "her", "they", "them", "their", "what", "which", "who",
    "whom", "when", "where", "why", "how", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "no",
    "only", "same", "than", "too", "very", "just", "about", "also",
    "new", "use", "used", "using", "one", "two", "get", "set",
})


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase word stems (simple splitting)."""
    # Remove markdown/code syntax
    text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'[#*_\[\](){}|\\~>!]', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    # Split into words
    words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fff]{2,}', text.lower())
    # Filter stopwords and very short words
    return [w for w in words if w not in _STOPWORDS and len(w) >= 2]


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    """Compute term frequency (normalized by total tokens)."""
    counts = Counter(tokens)
    total = len(tokens) if tokens else 1
    return {term: count / total for term, count in counts.items()}


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    common_terms = set(vec_a.keys()) & set(vec_b.keys())
    if not common_terms:
        return 0.0
    dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class SemanticIndex:
    """In-memory TF-IDF index for semantic search."""

    def __init__(self):
        self._documents: dict[str, dict] = {}  # id -> {tokens, tf, tfidf}
        self._idf: dict[str, float] = {}
        self._doc_count = 0
        self._loaded = False

    def _load_documents(self):
        """Load all memories and build the TF-IDF index."""
        from app.services.agentmemory import get_all_memories
        memories = get_all_memories()
        self._documents = {}
        all_tokens_per_doc = []
        df_counter: Counter = Counter()  # document frequency

        for m in memories:
            mid = m.get("id", "")
            text = f"{m.get('title', '')} {m.get('content', '')} {' '.join(m.get('concepts', []))} {' '.join(m.get('tags', []))}"
            tokens = _tokenize(text)
            tf = _compute_tf(tokens)
            self._documents[mid] = {
                "title": m.get("title", ""),
                "content": m.get("content", ""),
                "type": m.get("type", ""),
                "tags": m.get("tags", []),
                "tokens": tokens,
                "tf": tf,
                "tfidf": {},
            }
            all_tokens_per_doc.append(set(tf.keys()))
            for term in tf:
                df_counter[term] += 1

        self._doc_count = len(memories)
        if self._doc_count == 0:
            self._loaded = True
            return

        # Compute IDF: log(N / (1 + df(t))) + 1 (smooth IDF)
        self._idf = {}
        for term, df in df_counter.items():
            self._idf[term] = math.log(self._doc_count / (1 + df)) + 1

        # Compute TF-IDF vectors
        for mid, doc in self._documents.items():
            doc["tfidf"] = {
                term: tf_val * self._idf.get(term, 0)
                for term, tf_val in doc["tf"].items()
            }

        self._loaded = True

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Semantic search using cosine similarity on TF-IDF vectors.

        Returns list of {id, title, type, snippet, tags, similarity}.
        """
        if not self._loaded:
            self._load_documents()

        if not query or not self._documents:
            return []

        # Compute query TF-IDF vector
        query_tokens = _tokenize(query)
        query_tf = _compute_tf(query_tokens)
        query_tfidf = {
            term: tf_val * self._idf.get(term, 0)
            for term, tf_val in query_tf.items()
        }

        if not query_tfidf:
            return []

        # Compute similarity with all documents
        scored = []
        for mid, doc in self._documents.items():
            sim = _cosine_similarity(query_tfidf, doc["tfidf"])
            if sim > 0.01:  # Minimum threshold
                scored.append({
                    "id": mid,
                    "title": doc["title"],
                    "type": doc["type"],
                    "snippet": doc["content"][:120],
                    "tags": doc["tags"],
                    "similarity": round(sim * 100, 1),  # percentage
                    "match_type": "semantic",
                })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:limit]

    def invalidate(self):
        """Force rebuild on next search."""
        self._loaded = False
        self._documents = {}


# Singleton index
_index = SemanticIndex()


def semantic_search(query: str, limit: int = 10) -> list[dict]:
    """Public API for semantic search."""
    return _index.search(query, limit)


def invalidate_index():
    """Invalidate the semantic index (call after memory create/update/delete)."""
    _index.invalidate()
