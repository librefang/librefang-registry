#!/usr/bin/env python3
"""Topic-memory ingest hook.

Reads the topic store for the given agent and returns the top matching
topic summaries based on Jaccard similarity between the incoming message
keywords and each stored topic cluster.

This hook is READ-ONLY -- it never modifies the topic store.

Receives via stdin:
    {"type": "ingest", "agent_id": "...", "message": "user message text"}

Prints to stdout:
    {"type": "ingest_result", "memories": [{"content": "..."}]}
"""
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Stopwords & constants
# ---------------------------------------------------------------------------

STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "it", "its", "i", "me", "my", "you", "your", "he", "she", "we",
    "they", "them", "their", "this", "that", "these", "those", "what",
    "which", "who", "how", "when", "where", "why", "if", "then", "so",
    "not", "no", "just", "also", "very", "too", "about", "up", "out",
    "all", "some", "any", "each", "every", "into", "over", "after",
})

MIN_WORD_LEN = 3
MAX_RESULTS = 3
MIN_SIMILARITY = 0.15

STORE_DIR = os.path.join(os.path.expanduser("~"), ".librefang", "plugins", "topic-memory")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def extract_keywords(text):
    """Extract lowercase keywords from text, filtering stopwords and short tokens."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]", text)
    seen = set()
    keywords = set()
    for w in words:
        lower = w.lower()
        if lower not in STOPWORDS and len(lower) >= MIN_WORD_LEN and lower not in seen:
            seen.add(lower)
            keywords.add(lower)
    return keywords


def jaccard_similarity(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    return intersection / union


def load_store(agent_id):
    """Load the topic store JSON for an agent. Returns empty structure on any error."""
    path = os.path.join(STORE_DIR, f"{agent_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("topics"), list):
            return data
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return {"topics": []}


def empty_result():
    """Return an empty ingest result."""
    return json.dumps({"type": "ingest_result", "memories": []})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    try:
        request = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(empty_result())
        return

    message = request.get("message", "")
    agent_id = request.get("agent_id", "")

    if not message.strip() or not agent_id:
        print(empty_result())
        return

    msg_keywords = extract_keywords(message)
    if not msg_keywords:
        print(empty_result())
        return

    store = load_store(agent_id)
    topics = store.get("topics", [])

    # Score each topic cluster against the current message keywords
    scored = []
    for topic in topics:
        topic_kw = set(topic.get("keywords", []))
        sim = jaccard_similarity(msg_keywords, topic_kw)
        if sim >= MIN_SIMILARITY:
            scored.append((sim, topic))

    # Sort descending by similarity, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:MAX_RESULTS]

    memories = []
    for _sim, topic in top:
        summary = topic.get("summary", "")
        if summary:
            memories.append({"content": f"[topic-memory] Related context: {summary}"})

    print(json.dumps({"type": "ingest_result", "memories": memories}))


if __name__ == "__main__":
    main()
