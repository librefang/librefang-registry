#!/usr/bin/env python3
"""User-profile after_turn hook.

Analyses user messages from the completed turn and updates the persisted
user profile with extracted signals: expertise areas, message length
statistics, question ratio, and inferred technical level.

This hook is WRITE-ONLY -- it updates the profile store but never returns
memories.

Receives via stdin:
    {"type": "after_turn", "agent_id": "...", "messages": [...]}

    Each message: {"role": "user"|"assistant", "content": "..."}

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

STORE_DIR = os.path.join(
    os.path.expanduser("~"), ".librefang", "plugins", "user-profile"
)

MAX_EXPERTISE_ENTRIES = 20
MIN_KEYWORD_LEN = 3

# Technical abbreviations that signal intermediate+ level
TECH_ABBREVIATIONS = frozenset({
    "api", "cli", "sdk", "orm", "sql", "css", "html", "http", "https",
    "jwt", "oauth", "ssr", "csr", "dom", "cdn", "dns", "tcp", "udp",
    "grpc", "wasm", "yaml", "toml", "json", "xml", "cicd", "gpu",
    "cpu", "ram", "ssd", "tls", "ssh", "llm", "rag", "mlops", "etl",
    "crud", "rest", "graphql", "ide", "vcs", "iot", "saas", "paas",
})

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
    "been", "before", "between", "both", "down", "during", "few", "get",
    "got", "here", "him", "his", "her", "like", "make", "many", "more",
    "most", "much", "new", "now", "old", "one", "only", "other", "our",
    "own", "same", "say", "see", "still", "such", "take", "than",
    "there", "thing", "think", "time", "use", "used", "using", "want",
    "way", "well", "work", "know", "really", "right", "going", "back",
})

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ok_result():
    """Return an ok result."""
    return json.dumps({"type": "ok"})


def load_profile(agent_id):
    """Load the profile JSON for an agent. Returns default structure on any error."""
    path = os.path.join(STORE_DIR, f"{agent_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("interaction_count"), int):
            return data
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return {
        "interaction_count": 0,
        "expertise_areas": {},
        "avg_message_length": 0.0,
        "question_ratio": 0.0,
        "technical_level": "beginner",
        "last_updated": "",
    }


def save_profile(agent_id, profile):
    """Persist profile to disk."""
    os.makedirs(STORE_DIR, exist_ok=True)
    path = os.path.join(STORE_DIR, f"{agent_id}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def extract_keywords(text):
    """Extract meaningful keywords from text, filtering stopwords."""
    # Handle hyphenated compound terms and regular words
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]", text)
    keywords = []
    seen = set()
    for w in words:
        lower = w.lower()
        if lower not in STOPWORDS and len(lower) >= MIN_KEYWORD_LEN and lower not in seen:
            seen.add(lower)
            keywords.append(lower)
    return keywords


def has_code_blocks(text):
    """Check if text contains code blocks or backtick references."""
    return bool(re.search(r"```|`[^`]+`", text))


def has_version_numbers(text):
    """Check if text contains version references like v3.2, Python 3.12, etc."""
    return bool(re.search(r"v\d+\.\d+|(?<!\w)\d+\.\d+\.\d+", text))


def has_tech_abbreviations(text):
    """Check if text contains known technical abbreviations."""
    words = set(re.findall(r"\b[a-zA-Z]{2,6}\b", text))
    lower_words = {w.lower() for w in words}
    return bool(lower_words & TECH_ABBREVIATIONS)


def has_basic_questions(text):
    """Check if text contains beginner-style 'what is' / 'explain' patterns."""
    lower = text.lower()
    return bool(re.search(r"\bwhat\s+is\b|\bexplain\b|\bwhat\s+are\b", lower))


def average_word_length(text):
    """Compute average word length in the text."""
    words = re.findall(r"[a-zA-Z]+", text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def infer_technical_level(text):
    """Infer technical level from a single message. Returns a score.

    Score >= 3 -> "advanced"
    Score 1-2  -> "intermediate"
    Score <= 0 -> "beginner"
    """
    score = 0

    if has_code_blocks(text):
        score += 2
    if has_version_numbers(text):
        score += 1
    if has_tech_abbreviations(text):
        score += 1
    if has_basic_questions(text):
        score -= 1
    if average_word_length(text) > 5.5:
        score += 1

    return score


def tech_level_from_score(score):
    """Map a numeric score to a technical level label."""
    if score >= 3:
        return "advanced"
    elif score >= 1:
        return "intermediate"
    else:
        return "beginner"


def prune_expertise(expertise, max_entries):
    """Keep only the top max_entries expertise areas by count."""
    if len(expertise) <= max_entries:
        return expertise
    sorted_items = sorted(expertise.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_items[:max_entries])


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

    if not agent_id or not isinstance(messages, list):
        print(ok_result())
        return

    # Filter to user messages only
    user_messages = []
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                user_messages.append(content)

    if not user_messages:
        print(ok_result())
        return

    profile = load_profile(agent_id)

    old_count = profile["interaction_count"]
    new_count = old_count + len(user_messages)

    # --- Expertise areas ---
    expertise = profile.get("expertise_areas", {})
    for msg in user_messages:
        keywords = extract_keywords(msg)
        for kw in keywords:
            expertise[kw] = expertise.get(kw, 0) + 1

    expertise = prune_expertise(expertise, MAX_EXPERTISE_ENTRIES)
    profile["expertise_areas"] = expertise

    # --- Average message length (running average) ---
    old_avg = profile.get("avg_message_length", 0.0)
    total_new_len = sum(len(msg) for msg in user_messages)
    if old_count == 0:
        new_avg = total_new_len / len(user_messages)
    else:
        # Weighted running average: combine old aggregate with new messages
        old_total = old_avg * old_count
        new_avg = (old_total + total_new_len) / new_count
    profile["avg_message_length"] = round(new_avg, 1)

    # --- Question ratio (running ratio) ---
    old_ratio = profile.get("question_ratio", 0.0)
    questions_in_batch = sum(1 for msg in user_messages if "?" in msg)
    if old_count == 0:
        new_ratio = questions_in_batch / len(user_messages)
    else:
        old_question_count = round(old_ratio * old_count)
        new_ratio = (old_question_count + questions_in_batch) / new_count
    profile["question_ratio"] = round(new_ratio, 3)

    # --- Technical level (weighted towards recent) ---
    total_score = 0
    for msg in user_messages:
        total_score += infer_technical_level(msg)
    avg_score = total_score / len(user_messages)

    # Blend with historical level: map old level to a score, then average
    level_to_score = {"beginner": 0, "intermediate": 1.5, "advanced": 3}
    old_level_score = level_to_score.get(profile.get("technical_level", "beginner"), 0)
    if old_count == 0:
        blended_score = avg_score
    else:
        # Give 70% weight to history, 30% to this batch
        blended_score = 0.7 * old_level_score + 0.3 * avg_score
    profile["technical_level"] = tech_level_from_score(blended_score)

    # --- Bookkeeping ---
    profile["interaction_count"] = new_count
    profile["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    save_profile(agent_id, profile)
    print(ok_result())


if __name__ == "__main__":
    main()
