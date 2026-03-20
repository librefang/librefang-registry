#!/usr/bin/env python3
"""Validate all TOML files in the LibreFang registry.

Usage:
    python scripts/validate.py

Validates:
    - Provider TOML files (required fields, valid tiers, non-negative costs, no duplicates)
    - Agent TOML files (required fields: name, description, module)
    - Hand TOML files (required fields: id, name, description, category)
    - Integration TOML files (required fields: id, name, [transport])
    - Skill TOML files (required fields: [skill].name, [runtime].type)
    - aliases.toml parsing

Exit code 0 on success, 1 on any validation error.
"""

import os
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        print("ERROR: Python 3.11+ required, or install 'tomli': pip install tomli")
        sys.exit(1)

VALID_TIERS = {"frontier", "smart", "balanced", "fast", "local"}
VALID_HAND_CATEGORIES = {
    "communication", "content", "data", "development",
    "devops", "finance", "productivity", "research", "social",
}
VALID_SKILL_RUNTIMES = {"promptonly", "python", "node", "shell"}

REQUIRED_PROVIDER_FIELDS = {"id", "display_name", "api_key_env", "base_url", "key_required"}
REQUIRED_MODEL_FIELDS = {
    "id", "display_name", "tier",
    "context_window", "max_output_tokens",
    "input_cost_per_m", "output_cost_per_m",
}


def load_toml(filepath: Path) -> tuple[dict | None, str | None]:
    """Load a TOML file, return (data, error)."""
    try:
        with open(filepath, "rb") as f:
            return tomllib.load(f), None
    except Exception as e:
        return None, f"{filepath}: Failed to parse TOML: {e}"


def validate_provider_file(filepath: Path) -> list[str]:
    """Validate a single provider TOML file."""
    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []
    provider = data.get("provider")
    if provider is None:
        errors.append(f"{filepath.name}: Missing [provider] section")
    else:
        for field in REQUIRED_PROVIDER_FIELDS:
            if field not in provider:
                errors.append(f"{filepath.name}: Missing provider field '{field}'")

    models = data.get("models", [])
    seen_ids = set()

    for i, model in enumerate(models):
        label = model.get("id", f"models[{i}]")
        for field in REQUIRED_MODEL_FIELDS:
            if field not in model:
                errors.append(f"{filepath.name}: Model '{label}' missing field '{field}'")

        tier = model.get("tier")
        if tier is not None and tier not in VALID_TIERS:
            errors.append(f"{filepath.name}: Model '{label}' invalid tier '{tier}'")

        for cost_field in ("input_cost_per_m", "output_cost_per_m"):
            val = model.get(cost_field)
            if val is not None and (not isinstance(val, (int, float)) or val < 0):
                errors.append(f"{filepath.name}: Model '{label}' invalid {cost_field}: {val}")

        for int_field in ("context_window", "max_output_tokens"):
            val = model.get(int_field)
            if val is not None and (not isinstance(val, int) or val <= 0):
                errors.append(f"{filepath.name}: Model '{label}' invalid {int_field}: {val}")

        model_id = model.get("id")
        if model_id:
            if model_id in seen_ids:
                errors.append(f"{filepath.name}: Duplicate model ID '{model_id}'")
            seen_ids.add(model_id)

    return errors


def validate_agent_file(filepath: Path) -> list[str]:
    """Validate an agent.toml file."""
    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []
    rel = filepath.relative_to(filepath.parent.parent)

    for field in ("name", "description", "module"):
        if field not in data:
            errors.append(f"{rel}: Missing required field '{field}'")

    if "model" in data:
        model = data["model"]
        if "system_prompt" not in model and "provider" not in model:
            errors.append(f"{rel}: [model] section should have 'provider' or 'system_prompt'")

    return errors


def validate_hand_file(filepath: Path) -> list[str]:
    """Validate a HAND.toml file."""
    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []
    rel = filepath.relative_to(filepath.parent.parent.parent)

    for field in ("id", "name", "description"):
        if field not in data:
            errors.append(f"{rel}: Missing required field '{field}'")

    category = data.get("category")
    if category and category not in VALID_HAND_CATEGORIES:
        errors.append(f"{rel}: Invalid category '{category}' (valid: {', '.join(sorted(VALID_HAND_CATEGORIES))})")

    if "agent" not in data:
        errors.append(f"{rel}: Missing [agent] section")

    return errors


def validate_integration_file(filepath: Path) -> list[str]:
    """Validate an integration TOML file."""
    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []

    for field in ("id", "name"):
        if field not in data:
            errors.append(f"{filepath.name}: Missing required field '{field}'")

    if "transport" not in data:
        errors.append(f"{filepath.name}: Missing [transport] section")
    else:
        transport = data["transport"]
        if "type" not in transport:
            errors.append(f"{filepath.name}: Missing transport.type")
        if "command" not in transport:
            errors.append(f"{filepath.name}: Missing transport.command")

    return errors


def validate_skill_file(filepath: Path) -> list[str]:
    """Validate a skill.toml file."""
    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []
    rel = filepath.relative_to(filepath.parent.parent)

    skill = data.get("skill")
    if skill is None:
        errors.append(f"{rel}: Missing [skill] section")
    else:
        if "name" not in skill:
            errors.append(f"{rel}: Missing skill.name")

    runtime = data.get("runtime")
    if runtime is None:
        errors.append(f"{rel}: Missing [runtime] section")
    else:
        rt = runtime.get("type")
        if rt and rt not in VALID_SKILL_RUNTIMES:
            errors.append(f"{rel}: Invalid runtime type '{rt}' (valid: {', '.join(sorted(VALID_SKILL_RUNTIMES))})")

    return errors


def validate_aliases_file(filepath: Path) -> list[str]:
    """Validate aliases.toml."""
    if not filepath.exists():
        return [f"aliases.toml not found at {filepath}"]

    data, err = load_toml(filepath)
    if err:
        return [err]

    errors = []
    aliases = data.get("aliases", {})
    if not isinstance(aliases, dict):
        errors.append("aliases.toml: [aliases] must be a table of string -> string mappings")
    else:
        for alias, target in aliases.items():
            if not isinstance(target, str):
                errors.append(f"aliases.toml: Alias '{alias}' must map to a string, got {type(target).__name__}")

    return errors


def main():
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent

    all_errors = []
    stats = {}

    # --- Providers ---
    providers_dir = root / "providers"
    if providers_dir.is_dir():
        toml_files = sorted(providers_dir.glob("*.toml"))
        total_models = 0
        global_model_ids = {}

        for fp in toml_files:
            all_errors.extend(validate_provider_file(fp))
            data, _ = load_toml(fp)
            if data:
                models = data.get("models", [])
                total_models += len(models)
                provider_id = data.get("provider", {}).get("id", fp.stem)
                for m in models:
                    mid = m.get("id")
                    if mid:
                        key = (mid, provider_id)
                        if key in global_model_ids:
                            prev = global_model_ids[key]
                            if prev != fp.name:
                                all_errors.append(
                                    f"Cross-file duplicate: model '{mid}' (provider '{provider_id}') "
                                    f"in both {prev} and {fp.name}"
                                )
                        else:
                            global_model_ids[key] = fp.name

        stats["providers"] = len(toml_files)
        stats["models"] = total_models

    # --- Agents ---
    agents_dir = root / "agents"
    if agents_dir.is_dir():
        agent_dirs = sorted([d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        for d in agent_dirs:
            agent_toml = d / "agent.toml"
            if agent_toml.exists():
                all_errors.extend(validate_agent_file(agent_toml))
            else:
                all_errors.append(f"agents/{d.name}: Missing agent.toml")
        stats["agents"] = len(agent_dirs)

    # --- Hands ---
    hands_dir = root / "hands"
    if hands_dir.is_dir():
        hand_dirs = sorted([d for d in hands_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        for d in hand_dirs:
            hand_toml = d / "HAND.toml"
            if hand_toml.exists():
                all_errors.extend(validate_hand_file(hand_toml))
            else:
                all_errors.append(f"hands/{d.name}: Missing HAND.toml")
        stats["hands"] = len(hand_dirs)

    # --- Integrations ---
    integrations_dir = root / "integrations"
    if integrations_dir.is_dir():
        int_files = sorted(integrations_dir.glob("*.toml"))
        for fp in int_files:
            all_errors.extend(validate_integration_file(fp))
        stats["integrations"] = len(int_files)

    # --- Skills ---
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        for d in skill_dirs:
            skill_toml = d / "skill.toml"
            if skill_toml.exists():
                all_errors.extend(validate_skill_file(skill_toml))
            else:
                all_errors.append(f"skills/{d.name}: Missing skill.toml")
        stats["skills"] = len(skill_dirs)

    # --- Aliases ---
    all_errors.extend(validate_aliases_file(root / "aliases.toml"))

    # --- Report ---
    print("=" * 60)
    print("LibreFang Registry Validation")
    print("=" * 60)
    print()

    if all_errors:
        print(f"ERRORS ({len(all_errors)}):")
        for error in all_errors:
            print(f"  - {error}")
        print()

    print("Content summary:")
    for key in ("providers", "models", "agents", "hands", "integrations", "skills"):
        if key in stats:
            print(f"  {key:20s} {stats[key]:>4}")
    print()

    if all_errors:
        print(f"VALIDATION FAILED with {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
