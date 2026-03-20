#!/usr/bin/env python3
"""Topic-memory after_turn hook.

After each conversation turn, extracts keywords from the latest exchange,
then either merges into an existing topic cluster or creates a new one.

This hook is WRITE-ONLY -- it never returns memories.

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
MAX_TOPICS = 50
MERGE_THRESHOLD = 0.3
SUMMARY_MAX_LEN = 200

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


def save_store(agent_id, store):
    """Persist the topic store to disk."""
    os.makedirs(STORE_DIR, exist_ok=True)
    path = os.path.join(STORE_DIR, f"{agent_id}.json")
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def next_topic_id(topics):
    """Generate the next t_XXX topic ID."""
    max_num = 0
    for t in topics:
        tid = t.get("id", "")
        if tid.startswith("t_"):
            try:
                num = int(tid[2:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"t_{max_num + 1:03d}"


def build_summary(user_content, assistant_content):
    """Build a truncated summary from the latest user + assistant exchange."""
    parts = []
    if user_content:
        parts.append(f"User: {user_content.strip()}")
    if assistant_content:
        parts.append(f"Assistant: {assistant_content.strip()}")
    raw = " | ".join(parts)
    if len(raw) > SUMMARY_MAX_LEN:
        return raw[: SUMMARY_MAX_LEN - 3] + "..."
    return raw


def now_iso():
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ok_result():
    """Return the standard ok response."""
    return json.dumps({"type": "ok"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    try:
        request = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(ok_result())
        return

    agent_id = request.get("agent_id", "")
    messages = request.get("messages", [])

    if not agent_id or not isinstance(messages, list) or not messages:
        print(ok_result())
        return

    # Extract the latest user and assistant messages
    latest_user = ""
    latest_assistant = ""
    for msg in reversed(messages):
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "assistant" and not latest_assistant:
            latest_assistant = content
        elif role == "user" and not latest_user:
            latest_user = content
        if latest_user and latest_assistant:
            break

    if not latest_user and not latest_assistant:
        print(ok_result())
        return

    # Extract keywords from the combined exchange
    combined_text = f"{latest_user} {latest_assistant}"
    current_keywords = extract_keywords(combined_text)

    if not current_keywords:
        print(ok_result())
        return

    store = load_store(agent_id)
    topics = store.get("topics", [])
    timestamp = now_iso()

    # Find the best matching existing topic cluster
    best_sim = 0.0
    best_idx = -1
    for idx, topic in enumerate(topics):
        topic_kw = set(topic.get("keywords", []))
        sim = jaccard_similarity(current_keywords, topic_kw)
        if sim > best_sim:
            best_sim = sim
            best_idx = idx

    if best_sim >= MERGE_THRESHOLD and best_idx >= 0:
        # Merge into existing topic cluster
        topic = topics[best_idx]
        existing_kw = set(topic.get("keywords", []))
        merged_kw = existing_kw | current_keywords
        topic["keywords"] = sorted(merged_kw)
        topic["summary"] = build_summary(latest_user, latest_assistant)
        topic["last_seen"] = timestamp
        topic["hit_count"] = topic.get("hit_count", 0) + 1
    else:
        # Create a new topic cluster
        new_topic = {
            "id": next_topic_id(topics),
            "keywords": sorted(current_keywords),
            "summary": build_summary(latest_user, latest_assistant),
            "last_seen": timestamp,
            "hit_count": 1,
        }
        topics.append(new_topic)

    # Evict lowest hit_count topics if over capacity
    if len(topics) > MAX_TOPICS:
        topics.sort(key=lambda t: (t.get("hit_count", 0), t.get("last_seen", "")))
        topics = topics[len(topics) - MAX_TOPICS:]

    store["topics"] = topics
    save_store(agent_id, store)

    print(ok_result())


if __name__ == "__main__":
    main()
