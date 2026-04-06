---
name: devteam-hand-skill
version: "0.1.0"
description: "Expert knowledge for autonomous dev team coordination -- issue triage patterns, task decomposition, GitHub API workflows, and cross-role collaboration protocols"
runtime: prompt_only
---

# Dev Team Expert Knowledge

## GitHub API Reference

### Issue Management

**List open issues (sorted by creation, newest first)**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues?state=open&sort=created&direction=desc&per_page=30"
```

**Get a single issue with comments**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER"

curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/comments"
```

**Add a label to an issue**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/labels" \
  -d '{"labels":["bug","priority:high"]}'
```

**Assign an issue**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/assignees" \
  -d '{"assignees":["username"]}'
```

**Add a comment**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/comments" \
  -d '{"body":"Status update: implementation complete, moving to QA."}'
```

**Close an issue**:
```bash
curl -s -X PATCH -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER" \
  -d '{"state":"closed","state_reason":"completed"}'
```

### Pull Request Management

**Create a PR**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls" \
  -d '{
    "title": "fix: resolve issue #42",
    "body": "## Summary\n- Fixed the bug\n\nCloses #42",
    "head": "fix/issue-42",
    "base": "main"
  }'
```

**List PR files (to understand scope)**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/files"
```

**Check PR CI status**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/commits/SHA/check-runs"
```

### Repository Exploration

**Get repo languages**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/languages"
```

**Get directory listing**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/contents/PATH"
```

---

## Issue Triage Framework

### Classification Matrix

| Signal | Bug | Feature | Refactor | Docs |
|--------|-----|---------|----------|------|
| "doesn't work", "error", "crash", "broken" | x | | | |
| "add", "new", "support", "implement" | | x | | |
| "clean up", "simplify", "move", "rename" | | | x | |
| "document", "readme", "guide", "explain" | | | | x |

### Priority Assignment

| Priority | Criteria | SLA |
|----------|----------|-----|
| **P0 Critical** | Production down, data loss, security vulnerability | Immediate |
| **P1 High** | Core feature broken, blocks multiple users | Same day |
| **P2 Medium** | Feature request with clear value, non-critical bug | This sprint |
| **P3 Low** | Nice-to-have, cosmetic, minor improvement | Backlog |

### Size Estimation

| Size | Criteria |
|------|----------|
| **S** | Single file change, < 50 lines, well-understood area |
| **M** | 2-5 files, 50-200 lines, may need design discussion |
| **L** | 5-15 files, 200-1000 lines, needs architect review |
| **XL** | 15+ files, 1000+ lines, needs decomposition into sub-tasks |

---

## Task Decomposition Patterns

### Feature Implementation

```
1. [Architect] Design solution -> produce design doc
2. [Designer] UI spec (if applicable) -> wireframe/spec
3. [Backend] Implement API/logic -> code + tests
4. [Frontend] Implement UI (if applicable) -> code + tests
5. [QA] Verify implementation -> test report
6. [DevOps] Update deployment (if needed) -> deploy config
7. [PM] Review and close issue
```

### Bug Fix

```
1. [QA or PM] Reproduce and document
2. [Architect] Identify root cause (for complex bugs)
3. [Backend/Frontend] Fix + add regression test
4. [QA] Verify fix + run regression suite
5. [PM] Close issue
```

### Refactoring

```
1. [Architect] Review scope and propose plan
2. [Backend/Frontend] Implement in small incremental steps
3. [QA] Run full test suite after each step
4. [PM] Track progress, ensure no regressions
```

---

## Cross-Role Communication Protocols

### Task Assignment Message Format

When PM delegates to a team member via agent_send:
```
Task: [Issue #NUMBER] [Title]
Type: bug / feature / refactor
Priority: P0-P3
Size: S/M/L/XL

Context:
[Brief description of what needs to be done]

Acceptance Criteria:
- [ ] [Specific, testable criterion]
- [ ] [Another criterion]

Relevant Files:
- path/to/file.rs (line 42-60)
- path/to/related.rs

Branch: feat/issue-NUMBER or fix/issue-NUMBER

Design: [Link to architect's design if available]
```

### Completion Report Format

When a team member reports back to PM:
```
Completed: [Issue #NUMBER] [Title]
Status: done / blocked / needs review

Changes:
- path/to/file.rs -- [what changed]
- path/to/test.rs -- [tests added]

Build: pass / fail
Tests: X passed, Y failed
Lint: pass / fail

Notes: [Any concerns, trade-offs, or follow-up needed]
```

### Review Request Format

When requesting architect review:
```
Review Request: [Issue #NUMBER]
Branch: feat/issue-NUMBER
Files Changed: N

Summary: [1-2 sentences of what was done]

Specific Concerns:
- [Any area you're unsure about]
```

---

## Git Workflow Patterns

### Feature Branch Workflow

```bash
# Start new work
git checkout main && git pull
git checkout -b feat/issue-42-add-widget

# Work, commit incrementally
git add -p
git commit -m "feat: add widget component skeleton"
git commit -m "feat: implement widget data loading"
git commit -m "test: add widget unit tests"

# Push and create PR
git push -u origin feat/issue-42-add-widget
```

### Commit Message Convention

```
<type>(<scope>): <description>

Types: feat, fix, docs, refactor, test, chore, perf, ci
Scope: optional, e.g. (api), (ui), (db)

Examples:
feat(api): add user preferences endpoint
fix(ui): prevent double-submit on payment form
test(auth): add integration tests for OAuth flow
refactor(db): extract query builder from repository
```

---

## Tech Stack Detection

When tech_stack is "auto", detect from repository contents:

| File/Pattern | Stack |
|-------------|-------|
| `Cargo.toml` | Rust |
| `package.json` + `tsconfig.json` | TypeScript |
| `package.json` (no tsconfig) | JavaScript/Node.js |
| `go.mod` | Go |
| `pom.xml` or `build.gradle` | Java/Kotlin |
| `Package.swift` | Swift |
| `requirements.txt` or `pyproject.toml` | Python |
| `Gemfile` | Ruby |
| `*.csproj` or `*.sln` | C# / .NET |

### Build/Test Commands by Stack

| Stack | Build | Test | Lint |
|-------|-------|------|------|
| Rust | `cargo build` | `cargo test` | `cargo clippy -- -D warnings` |
| TypeScript | `npm run build` | `npm test` | `npm run lint` |
| Python | - | `pytest` | `ruff check .` |
| Go | `go build ./...` | `go test ./...` | `golangci-lint run` |
| Java | `mvn compile` | `mvn test` | `mvn checkstyle:check` |
| Swift | `swift build` | `swift test` | `swiftlint` |

---

## Project Board State Management

### Memory Keys

| Key | Purpose |
|-----|---------|
| `devteam_board` | Full project board JSON (backlog, in_progress, in_review, done) |
| `devteam_issues_triaged` | Counter: total issues triaged |
| `devteam_tasks_completed` | Counter: total tasks completed |
| `devteam_active_tasks` | Gauge: currently in-progress tasks |
| `devteam_prs_created` | Counter: PRs created |
| `devteam_last_scan` | Timestamp of last issue scan |
| `devteam_team_status` | Per-agent status (idle/busy/blocked) |

### Board Update Protocol

When updating the board, always:
1. memory_recall `devteam_board` -- get current state
2. Modify the relevant section
3. memory_store `devteam_board` -- save back
4. Update counters (devteam_active_tasks, etc.)
