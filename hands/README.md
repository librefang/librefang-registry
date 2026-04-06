# Hands

Hand definitions for LibreFang. Hands are pre-packaged capability bundles that compose **agents**, **tools**, **skills**, **MCP servers**, **workflows**, and **plugins** into a working application.

> "You have many hands helping you."

## Structure

```
hands/
├── devteam/
│   ├── HAND.toml          # Hand definition
│   ├── SKILL-pm.md        # Per-agent reference knowledge (PM)
│   ├── SKILL-engineer.md  # Per-agent reference knowledge (Engineer)
│   └── SKILL-qa.md        # Per-agent reference knowledge (QA)
├── browser/
│   ├── HAND.toml
│   └── SKILL.md           # Shared reference knowledge (all agents)
└── ...
```

## Composition Model

A hand composes registry resources — it doesn't reinvent them:

| Resource | How to compose | Example |
|----------|----------------|---------|
| **Agent templates** | `base = "coder"` on `[agents.*]` | Inherit prompt, model config, fallbacks from `agents/coder/agent.toml` |
| **Tools** | `tools = [...]` at hand level | All agents get these built-in tools |
| **Skills** | `skills = [...]` at hand level | Skill allowlist (empty = all) |
| **MCP servers** | `mcp_servers = [...]` at hand level | Agent interacts via MCP tools, not hardcoded API calls |
| **Workflows** | `workflow_run` tool in agent prompts | Agent calls `workflow_run bug-triage` at runtime |
| **Plugins** | `allowed_plugins = [...]` at hand level | Plugin allowlist (empty = all) |
| **Per-agent skills** | `SKILL-{role}.md` files | Different reference knowledge per agent role |
| **Per-agent capabilities** | `[agents.*.capabilities]` | Fine-grained shell/network/memory per agent |

## HAND.toml Format

```toml
id = "hand-id"
name = "Hand Name"
description = "What this hand does"
category = "development"
icon = "🔧"

# ─── Resource composition ────────────────────────────────────
tools = ["shell_exec", "file_read", "web_fetch", "workflow_run"]
mcp_servers = ["github", "sentry"]
skills = []                              # empty = all
allowed_plugins = ["todo-tracker"]

# ─── Requirements ────────────────────────────────────────────
[[requires]]
key = "git"
requirement_type = "binary"
check_value = "git"

# ─── Settings ────────────────────────────────────────────────
[[settings]]
key = "repo_url"
setting_type = "text"
default = ""

# ─── Agents ──────────────────────────────────────────────────

# Multi-agent with base template inheritance:
[agents.main]
coordinator = true
base = "planner"                         # inherits from agents/planner/agent.toml
invoke_hint = "Task coordination"

[agents.main.model]
system_prompt = """Custom prompt for this hand..."""

[agents.main.capabilities]
shell = ["gh *", "git *"]               # preserved by kernel (not overwritten)

# Single-agent (legacy):
# [agent]
# name = "my-agent"
# system_prompt = """..."""

# ─── Routing ─────────────────────────────────────────────────
[routing]
aliases = ["activate phrases"]
weak_aliases = ["keyword hints"]

# ─── Dashboard ───────────────────────────────────────────────
[dashboard]
[[dashboard.metrics]]
label = "Tasks Done"
memory_key = "metric_key"
format = "number"

# ─── i18n ────────────────────────────────────────────────────
[i18n.zh]
name = "中文名"
description = "中文描述"
```

## Current Hands (15)

| Hand | Category | Agents | Description |
|------|----------|--------|-------------|
| analytics | data | multi | Data analytics, visualization, and automated reporting |
| apitester | development | single | API testing, endpoint discovery, and load testing |
| browser | productivity | single | Web navigation, form filling, and multi-step web tasks |
| clip | content | multi | Long-form video to short clips with captions |
| collector | data | multi | Intelligence collection and change detection |
| **devteam** | **development** | **multi** | **Autonomous dev team — PM + Engineer + QA with base templates** |
| devops | development | multi | CI/CD management, monitoring, and incident response |
| lead | data | multi | Lead generation, enrichment, and scoring |
| linkedin | communication | multi | LinkedIn content creation and networking |
| predictor | data | single | Signal collection and calibrated predictions |
| reddit | communication | multi | Subreddit monitoring and content posting |
| researcher | productivity | multi | Deep research, fact-checking, and reports |
| strategist | productivity | multi | Market research and competitive analysis |
| trader | data | multi | Market intelligence and risk management |
| twitter | communication | multi | Twitter/X content creation and scheduling |

## Adding a New Hand

1. Create `hands/<name>/HAND.toml`
2. Add `SKILL.md` (shared) or `SKILL-{role}.md` (per-agent) for reference knowledge
3. Use `base = "agent-name"` to inherit from existing agent templates in `agents/`
4. Set `mcp_servers`, `skills`, `allowed_plugins` for resource composition
5. Ensure `id` matches the directory name
6. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
