# LibreFang Registry

Community-maintained content registry for [LibreFang](https://github.com/librefang/librefang) -- the open-source Agent Operating System.

This repository is the single source of truth for all installable content definitions. Anyone can submit a PR to add new agents, hands, integrations, skills, or provider models -- no changes to the LibreFang binary required.

## Structure

```
librefang-registry/
├── agents/             # Agent definitions (TOML manifests)
│   ├── hello-world/agent.toml
│   ├── researcher/agent.toml
│   └── ...             (33 agents)
├── hands/              # Hand definitions (TOML + docs)
│   ├── browser/HAND.toml
│   ├── trader/HAND.toml
│   └── ...             (14 hands)
├── integrations/       # MCP server integration templates
│   ├── github.toml
│   ├── slack.toml
│   └── ...             (25 integrations)
├── skills/             # Reusable skill definitions
│   ├── custom-skill-prompt/skill.toml
│   └── custom-skill-python/
├── providers/          # LLM provider & model metadata
│   ├── anthropic.toml
│   ├── openai.toml
│   └── ...             (46 providers, 190+ models)
├── plugins/            # Plugin packages
├── aliases.toml        # Global model alias mappings
├── schema.toml         # Provider/model schema reference
├── scripts/
│   └── validate.py     # Validation script
├── CONTRIBUTING.md
└── LICENSE             # MIT
```

## Content Types

### Agents

Agent definitions in `agents/<name>/agent.toml` describe autonomous agents with their model config, tools, capabilities, and routing aliases.

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

### Hands

Hands in `hands/<name>/HAND.toml` are higher-level application bundles -- the user-facing "apps" in LibreFang. Each hand bundles an agent config, tools, settings, dashboard metrics, and dependency requirements.

```toml
id = "browser"
name = "Browser Hand"
category = "productivity"
tools = ["browser_navigate", "browser_click", "browser_type"]

[agent]
name = "browser-hand"
module = "builtin:chat"
system_prompt = "You are an autonomous web browser agent..."

[[settings]]
key = "headless"
setting_type = "toggle"
default = "true"
```

### Integrations

Integration templates in `integrations/<name>.toml` define MCP server connections (GitHub, Slack, databases, etc.) with transport config, required env vars, and setup instructions.

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

### Skills

Skills in `skills/<name>/skill.toml` are reusable prompt templates or Python scripts that agents can invoke.

```toml
[skill]
name = "meeting-agenda"
description = "Generate a structured meeting agenda"

[runtime]
type = "promptonly"

[prompt]
template = "Create a meeting agenda for: {{topic}}"
```

### Providers

Provider files in `providers/<name>.toml` define LLM providers and their models with pricing, context windows, and capability flags. See [schema.toml](schema.toml) for the full field reference.

## How LibreFang Uses This Registry

LibreFang ships with built-in content compiled into the binary. This repository serves as the upstream source for updates and community contributions.

```bash
# Update all registry content
librefang catalog update

# Install a specific hand
librefang hand install browser

# Install a specific integration
librefang integration install github
```

### Custom Local Content

You can also create custom content locally without submitting a PR:

```bash
# Create a custom agent
mkdir -p ~/.librefang/agents/my-agent
# Edit ~/.librefang/agents/my-agent/agent.toml

# Add custom models to your config
# ~/.librefang/model_catalog.toml
```

## Validation

```bash
python scripts/validate.py
```

This validates all provider TOML files for correctness: required fields, valid tiers, non-negative costs, no duplicate IDs.

## How to Contribute

1. Fork this repository
2. Add or edit content in the appropriate directory
3. Run validation: `python scripts/validate.py`
4. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions for each content type.

## Current Stats

| Type | Count |
|------|-------|
| Agents | 33 |
| Hands | 14 |
| Integrations | 25 |
| Skills | 2 |
| Providers | 46 |
| Models | 190+ |
| Aliases | 80+ |

## License

MIT License. See [LICENSE](LICENSE).
