# Contributing to LibreFang Registry

Thank you for helping grow the LibreFang ecosystem! This guide explains how to add or update content for each type.

## General Workflow

1. Fork & clone the repository
2. Create a branch: `git checkout -b feat/add-my-content`
3. Add or edit files in the appropriate directory
4. Run validation: `python scripts/validate.py`
5. Submit a Pull Request

## Adding an Agent

Create a directory `agents/<name>/` with an `agent.toml` file:

```toml
name = "my-agent"
version = "0.1.0"
description = "What this agent does"
author = "your-name"
module = "builtin:chat"

[model]
provider = "default"
model = "default"
max_tokens = 4096
temperature = 0.7
system_prompt = """Your system prompt here."""

[capabilities]
tools = ["web_search", "file_read"]
```

### Agent Checklist

- [ ] `name` matches the directory name
- [ ] `description` is clear and concise (one sentence)
- [ ] `system_prompt` provides clear behavioral instructions
- [ ] `tools` only lists tools the agent actually needs
- [ ] Routing aliases (if any) are relevant and don't conflict with existing agents

## Adding a Hand

Create a directory `hands/<name>/` with a `HAND.toml` file and optionally a `SKILL.md`:

```toml
id = "my-hand"
name = "My Hand"
description = "What this hand does"
category = "productivity"  # communication | content | data | development | devops | finance | productivity | research | social
icon = "🔧"

tools = ["tool1", "tool2"]

[routing]
aliases = ["activate my hand", "do the thing"]

[agent]
name = "my-hand-agent"
module = "builtin:chat"
system_prompt = """Your agent prompt here."""

[[settings]]
key = "some_setting"
label = "Setting Label"
setting_type = "toggle"
default = "true"
```

### Hand Checklist

- [ ] `id` matches the directory name
- [ ] `category` is valid (`communication`, `content`, `data`, `development`, `devops`, `finance`, `productivity`, `research`, `social`)
- [ ] `tools` lists all required tools
- [ ] `[agent]` section has a complete system prompt
- [ ] `[[requires]]` sections list any external dependencies (binaries, services)
- [ ] `[[settings]]` sections provide user-configurable options where appropriate

## Adding an Integration

Create a file `integrations/<name>.toml`:

```toml
id = "my-service"
name = "My Service"
description = "What this integration provides"
category = "devtools"  # devtools | communication | storage | monitoring | data
icon = "🔌"
tags = ["relevant", "tags"]

[transport]
type = "stdio"
command = "npx"
args = ["-y", "@some/mcp-server"]

[[required_env]]
name = "MY_SERVICE_API_KEY"
label = "API Key"
help = "Get your key from https://..."
is_secret = true
get_url = "https://my-service.com/settings/api-keys"

setup_instructions = """
1. Get an API key from ...
2. Paste it into the field above.
"""
```

### Integration Checklist

- [ ] `id` matches the filename (without `.toml`)
- [ ] `[transport]` section is correct (test the MCP server command locally)
- [ ] `[[required_env]]` lists all needed environment variables
- [ ] `setup_instructions` are clear enough for first-time users
- [ ] `is_secret = true` for any sensitive values (API keys, tokens)

## Adding a Skill

Create a directory `skills/<name>/` with a `skill.toml` and optionally implementation files:

### Prompt-only Skill

```toml
[skill]
name = "my-skill"
version = "0.1.0"
description = "What this skill does"
author = "your-name"
tags = ["relevant", "tags"]

[runtime]
type = "promptonly"

[input]
param1 = { type = "string", description = "Description", required = true }

[prompt]
template = """Your prompt template using {{param1}}."""
```

### Python Skill

```toml
[skill]
name = "my-skill"
version = "0.1.0"
description = "What this skill does"

[runtime]
type = "python"
entry = "main.py"
```

Plus a `main.py` with your implementation.

### Skill Checklist

- [ ] `name` matches the directory name
- [ ] `[runtime].type` is `promptonly` or `python`
- [ ] `[input]` section documents all parameters
- [ ] Prompt-only skills have a `[prompt].template` with correct `{{param}}` placeholders
- [ ] Python skills include all required files

## Adding or Updating a Provider / Model

Edit the appropriate provider file in `providers/`. If the provider doesn't exist, create a new file.

```toml
[provider]
id = "my-provider"
display_name = "My Provider"
api_key_env = "MY_PROVIDER_API_KEY"
base_url = "https://api.my-provider.com"
key_required = true

[[models]]
id = "model-id"
display_name = "Model Name"
tier = "smart"                  # frontier | smart | balanced | fast | local
context_window = 128000
max_output_tokens = 16384
input_cost_per_m = 2.50         # USD per million input tokens
output_cost_per_m = 10.0        # USD per million output tokens
supports_tools = true
supports_vision = false
supports_streaming = true
aliases = ["short-name"]
```

### Provider Checklist

- [ ] `python scripts/validate.py` passes
- [ ] No duplicate model IDs
- [ ] Pricing is in USD per million tokens
- [ ] Tier is one of: `frontier`, `smart`, `balanced`, `fast`, `local`
- [ ] `context_window` and `max_output_tokens` are positive integers
- [ ] Boolean capability fields are correct
- [ ] Pricing verified from official source

## Where to Find Model Information

- **OpenAI**: https://openai.com/pricing
- **Anthropic**: https://docs.anthropic.com/en/docs/about-claude/models
- **Google Gemini**: https://ai.google.dev/pricing
- **DeepSeek**: https://platform.deepseek.com/api-docs/pricing
- **Mistral**: https://mistral.ai/technology/#pricing
- **Groq**: https://wow.groq.com/
- **xAI**: https://docs.x.ai/docs

## Guidelines

- **Don't guess** -- only add data you can verify from official sources
- **Keep descriptions concise** -- one sentence that explains the purpose
- **Test locally** -- try your content with LibreFang before submitting
- **One PR per content type** -- don't mix agent additions with provider updates
- **Keep aliases short** -- 1-3 word abbreviations users would naturally type
