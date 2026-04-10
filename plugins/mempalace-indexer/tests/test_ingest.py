"""Tests for the ingest hook (stdin/stdout interface)."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "ingest.py"


def run_hook(payload: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip())


def test_bad_json_returns_empty():
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json",
        capture_output=True,
        text=True,
    )
    out = json.loads(result.stdout.strip())
    assert out == {"memories": []}


def test_empty_message_returns_empty():
    out = run_hook({"type": "ingest", "agent_id": "a1", "message": ""})
    assert out == {"memories": []}


def test_short_message_returns_empty():
    out = run_hook({"type": "ingest", "agent_id": "a1", "message": "hi"})
    assert out == {"memories": []}


def test_no_mempalace_returns_error_not_crash():
    """Without mempalace installed, ingest returns error field but doesn't crash."""
    out = run_hook({"type": "ingest", "agent_id": "a1", "message": "What are my upcoming meetings?"})
    assert "memories" in out
    assert isinstance(out["memories"], list)
    assert "error" in out


# ---------------------------------------------------------------------------
# Similarity filtering (unit-level, no mempalace needed)
# ---------------------------------------------------------------------------

def _load_ingest_module(min_similarity="0.3"):
    saved = os.environ.get("MEMPALACE_MIN_SIMILARITY")
    os.environ["MEMPALACE_MIN_SIMILARITY"] = min_similarity
    spec = importlib.util.spec_from_file_location("ingest", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if saved is None:
        os.environ.pop("MEMPALACE_MIN_SIMILARITY", None)
    else:
        os.environ["MEMPALACE_MIN_SIMILARITY"] = saved
    return mod


def test_truncate_at_word_boundary():
    mod = _load_ingest_module()
    text = "one two three four five six seven"
    result = mod.truncate_at_word(text, 15)
    assert result.endswith("...")
    assert len(result) <= 18


def test_truncate_short_unchanged():
    mod = _load_ingest_module()
    assert mod.truncate_at_word("hello", 100) == "hello"


def test_similarity_threshold_filters_results():
    """Simulate the similarity filtering logic directly."""
    mod = _load_ingest_module(min_similarity="0.5")

    results = [
        {"text": "good match", "source_file": "s1", "wing": "w1", "similarity": 0.8},
        {"text": "bad match",  "source_file": "s2", "wing": "w1", "similarity": 0.2},
        {"text": "no score",   "source_file": "s3", "wing": "w1"},
    ]

    MIN_SIMILARITY = mod.MIN_SIMILARITY
    memories = []
    for r in results:
        text = r.get("text", "")
        similarity = r.get("similarity")
        if not text:
            continue
        if similarity is not None and MIN_SIMILARITY > 0 and similarity < MIN_SIMILARITY:
            continue
        memories.append(text)

    assert "good match" in memories
    assert "bad match" not in memories
    assert "no score" in memories   # passthrough when similarity is absent


def test_similarity_zero_disables_filtering():
    mod = _load_ingest_module(min_similarity="0")
    assert mod.MIN_SIMILARITY == 0.0


def test_min_similarity_default():
    mod = _load_ingest_module()
    assert mod.MIN_SIMILARITY == 0.3
