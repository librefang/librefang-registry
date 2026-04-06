---
name: devteam-hand-skill
version: "0.2.0"
description: "Expert knowledge for autonomous dev team -- GitHub API workflows, issue triage, task decomposition, and cross-agent collaboration"
runtime: prompt_only
---

# Dev Team Expert Knowledge

## GitHub API Reference

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
