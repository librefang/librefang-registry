# Providers

LLM provider and model metadata for LibreFang. Each `.toml` file defines one provider's API configuration and all its available models with pricing, context windows, and capability flags.

**Current state: 46 providers, 232+ models**

---

## Provider Categories

### Frontier / Major Cloud APIs

| ID | Display Name | API Key Env | Models | Notes |
|----|-------------|-------------|--------|-------|
| `anthropic` | Anthropic | `ANTHROPIC_API_KEY` | 7 | Claude family; native Anthropic protocol |
| `openai` | OpenAI | `OPENAI_API_KEY` | 15 | GPT + o-series; also used by codex-cli fallback |
| `gemini` | Google Gemini | `GEMINI_API_KEY` | 6 | Gemini family; native Google protocol |
| `xai` | xAI | `XAI_API_KEY` | 7 | Grok models |
| `mistral` | Mistral AI | `MISTRAL_API_KEY` | 3 | Mistral / Codestral |
| `cohere` | Cohere | `COHERE_API_KEY` | 4 | Command family |
| `deepseek` | DeepSeek | `DEEPSEEK_API_KEY` | 2 | DeepSeek-V3 / R1 |
| `meta-llama` | Meta Llama | `LLAMA_API_KEY` | 4 | Direct Meta Llama API (`api.llama.com`) |
| `perplexity` | Perplexity AI | `PERPLEXITY_API_KEY` | 4 | Sonar family with live search |

### Fast Inference / Compute Clouds

| ID | Display Name | API Key Env | Models | Notes |
|----|-------------|-------------|--------|-------|
| `groq` | Groq | `GROQ_API_KEY` | 3 | Hardware-accelerated inference (GroqChip) |
| `cerebras` | Cerebras | `CEREBRAS_API_KEY` | 4 | Wafer-scale chip inference |
| `sambanova` | SambaNova | `SAMBANOVA_API_KEY` | 3 | RDU-based fast inference |
| `fireworks` | Fireworks AI | `FIREWORKS_API_KEY` | 5 | Fast open-model hosting |
| `together` | Together AI | `TOGETHER_API_KEY` | 8 | Open-model hosting + fine-tuning |
| `nvidia-nim` | NVIDIA NIM | `NVIDIA_API_KEY` | 26 | NIM microservices on NVIDIA cloud |
| `replicate` | Replicate | `REPLICATE_API_TOKEN` | 3 | Serverless model hosting (any model) |
| `huggingface` | Hugging Face | `HF_API_KEY` | 3 | Inference API for HF-hosted models |

### Cloud Platform / Enterprise

| ID | Display Name | API Key Env | Models | Notes |
|----|-------------|-------------|--------|-------|
| `bedrock` | AWS Bedrock | `AWS_ACCESS_KEY_ID` | 11 | AWS-hosted models (Claude, Llama, etc.) |
| `vertex-ai` | Google Cloud Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS` | 6 | GCP-hosted models; uses service account auth |
| `github-copilot` | GitHub Copilot | `GITHUB_TOKEN` | 1 | `ApiFormat::Copilot` — not OpenAI-compatible; requires GitHub PAT |

### Aggregators / Routers

| ID | Display Name | API Key Env | Models | Notes |
|----|-------------|-------------|--------|-------|
| `openrouter` | OpenRouter | `OPENROUTER_API_KEY` | 18+ | Meta-provider; 300+ upstream models. OpenRouter-only providers are merged here by sync script |
| `siliconflow` | SiliconFlow | `SILICONFLOW_API_KEY` | dynamic | 硅基流动; models discovered at runtime, not hardcoded |

### Chinese Providers

| ID | Display Name | API Key Env | Models | Notes |
|----|-------------|-------------|--------|-------|
| `qwen` | Qwen (Alibaba) | `DASHSCOPE_API_KEY` | 9 | Qwen3 family; multi-region via `[provider.regions]` |
| `moonshot` | Moonshot (Kimi) | `MOONSHOT_API_KEY` | 5 | Kimi general chat models |
| `minimax` | MiniMax | `MINIMAX_API_KEY` | 8 | MiniMax M-series |
| `zhipu` | Zhipu AI (GLM) | `ZHIPU_API_KEY` | 6 | GLM-4 family |
| `zai` | Z.AI | `ZHIPU_API_KEY` | 2 | Z.AI general models (shares key with zhipu) |
| `baichuan` | Baichuan (百川) | `BAICHUAN_API_KEY` | 2 | Baichuan4 family |
| `volcengine` | Volcano Engine (Doubao) | `VOLCENGINE_API_KEY` | 8 | ByteDance Doubao models |
| `stepfun` | Stepfun (阶跃星辰) | `STEPFUN_API_KEY` | 4 | Step-2 family |
| `tencent` | Tencent | `HUNYUAN_API_KEY` | 1 | Hunyuan models |
| `qianfan` | Baidu Qianfan | `QIANFAN_API_KEY` | 3 | ERNIE family |

### Coding-Specific Endpoints

These have **separate `base_url`** for coding workloads — not just model aliases. They use the same API key as their general counterpart.

| ID | Display Name | API Key Env | Models | vs. General Endpoint |
|----|-------------|-------------|--------|---------------------|
| `kimi_coding` | Kimi for Code | `KIMI_API_KEY` | 1 | `api.kimi.com/coding` vs `api.moonshot.ai/v1` |
| `alibaba-coding-plan` | Alibaba Coding Plan (Intl) | `ALIBABA_CODING_PLAN_API_KEY` | 9 | `coding-intl.dashscope.aliyuncs.com/v1` vs dashscope |
| `volcengine_coding` | Volcano Engine Coding Plan | `VOLCENGINE_API_KEY` | dynamic | `api/coding/v3` vs `api/v3` |
| `zhipu_coding` | Zhipu Coding (CodeGeeX) | `ZHIPU_API_KEY` | 1 | `api/coding/paas/v4` vs `api/paas/v4` |
| `zai_coding` | Z.AI Coding | `ZHIPU_API_KEY` | 2 | `api.z.ai/api/coding/paas/v4` vs `api/paas/v4` |

### CLI-Based Providers (No API Key)

Route through a locally-installed CLI tool. `key_required = false`, `base_url` is empty.

| ID | Display Name | CLI Tool | Models | ApiFormat |
|----|-------------|----------|--------|-----------|
| `claude-code` | Claude Code | `claude` | 3 | `ClaudeCode` |
| `codex-cli` | Codex CLI | `codex` | 6 | `CodexCli` |
| `gemini-cli` | Gemini CLI | `gemini` | 2 | `GeminiCli` |
| `qwen-code` | Qwen Code | `qwen-code` | 3 | `QwenCode`; $0 cost |

### Local / Self-Hosted

| ID | Display Name | Default URL | Notes |
|----|-------------|------------|-------|
| `ollama` | Ollama | `localhost:11434` | No key required; models discovered at runtime |
| `lmstudio` | LM Studio | `localhost:1234` | No key required |
| `vllm` | vLLM | `localhost:8000` | No key required |

### Special / Niche

| ID | Display Name | Notes |
|----|-------------|-------|
| `chatgpt` | ChatGPT (Session Auth) | Uses `chatgpt.com/backend-api` with session cookie, not API key. Exposes GPT-5.x Codex models unavailable via OpenAI API |
| `elevenlabs` | ElevenLabs | TTS / voice generation only — has dedicated `elevenlabs.rs` driver. No chat models |

---

## Inclusion Criteria

A provider gets its own `.toml` file when it meets **at least one** of:

1. Has a **direct public API** not accessible via OpenRouter
2. Has a **unique endpoint** for a specific workload (e.g. coding plan endpoints)
3. Has a **dedicated driver** (`ApiFormat` beyond generic OpenAI-compatible)
4. Is a **local/self-hosted** runtime
5. Is a **CLI-based** provider

Providers that only route through `openrouter.ai/api/v1` with `OPENROUTER_API_KEY` are **not** given standalone files — their models are merged into `openrouter.toml` by the sync script.

---

## Provider TOML Format

```toml
[provider]
id = "provider-id"                # Unique identifier (lowercase, hyphenated)
display_name = "Provider Name"
api_key_env = "PROVIDER_API_KEY"  # Env var for API key
base_url = "https://api.example.com"
key_required = true

[[models]]
id = "model-id"                   # Exact API model ID
display_name = "Model Name"
tier = "smart"                    # frontier | smart | balanced | fast | local
context_window = 128000
max_output_tokens = 16384
input_cost_per_m = 2.50           # USD per million input tokens
output_cost_per_m = 10.0          # USD per million output tokens
supports_tools = true
supports_vision = false
supports_streaming = true
aliases = ["short-name"]
```

## Tier Definitions

| Tier | Description | Examples |
|------|-------------|---------|
| `frontier` | Most capable, cutting-edge | Claude Opus, GPT-4.1 |
| `smart` | Smart, cost-effective | Claude Sonnet, Gemini 2.5 Flash |
| `balanced` | Balanced speed/cost | GPT-4.1 Mini, Llama 3.3 70B |
| `fast` | Fastest, cheapest | GPT-4o Mini, Claude Haiku |
| `local` | Local models, zero cost | Ollama, vLLM, LM Studio |

---

## Sync Script

`scripts/sync-pricing.py` runs daily via CI to keep model pricing current.

```bash
python scripts/sync-pricing.py                        # Update prices only
python scripts/sync-pricing.py --create-missing       # Also add new providers
python scripts/sync-pricing.py --dry-run --create-missing  # Preview changes
```

**`--create-missing` routing logic:**
- Provider in `PROVIDER_API` map (has direct API) → create standalone `.toml`
- Provider not in `PROVIDER_API` (OpenRouter-only) → merge into `openrouter.toml` with `openrouter/{provider}/{model}` IDs
- Provider in `SKIP_PROVIDERS` (morph, aider, kwaipilot, …) → skipped entirely
- Provider ID starts with `~` (OpenRouter internal routing alias) → skipped entirely

---

## Validation

```bash
python scripts/validate.py        # Warn on issues
python scripts/validate.py --strict  # Treat warnings as errors
```

Checks: required fields, valid tiers, non-negative costs, no duplicate model IDs.

## Adding or Updating a Provider

1. Check inclusion criteria above — if OpenRouter-only, don't create a new file
2. Create or edit the `.toml` in `providers/`
3. Use exact API model IDs; verify pricing from official sources
4. Run `python scripts/validate.py`
5. Update the table in this README
6. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full guide.
