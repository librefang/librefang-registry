# MCP Servers Registry

MCP (Model Context Protocol) servers connect LibreFang agents to external services. Each entry in this directory is a single `.toml` file describing an MCP server: how to launch it, what credentials it requires, and which category of functionality it provides.

When an agent has an MCP server attached, the server's tools appear automatically in the agent's tool list alongside built-in tools like `file_read` and `web_search`.

## File Format

Each MCP server is a flat `.toml` file. The filename (without `.toml`) must match the `id` field.

```toml
id = "github"                         # must match filename
name = "GitHub"
description = "Access GitHub repos, issues, PRs, and organizations"
category = "devtools"                 # devtools | data | cloud | communication | productivity | ai
icon = "lucide:github"
tags = ["git", "vcs", "code"]

[transport]
type = "stdio"                        # stdio | sse
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github@2025.4.8"]

[[required_env]]                      # repeat block for each required credential
name = "GITHUB_PERSONAL_ACCESS_TOKEN"
label = "GitHub Personal Access Token"
help = "A fine-grained or classic PAT with repo and read:org scopes"
is_secret = true
get_url = "https://github.com/settings/tokens"

[oauth]                               # optional: OAuth flow config
provider = "github"
scopes = ["repo", "read:org"]
auth_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"

[health_check]
interval_secs = 60
unhealthy_threshold = 3

setup_instructions = """
1. Go to https://github.com/settings/tokens and create a Personal Access Token.
2. Paste the token into the GITHUB_PERSONAL_ACCESS_TOKEN field.
3. Alternatively, use the OAuth flow to authorize LibreFang directly.
"""

[i18n.zh]
name = "GitHub"
description = "通过官方 MCP 服务器访问 GitHub 仓库、Issue、Pull Request 与组织。"
```

## Installing an MCP Server

```bash
# List all available MCP servers
librefang catalog mcp

# Install an MCP server and attach it to an agent
librefang mcp install github
librefang mcp attach github --agent coder

# Or specify the agent when installing
librefang mcp install github --agent coder

# Set required credentials
librefang config set-env GITHUB_PERSONAL_ACCESS_TOKEN ghp_xxx

# List attached MCP servers for an agent
librefang mcp list --agent coder

# Remove an MCP server from an agent
librefang mcp detach github --agent coder
```

## All MCP Servers (33 total)

### Development Tools (devtools)

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| bitbucket | Bitbucket | stdio (npx) | `BITBUCKET_*` | Access Bitbucket repositories, pull requests, and pipelines |
| fetch | Fetch | stdio (npx) | none | Fetch any web URL and receive its content as clean Markdown |
| filesystem | Filesystem | stdio (npx) | none | Read, write, search, and manage local files |
| git | Git | stdio (npx) | none | Inspect local Git repos — commits, diffs, branches, blame |
| github | GitHub | stdio (npx) | `GITHUB_PERSONAL_ACCESS_TOKEN` | Access GitHub repos, issues, PRs, and organizations |
| gitlab | GitLab | stdio (npx) | `GITLAB_*` | Access GitLab projects, MRs, issues, and CI/CD pipelines |
| jira | Jira | stdio (npx) | `JIRA_*` | Access Jira issues, projects, boards, and sprints |
| linear | Linear | stdio (npx) | `LINEAR_API_KEY` | Manage Linear issues, projects, cycles, and teams |
| puppeteer | Puppeteer | stdio (npx) | none | Control headless Chrome — navigate, screenshot, scrape |
| sentry | Sentry | stdio (npx) | `SENTRY_AUTH_TOKEN` | Monitor Sentry error tracking, issues, and releases |

### Data

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| elasticsearch | Elasticsearch | stdio (npx) | `ELASTICSEARCH_*` | Search and manage Elasticsearch indices and documents |
| google-maps | Google Maps | stdio (npx) | `GOOGLE_MAPS_API_KEY` | Geocoding, directions, distance matrix, and place search |
| mongodb | MongoDB | stdio (npx) | `MONGODB_CONNECTION_STRING` | Query and manage MongoDB databases and collections |
| postgresql | PostgreSQL | stdio (npx) | `POSTGRES_CONNECTION_STRING` | Query and manage PostgreSQL databases |
| redis | Redis | stdio (npx) | `REDIS_URL` | Access and manage Redis key-value stores |
| sqlite-mcp | SQLite | stdio (npx) | none | Query and manage local SQLite databases |

### Cloud

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| aws | AWS | stdio (npx) | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Manage S3, EC2, Lambda, and other AWS resources |
| azure-mcp | Azure | stdio (npx) | `AZURE_*` | Manage Azure VMs, Storage, and App Services |
| gcp-mcp | GCP | stdio (npx) | `GOOGLE_APPLICATION_CREDENTIALS` | Manage GCP Compute, Cloud Storage, and BigQuery |

### Communication

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| discord-mcp | Discord | stdio (npx) | `DISCORD_TOKEN` | Access Discord servers, channels, and messages |
| slack | Slack | stdio (npx) | `SLACK_BOT_TOKEN` | Access Slack channels, messages, and users |
| teams-mcp | Microsoft Teams | stdio (npx) | `TEAMS_*` | Access Teams channels, chats, and messages |

### Productivity

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| dropbox | Dropbox | stdio (npx) | `DROPBOX_ACCESS_TOKEN` | Access and manage Dropbox files and folders |
| gmail | Gmail | stdio (npx) | `GMAIL_*` | Read, send, and manage Gmail messages and drafts |
| google-calendar | Google Calendar | stdio (npx) | `GOOGLE_*` | Manage Google Calendar events and availability |
| google-drive | Google Drive | stdio (npx) | `GOOGLE_*` | Browse, search, and read files from Google Drive |
| notion | Notion | stdio (npx) | `NOTION_API_KEY` | Access and manage Notion pages, databases, and blocks |
| time | Time | stdio (npx) | none | Get current time, convert timezones, calculate differences |
| todoist | Todoist | stdio (npx) | `TODOIST_API_TOKEN` | Manage Todoist tasks, projects, and labels |

### AI

| ID | Name | Transport | Credentials Required | Description |
|----|------|-----------|---------------------|-------------|
| brave-search | Brave Search | stdio (npx) | `BRAVE_API_KEY` | Perform web searches using the Brave Search API |
| exa-search | Exa Search | stdio (npx) | `EXA_API_KEY` | AI-powered neural search and web content retrieval |
| memory | Memory | stdio (npx) | none | Persistent knowledge graph for facts and relationships across sessions |
| sequential-thinking | Sequential Thinking | stdio (npx) | none | Structured multi-step reasoning with revisable thought chains |

## Adding a New MCP Server

1. Create `mcp/<name>.toml` — the filename must match the `id` field.
2. Test the transport command locally: run `npx -y <package>` and verify it starts without errors.
3. List all `[[required_env]]` entries so the UI can prompt users for credentials.
4. Run `python scripts/validate.py`.
5. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
