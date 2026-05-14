# DevOps Hand

Autonomous DevOps engineer -- CI/CD management, infrastructure monitoring, deployment automation, and incident response.

## Configuration

| Field | Value |
|-------|-------|
| Category | `development` |
| Agent | `devops-hand` |
| Routing | `ci/cd`, `pipeline`, `github actions`, `infrastructure monitoring`, `deployment automation`, `incident response`, `auto evolve`, `review github prs`, `triage issues`, `implement issue`, `fix bug from issue` |

## Integrations

None required.

## Settings

- **Infrastructure Type** -- `cloud`, `kubernetes`, `docker`, `bare_metal`, `serverless`
- **CI/CD Platform** -- `github_actions`, `gitlab_ci`, `jenkins`, `circleci`, `other`
- **Monitoring Focus** -- `uptime`, `performance`, `security`, `cost`, `balanced`
- **Auto Monitor** -- Automatically monitor infrastructure (default: off)
- **Health Check Interval** -- `1min`, `5min`, `15min`, `1hour`
- **Service URLs** -- Comma-separated URLs to monitor
- **Alert on Failure** -- Publish events on health check failures (default: on)
- **Rollback Strategy** -- `manual`, `auto_previous`, `blue_green`
- **Auto Evolution** -- Periodically scan GitHub repos and run PR review / issue triage / BMAD implementation (default: off)
- **Evolution Target Repos** -- Comma-separated `owner/repo` pairs to watch
- **Evolution Check Interval** -- `5min`, `15min`, `1hour`, `6hour`, `1day`
- **BMAD Strictness** -- `light`, `standard`, `strict` -- depth of the Brainstorm-Architect-PRD-Implement pipeline before producing a draft PR

## Usage

```bash
librefang hand run devops
```

## Auto-Evolution Mode

When `auto_evolve = true` and `evolution_repos` is set, the Hand's Phase 7 loop fires on `evolution_check_interval` and, for each watched repo:

1. **Reviews open PRs** -- pulls each PR's diff, asks the `code-reviewer` sub-agent for an assessment, posts a single `COMMENT` review back on GitHub. Already-reviewed `head_sha` values are skipped.
2. **Triages open issues** -- labels first, single-prompt LLM fallback if labels are absent. Result is one of `bug-fix | feature | needs-info | skip`.
3. **Implements actionable issues** -- dispatches `bug-fix` and `feature` issues to the `implementer` sub-agent which runs the BMAD pipeline scaled by `bmad_strictness` and produces a **draft PR**.

### Safety floor (always on)

- Draft PRs only. The Hand never marks PRs ready-for-review and never merges.
- Never pushes to `main` / `master` / protected branches.
- Never `--force` / `--no-verify` / `--amend` against a remote branch.
- Stops and queues to `devops_queue.json` if the change touches `Cargo.toml` workspace members, migration files, or anything under a `secrets` / credential glob.
- Hard cap of 30 changed files per PR; larger changes get split.
- Per-tick token budget capped at 70% so subsequent ticks have headroom.

### Required GitHub token scopes

For public-repo evolution, a fine-grained token with:
- **Pull requests**: read & write (review posting, draft PR creation)
- **Issues**: read & write (triage comments, issue cross-links)
- **Contents**: read & write (branch push)
- **Metadata**: read

For private repos, add the `repo` scope and ensure the repo is listed in `evolution_repos`.

### What it does NOT do

It will never merge a PR, mark a draft as ready, or auto-approve. Human review is always required. See `SKILL.md` -> `What this Hand does NOT do` for the full list.
