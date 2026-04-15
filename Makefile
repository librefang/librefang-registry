# LibreFang Registry — Development Tooling
# Usage: make help

.DEFAULT_GOAL := help
SHELL := /bin/bash

TEMPLATES_DIR := templates
AGENTS_DIR    := agents
HANDS_DIR     := hands
INTEGRATIONS_DIR := integrations
SKILLS_DIR    := skills
PLUGINS_DIR   := plugins
PROVIDERS_DIR := providers

# ── Setup ────────────────────────────────────────────────────────────────────

.PHONY: setup
setup: ## Configure git hooks for auto-formatting
	git config core.hooksPath .githooks
	@echo "Git hooks installed (.githooks/pre-commit)"

# Auto-configure hooks on first make invocation
-include .make-setup-done
.make-setup-done:
	@git config core.hooksPath .githooks 2>/dev/null || true
	@touch .make-setup-done

# ── Validation ────────────────────────────────────────────────────────────────

.PHONY: validate
validate: ## Run registry validation
	python3 scripts/validate.py

.PHONY: validate-strict
validate-strict: ## Run validation treating warnings as errors
	python3 scripts/validate.py --strict

# ── Formatting ────────────────────────────────────────────────────────────────

.PHONY: fmt
fmt: ## Format all TOML files with taplo (skips if not installed)
	@if command -v taplo >/dev/null 2>&1; then \
		echo "Formatting TOML files..."; \
		find . -name '*.toml' -not -path './.git/*' -exec taplo fmt {} +; \
		echo "Done."; \
	else \
		echo "taplo not found — skipping TOML formatting."; \
		echo "Install: cargo install taplo-cli  or  brew install taplo"; \
	fi

.PHONY: fmt-check
fmt-check: ## Check TOML formatting without modifying
	@if command -v taplo >/dev/null 2>&1; then \
		taplo fmt --check $$(find . -name '*.toml' -not -path './.git/*'); \
	else \
		echo "taplo not found — skipping format check."; \
		echo "Install: cargo install taplo-cli  or  brew install taplo"; \
	fi

# ── Scaffolding ───────────────────────────────────────────────────────────────

.PHONY: new-agent
new-agent: ## Scaffold a new agent (usage: make new-agent NAME=my-agent)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-agent NAME=my-agent"; exit 1; fi
	@if [ -d "$(AGENTS_DIR)/$(NAME)" ]; then echo "ERROR: Agent '$(NAME)' already exists."; exit 1; fi
	@mkdir -p "$(AGENTS_DIR)/$(NAME)"
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/agent.toml" > "$(AGENTS_DIR)/$(NAME)/agent.toml"
	@echo "Created $(AGENTS_DIR)/$(NAME)/agent.toml"
	@echo "Next: edit the agent.toml to fill in TODO placeholders."

.PHONY: new-hand
new-hand: ## Scaffold a new hand (usage: make new-hand NAME=my-hand)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-hand NAME=my-hand"; exit 1; fi
	@if [ -d "$(HANDS_DIR)/$(NAME)" ]; then echo "ERROR: Hand '$(NAME)' already exists."; exit 1; fi
	@mkdir -p "$(HANDS_DIR)/$(NAME)"
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/HAND.toml" > "$(HANDS_DIR)/$(NAME)/HAND.toml"
	@echo "Created $(HANDS_DIR)/$(NAME)/HAND.toml"
	@echo "Next: edit the HAND.toml to fill in TODO placeholders."

.PHONY: new-integration
new-integration: ## Scaffold a new integration (usage: make new-integration NAME=my-service)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-integration NAME=my-service"; exit 1; fi
	@if [ -f "$(INTEGRATIONS_DIR)/$(NAME).toml" ]; then echo "ERROR: Integration '$(NAME)' already exists."; exit 1; fi
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/integration.toml" > "$(INTEGRATIONS_DIR)/$(NAME).toml"
	@echo "Created $(INTEGRATIONS_DIR)/$(NAME).toml"
	@echo "Next: edit the file to fill in TODO placeholders."

.PHONY: new-skill
new-skill: ## Scaffold a new skill (usage: make new-skill NAME=my-skill)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-skill NAME=my-skill"; exit 1; fi
	@if [ -d "$(SKILLS_DIR)/$(NAME)" ]; then echo "ERROR: Skill '$(NAME)' already exists."; exit 1; fi
	@mkdir -p "$(SKILLS_DIR)/$(NAME)"
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/skill.toml" > "$(SKILLS_DIR)/$(NAME)/skill.toml"
	@echo "Created $(SKILLS_DIR)/$(NAME)/skill.toml"
	@echo "Next: edit the skill.toml to fill in TODO placeholders."

.PHONY: new-plugin
new-plugin: ## Scaffold a new plugin (usage: make new-plugin NAME=my-plugin)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-plugin NAME=my-plugin"; exit 1; fi
	@if [ -d "$(PLUGINS_DIR)/$(NAME)" ]; then echo "ERROR: Plugin '$(NAME)' already exists."; exit 1; fi
	@mkdir -p "$(PLUGINS_DIR)/$(NAME)/hooks"
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/plugin.toml" > "$(PLUGINS_DIR)/$(NAME)/plugin.toml"
	@touch "$(PLUGINS_DIR)/$(NAME)/hooks/ingest.py"
	@touch "$(PLUGINS_DIR)/$(NAME)/hooks/after_turn.py"
	@touch "$(PLUGINS_DIR)/$(NAME)/requirements.txt"
	@echo "Created $(PLUGINS_DIR)/$(NAME)/ with plugin.toml and hooks/"
	@echo "Next: implement the hook scripts and fill in TODO placeholders."

.PHONY: new-provider
new-provider: ## Scaffold a new provider (usage: make new-provider NAME=my-provider)
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME is required. Usage: make new-provider NAME=my-provider"; exit 1; fi
	@if [ -f "$(PROVIDERS_DIR)/$(NAME).toml" ]; then echo "ERROR: Provider '$(NAME)' already exists."; exit 1; fi
	@sed 's/{{NAME}}/$(NAME)/g' "$(TEMPLATES_DIR)/provider.toml" > "$(PROVIDERS_DIR)/$(NAME).toml"
	@echo "Created $(PROVIDERS_DIR)/$(NAME).toml"
	@echo "Next: edit the file to fill in TODO placeholders."

# ── Help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@echo "LibreFang Registry — Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Scaffold examples:"
	@echo "  make new-agent NAME=my-agent"
	@echo "  make new-hand NAME=my-hand"
	@echo "  make new-integration NAME=my-service"
	@echo "  make new-skill NAME=my-skill"
	@echo "  make new-plugin NAME=my-plugin"
	@echo "  make new-provider NAME=my-provider"
