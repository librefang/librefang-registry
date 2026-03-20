#!/usr/bin/env python3
"""Episodic memory after_turn hook.

Maintains the episode store by tracking topic continuity across turns.
Detects topic shifts via Jaccard similarity between the current turn's
keywords and the running episode's keywords. When a shift is detected
(and the current episode has enough messages), the episode is completed
and a new one starts.

This hook is write-only -- it never returns memories.

Receives via stdin:
    {"type": "after_turn", "agent_id": "...", "messages": [...]}

Prints to stdout:
    {"type": "ok"}
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Stopwords & keyword extraction (identical logic to ingest.py)
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

# Topic shift detection threshold
TOPIC_SHIFT_THRESHOLD = 0.1

# Minimum messages before allowing topic shift completion
MIN_MESSAGES_FOR_COMPLETION = 4

# Maximum completed episodes to retain
MAX_EPISODES = 30

# Maximum summary length in characters
MAX_SUMMARY_LEN = 150


def extract_keywords(text):
    """Extract deduplicated keywords from text."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]", text)
    seen = set()
    keywords = []
    for w in words:
        lower = w.lower()
        if lower not in STOPWORDS and len(lower) >= MIN_WORD_LEN and lower not in seen:
            seen.add(lower)
            keywords.append(lower)
    return keywords


def extract_keywords_from_messages(messages):
    """Extract combined keywords from all messages in the turn."""
    all_keywords = []
    seen = set()
    for msg in messages:
        content = msg.get("content", "")
        for kw in extract_keywords(content):
            if kw not in seen:
                seen.add(kw)
                all_keywords.append(kw)
    return all_keywords


def extract_first_user_message(messages):
    """Return the content of the first user message, or empty string."""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "").strip()
            if content:
                return content
    return ""


def extract_latest_user_message(messages):
    """Return the content of the last user message, or empty string."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "").strip()
            if content:
                return content
    return ""


def jaccard_similarity(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0  # Both empty = identical (no topic)
    a = set(set_a)
    b = set(set_b)
    intersection = a & b
    union = a | b
    if not union:
        return 1.0
    return len(intersection) / len(union)


def generate_summary(current_episode):
    """Generate a short episode summary from stored episode context.

    Uses the first_user_message and latest_user_message fields that are
    accumulated on the current_episode during normal (non-shift) turns.
    This avoids the problem of using the wrong turn's messages when a
    topic shift is detected.
    """
    parts = []

    first_msg = current_episode.get("first_user_message", "")
    if first_msg:
        parts.append(first_msg)

    latest_msg = current_episode.get("latest_user_message", "")
    if latest_msg and latest_msg != first_msg:
        parts.append(latest_msg)

    if not parts:
        # Fallback: summarize from keywords
        keywords = current_episode.get("keywords", [])
        if keywords:
            return f"Discussion about: {', '.join(keywords[:8])}"
        return "No summary available"

    summary = " | ".join(parts)
    if len(summary) > MAX_SUMMARY_LEN:
        summary = summary[: MAX_SUMMARY_LEN - 3] + "..."
    return summary


def now_iso():
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def next_episode_id(episodes):
    """Generate the next episode ID in ep_XXX format."""
    max_num = 0
    for ep in episodes:
        ep_id = ep.get("id", "")
        if ep_id.startswith("ep_"):
            try:
                num = int(ep_id[3:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"ep_{max_num + 1:03d}"


def get_store_path(agent_id):
    """Return the filesystem path for an agent's episode store."""
    store_dir = os.path.join(
        os.path.expanduser("~"), ".librefang", "plugins", "episodic-memory"
    )
    os.makedirs(store_dir, exist_ok=True)
    return os.path.join(store_dir, f"{agent_id}.json")


def load_episode_store(agent_id):
    """Load the episode store, returning a default structure on any failure."""
    store_path = get_store_path(agent_id)
    if not os.path.isfile(store_path):
        return {"episodes": [], "current_episode": None}
    try:
        with open(store_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure expected structure
        if not isinstance(data, dict):
            return {"episodes": [], "current_episode": None}
        if "episodes" not in data:
            data["episodes"] = []
        return data
    except (json.JSONDecodeError, OSError):
        return {"episodes": [], "current_episode": None}


def save_episode_store(agent_id, store):
    """Persist the episode store to disk."""
    store_path = get_store_path(agent_id)
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def evict_oldest_episodes(episodes):
    """Keep only the MAX_EPISODES most recent completed episodes."""
    if len(episodes) <= MAX_EPISODES:
        return episodes
    # Sort by ended date descending, keep newest
    episodes.sort(
        key=lambda ep: ep.get("ended", ep.get("started", "")),
        reverse=True,
    )
    return episodes[:MAX_EPISODES]


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

    store = load_episode_store(agent_id)
    turn_keywords = extract_keywords_from_messages(messages)

    current = store.get("current_episode")

    if current is None:
        # No active episode -- start one
        ep_id = next_episode_id(store["episodes"])
        first_msg = extract_first_user_message(messages)
        store["current_episode"] = {
            "id": ep_id,
            "started": now_iso(),
            "keywords": turn_keywords,
            "messages_seen": 1,
            "last_keywords": turn_keywords,
            "first_user_message": first_msg,
            "latest_user_message": first_msg,
        }
        save_episode_store(agent_id, store)
        print(json.dumps({"type": "ok"}))
        return

    # Compare current turn keywords against running episode keywords
    episode_keywords = current.get("keywords", [])
    similarity = jaccard_similarity(turn_keywords, episode_keywords)
    messages_seen = current.get("messages_seen", 0)

    if similarity < TOPIC_SHIFT_THRESHOLD and messages_seen >= MIN_MESSAGES_FOR_COMPLETION:
        # Topic shift detected -- complete the current episode
        completed_episode = {
            "id": current.get("id", next_episode_id(store["episodes"])),
            "started": current.get("started", now_iso()),
            "ended": now_iso(),
            "keywords": episode_keywords,
            "summary": generate_summary(current),
            "message_count": messages_seen,
            "status": "completed",
        }
        store["episodes"].append(completed_episode)
        store["episodes"] = evict_oldest_episodes(store["episodes"])

        # Start a new episode with current turn's keywords
        new_id = next_episode_id(store["episodes"])
        first_msg = extract_first_user_message(messages)
        store["current_episode"] = {
            "id": new_id,
            "started": now_iso(),
            "keywords": turn_keywords,
            "messages_seen": 1,
            "last_keywords": turn_keywords,
            "first_user_message": first_msg,
            "latest_user_message": first_msg,
        }
    else:
        # No topic shift -- update the current episode
        existing_kw_set = set(episode_keywords)
        merged_keywords = list(episode_keywords)
        for kw in turn_keywords:
            if kw not in existing_kw_set:
                existing_kw_set.add(kw)
                merged_keywords.append(kw)

        current["keywords"] = merged_keywords
        current["messages_seen"] = messages_seen + 1
        current["last_keywords"] = turn_keywords

        # Track user messages for summary generation
        latest_msg = extract_latest_user_message(messages)
        if latest_msg:
            current["latest_user_message"] = latest_msg
            if not current.get("first_user_message"):
                current["first_user_message"] = latest_msg

        store["current_episode"] = current

    save_episode_store(agent_id, store)
    print(json.dumps({"type": "ok"}))


if __name__ == "__main__":
    main()
