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
    # Specialized coding tools / CLI wrappers — not general LLM providers
    "morph", "aider", "kwaipilot",
}

# Skip creating NEW provider files for these — they overlap with hand-written
# providers but may contain unique models, so existing files are kept.
SKIP_DUPLICATES = {
    "alibaba",      # overlaps with qwen.toml but has unique models
    "amazon",       # overlaps with bedrock.toml but has unique models
    "bytedance",    # overlaps with volcengine.toml but has unique models
    "nvidia",       # overlaps with nvidia-nim.toml but has unique models
    "rekaai",       # overlaps with reka.toml but has unique models
}

# Providers with known public APIs — set their official base_url + api_key_env.
# Providers NOT in this map route through OpenRouter.
PROVIDER_API = {
    "aion-labs":    ("https://api.aionlabs.ai/v1", "AION_LABS_API_KEY"),
    "arcee-ai":     ("https://api.arcee.ai/v1", "ARCEE_API_KEY"),
    "eleutherai":   ("https://api.krater.ai/v1", "KRATER_API_KEY"),
    "ibm-granite":  ("https://us-south.ml.cloud.ibm.com/ml/v1", "WATSONX_API_KEY"),
    "inception":    ("https://api.inceptionlabs.ai/v1", "INCEPTION_API_KEY"),
    "meta-llama":   ("https://api.llama.com/v1", "LLAMA_API_KEY"),
    "microsoft":    ("https://models.inference.ai.azure.com", "GITHUB_TOKEN"),
    "morph":        ("https://api.morphllm.com/v1", "MORPH_API_KEY"),
    "nvidia":       ("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY"),
    "reka":         ("https://api.reka.ai/v1", "REKA_API_KEY"),
    "tencent":      ("https://api.hunyuan.cloud.tencent.com/v1", "HUNYUAN_API_KEY"),
    "upstage":      ("https://api.upstage.ai/v1", "UPSTAGE_API_KEY"),
    "xiaomi":       ("https://cnbj3-cloud-ml.api.xiaomi.net", "XIAOMI_ACCESS_KEY_ID"),
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


def _build_model_fields(provider_id, m, model_id_prefix=""):
    """Extract and normalise fields for a single OpenRouter model entry.

    Returns a dict of fields, or None if pricing is missing.
    The caller supplies *model_id_prefix* (e.g. "openrouter/kwaipilot/") so
    the same helper works for both standalone files and openrouter.toml merges.
    """
    raw_id = m["id"].split("/")[-1] if "/" in m["id"] else m["id"]
    model_id = f"{model_id_prefix}{raw_id}"
    display = m.get("name", raw_id)
    ctx = m.get("context_length", 0)
    max_out = m.get("top_provider", {}).get("max_completion_tokens", 0)
    inp, outp = parse_pricing(m)
    if inp is None:
        return None

    supports_tools = "tool_use" in str(m.get("supported_parameters", []))
    supports_vision = "vision" in str(m.get("architecture", {}).get("modality", ""))

    if inp == 0 and outp == 0:
        tier = "fast"
    elif inp < 0.5:
        tier = "fast"
    elif inp < 3.0:
        tier = "smart"
    else:
        tier = "frontier"

    if not max_out:
        max_out = min(ctx // 4, 16384) if ctx > 0 else 4096

    return dict(
        model_id=model_id, display=display, tier=tier,
        ctx=ctx, max_out=max_out, inp=inp, outp=outp,
        supports_tools=supports_tools, supports_vision=supports_vision,
    )


def _model_lines(f):
    """Render a model-fields dict as TOML [[models]] lines."""
    lines = [
        "[[models]]",
        f'id = "{f["model_id"]}"',
        f'display_name = "{f["display"]}"',
        f'tier = "{f["tier"]}"',
        f'context_window = {f["ctx"]}',
        f'max_output_tokens = {f["max_out"]}',
        f'input_cost_per_m = {f["inp"]}',
        f'output_cost_per_m = {f["outp"]}',
    ]
    if f["supports_tools"]:
        lines.append("supports_tools = true")
    if f["supports_vision"]:
        lines.append("supports_vision = true")
    lines.append("supports_streaming = true")
    lines.append("")
    return lines


def merge_into_openrouter(provider_id, models, dry_run=False):
    """Append models from an OpenRouter-only provider into openrouter.toml.

    Model IDs get the prefix "openrouter/{provider_id}/" so they stay
    unambiguous and match the existing openrouter.toml convention.
    Already-present IDs are skipped to keep the operation idempotent.
    """
    openrouter_path = PROVIDERS_DIR / "openrouter.toml"
    if not openrouter_path.exists():
        return 0

    existing = openrouter_path.read_text()
    existing_ids = set(re.findall(r'^id\s*=\s*"([^"]+)"', existing, re.MULTILINE))

    new_lines = []
    for m in sorted(models, key=lambda x: x.get("id", "")):
        prefix = f"openrouter/{provider_id}/"
        f = _build_model_fields(provider_id, m, model_id_prefix=prefix)
        if f is None or f["model_id"] in existing_ids:
            continue
        # Append provider name to display so provenance is clear in the UI
        f["display"] = f'{f["display"]} (OpenRouter)'
        new_lines.extend(_model_lines(f))

    if not new_lines:
        return 0

    count = sum(1 for l in new_lines if l == "[[models]]")
    print(f"  openrouter.toml: +{count} models from {provider_id}")
    if not dry_run:
        with open(openrouter_path, "a") as fh:
            fh.write("\n" + "\n".join(new_lines))
    return count


def generate_provider_toml(provider_id, models, dry_run=False):
    """Generate a new standalone provider TOML file (direct-API providers only)."""
    our_name = PROVIDER_ALIAS.get(provider_id, provider_id)
    toml_path = PROVIDERS_DIR / f"{our_name}.toml"

    if toml_path.exists():
        return 0

    if our_name in SKIP_DUPLICATES:
        return 0

    if our_name not in PROVIDER_API:
        # No direct public API — caller should use merge_into_openrouter instead.
        return 0

    base_url, env_key = PROVIDER_API[our_name]
    key_required = "true"

    lines = [
        f'# {provider_id} — auto-generated from OpenRouter API',
        f"",
        f"[provider]",
        f'id = "{our_name}"',
        f'display_name = "{provider_id.replace("-", " ").title()}"',
        f'api_key_env = "{env_key}"',
        f'base_url = "{base_url}"',
        f"key_required = {key_required}",
        f"",
    ]

    count = 0
    for m in sorted(models, key=lambda x: x.get("id", "")):
        f = _build_model_fields(provider_id, m)
        if f is None:
            continue
        lines.extend(_model_lines(f))
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
            # Skip OpenRouter internal auto-routing aliases (e.g. "~anthropic")
            # These are not real providers — they map to openrouter.toml.
            if provider_id.startswith("~"):
                continue
            our_name = PROVIDER_ALIAS.get(provider_id, provider_id)
            if (PROVIDERS_DIR / f"{our_name}.toml").exists():
                continue
            if our_name in PROVIDER_API:
                # Provider has a known direct API — create a standalone file.
                count = generate_provider_toml(provider_id, models, dry_run=dry_run)
            else:
                # No direct API — merge models into openrouter.toml instead of
                # creating a new file that just wraps the OpenRouter endpoint.
                count = merge_into_openrouter(provider_id, models, dry_run=dry_run)
            total_created += count

    action = "Would" if dry_run else "Done:"
    print(f"\n{action} updated {total_updated} prices, created {total_created} new model entries")


if __name__ == "__main__":
    main()
