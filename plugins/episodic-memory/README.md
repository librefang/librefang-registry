# episodic-memory

Episode-based conversation segmentation and cross-session recall. Automatically detects topic shifts to split conversations into discrete episodes, then recalls relevant past episodes when similar topics arise.

## How it works

**After each turn**, the plugin tracks a "current episode" with accumulated keywords. When the Jaccard similarity between the current turn's keywords and the running episode keywords drops below 0.1 (and the episode has at least 4 messages), it marks the episode as completed with a summary and starts a new one.

**On ingest**, the plugin scores all completed episodes against the incoming message keywords and returns the top 2 matches (overlap > 0.2) as contextual memories including the episode timestamp and summary.

This gives agents episodic recall -- "last time we discussed Docker deployment, we configured nginx as a reverse proxy."

## Hooks

| Hook | Script | Description |
|------|--------|-------------|
| ingest | `hooks/ingest.py` | Scores completed episodes against message keywords, returns top matches |
| after_turn | `hooks/after_turn.py` | Tracks current episode, detects topic shifts, segments conversations |

## Storage

Episodes are stored at `~/.librefang/plugins/episodic-memory/{agent_id}.json`. Max 30 completed episodes per agent (oldest evicted when full).

## Usage

Installed automatically when enabled in agent configuration.
