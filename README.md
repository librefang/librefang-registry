# LibreFang Registry

Community-maintained content registry for [LibreFang](https://github.com/librefang/librefang) — the open-source Agent Operating System.

This repository is the **single source of truth** for all installable content definitions. Anyone can submit a PR to add new agents, hands, integrations, skills, or provider models — no changes to the LibreFang binary required.

## Overview

| Type | Count | Description |
|------|------:|-------------|
| [Hands](#hands) | 14 | User-facing "apps" — agent + tools + settings + dashboard |
| [Agents](#agents) | 32 | Autonomous agent definitions with model config and tools |
| [Integrations](#integrations) | 25 | MCP server connections (GitHub, Slack, DBs, etc.) |
| [Providers](#providers) | 49 | LLM provider & model metadata with pricing |
| [Models](#providers) | 339 | Individual model definitions across all providers |
| [Aliases](#aliases) | 70 | Short names mapped to canonical model IDs |
| [Plugins](#plugins) | 10 | Memory, guardrails, and conversation plugins |
| [Skills](#skills) | 2 | Reusable prompt templates and Python scripts |
| [Workflows](#workflows) | 9 | Pre-built multi-agent workflow definitions |
| [Templates](#templates) | 6 | Starter templates for each content type |

## Repository Structure

```
librefang-registry/
├── agents/                # Agent definitions (TOML manifests)
│   ├── hello-world/
│   │   └── agent.toml
│   ├── researcher/
│   │   └── agent.toml
│   └── ...                (32 agents)
├── hands/                 # Hand definitions (app bundles)
│   ├── browser/
│   │   ├── HAND.toml      # Metadata, tools, settings, i18n (6 languages)
│   │   └── SKILL.md       # Domain expert knowledge injected at runtime
│   ├── trader/
│   │   ├── HAND.toml
│   │   └── SKILL.md
│   └── ...                (14 hands)
├── integrations/          # MCP server integration templates
│   ├── github.toml
│   ├── slack.toml
│   └── ...                (25 integrations)
├── providers/             # LLM provider & model metadata
│   ├── anthropic.toml
│   ├── openai.toml
│   └── ...                (49 providers, 339 models)
├── plugins/               # Memory, guardrails, and utility plugins
│   ├── episodic-memory/
│   ├── guardrails/
│   └── ...                (10 plugins)
├── skills/                # Reusable skill definitions
│   ├── custom-skill-prompt/skill.toml
│   └── custom-skill-python/
├── workflows/             # Pre-built multi-agent workflow definitions
│   ├── code-review.toml
│   ├── research.toml
│   └── ...                (9 workflows)
├── templates/             # Starter templates for each content type
│   ├── agent.toml
│   ├── HAND.toml
│   └── ...                (6 templates)
├── docs/                  # Additional documentation
│   └── content-guide.md   # Content contribution guidelines
├── aliases.toml           # Global model alias mappings (70 aliases)
├── schema.toml            # Provider/model schema reference
├── scripts/
│   └── validate.py        # Content validation script
├── CONTRIBUTING.md
└── LICENSE                # MIT
```

## Content Types

### Hands

Hands are the **user-facing "apps"** in LibreFang. Each hand bundles an agent, tools, user-configurable settings, dashboard metrics, dependency checks, and i18n translations into a single deployable unit.

Every hand includes a `SKILL.md` — domain-specific expert knowledge that is injected into the agent's context at runtime, giving it deep expertise in its domain.

| Icon | Hand | Category | Description |
|:----:|------|----------|-------------|
| 📈 | analytics | data | Data collection, analysis, visualization, dashboards, and automated reporting |
| 🔌 | apitester | development | Endpoint discovery, request validation, load testing, and regression detection |
| 🌐 | browser | productivity | Web navigation, form filling, and multi-step web tasks with user approval |
| 🎬 | clip | content | Turns long-form video into viral short clips with captions and thumbnails |
| 🔍 | collector | data | Intelligence collection, change detection, and knowledge graphs |
| 👷 | devops | development | CI/CD management, infrastructure monitoring, deployment, and incident response |
| 📊 | lead | data | Lead generation, enrichment, scoring, and scheduled delivery |
| 💼 | linkedin | communication | Profile optimization, content creation, networking, and engagement |
| 🔮 | predictor | data | Signal collection, calibrated predictions, and accuracy tracking |
| 📢 | reddit | communication | Subreddit monitoring, content posting, and engagement tracking |
| 🧪 | researcher | productivity | Deep research, cross-referencing, fact-checking, and structured reports |
| 🎯 | strategist | productivity | Market research, competitive analysis, and strategic planning |
| 📈 | trader | data | Multi-signal analysis, adversarial reasoning, and risk management |
| 𝕏 | twitter | communication | Content creation, scheduled posting, engagement, and analytics |

**HAND.toml format:**

```toml
id = "browser"
name = "Browser Hand"
description = "Autonomous web browser"
category = "productivity"
icon = "🌐"
tools = ["browser_navigate", "browser_click", "browser_type"]

[routing]
aliases = ["browse", "open website"]
weak_aliases = ["web", "url"]

[[requires]]
key = "chromium"
requirement_type = "binary"
check_value = "chromium"

[[settings]]
key = "headless"
setting_type = "toggle"
default = "true"

[agent]
name = "browser-hand"
module = "builtin:chat"
system_prompt = """You are an autonomous web browser agent..."""

[dashboard]
[[dashboard.metrics]]
label = "Pages Visited"
memory_key = "pages_visited"
format = "number"

# i18n — 6 languages supported: zh, ja, ko, es, fr, de
[i18n.zh]
name = "浏览器 Hand"
description = "自主网页浏览器"
category = "生产力"

[i18n.zh.settings.headless]
label = "无头模式"
description = "在后台运行浏览器"
```

### Agents

Agent definitions describe autonomous agents with model configuration, tools, capabilities, and routing aliases.

```toml
name = "hello-world"
description = "A friendly greeting agent"
module = "builtin:chat"

[model]
provider = "default"
model = "default"
system_prompt = "You are a helpful assistant."

[capabilities]
tools = ["web_search", "file_read"]
```

**32 built-in agents:** academic-researcher, analyst, architect, assistant, code-reviewer, coder, customer-support, data-scientist, debugger, devops-lead, doc-writer, email-assistant, health-tracker, hello-world, home-automation, legal-assistant, meeting-assistant, ops, orchestrator, personal-finance, planner, recipe-assistant, recruiter, researcher, sales-assistant, security-auditor, social-media, test-engineer, translator, travel-planner, tutor, writer

### Integrations

Integration templates define [MCP](https://modelcontextprotocol.io/) server connections with transport configuration, required environment variables, and setup instructions.

```toml
id = "github"
name = "GitHub"
category = "devtools"

[transport]
type = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]

[[required_env]]
name = "GITHUB_PERSONAL_ACCESS_TOKEN"
is_secret = true
```

**25 integrations across 6 categories:**

| Category | Integrations |
|----------|-------------|
| DevTools | bitbucket, github, gitlab, jira, linear, sentry |
| Data | elasticsearch, mongodb, postgresql, redis, sqlite |
| Productivity | dropbox, gmail, google-calendar, google-drive, notion, todoist |
| Communication | discord, slack, teams |
| Cloud | aws, azure, gcp |
| AI Search | brave-search, exa-search |

### Providers

Provider files define LLM providers and their models with pricing, context windows, and capability flags. See [schema.toml](schema.toml) for the full field reference.

**49 providers** including: Anthropic, OpenAI, Google Gemini, DeepSeek, Groq, Mistral, Cohere, xAI, Together, Fireworks, Ollama (local), LM Studio (local), vLLM (self-hosted), Alibaba Coding Plan, and many more.

**339 models** with metadata for each: pricing (input/output per token), context window size, capability flags (vision, function calling, streaming), and tier classification.

### Aliases

Global model alias mappings in [aliases.toml](aliases.toml) let users reference models by short names:

```toml
"sonnet" = "claude-sonnet-4-6"
"gpt4" = "gpt-4o"
"flash" = "gemini-2.5-flash"
"deepseek" = "deepseek-chat"
```

Models can also define aliases directly in their provider TOML files, which are auto-registered at load time.

### Plugins

Plugins extend agent capabilities with memory systems, safety guardrails, and conversation utilities.

**10 plugins:** auto-summarizer, context-decay, conversation-logger, episodic-memory, guardrails, keyword-memory, sentiment-tracker, todo-tracker, topic-memory, user-profile

### Skills

Reusable prompt templates or Python scripts that agents can invoke.

```toml
[skill]
name = "meeting-agenda"
description = "Generate a structured meeting agenda"

[runtime]
type = "promptonly"

[prompt]
template = "Create a meeting agenda for: {{topic}}"
```

### Workflows

Pre-built multi-agent workflow definitions in `workflows/<name>.toml` orchestrate multiple agents for complex tasks.

**9 workflows:** brainstorm, code-review, content-pipeline, content-review, customer-support, data-pipeline, research, translate-polish, weekly-report

### Templates

Starter templates in `templates/` for creating new content. Copy a template to get started quickly:

```bash
cp templates/agent.toml agents/my-agent/agent.toml
cp templates/HAND.toml hands/my-hand/HAND.toml
```

**6 templates:** agent.toml, HAND.toml, integration.toml, plugin.toml, provider.toml, skill.toml

See also [docs/content-guide.md](docs/content-guide.md) for naming conventions and contribution guidelines.

## Usage

### Install from Registry

```bash
# Update all registry content
librefang catalog update

# Install a specific hand
librefang hand install browser

# Install a specific integration
librefang integration install github
```

### Custom Local Content

Create custom content locally without submitting to this registry:

```bash
# Custom agent
mkdir -p ~/.librefang/agents/my-agent
# Edit ~/.librefang/agents/my-agent/agent.toml

# Custom model aliases
# Add to ~/.librefang/model_catalog.toml
```

## Validation

```bash
python scripts/validate.py
```

Validates all content files for correctness: required fields, valid types, non-negative costs, no duplicate IDs.

## Contributing

1. Fork this repository
2. Add or edit content in the appropriate directory
3. Run validation: `python scripts/validate.py`
4. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions for each content type.

## License

MIT License. See [LICENSE](LICENSE).
