# Skills

Reusable skill definitions for LibreFang agents. A skill is either a prompt
template or a code script that an agent can invoke to perform a specific task.

## File Convention

Every skill directory **must** contain a `SKILL.md` (the entry point).
A `skill.toml` is **optional** and only needed for structured metadata that
does not fit in Markdown frontmatter (runtime, input schema, version, tags).

```
skills/
├── docker/
│   └── SKILL.md              # Prompt-only expert — no skill.toml needed
├── custom-skill-prompt/
│   ├── SKILL.md              # Prompt body + name/description
│   └── skill.toml            # Runtime + input schema
└── custom-skill-python/
    ├── SKILL.md              # Overview (prompt body unused)
    ├── skill.toml            # Runtime = python, entry = main.py
    └── main.py
```

### `SKILL.md` (required)

The source of truth for the skill's prompt and identity. Must start with YAML
frontmatter containing at least `name` and `description`:

```markdown
---
name: docker
description: Docker expert for containers, Compose, and Dockerfiles.
---

You are a Docker specialist. You help users build, run, debug, and optimize
containers...
```

This format is compatible with Claude Code skills, so a `SKILL.md` authored
here can be dropped into other tools without modification.

### `skill.toml` (optional)

Add one only when you need to declare any of:

- `[runtime]` — `promptonly` / `python` / `node` / `shell` (default is `promptonly`)
- `[input]` — typed input parameter schema
- `version`, `author`, `tags` — structured metadata

```toml
[skill]
name = "meeting-agenda"
version = "0.1.0"
description = "Generate a structured meeting agenda from a topic and duration."
tags = ["meeting", "productivity"]

[runtime]
type = "promptonly"

[input]
topic = { type = "string", description = "The meeting topic", required = true }
duration_minutes = { type = "string", description = "Duration in minutes", required = true }
```

**Consistency rule:** if both files exist, `skill.name` and `skill.description`
in `skill.toml` must match the `name` and `description` in `SKILL.md`'s
frontmatter. The validator enforces this to prevent drift.

**Do not duplicate the prompt body in TOML.** The prompt lives in `SKILL.md`;
`skill.toml` is for metadata the prompt cannot express.

## Testing Skills Locally

```bash
librefang skill test ./skills/custom-skill-prompt \
  --input '{"topic": "Q1 planning", "duration_minutes": "30"}'
```

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`) and the prompt body.
2. If you need `[runtime]`, `[input]`, or structured metadata, add `skills/<name>/skill.toml`.
3. Add implementation files (`main.py`, etc.) when `runtime` is not `promptonly`.
4. Run `python scripts/validate.py`.
5. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
