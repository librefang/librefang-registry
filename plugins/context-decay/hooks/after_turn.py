#!/usr/bin/env python3
"""Context-decay after_turn hook.

Extracts memorable statements from the conversation turn, stores new memories
or reinforces existing ones, applies time-based decay to all memories, and
prunes dead memories.

Receives via stdin:
    {"type": "after_turn", "agent_id": "...", "messages": [
        {"role": "user"|"assistant", "content": "..."}
    ]}

Prints to stdout:
    {"type": "ok"}
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

# Confidence below this gets pruned
PRUNE_THRESHOLD = 0.1

# Maximum memories per agent
MAX_MEMORIES = 100

# Initial confidence for new memories
INITIAL_CONFIDENCE = 0.8

# Confidence boost when reinforcing an existing memory
REINFORCE_BOOST = 0.1

# Minimum keyword overlap to consider memories similar
SIMILARITY_THRESHOLD = 0.5

# Maximum content length for a single memory
MAX_CONTENT_LEN = 200

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

# Patterns that indicate a memorable statement
PREFERENCE_PATTERNS = [
    re.compile(r"\bi\s+prefer\b", re.IGNORECASE),
    re.compile(r"\bi\s+like\b", re.IGNORECASE),
    re.compile(r"\bi\s+use\b", re.IGNORECASE),
    re.compile(r"\bi\s+want\b", re.IGNORECASE),
    re.compile(r"\bi\s+need\b", re.IGNORECASE),
    re.compile(r"\bi\s+always\b", re.IGNORECASE),
]

DECISION_PATTERNS = [
    re.compile(r"\blet'?s?\s+use\b", re.IGNORECASE),
    re.compile(r"\bwe\s+decided\b", re.IGNORECASE),
    re.compile(r"\bgoing\s+with\b", re.IGNORECASE),
    re.compile(r"\bwe\s+should\s+use\b", re.IGNORECASE),
    re.compile(r"\bi'?ll\s+go\s+with\b", re.IGNORECASE),
]

CORRECTION_PATTERNS = [
    re.compile(r"\bno,?\s+actually\b", re.IGNORECASE),
    re.compile(r"\bthat'?s?\s+wrong\b", re.IGNORECASE),
    re.compile(r"\bi\s+meant\b", re.IGNORECASE),
    re.compile(r"\bactually,?\s+i\b", re.IGNORECASE),
    re.compile(r"\bnot\s+that,?\s+", re.IGNORECASE),
]

# Pattern for specific facts: contains version numbers, URLs, or proper nouns
FACT_PATTERNS = [
    re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b"),  # version numbers
    re.compile(r"https?://[^\s]+"),  # URLs
    re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"),  # proper noun phrases
]


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
    """Parse an ISO 8601 timestamp string to a datetime object."""
    if not ts:
        return None
    try:
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


def next_memory_id(memories):
    """Generate the next incrementing memory ID in m_XXX format."""
    max_num = 0
    for mem in memories:
        mid = mem.get("id", "")
        if mid.startswith("m_"):
            try:
                num = int(mid[2:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"m_{max_num + 1:03d}"


def truncate(text, max_len):
    """Truncate text to max_len, appending ... if trimmed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def matches_any(text, patterns):
    """Return True if text matches any of the compiled regex patterns."""
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def extract_sentences(text):
    """Split text into sentences on common boundaries."""
    # Split on period, exclamation, question mark followed by space or end
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]


def extract_memorable_statements(messages):
    """Extract statements worth remembering from conversation messages.

    Focuses on user messages containing preferences, decisions, corrections,
    or specific facts.
    """
    statements = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "")
        if not content.strip():
            continue

        sentences = extract_sentences(content)
        for sentence in sentences:
            # Check if this sentence matches any memorable pattern
            is_memorable = (
                matches_any(sentence, PREFERENCE_PATTERNS)
                or matches_any(sentence, DECISION_PATTERNS)
                or matches_any(sentence, CORRECTION_PATTERNS)
                or matches_any(sentence, FACT_PATTERNS)
            )
            if is_memorable:
                trimmed = truncate(sentence.strip(), MAX_CONTENT_LEN)
                keywords = extract_keywords(trimmed)
                if keywords:
                    statements.append({
                        "content": trimmed,
                        "keywords": keywords,
                    })

    return statements


def find_similar_memory(memories, keywords):
    """Find an existing memory with keyword overlap above the similarity threshold.

    Returns the index of the best match, or -1 if none found.
    """
    best_idx = -1
    best_overlap = 0.0
    for i, mem in enumerate(memories):
        overlap = keyword_overlap(mem.get("keywords", []), keywords)
        if overlap > SIMILARITY_THRESHOLD and overlap > best_overlap:
            best_overlap = overlap
            best_idx = i
    return best_idx


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        request = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({"type": "ok"}))
        return

    agent_id = request.get("agent_id", "")
    messages = request.get("messages", [])

    if not agent_id or not messages:
        print(json.dumps({"type": "ok"}))
        return

    data = load_store(agent_id)
    memories = data.get("memories", [])
    now = datetime.now(timezone.utc)
    now_str = now_iso()

    # -----------------------------------------------------------------------
    # Step 1: Extract memorable statements from the conversation turn
    # -----------------------------------------------------------------------
    statements = extract_memorable_statements(messages)

    # -----------------------------------------------------------------------
    # Step 2: Store new memories or reinforce existing ones
    # -----------------------------------------------------------------------
    for stmt in statements:
        similar_idx = find_similar_memory(memories, stmt["keywords"])

        if similar_idx >= 0:
            # Reinforce existing memory
            existing = memories[similar_idx]
            existing["confidence"] = min(
                existing.get("confidence", 0.0) + REINFORCE_BOOST, 1.0
            )
            existing["content"] = stmt["content"]
            existing["keywords"] = stmt["keywords"]
            existing["last_accessed"] = now_str
            existing["access_count"] = existing.get("access_count", 0) + 1
        else:
            # Add new memory
            new_mem = {
                "id": next_memory_id(memories),
                "content": stmt["content"],
                "keywords": stmt["keywords"],
                "confidence": INITIAL_CONFIDENCE,
                "created": now_str,
                "last_accessed": now_str,
                "access_count": 0,
            }
            memories.append(new_mem)

    # -----------------------------------------------------------------------
    # Step 3: Apply decay pass to ALL memories
    # -----------------------------------------------------------------------
    for mem in memories:
        elapsed = hours_since(mem.get("last_accessed", mem.get("created", "")), now)
        mem["confidence"] = apply_decay(mem.get("confidence", 0.0), elapsed)
        # Update last_accessed to now so next decay is relative to this pass
        # (decay is applied on each hook invocation, not accumulated)
        mem["last_accessed"] = now_str

    # -----------------------------------------------------------------------
    # Step 4: Prune memories below the prune threshold
    # -----------------------------------------------------------------------
    memories = [m for m in memories if m.get("confidence", 0.0) >= PRUNE_THRESHOLD]

    # -----------------------------------------------------------------------
    # Step 5: Evict lowest-confidence memories if over capacity
    # -----------------------------------------------------------------------
    if len(memories) > MAX_MEMORIES:
        memories.sort(key=lambda m: m.get("confidence", 0.0), reverse=True)
        memories = memories[:MAX_MEMORIES]

    # -----------------------------------------------------------------------
    # Step 6: Save
    # -----------------------------------------------------------------------
    data["memories"] = memories
    save_store(agent_id, data)

    print(json.dumps({"type": "ok"}))


if __name__ == "__main__":
    main()
