# Hands Registry

Hands are pre-packaged capability bundles that compose agents, tools, skills, MCP servers, and plugins into a working application. Installing a hand gives you a complete, ready-to-use workflow — not just a single agent.

> "You have many hands helping you."

A hand can contain one agent (single-agent) or multiple coordinated agents (multi-agent). Each agent in a multi-agent hand can have its own role-specific skills, model config, and capability restrictions.

## File Format

Each hand lives in its own subdirectory:

```
hands/
├── researcher/
│   ├── HAND.toml          # required: hand definition
│   └── SKILL.md           # optional: shared reference knowledge for all agents
├── devteam/
│   ├── HAND.toml
│   ├── SKILL-pm.md        # optional: role-specific knowledge for PM agent
│   ├── SKILL-engineer.md  # optional: role-specific knowledge for Engineer agent
│   └── SKILL-qa.md        # optional: role-specific knowledge for QA agent
```

### HAND.toml format

```toml
id = "researcher"
version = "1.1.1"
name = "Researcher Hand"
description = "Autonomous deep researcher — exhaustive investigation, cross-referencing, fact-checking, and structured reports"
category = "productivity"           # productivity | development | data | content | communication
icon = "lucide:flask-conical"

# Tools available to all agents in this hand
tools = [
  "shell_exec", "file_read", "file_write", "web_fetch", "web_search",
  "memory_store", "memory_recall", "knowledge_query", "event_publish",
]

# MCP servers all agents can use
mcp_servers = ["github"]

# Skills allowlist (empty = all available)
skills = []

# Plugin allowlist
allowed_plugins = ["todo-tracker", "auto-summarizer"]

# ─── Routing ──────────────────────────────────────────────────────────────────
[routing]
aliases = ["deep research", "investigate", "fact check"]    # exact activation phrases
weak_aliases = ["research", "look into"]                    # keyword hints

# ─── Configurable settings ────────────────────────────────────────────────────
[[settings]]
key = "research_depth"
label = "Research Depth"
description = "How exhaustive each investigation should be"
setting_type = "select"            # select | toggle | text
default = "thorough"

[[settings.options]]
value = "quick"
label = "Quick (5-10 sources, 1 pass)"

[[settings.options]]
value = "thorough"
label = "Thorough (20-30 sources, cross-referenced)"

# ─── Single-agent definition ──────────────────────────────────────────────────
[agent]
name = "researcher"
base = "researcher"               # inherits from agents/researcher/agent.toml

[agent.model]
system_prompt = """Custom prompt override..."""

# ─── Multi-agent definition (alternative to [agent]) ─────────────────────────
[agents.pm]
coordinator = true
base = "planner"                  # inherits from agents/planner/agent.toml
invoke_hint = "Task coordination and issue triage"

[agents.engineer]
base = "coder"
invoke_hint = "Implementation"

[agents.qa]
base = "test-engineer"
invoke_hint = "Quality assurance and validation"

# ─── Dashboard metrics ────────────────────────────────────────────────────────
[dashboard]
[[dashboard.metrics]]
label = "Reports Written"
memory_key = "metric_reports_written"
format = "number"

# ─── i18n ─────────────────────────────────────────────────────────────────────
[i18n.zh]
name = "研究员"
description = "自主深度研究员 — 详尽调查、交叉核实、事实核查与结构化报告"
```

## Installing and Using Hands

```bash
# List all available hands
librefang catalog hands

# Install a hand
librefang hand install researcher

# Install with a specific agent name
librefang hand install researcher --name my-researcher

# List installed hands
librefang hand list

# Remove a hand
librefang hand remove my-researcher
```

## All Hands (18 total)

### Productivity

| ID | Name | Category | Description |
|----|------|----------|-------------|
| researcher | Researcher Hand | productivity | Autonomous deep researcher — exhaustive investigation, cross-referencing, fact-checking, and structured reports |
| strategist | Strategist Hand | productivity | Autonomous strategy analyst — market research, competitive analysis, business planning, and strategic recommendations |
| wiki | Wiki Hand | productivity | LLM-maintained personal knowledge base — builds an Obsidian-compatible wiki from raw sources with provenance tracking |
| browser | Browser Hand | productivity | Autonomous web browser — navigates sites, fills forms, clicks buttons, and completes multi-step web tasks |

### Development

| ID | Name | Category | Description |
|----|------|----------|-------------|
| devteam | Dev Team | development | Autonomous software development team — PM triages issues, Engineer implements, QA validates |
| devops | DevOps Hand | development | Autonomous DevOps engineer — CI/CD management, infrastructure monitoring, deployment automation, and incident response |
| apitester | API Tester Hand | development | Autonomous API testing agent — endpoint discovery, request validation, load testing, and regression detection |

### Data

| ID | Name | Category | Description |
|----|------|----------|-------------|
| analytics | Analytics Hand | data | Autonomous data analytics agent — data collection, analysis, visualization, dashboards, and automated reporting |
| collector | Collector Hand | data | Autonomous intelligence collector — monitors any target continuously with change detection and knowledge graphs |
| lead | Lead Hand | data | Autonomous lead generation — discovers, enriches, and delivers qualified leads on a schedule |
| predictor | Predictor Hand | data | Autonomous future predictor — collects signals, builds reasoning chains, makes calibrated predictions, and tracks accuracy |
| trader | Trading Hand | data | Autonomous market intelligence and trading engine — multi-signal analysis, adversarial bull/bear reasoning, and strict risk management |

### Content

| ID | Name | Category | Description |
|----|------|----------|-------------|
| clip | Clip Hand | content | Turns long-form video into viral short clips with captions and thumbnails |
| creator | Creator Hand | content | AI media studio — generates images, videos, music, and speech from text prompts |

### Communication

| ID | Name | Category | Description |
|----|------|----------|-------------|
| linkedin | LinkedIn Hand | communication | Autonomous LinkedIn manager — profile optimization, content creation, networking, and professional engagement |
| reddit | Reddit Hand | communication | Autonomous Reddit manager — monitors subreddits, posts content, replies to threads, and tracks engagement |
| twitter | Twitter Hand | communication | Autonomous Twitter/X manager — content creation, scheduled posting, engagement, and performance tracking |

### Data (additional)

| ID | Name | Category | Description |
|----|------|----------|-------------|
| clip | Clip Hand | content | Turns long-form video into viral short clips with captions and thumbnails |

## Resource Composition Summary

| Resource | How to compose | Notes |
|----------|----------------|-------|
| Agent templates | `base = "coder"` on `[agents.*]` | Inherits prompt, model config, fallbacks from `agents/coder/agent.toml` |
| Tools | `tools = [...]` at hand level | All agents in the hand share these built-in tools |
| Skills | `skills = [...]` at hand level | Empty list means all available skills are allowed |
| MCP servers | `mcp_servers = [...]` at hand level | Agent interacts via MCP tools, not hardcoded API calls |
| Plugins | `allowed_plugins = [...]` at hand level | Empty list means all installed plugins are allowed |
| Per-agent knowledge | `SKILL-{role}.md` files | Different reference prompts per agent role |
| Per-agent capabilities | `[agents.*.capabilities]` | Fine-grained shell / network / memory per agent |

## Adding a New Hand

1. Create `hands/<name>/HAND.toml` with at least `id`, `name`, `description`, and `category`.
2. Add `SKILL.md` (shared) or `SKILL-{role}.md` (per-agent) files for reference knowledge.
3. Use `base = "agent-name"` in each `[agents.*]` block to inherit from existing agent templates.
4. Specify `mcp_servers`, `skills`, and `allowed_plugins` for resource composition.
5. Ensure `id` matches the directory name.
6. Run `python scripts/validate.py`.
7. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
