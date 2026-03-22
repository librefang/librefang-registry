# Hands

Hand definitions for LibreFang. Hands are the user-facing "apps" -- higher-level application bundles that package an agent with tools, settings, dashboard metrics, and dependency requirements.

> "You have many hands helping you." -- Hands are how LibreFang users interact with specialized capabilities.

## Structure

```
hands/
├── browser/
│   ├── HAND.toml    # Hand definition
│   └── SKILL.md     # Expert knowledge for the agent
├── trader/
│   ├── HAND.toml
│   └── SKILL.md
└── ...
```

## HAND.toml Format

```toml
id = "hand-id"                   # Must match directory name
name = "Hand Name"
description = "What this hand does"
category = "productivity"         # communication | content | data | development |
                                  # devops | finance | productivity | research | social
icon = "🔧"
tools = ["tool1", "tool2"]

[routing]
aliases = ["activate phrases"]
weak_aliases = ["keyword hints"]

[[requires]]                      # External dependencies
key = "python3"
requirement_type = "binary"
check_value = "python3"

[[settings]]                      # User-configurable options
key = "headless"
setting_type = "toggle"
default = "true"

[agent]                           # The agent powering this hand
name = "hand-agent"
module = "builtin:chat"
system_prompt = """..."""

# Optional: i18n for name, description, category, and settings
# Supported languages: zh, ja, ko, es, fr, de
[i18n.zh]
name = "浏览器 Hand"
description = "自主网页浏览器"
category = "生产力"

[i18n.zh.settings.headless]      # Per-setting label/description translation
label = "无头模式"
description = "在后台运行浏览器"

[dashboard]                       # Dashboard metrics
[[dashboard.metrics]]
label = "Tasks Completed"
memory_key = "metric_key"
format = "number"
```

## Current Hands (14)

| Hand | Category | Description |
|------|----------|-------------|
| analytics | data | Data analytics, visualization, dashboards, and automated reporting |
| apitester | development | API testing, endpoint discovery, load testing, and regression detection |
| browser | productivity | Web navigation, form filling, and multi-step web tasks |
| clip | content | Turns long-form video into short clips with captions and thumbnails |
| collector | data | Intelligence collection, change detection, and knowledge graphs |
| devops | development | CI/CD management, infrastructure monitoring, and incident response |
| lead | data | Lead generation, enrichment, scoring, and scheduled delivery |
| linkedin | communication | LinkedIn content creation, networking, and engagement |
| predictor | data | Signal collection, calibrated predictions, and accuracy tracking |
| reddit | communication | Subreddit monitoring, content posting, and engagement tracking |
| researcher | productivity | Deep research, cross-referencing, fact-checking, and reports |
| strategist | productivity | Market research, competitive analysis, and strategic planning |
| trader | data | Market intelligence, multi-signal analysis, and risk management |
| twitter | communication | Twitter/X content creation, scheduling, and performance tracking |

## Adding a New Hand

1. Create `hands/<name>/HAND.toml` and `SKILL.md` (expert knowledge for the agent)
2. Ensure `id` matches the directory name
3. Run `python scripts/validate.py`
4. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
