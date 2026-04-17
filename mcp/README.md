# MCP Servers

MCP (Model Context Protocol) server templates for LibreFang. Each entry connects LibreFang to an external service (GitHub, Slack, databases, etc.).

## Structure

```
mcp/
├── github.toml
├── slack.toml
├── postgresql.toml
└── ...
```

## MCP Server TOML Format

```toml
id = "service-id"                 # Must match filename (without .toml)
name = "Service Name"
description = "What this MCP server provides"
category = "devtools"             # devtools | communication | storage | monitoring | data
icon = "🐙"
tags = ["relevant", "tags"]

[transport]                       # MCP server transport config
type = "stdio"                    # "stdio" or "sse"
command = "npx"
args = ["-y", "@pkg/mcp-server"]

[[required_env]]                  # Required environment variables
name = "SERVICE_API_KEY"
label = "API Key"
help = "How to obtain this key"
is_secret = true
get_url = "https://..."

[oauth]                           # Optional: OAuth config
provider = "github"
scopes = ["repo"]
auth_url = "https://..."
token_url = "https://..."

[health_check]
interval_secs = 60
unhealthy_threshold = 3

setup_instructions = """
Step-by-step setup guide for users.
"""
```

## Current MCP Servers (25)

| MCP Server | Category | Service |
|------------|----------|---------|
| github | devtools | GitHub repos, issues, PRs |
| slack | communication | Slack messaging |
| notion | productivity | Notion pages and databases |
| postgresql | storage | PostgreSQL database |
| ... | | See each file for details |

## Adding a New MCP Server

1. Create `mcp/<name>.toml`
2. Ensure `id` matches the filename
3. Test the MCP server command locally
4. Run `python scripts/validate.py`
5. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
