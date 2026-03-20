#!/usr/bin/env python3
"""Episodic memory ingest hook.

Loads the episode store for the current agent, scores completed episodes
against the incoming message's keywords using keyword overlap ratio, and
returns the top 2 matching episodes as contextual memories.

This hook is read-only -- it never modifies the episode store.

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
# Stopwords & keyword extraction
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

# Minimum overlap ratio to consider an episode relevant
MIN_OVERLAP = 0.2

# Maximum episodes to return
MAX_RESULTS = 2


def extract_keywords(text):
    """Extract deduplicated keywords from text.

    Lowercases, removes stopwords, filters words shorter than MIN_WORD_LEN.
    """
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]", text)
    seen = set()
    keywords = []
    for w in words:
        lower = w.lower()
        if lower not in STOPWORDS and len(lower) >= MIN_WORD_LEN and lower not in seen:
            seen.add(lower)
            keywords.append(lower)
    return keywords


def load_episode_store(agent_id):
    """Load the episode store JSON for the given agent. Returns None on failure."""
    store_dir = os.path.join(
        os.path.expanduser("~"), ".librefang", "plugins", "episodic-memory"
    )
    store_path = os.path.join(store_dir, f"{agent_id}.json")
    if not os.path.isfile(store_path):
        return None
    try:
        with open(store_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def score_episode(episode_keywords, query_keywords):
    """Compute keyword overlap ratio between an episode and the query.

    overlap_ratio = |intersection| / |union|  (Jaccard similarity)
    """
    if not episode_keywords or not query_keywords:
        return 0.0
    ep_set = set(episode_keywords)
    q_set = set(query_keywords)
    intersection = ep_set & q_set
    union = ep_set | q_set
    if not union:
        return 0.0
    return len(intersection) / len(union)


def main():
    try:
        request = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({"type": "ingest_result", "memories": []}))
        return

    message = request.get("message", "")
    agent_id = request.get("agent_id", "")

    if not message.strip() or not agent_id:
        print(json.dumps({"type": "ingest_result", "memories": []}))
        return

    query_keywords = extract_keywords(message)
    if not query_keywords:
        print(json.dumps({"type": "ingest_result", "memories": []}))
        return

    store = load_episode_store(agent_id)
    if not store:
        print(json.dumps({"type": "ingest_result", "memories": []}))
        return

    episodes = store.get("episodes", [])

    # Score only completed episodes
    scored = []
    for ep in episodes:
        if ep.get("status") != "completed":
            continue
        overlap = score_episode(ep.get("keywords", []), query_keywords)
        if overlap > MIN_OVERLAP:
            scored.append((overlap, ep))

    # Sort by overlap descending, take top MAX_RESULTS
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:MAX_RESULTS]

    memories = []
    for _score, ep in top:
        timestamp = ep.get("ended", ep.get("started", "unknown"))
        summary = ep.get("summary", "no summary")
        memories.append({
            "content": f"[episodic-memory] Past episode ({timestamp}): {summary}"
        })

    print(json.dumps({"type": "ingest_result", "memories": memories}))


if __name__ == "__main__":
    main()
