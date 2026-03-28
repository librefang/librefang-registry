#!/usr/bin/env python3
"""Sync model pricing and providers from OpenRouter API.

Usage:
    python scripts/sync-pricing.py [--dry-run] [--create-missing]

Fetches current pricing from https://openrouter.ai/api/v1/models and:
1. Updates input_cost_per_m / output_cost_per_m in existing providers/*.toml
2. With --create-missing: generates TOML files for providers not yet in registry
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

OPENROUTER_API = "https://openrouter.ai/api/v1/models"
PROVIDERS_DIR = Path(__file__).parent.parent / "providers"

# Map OpenRouter provider prefixes → our TOML filenames (when they differ)
PROVIDER_ALIAS = {
    "google": "gemini",
    "mistralai": "mistral",
    "x-ai": "xai",
    "moonshotai": "moonshot",
    "z-ai": "zhipu",
    "bytedance-seed": "volcengine",
    "baidu": "qianfan",
    "meta-llama": "meta-llama",
}

# Skip these — community finetunes, not real providers
SKIP_PROVIDERS = {
    "sao10k", "thedrummer", "undi95", "gryphe", "cognitivecomputations",
    "anthracite-org", "alpindale", "alfredpros", "mancer",
}


def fetch_openrouter_models():
    """Fetch all models from OpenRouter."""
    req = urllib.request.Request(OPENROUTER_API)
    req.add_header("User-Agent", "librefang-registry/sync-pricing")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("data", [])


def parse_pricing(model):
    """Extract per-million pricing from an OpenRouter model entry."""
    p = model.get("pricing", {})
    prompt = p.get("prompt")
    completion = p.get("completion")
    if not prompt or not completion:
        return None, None
    try:
        return round(float(prompt) * 1_000_000, 4), round(float(completion) * 1_000_000, 4)
    except (ValueError, TypeError):
        return None, None


def update_toml_prices(toml_path, models_by_id, dry_run=False):
    """Update pricing fields in an existing TOML file."""
    content = toml_path.read_text()
    lines = content.split("\n")
    updated = 0
    current_model_id = None
    new_lines = []

    for line in lines:
        id_match = re.match(r'^id\s*=\s*"([^"]+)"', line)
        if id_match:
            current_model_id = id_match.group(1)

        cost_match = re.match(r'^(input_cost_per_m|output_cost_per_m)\s*=\s*([\d.]+)', line)
        if cost_match and current_model_id:
            field = cost_match.group(1)
            old_val = float(cost_match.group(2))

            # Find best matching OpenRouter model — prefer exact match over substring
            new_val = None
            best_match = None
            best_specificity = 0
            for or_id, (inp, outp) in models_by_id.items():
                or_model = or_id.split("/")[-1] if "/" in or_id else or_id
                if current_model_id == or_model:
                    # Exact match on model name (highest priority)
                    best_match = (inp, outp)
                    best_specificity = 3
                    break
                elif or_model == current_model_id + ":free" and best_specificity < 1:
                    # Free variant — only use if no paid version found
                    best_match = (inp, outp)
                    best_specificity = 1
                elif current_model_id in or_id and ":free" not in or_id and best_specificity < 2:
                    # Substring match on paid model
                    best_match = (inp, outp)
                    best_specificity = 2
            if best_match:
                new_val = best_match[0] if field == "input_cost_per_m" else best_match[1]

            if new_val is not None and abs(new_val - old_val) > 0.001:
                new_lines.append(f"{field} = {new_val}")
                print(f"  {toml_path.name}: {current_model_id}.{field}: {old_val} -> {new_val}")
                updated += 1
                continue

        new_lines.append(line)

    if updated > 0 and not dry_run:
        toml_path.write_text("\n".join(new_lines))
    return updated


def generate_provider_toml(provider_id, models, dry_run=False):
    """Generate a new provider TOML file from OpenRouter data."""
    our_name = PROVIDER_ALIAS.get(provider_id, provider_id)
    toml_path = PROVIDERS_DIR / f"{our_name}.toml"

    if toml_path.exists():
        return 0

    # Derive api_key_env from provider name: FOO_BAR -> FOO_BAR_API_KEY
    env_key = our_name.upper().replace("-", "_") + "_API_KEY"

    lines = [
        f'# {provider_id} — auto-generated from OpenRouter API',
        f"",
        f"[provider]",
        f'id = "{our_name}"',
        f'display_name = "{provider_id.replace("-", " ").title()}"',
        f'api_key_env = "{env_key}"',
        f'base_url = ""',
        f"key_required = true",
        f"",
    ]

    count = 0
    for m in sorted(models, key=lambda x: x.get("id", "")):
        model_id = m["id"].split("/")[-1] if "/" in m["id"] else m["id"]
        display = m.get("name", model_id)
        ctx = m.get("context_length", 0)
        max_out = m.get("top_provider", {}).get("max_completion_tokens", 0)
        inp, outp = parse_pricing(m)
        if inp is None:
            continue

        supports_tools = "tool_use" in str(m.get("supported_parameters", []))
        supports_vision = "vision" in str(m.get("architecture", {}).get("modality", ""))

        # Infer tier from pricing
        if inp == 0 and outp == 0:
            tier = "fast"
        elif inp < 0.5:
            tier = "fast"
        elif inp < 3.0:
            tier = "smart"
        else:
            tier = "frontier"

        # Default max_output_tokens if not provided
        if not max_out:
            max_out = min(ctx // 4, 16384) if ctx > 0 else 4096

        lines.append("[[models]]")
        lines.append(f'id = "{model_id}"')
        lines.append(f'display_name = "{display}"')
        lines.append(f'tier = "{tier}"')
        lines.append(f"context_window = {ctx}")
        lines.append(f"max_output_tokens = {max_out}")
        lines.append(f"input_cost_per_m = {inp}")
        lines.append(f"output_cost_per_m = {outp}")
        if supports_tools:
            lines.append("supports_tools = true")
        if supports_vision:
            lines.append("supports_vision = true")
        lines.append("supports_streaming = true")
        lines.append("")
        count += 1

    if count == 0:
        return 0

    print(f"  NEW: {our_name}.toml ({count} models)")

    if not dry_run:
        toml_path.write_text("\n".join(lines))
    return count


def main():
    dry_run = "--dry-run" in sys.argv
    create_missing = "--create-missing" in sys.argv

    print("Fetching models from OpenRouter API...")
    all_models = fetch_openrouter_models()
    print(f"Got {len(all_models)} models")

    # Build pricing index
    pricing = {}
    by_provider = {}
    for m in all_models:
        mid = m.get("id", "")
        inp, outp = parse_pricing(m)
        if inp is not None:
            pricing[mid] = (inp, outp)
        if "/" in mid:
            p = mid.split("/")[0]
            by_provider.setdefault(p, []).append(m)

    # Update existing providers
    total_updated = 0
    for toml_file in sorted(PROVIDERS_DIR.glob("*.toml")):
        count = update_toml_prices(toml_file, pricing, dry_run=dry_run)
        total_updated += count

    # Create missing providers
    total_created = 0
    if create_missing:
        print("\nChecking for missing providers...")
        for provider_id, models in sorted(by_provider.items()):
            if provider_id in SKIP_PROVIDERS:
                continue
            our_name = PROVIDER_ALIAS.get(provider_id, provider_id)
            if not (PROVIDERS_DIR / f"{our_name}.toml").exists():
                count = generate_provider_toml(provider_id, models, dry_run=dry_run)
                total_created += count

    action = "Would" if dry_run else "Done:"
    print(f"\n{action} updated {total_updated} prices, created {total_created} new model entries")


if __name__ == "__main__":
    main()
