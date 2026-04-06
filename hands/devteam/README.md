# Dev Team Hand

Autonomous software development team -- PM triages issues, architect designs, developers implement, QA validates, DevOps ships.

## Configuration

| Field | Value |
|-------|-------|
| Category | `development` |
| Agents | `pm` (coordinator), `architect`, `frontend`, `backend`, `devops`, `qa`, `designer` |
| Routing | `dev team`, `development team`, `software team`, `project team`, `build a project`, `issue triage` |

## Team Tiers

| Tier | Roles | Best For |
|------|-------|----------|
| **Simple** | PM + Backend | Solo projects, quick fixes, small features |
| **Standard** | PM + Architect + Backend + QA | Most projects -- design review + testing |
| **Full** | All 7 roles | Large projects with frontend, CI/CD, and design needs |

## Workflow

```
GitHub Issue
  |
  v
PM scans & triages (via cron)
  |
  v
PM assigns to role based on tier
  |
  v
Architect designs (standard/full) -----> Developer implements
  |                                           |
  v                                           v
Designer provides UI spec (full)         QA verifies (standard/full)
  |                                           |
  v                                           v
DevOps deploys (full)                    PM reviews & closes issue
```

## Settings

- **Team Size** -- `simple`, `standard`, `full`
- **Repository URL** -- GitHub `owner/repo` to work on
- **Issue Scan Interval** -- `5min`, `15min`, `1hour`, `manual`
- **Tech Stack** -- `auto`, `rust`, `typescript`, `python`, `go`, `java`, `swift`
- **Approval Mode** -- Require human approval before commits (default: on)
- **Branch Strategy** -- `feature_branch`, `gitflow`, `trunk`

## Requirements

- `git` -- installed on PATH
- `GITHUB_TOKEN` -- for issue scanning and PR creation

## Usage

```bash
# Activate with default settings (standard tier)
librefang hand activate devteam

# Configure
librefang hand set devteam repo_url "owner/repo"
librefang hand set devteam team_size "full"

# Chat with the team
librefang hand chat devteam

# Send a task
curl -s -X POST http://127.0.0.1:4545/api/hands/instances/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Implement issue #42"}'
```
