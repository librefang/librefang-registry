---
name: devteam-hand-skill
version: "0.2.0"
description: "Expert knowledge for autonomous dev team -- GitHub API workflows, issue triage, task decomposition, and cross-agent collaboration"
runtime: prompt_only
---

# Dev Team Expert Knowledge

## GitHub CLI Reference (preferred)

```bash
# Issues
gh issue list --repo OWNER/REPO --state open --json number,title,labels,assignees,createdAt --limit 30
gh issue view NUMBER --repo OWNER/REPO --json body,comments
gh issue comment NUMBER --repo OWNER/REPO --body "message"
gh issue close NUMBER --repo OWNER/REPO --reason completed
gh issue edit NUMBER --repo OWNER/REPO --add-label "bot:triaged,type:bug"

# Pull Requests
gh pr list --repo OWNER/REPO --state open --json number,title,headRefName,author,statusCheckRollup
gh pr view NUMBER --repo OWNER/REPO --json files,additions,deletions,reviews
gh pr create --repo OWNER/REPO --title "fix: desc" --body "Closes #N" --head BRANCH --base main
gh pr review NUMBER --repo OWNER/REPO --approve --body "QA passed"
gh pr review NUMBER --repo OWNER/REPO --request-changes --body "See comments"
gh pr comment NUMBER --repo OWNER/REPO --body "Addressed feedback"
gh pr merge NUMBER --repo OWNER/REPO --squash
gh pr diff NUMBER --repo OWNER/REPO

# CI Status
gh pr checks NUMBER --repo OWNER/REPO

# Code browsing
gh api repos/OWNER/REPO/contents/PATH --jq '.content' | base64 -d
gh api repos/OWNER/REPO/languages
```

## GitHub REST API Reference (curl fallback)

### Issue Management

**List open issues**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues?state=open&sort=created&direction=desc&per_page=30"
```

**Get issue with comments**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER"

curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/comments"
```

**Label an issue**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/labels" \
  -d '{"labels":["bug","priority:high"]}'
```

**Comment on an issue**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/issues/NUMBER/comments" \
  -d '{"body":"Implementation complete, moving to QA."}'
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

**List PR files** (review scope):
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/files"
```

**Get PR diff**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3.diff" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER"
```

**Read PR reviews**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/reviews"
```

**Read PR review comments** (line-level):
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/comments"
```

**Submit a PR review** (APPROVE / REQUEST_CHANGES / COMMENT):
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/reviews" \
  -d '{
    "event": "REQUEST_CHANGES",
    "body": "Overall review summary",
    "comments": [
      {"path": "src/main.rs", "line": 42, "body": "This will panic on empty input"}
    ]
  }'
```

**Reply to a review comment**:
```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/comments/COMMENT_ID/replies" \
  -d '{"body": "Fixed in latest push"}'
```

**Merge a PR**:
```bash
curl -s -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/pulls/NUMBER/merge" \
  -d '{"merge_method": "squash"}'
```

**Check PR CI status**:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/commits/SHA/check-runs"
```

**Get repo languages** (for tech stack auto-detection):
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/languages"
```

---

## Issue Triage Framework

### Classification

| Signal | Type |
|--------|------|
| "doesn't work", "error", "crash", "broken" | bug |
| "add", "new", "support", "implement" | feature |
| "clean up", "simplify", "move", "rename" | refactor |
| "document", "readme", "guide" | docs |

### Priority

| Priority | Criteria | Response |
|----------|----------|----------|
| P0 | Production down, data loss, security vuln | Immediate |
| P1 | Core feature broken, blocks users | Same day |
| P2 | Feature request, non-critical bug | This sprint |
| P3 | Nice-to-have, cosmetic | Backlog |

### Size Estimation

| Size | Scope | Approach |
|------|-------|----------|
| S | < 50 lines, 1 file | Implement directly |
| M | 50-200 lines, 2-5 files | Brief design then implement |
| L | 200-1000 lines, 5-15 files | Design doc -> PM alignment -> implement |
| XL | 1000+ lines, 15+ files | Decompose into sub-issues first |

---

## Tech Stack Detection

| File | Stack | Build | Test | Lint |
|------|-------|-------|------|------|
| `Cargo.toml` | Rust | `cargo build` | `cargo test` | `cargo clippy -- -D warnings` |
| `package.json` + `tsconfig.json` | TypeScript | `npm run build` | `npm test` | `npm run lint` |
| `package.json` | JavaScript | `npm run build` | `npm test` | `npm run lint` |
| `go.mod` | Go | `go build ./...` | `go test ./...` | `golangci-lint run` |
| `pyproject.toml` / `requirements.txt` | Python | -- | `pytest` | `ruff check .` |
| `pom.xml` / `build.gradle` | Java/Kotlin | `mvn compile` | `mvn test` | `mvn checkstyle:check` |
| `Package.swift` | Swift | `swift build` | `swift test` | `swiftlint` |

---

## Task Handoff Protocols

### PM -> Engineer (task assignment)

```
Task: [Issue #NUMBER] [Title]
Type: bug / feature / refactor
Size: S / M / L

Acceptance Criteria:
- [ ] [specific, testable]
- [ ] [specific, testable]

Context:
- [relevant file paths]
- [reproduction steps for bugs]
- [expected behavior for features]

Branch: feat/issue-NUMBER or fix/issue-NUMBER
```

### Engineer -> PM (completion report)

```
Done: [Issue #NUMBER] [Title]

Changes:
- path/to/file.rs -- [what and why]

Build: pass
Tests: N passed, 0 failed (M new tests added)
Lint: pass

Concerns: [any trade-offs or follow-up needed, or "none"]
```

### PM -> QA (verification request)

```
Verify: [Issue #NUMBER] [Title]
Branch: fix/issue-42
Engineer changed: [list of files]

Acceptance Criteria:
- [ ] [same as original task]

Run: [build + test commands for this stack]
```

### QA -> PM (verification result)

```
Result: PASS / FAIL
Issue: #NUMBER

[If PASS]
All acceptance criteria met. Test suite: X passed, 0 failed. No regressions.

[If FAIL]
Bug: [title]
File: path/to/file.rs:42
Severity: critical / major / minor
Steps: [reproduction]
Expected: [...]
Actual: [...]
```

---

## Project Board (memory schema)

### Keys

| Key | Type | Purpose |
|-----|------|---------|
| `devteam_board` | JSON | Full board state |
| `devteam_issues_triaged` | number | Total issues triaged |
| `devteam_tasks_completed` | number | Total tasks done |
| `devteam_active_tasks` | number | Currently in-progress |
| `devteam_bugs_found` | number | Bugs found by QA |
| `devteam_last_scan` | timestamp | Last issue scan time |

### Board Structure

```json
{
  "backlog": [
    {"issue": 42, "title": "...", "type": "bug", "size": "M", "priority": "P1"}
  ],
  "in_progress": [
    {"issue": 43, "assignee": "engineer", "branch": "fix/issue-43", "started": "2025-01-01T10:00:00Z"}
  ],
  "in_review": [
    {"issue": 44, "branch": "feat/issue-44"}
  ],
  "done": [
    {"issue": 45, "closed_at": "2025-01-02T14:00:00Z"}
  ]
}
```

### Update Protocol

1. `memory_recall devteam_board`
2. Modify the relevant section
3. `memory_store devteam_board` with updated state
4. Update counters (`devteam_active_tasks`, etc.)
