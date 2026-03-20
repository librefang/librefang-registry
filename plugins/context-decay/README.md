# context-decay

Time-based memory decay with relevance scoring. Memories lose confidence over time (5% per day) and are only recalled when they pass both a decay threshold and a relevance check against the current message. Implements "use it or lose it" -- recalled memories get their access timestamps refreshed.

## How it works

**After each turn**, the plugin extracts memorable statements from the conversation:

- User preferences ("I prefer...", "I use...")
- Decisions ("let's use...", "we decided...")
- Important facts (names, versions, URLs)
- Corrections ("no, actually...", "that's wrong...")

Similar memories are reinforced (confidence +0.1, cap 1.0). All memories receive a decay pass, and those below 0.1 confidence are pruned.

**On ingest**, each memory's confidence is decayed based on time elapsed, then scored for relevance to the current message via keyword overlap. The composite score `decayed_confidence * (0.5 + 0.5 * relevance)` must exceed 0.3 to be recalled. Recalled memories get their `last_accessed` timestamp updated.

## Hooks

| Hook | Script | Description |
|------|--------|-------------|
| ingest | `hooks/ingest.py` | Applies decay, scores relevance, returns top 5 memories above threshold |
| after_turn | `hooks/after_turn.py` | Extracts new memories, reinforces similar ones, prunes decayed entries |

## Storage

Memories are stored at `~/.librefang/plugins/context-decay/{agent_id}.json`. Max 100 memories per agent. Decay formula: `confidence * 0.95^(hours / 24)`.

## Usage

Installed automatically when enabled in agent configuration.
