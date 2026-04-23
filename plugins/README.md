# Plugins Registry

Plugins extend agent behavior through lifecycle hooks. They can inject memories into context before a turn, perform side-effect processing after a turn, or do both. Unlike skills (which add knowledge) or MCP servers (which add tools), plugins run as Python scripts that intercept the agent loop.

## File Format

Each plugin lives in its own subdirectory:

```
plugins/
└── <plugin-name>/
    ├── plugin.toml          # required: plugin manifest
    ├── hooks/
    │   ├── ingest.py        # called on each incoming user message
    │   └── after_turn.py    # called after each completed agent turn
    └── requirements.txt     # Python dependencies (prefer stdlib-only)
```

### plugin.toml format

```toml
name = "episodic-memory"         # must match directory name
version = "0.1.0"
description = "Episode-based memory segmentation and recall for cross-conversation context continuity"
author = "librefang"

[hooks]
ingest = "hooks/ingest.py"       # optional
after_turn = "hooks/after_turn.py" # optional

[i18n.zh]
name = "情景记忆"
description = "基于情景的记忆分段与召回，实现跨会话的上下文延续。"
```

## Hook Protocol

Hooks communicate with the agent runtime via stdin/stdout JSON lines.

### ingest hook

Receives the incoming user message and returns zero or more memory objects to inject into the agent's context for this turn:

```
stdin:  {"type": "ingest", "agent_id": "abc123", "session_id": "...", "message": "user message text"}
stdout: {"type": "ingest_result", "memories": [{"content": "Relevant fact from earlier session"}]}
```

### after_turn hook

Receives the full turn transcript after the agent responds. Used for persistence (saving summaries, updating profiles, appending logs):

```
stdin:  {"type": "after_turn", "agent_id": "abc123", "session_id": "...", "messages": [...]}
stdout: {"type": "ok"}
```

## Installing and Using Plugins

```bash
# List all available plugins
librefang catalog plugins

# Install a plugin globally
librefang plugin install episodic-memory

# Enable a plugin for a specific agent
librefang plugin enable episodic-memory --agent coder

# Disable a plugin for an agent
librefang plugin disable episodic-memory --agent coder

# List plugins active for an agent
librefang plugin list --agent coder
```

Hands can also declare an `allowed_plugins` list in `HAND.toml`, which restricts which installed plugins are active within that hand.

## All Plugins (12 total)

| Name | Version | Hooks | Description |
|------|---------|-------|-------------|
| auto-summarizer | 0.1.0 | ingest, after_turn | Maintains a running conversation summary to help agents handle long conversations without losing context |
| context-decay | 0.1.0 | ingest, after_turn | Time-based memory decay with relevance scoring for natural context forgetting |
| conversation-logger | 0.1.0 | after_turn | Logs all conversations to JSONL files for auditing, analytics, and debugging |
| episodic-memory | 0.1.0 | ingest, after_turn | Episode-based memory segmentation and recall for cross-conversation context continuity |
| guardrails | 0.1.0 | ingest | Safety filter that detects potentially harmful content patterns and injects warnings into agent context |
| keyword-memory | 0.1.0 | ingest | Extracts keywords and named entities from user messages and returns them as contextual memories |
| mempalace-indexer | 0.3.0 | ingest, after_turn | Auto-indexes conversations into MemPalace and recalls relevant memories — no API keys, no cloud |
| sentiment-tracker | 0.1.0 | ingest | Analyzes user message sentiment and injects emotional context so agents can respond with appropriate tone |
| todo-tracker | 0.1.0 | ingest, after_turn | Detects action items and tasks mentioned in conversations, persists them, and recalls them as context |
| topic-memory | 0.1.0 | ingest, after_turn | Topic-aware memory recall with keyword clustering for cross-conversation context |
| user-profile | 0.1.0 | ingest, after_turn | Persistent user profiling from conversation patterns for personalized agent responses |

Note: the `guardrails` and `mempalace-indexer` plugins have no `after_turn` hook; `conversation-logger` has no `ingest` hook.

## Hook Execution Order

For each agent turn, the runtime executes hooks in this order:

1. All `ingest` hooks run (in plugin installation order) — memories are collected and merged
2. Agent turn executes with the injected context
3. All `after_turn` hooks run (in plugin installation order)

## Adding a New Plugin

1. Create `plugins/<name>/plugin.toml` with `name`, `version`, `description`, and `[hooks]`.
2. Add hook scripts under `hooks/` for each declared hook.
3. Keep hooks fast (under 500 ms) — they run synchronously on every turn.
4. List Python dependencies in `requirements.txt`; prefer standard library where possible.
5. Run `python scripts/validate.py`.
6. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
