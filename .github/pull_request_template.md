## Content Type

<!-- Check all that apply -->

- [ ] Agent (`agents/`)
- [ ] Hand (`hands/`)
- [ ] Integration (`integrations/`)
- [ ] Skill (`skills/`)
- [ ] Provider / Model (`providers/`)
- [ ] Other

## Changes

### Added/Updated
-

### Details
<!-- Brief description of what was added or changed -->

## Checklist

### General
- [ ] Content placed in the correct directory
- [ ] TOML files parse without errors
- [ ] Description is clear and concise

### Providers / Models (if applicable)
- [ ] `python scripts/validate.py` passes
- [ ] No duplicate model IDs
- [ ] Pricing is in USD per million tokens and verified from official source
- [ ] Tier is one of: `frontier`, `smart`, `balanced`, `fast`, `local`

### Agents (if applicable)
- [ ] `name` matches directory name
- [ ] System prompt provides clear instructions
- [ ] Tools list only includes required tools

### Hands (if applicable)
- [ ] `id` matches directory name
- [ ] `[agent]` section has complete system prompt
- [ ] `[[requires]]` lists external dependencies
- [ ] `[[settings]]` provides user-configurable options

### Integrations (if applicable)
- [ ] `[transport]` config tested locally
- [ ] `[[required_env]]` lists all needed variables
- [ ] `setup_instructions` are clear for first-time users

### Skills (if applicable)
- [ ] `[runtime].type` is correct
- [ ] `[input]` documents all parameters
- [ ] Prompt templates use correct `{{param}}` syntax
