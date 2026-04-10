# Wiki Hand

Autonomous personal knowledge base agent -- builds and maintains an Obsidian-compatible wiki from raw sources. It extracts entities, concepts, and claims with strict provenance tracking, cross-references everything, and performs periodic health checks.

## Configuration

| Field | Value |
|-------|-------|
| Category | `knowledge` |
| Agent | `librarian` |
| Routing | `wiki`, `knowledge base`, `ingest source`, `ingest deep`, `deep ingest`, `crawl`, `wiki query`, `wiki lint` |

## Integrations

- **Git** -- Required for version control. Every operation (ingest, query, lint, maintain) is automatically committed to your vault history.
- **qmd** -- (Optional) A local hybrid search engine. Recommended for wikis scaling beyond 200 pages.

## Settings

- **Wiki Vault Path** -- Directory where your wiki files will be stored (default: `./wiki`)
- **File-Back Mode** -- How to handle saving generated syntheses (`auto`, `ask`, `never`)
- **Search Backend** -- The search engine to use for queries (`index`, `qmd`)
- **Wiki Content Language** -- Target language for all generated content in the wiki (default: `en`)

## Features

- **Ingestion:** Give the agent raw sources (markdown, text, HTML, PDF via terminal) and it will extract factual claims, identify entities, and build connected concept pages.
- **Deep Ingestion (`ingest-deep`):** Provide a starting URL, and the agent will intelligently crawl the main page along with up to 5 of its most substantive sub-pages to build a comprehensive knowledge tree in one go.
- **Synthesized Queries:** Ask questions across your entire knowledge base. The agent provides answers backed by `[[wikilink]]` citations, effectively compiling its response from your collected literature.
- **Linting & Maintenance:** The agent can periodically scan the wiki to merge duplicate entities, fix broken links, identify contradictions, and point out orphan pages.

## Usage

```bash
librefang hand run wiki
```
