#!/usr/bin/env python3
"""Context-decay ingest hook.

Loads the memory store for the current agent, applies time-based decay to
all memories, scores them for relevance to the incoming message, and returns
the top matches above the recall threshold.

This hook updates last_accessed timestamps for recalled memories to implement
"use it or lose it" dynamics -- the one exception where ingest modifies storage.

Receives via stdin:
    {"type": "ingest", "agent_id": "...", "message": "user message text"}

Prints to stdout:
    {"type": "ingest_result", "memories": [{"content": "..."}]}
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Decay: 5% confidence loss per day
DECAY_FACTOR = 0.95

# Minimum final_score to recall a memory
RECALL_THRESHOLD = 0.3

# Maximum memories to return per ingest
MAX_RECALL = 5

# Minimum keyword length
MIN_WORD_LEN = 3

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_keywords(text):
    """Extract deduplicated lowercase keywords from text."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]", text)
    seen = set()
    keywords = []
    for w in words:
        lower = w.lower()
        if lower not in STOPWORDS and len(lower) >= MIN_WORD_LEN and lower not in seen:
            seen.add(lower)
            keywords.append(lower)
    return keywords


def store_dir():
    """Return the storage directory path for context-decay."""
    return os.path.join(
        os.path.expanduser("~"), ".librefang", "plugins", "context-decay"
    )


def store_path(agent_id):
    """Return the JSON store file path for a given agent."""
    return os.path.join(store_dir(), f"{agent_id}.json")


def load_store(agent_id):
    """Load the memory store for an agent. Returns default on failure."""
    path = store_path(agent_id)
    if not os.path.isfile(path):
        return {"memories": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "memories" not in data:
            return {"memories": []}
        return data
    except (json.JSONDecodeError, OSError):
        return {"memories": []}


def save_store(agent_id, data):
    """Persist the memory store for an agent."""
    dirpath = store_dir()
    os.makedirs(dirpath, exist_ok=True)
    path = store_path(agent_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def now_iso():
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def parse_iso(ts):
    """Parse an ISO 8601 timestamp string to a datetime object.

    Handles both +00:00 and Z suffixes. Returns None on failure.
    """
    if not ts:
        return None
    try:
        # Replace Z suffix for compatibility with fromisoformat on older Python
        cleaned = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except (ValueError, TypeError):
        return None


def hours_since(ts_str, now):
    """Calculate hours elapsed between a timestamp string and now."""
    dt = parse_iso(ts_str)
    if dt is None:
        return 0.0
    delta = now - dt
    return max(delta.total_seconds() / 3600.0, 0.0)


def apply_decay(confidence, hours_elapsed):
    """Apply exponential decay: confidence * 0.95^(hours / 24)."""
    if hours_elapsed <= 0:
        return confidence
    return confidence * (DECAY_FACTOR ** (hours_elapsed / 24.0))


def keyword_overlap(keywords_a, keywords_b):
    """Compute Jaccard similarity between two keyword lists."""
    if not keywords_a or not keywords_b:
        return 0.0
    set_a = set(keywords_a)
    set_b = set(keywords_b)
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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

    data = load_store(agent_id)
    memories = data.get("memories", [])

    if not memories:
        print(json.dumps({"type": "ingest_result", "memories": []}))
        return

    now = datetime.now(timezone.utc)
    scored = []
    store_modified = False

    for mem in memories:
        # Apply time-based decay
        elapsed = hours_since(mem.get("last_accessed", mem.get("created", "")), now)
        decayed = apply_decay(mem.get("confidence", 0.0), elapsed)

        # Score relevance via keyword overlap
        relevance = keyword_overlap(mem.get("keywords", []), query_keywords)

        # Composite score: decayed confidence weighted with relevance
        final_score = decayed * (0.5 + 0.5 * relevance)

        if final_score > RECALL_THRESHOLD:
            scored.append((final_score, decayed, mem))

    # Sort by final_score descending, take top MAX_RECALL
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:MAX_RECALL]

    result_memories = []
    for final_score, decayed, mem in top:
        confidence_pct = int(round(decayed * 100))
        content = mem.get("content", "")
        result_memories.append({
            "content": f"[context-decay] Recalled ({confidence_pct}%): {content}"
        })

        # Update last_accessed and save back -- "use it or lose it"
        mem["last_accessed"] = now_iso()
        mem["access_count"] = mem.get("access_count", 0) + 1
        store_modified = True

    # Persist access timestamp updates
    if store_modified:
        save_store(agent_id, data)

    print(json.dumps({"type": "ingest_result", "memories": result_memories}))


if __name__ == "__main__":
    main()
