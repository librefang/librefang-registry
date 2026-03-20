# topic-memory

Topic-aware memory recall using keyword clustering. Tracks conversation topics per agent and recalls related context when similar topics arise in future conversations.

## How it works

**After each turn**, the plugin extracts keywords from user and assistant messages, then either merges them into an existing topic cluster (Jaccard similarity > 0.3) or creates a new one. Each cluster stores a keyword set, a summary, a hit count, and a last-seen timestamp.

**On ingest**, the plugin scores all stored topic clusters against the incoming message keywords using Jaccard similarity and returns the top 3 matches (threshold > 0.15) as contextual memories.

This gives agents cross-conversation topic awareness -- if a user discussed Python async patterns last week, bringing up `asyncio` today will recall that context.

## Hooks

| Hook | Script | Description |
|------|--------|-------------|
| ingest | `hooks/ingest.py` | Scores stored topics against message keywords, returns top matches |
| after_turn | `hooks/after_turn.py` | Extracts keywords, merges or creates topic clusters |

## Storage

Topic clusters are stored at `~/.librefang/plugins/topic-memory/{agent_id}.json`. Max 50 clusters per agent (lowest hit-count evicted when full).

## Usage

Installed automatically when enabled in agent configuration.
