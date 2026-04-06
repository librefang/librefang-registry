# Dev Team Hand

Autonomous software development team -- PM triages issues and coordinates, Engineer implements, QA validates.

## Why 3 Agents, Not 7

A dev team hand with PM/Architect/Frontend/Backend/DevOps/QA/Designer sounds good on paper, but agent_send is synchronous -- PM waits for each response. A 7-agent pipeline means 5-6 serial round-trips per issue, massive token consumption, and information loss at every handoff.

Instead: one strong **Engineer** who handles architecture, implementation, testing, and CI/CD in a single context. A separate **QA** because verification requires a skeptical perspective independent from the implementer. And **PM** to hold the global view without getting polluted by implementation details.

## Tiers

| Tier | Agents | When to Use |
|------|--------|-------------|
| **Lite** | PM + Engineer | Small projects, quick fixes. PM does QA. |
| **Standard** | PM + Engineer + QA | Most projects. Separate verification. |

## Workflow

```
GitHub Issue
  |
  v
PM scans & triages (cron)
  |
  v
PM assigns to Engineer (with acceptance criteria)
  |
  v
Engineer: read code -> design (if needed) -> implement + test -> report
  |
  v
QA verifies (standard) / PM verifies (lite)
  |
  v
PM closes issue, updates board
```

## Settings

| Setting | Options | Default |
|---------|---------|---------|
| Team Size | `lite`, `standard` | `standard` |
| Repository URL | `owner/repo` | (empty) |
| Issue Scan Interval | `5min`, `15min`, `1hour`, `manual` | `15min` |
| Tech Stack | `auto`, `rust`, `typescript`, `python`, `go`, `java`, `swift` | `auto` |
| Approval Mode | on/off | on |
| Branch Strategy | `feature_branch`, `gitflow`, `trunk` | `feature_branch` |

## Requirements

- `git` on PATH
- `GITHUB_TOKEN` env var

## Usage

```bash
librefang hand activate devteam
librefang hand set devteam repo_url "owner/repo"
librefang hand chat devteam
```
