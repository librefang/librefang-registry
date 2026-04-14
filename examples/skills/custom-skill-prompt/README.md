# meeting-agenda

Generate a structured meeting agenda from a topic and duration. Pure prompt engineering — no code required.

## Configuration

| Field | Value |
|-------|-------|
| Type | `promptonly` |
| Entry | N/A (template-only) |

## Input

- **topic** (string, required) — The meeting topic
- **duration_minutes** (string, required) — Meeting duration in minutes

## Usage

```bash
librefang skill test ./skills/custom-skill-prompt --input '{"topic": "Q1 planning", "duration_minutes": "30"}'
```
