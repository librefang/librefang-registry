# Skills Registry

Skills are reusable expertise modules that can be attached to any agent. Each skill carries a system prompt that injects domain knowledge, best practices, and behavioral guidelines into an agent's context at conversation time. Skills are composable — a single agent can load multiple skills simultaneously.

## File Format

A skill lives in its own subdirectory. The only required file is `SKILL.md`. An optional `skill.toml` provides structured metadata when `[runtime]`, `[input]` schema, or explicit versioning is needed.

```
skills/
├── rust-expert/
│   └── SKILL.md              # required: frontmatter + prompt body
├── meeting-agenda/
│   ├── SKILL.md              # required: frontmatter + prompt body
│   └── skill.toml            # optional: runtime type, input schema, version
└── code-runner/
    ├── SKILL.md              # overview (prompt body unused for script skills)
    ├── skill.toml            # runtime = python, entry = main.py
    └── main.py
```

### SKILL.md format

```markdown
---
name: rust-expert
description: "Rust programming expert for ownership, lifetimes, async/await, traits, and unsafe code"
---
# Rust Programming Expertise

You are an expert Rust developer with deep understanding of the ownership system...
```

The frontmatter must contain `name` and `description`. The Markdown body becomes the injected prompt.

### skill.toml format (optional)

Only required when you need `[runtime]`, `[input]` schema, or structured metadata beyond what frontmatter supports:

```toml
[skill]
name = "meeting-agenda"
version = "0.1.0"
description = "Generate a structured meeting agenda from a topic and duration."
tags = ["meeting", "productivity"]

[runtime]
type = "promptonly"    # promptonly | python | node | shell

[input]
topic = { type = "string", description = "The meeting topic", required = true }
duration_minutes = { type = "string", description = "Duration in minutes", required = true }
```

If both files exist, `skill.name` and `skill.description` in `skill.toml` must match the frontmatter in `SKILL.md`. The validator enforces this to prevent drift.

## Installing and Using Skills

```bash
# List all available skills in the registry
librefang catalog skills

# Attach a skill to an agent
librefang skill attach <agent-name> rust-expert

# Attach multiple skills
librefang skill attach <agent-name> rust-expert security-audit

# Detach a skill
librefang skill detach <agent-name> rust-expert

# Test a skill locally with sample input
librefang skill test ./skills/meeting-agenda \
  --input '{"topic": "Q1 planning", "duration_minutes": "30"}'
```

## All Skills (61 total)

### Programming Languages

| Name | Description |
|------|-------------|
| css-expert | CSS expert for flexbox, grid, animations, responsive design, and modern layout techniques |
| golang-expert | Go programming expert for goroutines, channels, interfaces, modules, and concurrency patterns |
| python-expert | Python expert for stdlib, packaging, type hints, async/await, and performance optimization |
| rust-expert | Rust programming expert for ownership, lifetimes, async/await, traits, and unsafe code |
| typescript-expert | TypeScript expert for type system, generics, utility types, and strict mode patterns |
| wasm-expert | WebAssembly expert for WASI, component model, Rust/C compilation, and browser integration |

### Web Frameworks and APIs

| Name | Description |
|------|-------------|
| graphql-expert | GraphQL expert for schema design, resolvers, subscriptions, and performance optimization |
| nextjs-expert | Next.js expert for App Router, SSR/SSG, API routes, middleware, and deployment |
| oauth-expert | OAuth 2.0 and OpenID Connect expert for authorization flows, PKCE, and token management |
| openapi-expert | OpenAPI/Swagger expert for API specification design, validation, and code generation |
| react-expert | React expert for hooks, state management, Server Components, and performance optimization |

### Databases

| Name | Description |
|------|-------------|
| elasticsearch | Elasticsearch expert for queries, mappings, aggregations, index management, and cluster operations |
| mongodb | MongoDB operations expert for queries, aggregation pipelines, indexes, and schema design |
| postgres-expert | PostgreSQL expert for query optimization, indexing, extensions, and database administration |
| redis-expert | Redis expert for data structures, caching patterns, Lua scripting, and cluster operations |
| sql-analyst | SQL query expert for optimization, schema design, and data analysis |
| sqlite-expert | SQLite expert for WAL mode, query optimization, embedded patterns, and advanced features |
| vector-db | Vector database expert for embeddings, similarity search, RAG patterns, and indexing strategies |

### Cloud and Infrastructure

| Name | Description |
|------|-------------|
| ansible | Ansible automation expert for playbooks, roles, inventories, and infrastructure management |
| aws | AWS cloud services expert for EC2, S3, Lambda, IAM, and AWS CLI |
| azure | Microsoft Azure expert for az CLI, AKS, App Service, and cloud infrastructure |
| docker | Docker expert for containers, Compose, Dockerfiles, and debugging |
| gcp | Google Cloud Platform expert for gcloud CLI, GKE, Cloud Run, and managed services |
| helm | Helm chart expert for Kubernetes package management, templating, and dependency management |
| kubernetes | Kubernetes operations expert for kubectl, pods, deployments, and debugging |
| nginx | Nginx configuration expert for reverse proxy, load balancing, TLS, and performance tuning |
| terraform | Terraform IaC expert for providers, modules, state management, and planning |

### DevOps and CI/CD

| Name | Description |
|------|-------------|
| ci-cd | CI/CD pipeline expert for GitHub Actions, GitLab CI, Jenkins, and deployment automation |
| git-expert | Git operations expert for branching, rebasing, conflicts, and workflows |
| github | GitHub operations expert for PRs, issues, code review, Actions, and gh CLI |
| linux-networking | Linux networking expert for iptables, nftables, routing, DNS, and network troubleshooting |
| prometheus | Prometheus monitoring expert for PromQL, alerting rules, Grafana dashboards, and observability |
| sentry | Sentry error tracking and debugging specialist |
| shell-scripting | Shell scripting expert for Bash, POSIX compliance, error handling, and automation |
| sysadmin | System administration expert for Linux, macOS, Windows, services, and monitoring |

### Security

| Name | Description |
|------|-------------|
| compliance | Compliance expert for SOC 2, GDPR, HIPAA, PCI-DSS, and security frameworks |
| crypto-expert | Cryptography expert for TLS, symmetric/asymmetric encryption, hashing, and key management |
| security-audit | Security audit expert for OWASP Top 10, CVE analysis, code review, and penetration testing methodology |

### AI and Machine Learning

| Name | Description |
|------|-------------|
| llm-finetuning | LLM fine-tuning expert for LoRA, QLoRA, dataset preparation, and training optimization |
| ml-engineer | Machine learning engineer expert for PyTorch, scikit-learn, model evaluation, and MLOps |
| prompt-engineer | Prompt engineering expert for chain-of-thought, few-shot learning, evaluation, and LLM optimization |
| web-search | Web search and research specialist for finding and synthesizing information |

### Productivity Tools

| Name | Description |
|------|-------------|
| confluence | Confluence wiki expert for page structure, spaces, macros, and content organization |
| figma-expert | Figma design expert for components, auto-layout, design systems, and developer handoff |
| jira | Jira project management expert for issues, sprints, workflows, and reporting |
| linear-tools | Linear project management expert for issues, cycles, projects, and workflow automation |
| notion | Notion workspace management and content creation specialist |
| pdf-reader | PDF content extraction and analysis specialist |
| slack-tools | Slack workspace management and automation specialist |

### Writing and Communication

| Name | Description |
|------|-------------|
| email-writer | Professional email writing expert for tone, structure, clarity, and business communication |
| presentation | Presentation expert for slide structure, storytelling, visual design, and audience engagement |
| technical-writer | Technical writing expert for API docs, READMEs, ADRs, and developer documentation |
| writing-coach | Writing improvement specialist for grammar, style, clarity, and structure |

### Engineering Practice

| Name | Description |
|------|-------------|
| api-tester | API testing expert for curl, REST, GraphQL, authentication, and debugging |
| code-reviewer | Code review specialist focused on patterns, bugs, security, and performance |
| data-analyst | Data analysis expert for statistics, visualization, pandas, and exploration |
| data-pipeline | Data pipeline expert for ETL, Apache Spark, Airflow, dbt, and data quality |
| interview-prep | Technical interview preparation expert for algorithms, system design, and behavioral questions |
| project-manager | Project management expert for Agile, estimation, risk management, and stakeholder communication |
| regex-expert | Regular expression expert for crafting, debugging, and explaining patterns |

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`) and the prompt body.
2. If you need `[runtime]`, `[input]`, or structured metadata, add `skills/<name>/skill.toml`.
3. Add implementation files (`main.py`, etc.) when `runtime` is not `promptonly`.
4. Run `python scripts/validate.py`.
5. Submit a PR.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
