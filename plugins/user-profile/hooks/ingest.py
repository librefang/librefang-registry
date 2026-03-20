#!/usr/bin/env python3
"""User-profile ingest hook.

Reads the persisted user profile for the given agent and, when enough
interaction data has been collected (>= 5 interactions), returns a
compact profile summary as injected memory so the agent can personalise
its responses.

This hook is READ-ONLY -- it never modifies the profile store.

Receives via stdin:
    {"type": "ingest", "agent_id": "...", "message": "user message text"}

Prints to stdout:
    {"type": "ingest_result", "memories": [{"content": "..."}]}
"""
import json
import os
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STORE_DIR = os.path.join(
    os.path.expanduser("~"), ".librefang", "plugins", "user-profile"
)

MIN_INTERACTIONS = 5
MAX_SUMMARY_LEN = 200
TOP_EXPERTISE = 5

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def empty_result():
    """Return an empty ingest result."""
    return json.dumps({"type": "ingest_result", "memories": []})


def load_profile(agent_id):
    """Load the profile JSON for an agent. Returns None on any error."""
    path = os.path.join(STORE_DIR, f"{agent_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("interaction_count"), int):
            return data
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return None


def message_length_bucket(avg_len):
    """Classify average message length into a human-readable bucket."""
    if avg_len < 50:
        return "brief"
    elif avg_len <= 200:
        return "moderate"
    else:
        return "detailed"


def build_summary(profile):
    """Build a compact profile summary string (max MAX_SUMMARY_LEN chars)."""
    parts = []

    # Top expertise areas
    expertise = profile.get("expertise_areas", {})
    if expertise:
        sorted_areas = sorted(expertise.items(), key=lambda x: x[1], reverse=True)
        top = [area for area, _count in sorted_areas[:TOP_EXPERTISE]]
        parts.append("expertise=" + ",".join(top))

    # Communication style
    avg_len = profile.get("avg_message_length", 0)
    parts.append("style=" + message_length_bucket(avg_len))

    # Technical level
    tech_level = profile.get("technical_level", "")
    if tech_level:
        parts.append("level=" + tech_level)

    # Question ratio
    q_ratio = profile.get("question_ratio", 0.0)
    if q_ratio > 0.5:
        parts.append("asks-many-questions")

    summary = "; ".join(parts)
    if len(summary) > MAX_SUMMARY_LEN:
        summary = summary[:MAX_SUMMARY_LEN - 3] + "..."
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    try:
        request = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(empty_result())
        return

    agent_id = request.get("agent_id", "")
    if not agent_id:
        print(empty_result())
        return

    profile = load_profile(agent_id)
    if profile is None:
        print(empty_result())
        return

    interaction_count = profile.get("interaction_count", 0)
    if interaction_count < MIN_INTERACTIONS:
        print(empty_result())
        return

    summary = build_summary(profile)
    if not summary:
        print(empty_result())
        return

    memory = {"content": f"[user-profile] User context: {summary}"}
    print(json.dumps({"type": "ingest_result", "memories": [memory]}))


if __name__ == "__main__":
    main()
