# mempalace-indexer

LibreFang plugin for persistent, local semantic memory via [MemPalace](https://github.com/milla-jovovich/mempalace). No API keys, no cloud.

## Quick start

```bash
librefang plugin install mempalace-indexer
librefang plugin requirements mempalace-indexer

mempalace init /path/to/workspace --yes
mempalace mine /path/to/workspace
```

Restart the daemon. Done.

## Hooks

| Hook | When | What |
|------|------|------|
| `ingest` | Message arrives | Searches palace for relevant memories, injects into context |
| `after_turn` | After LLM responds | Auto-saves memorable turns with dedup + classification |
| `prune` | On demand / scheduled | Deletes drawers older than `MEMPALACE_MAX_AGE_DAYS` |

## How after_turn saves

Five filters run before writing to the palace:

1. **MCP dedup** — skip if the agent already called `mcp_mempalace_add_drawer` this turn
2. **Length** — skip exchanges under `MEMPALACE_MIN_CHARS` (default 80)
3. **Relevance** — English text must match keywords (decisions, appointments, contacts, etc.); non-English passes on length alone
4. **Content dedup** — skip if a near-identical turn was already saved (SHA-256 hash store)
5. **Noise** — code blocks are stripped; residual tool/error output is discarded

Matched turns are classified and written to the appropriate room:

| Content type | Wing | Room |
|---|---|---|
| Contacts, email addresses, family | `people` | `contacts` |
| Appointments, meetings, reminders | `time` | `calendar` |
| Payments, invoices, expenses | `finance` | `transactions` |
| Packages, shipments | `logistics` | `orders` |
| Decisions, preferences | `knowledge` | `decisions` |
| Everything else | `default` | `sessions` |

A single turn can match multiple rooms and will be written to all of them.

## Configuration

All settings are optional environment variables:

| Variable | Default | Description |
|---|---|---|
| `MEMPALACE_PALACE_PATH` | `~/.mempalace/palace` | Palace directory |
| `MEMPALACE_MIN_CHARS` | `80` | Minimum text length to save |
| `MEMPALACE_WINDOW_SIZE` | `6` | Recent messages to consider |
| `MEMPALACE_DEDUP_MAX` | `500` | Hash store rolling cap |
| `MEMPALACE_LANG_DETECT` | `1` | Set to `0` to disable language detection |
| `MEMPALACE_MAX_CHARS` | `300` | Max characters per injected memory snippet |
| `MEMPALACE_MIN_SIMILARITY` | `0.3` | Min similarity score for ingest results (0 = disabled) |
| `MEMPALACE_N_RESULTS` | `5` | Number of memories to inject per turn |
| `MEMPALACE_MAX_AGE_DAYS` | `90` | Prune drawers older than this (0 = disabled) |

## MCP server (optional)

Add 19 explicit memory tools to all agents:

```toml
[[mcp_servers]]
name = "mempalace"
timeout_secs = 60
[mcp_servers.transport]
type = "stdio"
command = "python3"
args = ["-m", "mempalace.mcp_server"]
```

## Pruning

Run manually:

```bash
python3 ~/.librefang/plugins/mempalace-indexer/hooks/prune.py --dry-run
python3 ~/.librefang/plugins/mempalace-indexer/hooks/prune.py
```

Or trigger via the LibreFang hook system on a schedule.
