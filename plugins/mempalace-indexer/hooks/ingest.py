#!/usr/bin/env python3
"""MemPalace ingest hook for LibreFang.

Searches MemPalace for memories relevant to the incoming user message
and injects them into the agent's context as MemoryFragments.

Input (stdin):  {"type": "ingest", "agent_id": "...", "message": "user text"}
Output (stdout): {"memories": [{"content": "..."}]}

Install: librefang plugin install mempalace-indexer && librefang plugin requirements mempalace-indexer
"""
import sys
import json
import os

# ---------------------------------------------------------------------------
# Configuration: read from LIBREFANG_PLUGIN_CONFIG (written by the runtime),
# fall back to individual environment variables for direct invocation.
# ---------------------------------------------------------------------------

def _load_config():
    cfg_path = os.environ.get("LIBREFANG_PLUGIN_CONFIG")
    if cfg_path:
        try:
            with open(cfg_path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {}

_cfg = _load_config()


def _cfg_str(key, env_key, default):
    if key in _cfg:
        return str(_cfg[key])
    return os.environ.get(env_key, default)


def _cfg_int(key, env_key, default):
    if key in _cfg:
        try:
            return int(_cfg[key])
        except (TypeError, ValueError):
            pass
    return int(os.environ.get(env_key, default))


def _cfg_float(key, env_key, default):
    if key in _cfg:
        try:
            return float(_cfg[key])
        except (TypeError, ValueError):
            pass
    return float(os.environ.get(env_key, default))


PALACE_PATH = _cfg_str("palace_path", "MEMPALACE_PALACE_PATH",
                        os.path.expanduser("~/.mempalace/palace"))
MAX_MEMORY_CHARS = _cfg_int("max_chars", "MEMPALACE_MAX_CHARS", "300")

# MemPalace returns similarity in [0, 1] — higher means more relevant.
# Results below MIN_SIMILARITY are too dissimilar to be useful.
# Set to 0 (or MEMPALACE_MIN_SIMILARITY=0) to disable filtering.
MIN_SIMILARITY = _cfg_float("min_similarity", "MEMPALACE_MIN_SIMILARITY", "0.3")
N_RESULTS = _cfg_int("n_results", "MEMPALACE_N_RESULTS", "5")


def emit(obj):
    """Write JSON response to stdout with trailing newline."""
    json.dump(obj, sys.stdout)
    sys.stdout.write("\n")


def truncate_at_word(text, max_len):
    """Truncate text at nearest word boundary."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len // 2:
        return truncated[:last_space] + "..."
    return truncated + "..."


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        emit({"memories": []})
        return

    message = data.get("message", "")
    if not message or len(message) < 5:
        emit({"memories": []})
        return

    try:
        from mempalace.searcher import search_memories

        results = search_memories(message, PALACE_PATH, n_results=N_RESULTS)

        memories = []
        for r in results.get("results", []):
            text = r.get("text", "")
            wing = r.get("wing", "") or "memory"
            room = r.get("room", "")
            similarity = r.get("similarity")

            if not text:
                continue

            # Filter out low-relevance results when the backend provides a score.
            # similarity=None means the backend didn't return one — allow through.
            if similarity is not None and MIN_SIMILARITY > 0 and similarity < MIN_SIMILARITY:
                continue

            snippet = truncate_at_word(text, MAX_MEMORY_CHARS)
            # Use wing/room (semantically meaningful) instead of raw source filename.
            label = f"{wing}/{room}" if room else wing
            memories.append({"content": f"[{label}] {snippet}"})

        emit({"memories": memories})
    except Exception as e:
        emit({"memories": [], "error": str(e)})


if __name__ == "__main__":
    main()
