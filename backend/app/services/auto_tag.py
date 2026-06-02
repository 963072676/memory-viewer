"""AI Auto-Tagging & Summarization service (F-34).

Uses TF-IDF-based keyword extraction as the default local provider.
No external LLM needed — extracts top keywords from memory content
to suggest relevant tags and generate simple extractive summaries.
"""

import re
import math
from collections import Counter
from typing import Optional

# Stopwords for keyword extraction
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
    "also", "been", "much", "well", "back", "even", "still", "way",
    "take", "make", "like", "just", "over", "such", "use", "using",
    "used", "need", "want", "one", "two", "first", "get", "set",
    "new", "now", "see", "time", "look", "come", "go", "know",
})


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    # Remove markdown/code syntax
    text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'[#*_\[\](){}|\\~>!]', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    words = re.findall(r'[a-zA-Z0-9][a-zA-Z0-9_-]{1,}', text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) >= 2]


def _extract_keyphrases(text: str, max_tags: int = 5) -> list[str]:
    """Extract key phrases using TF scoring with phrase detection."""
    tokens = _tokenize(text)
    if not tokens:
        return []

    # Unigram TF scores
    counts = Counter(tokens)
    total = len(tokens)

    # Also extract bigrams for compound terms
    bigrams = []
    for i in range(len(tokens) - 1):
        bigrams.append(f"{tokens[i]}_{tokens[i+1]}")
    bigram_counts = Counter(bigrams)

    # Score bigrams higher if both words appear frequently
    scores = {}
    for term, count in counts.items():
        scores[term] = count / total

    for bigram, count in bigram_counts.items():
        if count >= 2:  # Only consider repeated bigrams
            scores[bigram] = (count / total) * 1.5  # Boost bigrams

    # Sort by score and clean up
    sorted_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    result = []
    seen = set()
    for term, score in sorted_terms:
        # Convert bigram back to readable form
        clean = term.replace("_", "-")
        # Avoid duplicates and substrings
        if clean not in seen and not any(clean in s or s in clean for s in seen):
            result.append(clean)
            seen.add(clean)
        if len(result) >= max_tags:
            break

    return result


def _generate_summary(title: str, content: str, max_sentences: int = 2) -> str:
    """Generate an extractive summary by picking the most informative sentences."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    if not sentences:
        return content[:200] if content else ""

    # If content is short enough, return as-is
    if len(content) <= 200:
        return content

    # Score sentences by: position, length, keyword density
    title_tokens = set(_tokenize(title))
    scored = []
    for i, sentence in enumerate(sentences):
        if len(sentence.strip()) < 10:
            continue
        sent_tokens = set(_tokenize(sentence))
        # Position score: first sentences are better
        pos_score = 1.0 / (i + 1)
        # Title overlap: sentences related to title are better
        title_overlap = len(sent_tokens & title_tokens) / max(len(title_tokens), 1)
        # Length score: prefer medium-length sentences
        words = len(sentence.split())
        len_score = min(1.0, words / 20) if words <= 30 else max(0.3, 1.0 - (words - 30) / 100)
        total_score = pos_score * 0.4 + title_overlap * 0.4 + len_score * 0.2
        scored.append((total_score, sentence.strip()))

    scored.sort(key=lambda x: x[0], reverse=True)
    # Return top N sentences in original order
    top = [s for _, s in scored[:max_sentences]]
    # Sort by original position
    ordered = sorted(top, key=lambda s: content.find(s))
    return " ".join(ordered)


def suggest_tags(title: str, content: str, concepts: list[str] = None, existing_tags: list[str] = None, max_tags: int = 5) -> list[str]:
    """Suggest tags for a memory based on content analysis.

    Uses TF-IDF keyword extraction to suggest relevant tags.
    Returns a list of suggested tag strings.
    """
    text = f"{title} {content}"
    if concepts:
        text += " " + " ".join(concepts)

    extracted = _extract_keyphrases(text, max_tags=max_tags * 2)

    # Filter out existing tags
    existing_set = set(t.lower() for t in (existing_tags or []))
    filtered = [t for t in extracted if t.lower() not in existing_set]

    return filtered[:max_tags]


def summarize_memory(title: str, content: str) -> str:
    """Generate a 1-2 sentence summary of a memory."""
    return _generate_summary(title, content, max_sentences=2)


def bulk_auto_tag(memories: list[dict], max_tags_per_memory: int = 5) -> list[dict]:
    """Process multiple memories and suggest tags for each.

    Returns list of {id, title, suggested_tags}.
    """
    results = []
    for m in memories:
        mid = m.get("id", "")
        title = m.get("title", "")
        content = m.get("content", "")
        concepts = m.get("concepts", [])
        existing = m.get("tags", [])

        suggested = suggest_tags(title, content, concepts, existing, max_tags_per_memory)
        results.append({
            "id": mid,
            "title": title,
            "suggested_tags": suggested,
        })

    return results
