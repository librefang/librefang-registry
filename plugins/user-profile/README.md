# user-profile

Persistent user profiling from conversation patterns. Builds a profile of user expertise areas, communication style, and technical level, then injects it as context so agents can personalize responses.

## How it works

**After each turn**, the plugin analyzes user messages to update the profile:

- **Expertise areas** -- extracts technical keywords and tracks frequency (top 20 retained)
- **Communication style** -- running average of message lengths (brief / moderate / detailed)
- **Technical level** -- scored from signals like code blocks, version numbers, tech abbreviations, and question patterns (beginner / intermediate / advanced)
- **Question ratio** -- fraction of user messages containing questions

**On ingest**, once the profile has at least 5 interactions, the plugin returns a compact profile summary as a memory fragment: `expertise=python,devops; style=detailed; level=advanced`.

## Hooks

| Hook | Script | Description |
|------|--------|-------------|
| ingest | `hooks/ingest.py` | Returns the profile summary as a memory fragment (after 5+ interactions) |
| after_turn | `hooks/after_turn.py` | Analyzes user messages to update the profile |

## Storage

Profiles are stored at `~/.librefang/plugins/user-profile/{agent_id}.json`.

## Usage

Installed automatically when enabled in agent configuration.
