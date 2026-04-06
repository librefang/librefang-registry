# Dev Team Hand

Autonomous software development team -- PM triages issues, Engineer implements, QA validates.

## Architecture

```
User / Cron
    |
    v
 PM (coordinator)
    |--- scans GitHub issues + PRs
    |--- triages, labels, comments
    |--- delegates to Engineer
    |--- sends to QA for verification
    |--- merges PRs, closes issues
    |--- daily standups + notifications
    |
    |---> Engineer
    |       |--- clones shared repo (first time)
    |       |--- designs + implements + tests
    |       |--- creates PRs
    |       |--- handles fix requests + rebases
    |       |--- reviews external PRs
    |       |--- accumulates knowledge
    |
    |---> QA
            |--- reads shared checkout
            |--- reviews code (correctness, security, edge cases)
            |--- runs full test suite
            |--- leaves PR reviews with line comments
            |--- reports test gaps
```

## Tiers

| Tier | Agents | When to Use |
|------|--------|-------------|
| **Lite** | PM + Engineer | Small projects, quick fixes. PM does QA. |
| **Standard** | PM + Engineer + QA | Most projects. Separate verification. |

## Lifecycle

### First Activation (Onboarding)
1. PM sends Engineer to analyze the repo (structure, stack, CI, entry points)
2. Profile stored in knowledge graph + memory
3. PM creates cron schedule for issue scanning + daily standup
4. Team starts processing issues

### Steady State
```
Cron fires → PM scans issues/PRs → triage → delegate → implement → QA → merge → notify
                                                    ↑                    |
                                                    └── fix request ←────┘ (max 3 rounds)
```

### Rollback
User reports regression → PM identifies guilty PR → `gh pr revert` → re-opens issue → postmortem

## GitHub Interaction (3-layer fallback)

| Priority | Method | When |
|----------|--------|------|
| 1 | `gh` CLI | Preferred — handles auth, pagination, JSON natively |
| 2 | GitHub MCP | When gh CLI not available but MCP connected |
| 3 | `curl` + REST API | Last resort fallback |

## Workflows Used

| Workflow | Used By | When |
|----------|---------|------|
| `bug-triage` | PM | Triaging bug issues — root cause analysis + fix plan |
| `code-review` | Engineer, QA | PR reviews — parallel correctness/security/style |
| `test-generation` | Engineer, QA | Adding test coverage for existing code |
| `refactor-plan` | Engineer | Refactoring tasks — smell analysis + migration plan |
| `product-spec` | PM | Vague feature requests — generates full PRD |
| `api-design` | Engineer | New API endpoints — resource model + OpenAPI spec |
| `weekly-report` | PM | Daily standup + weekly summaries |
| `incident-postmortem` | PM | After rollback — timeline + root cause + action items |

## MCP Integrations

| MCP | Purpose | Required |
|-----|---------|----------|
| `github` | Issues, PRs, reviews, code | Recommended |
| `sentry` | Error tracking context for bug fixes | Optional |
| `slack` | Status notifications | Optional |
| `discord-mcp` | Status notifications (alt) | Optional |
| `linear` | Project management (if issue_tracker=linear) | Optional |
| `jira` | Project management (if issue_tracker=jira) | Optional |

## Settings

| Setting | Options | Default |
|---------|---------|---------|
| Team Size | `lite`, `standard` | `standard` |
| Repository URL | `owner/repo` | (required) |
| Issue Scan Interval | `5min`, `15min`, `1hour`, `manual` | `15min` |
| Tech Stack | `auto`, `rust`, `typescript`, `python`, `go`, `java`, `swift` | `auto` |
| Approval Mode | on/off | on (wait for human before merge) |
| Branch Strategy | `feature_branch`, `gitflow`, `trunk` | `feature_branch` |
| Notification Channel | `none`, `slack`, `discord` | `none` |
| Issue Tracker | `github`, `linear`, `jira` | `github` |

## Requirements

| Requirement | Required | Purpose |
|-------------|----------|---------|
| `git` | Yes | Version control |
| `python3` | Yes | JSON parsing in API calls |
| `gh` | No (recommended) | GitHub CLI, preferred over curl |
| `npx` | No | MCP server runtime |
| `GITHUB_TOKEN` | Yes | GitHub API authentication |
| `SENTRY_AUTH_TOKEN` | No | Sentry error tracking |

## Usage

```bash
# Activate
librefang hand activate devteam

# Configure (required)
librefang hand set devteam repo_url "owner/repo"

# Optional
librefang hand set devteam team_size "lite"
librefang hand set devteam scan_interval "5min"
librefang hand set devteam notify_channel "slack"
librefang hand set devteam approval_mode "false"

# Chat
librefang hand chat devteam

# Direct commands
"Work on issue #42"
"What's the status?"
"Review PR #50"
"Stop #42"
"Rollback PR #55"
```
