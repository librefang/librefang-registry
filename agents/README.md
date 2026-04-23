# Agents Registry

Agent templates for LibreFang. Each entry is a ready-to-install agent definition with a pre-configured system prompt, model settings, capability declarations, and routing aliases.

These are the reference agents shipped with the registry. You can install them as-is, override individual fields (model, system_prompt, tools) after installation, or use them as `base` templates inside a Hand.

## File Format

Each agent lives in its own subdirectory containing a single `agent.toml`:

```
agents/
├── coder/
│   └── agent.toml
├── orchestrator/
│   └── agent.toml
└── ...
```

### agent.toml format

```toml
name = "coder"                       # must match directory name
version = "0.4.3-beta3-20260314"
description = "Expert software engineer. Reads, writes, and analyzes code."
author = "librefang"
module = "builtin:chat"              # runtime module — builtin:chat for all current agents

[metadata.routing]
aliases = ["write code", "fix bug", "implement feature"]    # exact activation phrases
weak_aliases = ["refactor", "patch", "code change"]         # keyword hints

[model]
provider = "default"                 # default = use LibreFang's configured primary provider
model = "default"
api_key_env = "GEMINI_API_KEY"       # optional override: use this key env var
max_tokens = 8192
temperature = 0.3
system_prompt = """You are Coder, an expert software engineer..."""

[[fallback_models]]                  # optional: try these providers on failure
provider = "default"
model = "default"
api_key_env = "GROQ_API_KEY"

[schedule]                           # optional: continuous or cron activation
continuous = { check_interval_secs = 120 }

[resources]
max_llm_tokens_per_hour = 200000
max_concurrent_tools = 10

[capabilities]
tools = ["file_read", "file_write", "file_list", "shell_exec", "web_search", "web_fetch",
         "memory_store", "memory_recall"]
network = ["*"]                      # "*" = all, or list specific domains
memory_read = ["*"]
memory_write = ["self.*"]            # "self.*" = own namespace only
shell = ["cargo *", "rustc *", "git *", "npm *", "python *"]  # shell command allowlist
agent_spawn = false
agent_message = []                   # agents this agent may message

[i18n.zh]
name = "编码工程师"
description = "资深软件工程师：阅读、编写与分析代码。"
```

## Installing and Using Agents

```bash
# List all available agent templates
librefang catalog agents

# Install an agent from the registry
librefang agent install coder

# Install with a custom name
librefang agent install coder --name my-coder

# List installed agents
librefang agent list

# Send a message to an installed agent
librefang agent message coder "Implement a binary search function in Rust"

# Remove an agent
librefang agent remove my-coder
```

Agents can also be used as base templates in a Hand by setting `base = "coder"` in `HAND.toml`.

## All Agents (33 total)

### Development

| Name | Description | Key Tools |
|------|-------------|-----------|
| architect | System architect. Designs software architectures, evaluates trade-offs, creates technical specifications. | file_read, file_write, web_search, web_fetch |
| code-reviewer | Senior code reviewer. Reviews PRs, identifies issues, suggests improvements with production standards. | file_read, shell_exec, web_search |
| coder | Expert software engineer. Reads, writes, and analyzes code. | file_read, file_write, shell_exec, web_search |
| debugger | Expert debugger. Traces bugs, analyzes stack traces, performs root cause analysis. | file_read, shell_exec, web_search |
| devops-lead | DevOps lead. Manages CI/CD, infrastructure, deployments, monitoring, and incident response. | shell_exec, file_read, web_search |
| ops | DevOps agent. Monitors systems, runs diagnostics, manages deployments. | shell_exec, file_read, web_search |
| test-engineer | Quality assurance engineer. Designs test strategies, writes tests, validates correctness. | file_read, file_write, shell_exec |

### Research and Analysis

| Name | Description | Key Tools |
|------|-------------|-----------|
| academic-researcher | Academic research agent. Searches scholarly papers, summarizes findings, and generates literature reviews. | web_search, web_fetch, file_write |
| analyst | Data analyst. Processes data, generates insights, creates reports. | file_read, web_search, web_fetch |
| data-scientist | Data scientist. Analyzes datasets, builds models, creates visualizations, performs statistical analysis. | file_read, file_write, shell_exec |
| researcher | Research agent. Fetches web content and synthesizes information. | web_search, web_fetch, memory_store |

### Writing and Documentation

| Name | Description | Key Tools |
|------|-------------|-----------|
| doc-writer | Technical writer. Creates documentation, README files, API docs, tutorials, and architecture guides. | file_read, file_write, web_fetch |
| writer | Content writer. Creates documentation, articles, and technical writing. | file_read, file_write, web_search |

### Orchestration

| Name | Description | Key Capabilities |
|------|-------------|-----------------|
| orchestrator | Meta-agent that decomposes complex tasks, delegates to specialist agents, and synthesizes results. | agent_spawn, agent_send, agent_list, agent_kill |
| planner | Project planner. Creates project plans, breaks down epics, estimates effort, identifies risks and dependencies. | file_read, file_write, web_search |

### Business and Operations

| Name | Description | Key Tools |
|------|-------------|-----------|
| customer-support | Customer support agent for ticket handling, issue resolution, and customer communication. | memory_store, memory_recall, web_search |
| email-assistant | Email triage, drafting, scheduling, and inbox management agent. | memory_store, memory_recall, file_write |
| legal-assistant | Legal assistant agent for contract review, legal research, compliance checking, and document drafting. | file_read, file_write, web_search |
| meeting-assistant | Meeting notes, action items, agenda preparation, and follow-up tracking agent. | memory_store, memory_recall, file_write |
| recruiter | Recruiting agent for resume screening, candidate outreach, job description writing, and hiring pipeline management. | web_search, file_read, memory_store |
| sales-assistant | Sales assistant agent for CRM updates, outreach drafting, pipeline management, and deal tracking. | memory_store, memory_recall, web_search |
| security-auditor | Security specialist. Reviews code for vulnerabilities, checks configurations, performs threat modeling. | file_read, shell_exec, web_search |

### Personal Productivity

| Name | Description | Key Tools |
|------|-------------|-----------|
| assistant | General-purpose assistant agent. The default agent for everyday tasks, questions, and conversations. | file_read, file_write, web_search, memory_store |
| health-tracker | Wellness tracking agent for health metrics, medication reminders, fitness goals, and lifestyle habits. | memory_store, memory_recall, file_write |
| hello-world | A friendly greeting agent that can read files, search the web, and answer everyday questions. | file_read, web_search, web_fetch |
| home-automation | Smart home control agent for IoT device management, automation rules, and home monitoring. | shell_exec, memory_store, web_fetch |
| personal-finance | Personal finance agent for budget tracking, expense analysis, savings goals, and financial planning. | file_read, memory_store, web_search |
| recipe-assistant | Cooking assistant that helps with recipes, meal plans, ingredient substitutions, and portion adjustments. | web_search, memory_recall, file_write |
| social-media | Social media content creation, scheduling, and engagement strategy agent. | web_fetch, web_search, file_write |
| translator | Multi-language translation agent for document translation, localization, and cross-cultural communication. | file_read, file_write, web_fetch |
| travel-planner | Trip planning agent for itinerary creation, booking research, budget estimation, and travel logistics. | web_search, web_fetch, memory_store |
| tutor | Teaching and explanation agent for learning, tutoring, and educational content creation. | web_search, memory_recall, file_write |

## Capability Reference

| Capability field | Values | Effect |
|-----------------|--------|--------|
| `tools` | list of tool names | Which built-in tools the agent may invoke |
| `network` | `["*"]` or domain list | Outbound HTTP domain allowlist |
| `memory_read` | `["*"]` or namespace list | Which memory namespaces the agent can read |
| `memory_write` | `["self.*"]` or `["*"]` | Which memory namespaces the agent can write |
| `shell` | glob patterns | Shell command allowlist (e.g. `"cargo *"`) |
| `agent_spawn` | `true` / `false` | Whether the agent can spawn child agents |
| `agent_message` | `["*"]` or agent name list | Which agents this agent may send messages to |

## Adding a New Agent

1. Create `agents/<name>/agent.toml` — `name` must match the directory name.
2. Set `module = "builtin:chat"` unless you have a custom runtime module.
3. Write a focused `system_prompt` — clear role definition, methodology, and constraints.
4. Declare only the tools and capabilities the agent actually needs.
5. Add `[metadata.routing]` aliases so the router can activate the agent by intent.
6. Run `python scripts/validate.py`.
7. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
