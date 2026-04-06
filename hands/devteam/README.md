# Dev Team Hand

Autonomous software development team — PM triages issues, Engineer implements, QA validates.

## Composition

This hand demonstrates proper resource composition:

| Resource | How Used |
|----------|----------|
| **Agent templates** | `base = "planner"` / `"coder"` / `"code-reviewer"` — inherit proven prompts |
| **MCP servers** | `github` — agents interact via MCP tools, not hardcoded curl |
| **Workflows** | `bug-triage`, `code-review`, `test-generation`, `product-spec`, etc. — via `workflow_run` tool |
| **Plugins** | `todo-tracker`, `auto-summarizer`, `episodic-memory` |
| **Per-agent skills** | `SKILL-pm.md`, `SKILL-engineer.md`, `SKILL-qa.md` — targeted reference knowledge |
| **Per-agent capabilities** | QA can't write files, Engineer has full shell, PM only uses gh/git |

## Architecture

```
PM (coordinator, base=planner)
  ├─ Scans GitHub issues via MCP
  ├─ Triages, delegates, tracks board
  ├─ Uses workflow_run for bug-triage, product-spec
  ├─ Merges PRs after QA passes
  │
  ├──▶ Engineer (base=coder)
  │     ├─ Clones shared repo, branches, implements
  │     ├─ Uses workflow_run for test-generation, refactor-plan
  │     ├─ Creates PRs via GitHub MCP
  │     └─ Accumulates knowledge per module
  │
  └──▶ QA (base=code-reviewer)
        ├─ Reviews code (correctness + security + performance)
        ├─ Runs full test suite (no file_write access)
        ├─ Uses workflow_run for comprehensive code-review
        └─ Submits PR reviews with line comments
```

## Usage

```bash
librefang hand activate devteam
librefang hand set devteam repo_url "owner/repo"
librefang hand chat devteam
```
