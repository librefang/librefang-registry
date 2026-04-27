# Providers

LLM provider and model metadata for LibreFang. Each `.toml` file defines one provider's API configuration and all its available models with pricing, context windows, and capability flags.

**Current state: 46 providers, 232+ models**

---

## Provider Categories

### Frontier / Major Cloud APIs

| ID | Display Name | Base URL | API Key Env | Models | Description |
|----|-------------|----------|-------------|--------|-------------|
| `anthropic` | Anthropic | `https://api.anthropic.com` | `ANTHROPIC_API_KEY` | 7 | Claude family (Haiku / Sonnet / Opus); native Anthropic wire protocol, not OpenAI-compatible |
| `openai` | OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` | 15 | GPT-4.x, o-series reasoning, image generation, TTS; also the fallback for codex-cli |
| `gemini` | Google Gemini | `https://generativelanguage.googleapis.com` | `GEMINI_API_KEY` | 6 | Gemini 2.x family; native Google GenerativeLanguage protocol |
| `xai` | xAI | `https://api.x.ai/v1` | `XAI_API_KEY` | 7 | Grok-3 family from Elon Musk's xAI |
| `mistral` | Mistral AI | `https://api.mistral.ai/v1` | `MISTRAL_API_KEY` | 3 | Mistral Large / Small / Codestral; European frontier models |
| `cohere` | Cohere | `https://api.cohere.com/v2` | `COHERE_API_KEY` | 4 | Command R+ family; strong RAG and tool-use models |
| `deepseek` | DeepSeek | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` | 2 | DeepSeek-V3 (chat) + R1 (reasoning); extremely cost-effective |
| `meta-llama` | Meta Llama | `https://api.llama.com/v1` | `LLAMA_API_KEY` | 4 | Official Meta Llama API — direct access to Llama 3.x |
| `perplexity` | Perplexity AI | `https://api.perplexity.ai` | `PERPLEXITY_API_KEY` | 4 | Sonar family with live web search built in |

### Fast Inference / Compute Clouds

| ID | Display Name | Base URL | API Key Env | Models | Description |
|----|-------------|----------|-------------|--------|-------------|
| `groq` | Groq | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | 3 | GroqChip hardware; ~10× faster than GPU inference for supported models |
| `cerebras` | Cerebras | `https://api.cerebras.ai/v1` | `CEREBRAS_API_KEY` | 4 | Wafer-scale chip inference; best-in-class throughput for Llama |
| `sambanova` | SambaNova | `https://api.sambanova.ai/v1` | `SAMBANOVA_API_KEY` | 3 | Reconfigurable Dataflow Unit (RDU) inference; fast Llama variants |
| `fireworks` | Fireworks AI | `https://api.fireworks.ai/inference/v1` | `FIREWORKS_API_KEY` | 5 | Serverless open-model hosting; fast cold-start |
| `together` | Together AI | `https://api.together.xyz/v1` | `TOGETHER_API_KEY` | 8 | Open-model hosting (Llama, Qwen, Mistral) + fine-tuning API |
| `nvidia-nim` | NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `NVIDIA_API_KEY` | 26 | NVIDIA NIM microservices; largest model selection in registry |
| `replicate` | Replicate | `https://api.replicate.com/v1` | `REPLICATE_API_TOKEN` | 3 | Run any model as a serverless API; image + video + LLM |
| `huggingface` | Hugging Face | `https://api-inference.huggingface.co/v1` | `HF_API_KEY` | 3 | HF Serverless Inference API for hosted open models |

### Cloud Platform / Enterprise

| ID | Display Name | Base URL | API Key Env | Models | Description |
|----|-------------|----------|-------------|--------|-------------|
| `bedrock` | AWS Bedrock | `https://bedrock-runtime.us-east-1.amazonaws.com` | `AWS_ACCESS_KEY_ID` | 8 | AWS-managed models (Claude, Llama, Mistral, Nova); IAM auth |
| `vertex-ai` | Google Cloud Vertex AI | `https://us-central1-aiplatform.googleapis.com` | `GOOGLE_APPLICATION_CREDENTIALS` | 4 | GCP-hosted Gemini + third-party models; service account JSON auth |
| `github-copilot` | GitHub Copilot | `https://api.githubcopilot.com` | `GITHUB_TOKEN` | 1 | Uses `ApiFormat::Copilot` — proprietary protocol, not OpenAI-compatible; requires GitHub PAT with Copilot access |

### Aggregators / Routers

| ID | Display Name | Base URL | API Key Env | Models | Description |
|----|-------------|----------|-------------|--------|-------------|
| `openrouter` | OpenRouter | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | 40+ | Meta-provider routing to 300+ models; also receives models from OpenRouter-only providers via sync script |
| `siliconflow` | SiliconFlow | `https://api.siliconflow.cn/v1` | `SILICONFLOW_API_KEY` | dynamic | 硅基流动 — Chinese open-model hosting; models discovered at runtime, not hardcoded in TOML |

### Chinese Providers

| ID | Display Name | Base URL | API Key Env | Models | Description |
|----|-------------|----------|-------------|--------|-------------|
| `qwen` | Qwen (Alibaba) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` | 9 | Qwen3 family by Alibaba; multi-region support (`intl` / `us`) via `[provider.regions]` |
| `moonshot` | Moonshot (Kimi) | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY` | 2 | Kimi K2 / K2.5 |
| `minimax` | MiniMax | `https://api.minimax.io/v1` | `MINIMAX_API_KEY` | 4 | MiniMax M-series; strong Chinese + multilingual models |
| `zhipu` | Zhipu AI (GLM) | `https://open.bigmodel.cn/api/paas/v4` | `ZHIPU_API_KEY` | 3 | GLM-4.7 / GLM-5 by Zhipu AI (智谱); general chat + vision |
| `zai` | Z.AI | `https://api.z.ai/api/paas/v4` | `ZHIPU_API_KEY` | 2 | Z.AI general models; shares API key with zhipu |
| `baichuan` | Baichuan (百川) | `https://api.baichuan-ai.com/v1` | `BAICHUAN_API_KEY` | 1 | Baichuan4; strong Chinese-language performance |
| `volcengine` | Volcano Engine (Doubao) | `https://ark.cn-beijing.volces.com/api/v3` | `VOLCENGINE_API_KEY` | 5 | ByteDance Doubao 2.0 + UI-TARS; Ark platform |
| `stepfun` | Stepfun (阶跃星辰) | `https://api.stepfun.com/v1` | `STEPFUN_API_KEY` | 2 | Step-3 / Step-3.5 Flash; long-context reasoning |
| `tencent` | Tencent | `https://api.hunyuan.cloud.tencent.com/v1` | `HUNYUAN_API_KEY` | 1 | Hunyuan models by Tencent |
| `qianfan` | Baidu Qianfan | `https://qianfan.baidubce.com/v2` | `QIANFAN_API_KEY` | 3 | ERNIE family by Baidu; Qianfan platform |

### Coding-Specific Endpoints

Separate `base_url` for coding workloads — not just model aliases. Same API key as the general counterpart.

| ID | Display Name | Base URL | API Key Env | Models | vs. General |
|----|-------------|----------|-------------|--------|-------------|
| `kimi_coding` | Kimi for Code | `https://api.kimi.com/coding` | `KIMI_API_KEY` | 1 | vs `moonshot`: `api.moonshot.ai/v1` |
| `alibaba-coding-plan` | Alibaba Coding Plan (Intl) | `https://coding-intl.dashscope.aliyuncs.com/v1` | `ALIBABA_CODING_PLAN_API_KEY` | 9 | vs `qwen`: `dashscope.aliyuncs.com`; aggregates models from multiple vendors (MiniMax, GLM, Kimi) |
| `volcengine_coding` | Volcano Engine Coding Plan | `https://ark.cn-beijing.volces.com/api/coding/v3` | `VOLCENGINE_API_KEY` | dynamic | vs `volcengine`: `/api/v3`; models discovered at runtime |
| `zhipu_coding` | Zhipu Coding (CodeGeeX) | `https://open.bigmodel.cn/api/coding/paas/v4` | `ZHIPU_API_KEY` | 1 | vs `zhipu`: `/api/paas/v4`; CodeGeeX-4 coding model |
| `zai_coding` | Z.AI Coding | `https://api.z.ai/api/coding/paas/v4` | `ZHIPU_API_KEY` | 2 | vs `zai`: `/api/paas/v4`; GLM coding variants |

### CLI-Based Providers (No API Key)

Route through a locally-installed CLI tool. `key_required = false`, `base_url` is empty. Cost is $0.

| ID | Display Name | CLI Binary | Models | ApiFormat | Description |
|----|-------------|-----------|--------|-----------|-------------|
| `claude-code` | Claude Code | `claude` | 3 | `ClaudeCode` | Anthropic's official CLI; routes through Claude API with OAuth |
| `codex-cli` | Codex CLI | `codex` | 6 | `CodexCli` | OpenAI Codex CLI; also serves as fallback for `openai` provider |
| `gemini-cli` | Gemini CLI | `gemini` | 2 | `GeminiCli` | Google Gemini CLI; also serves as fallback for `gemini` provider |
| `qwen-code` | Qwen Code | `qwen-code` | 3 | `QwenCode` | Alibaba Qwen coding CLI |

### Local / Self-Hosted

| ID | Display Name | Default Base URL | API Key Env | Notes |
|----|-------------|-----------------|-------------|-------|
| `ollama` | Ollama | `http://localhost:11434/v1` | `OLLAMA_API_KEY` | No key required; models discovered dynamically at runtime via `/api/tags` |
| `lmstudio` | LM Studio | `http://localhost:1234/v1` | `LMSTUDIO_API_KEY` | No key required; GUI app for running GGUF models locally |
| `vllm` | vLLM | `http://localhost:8000/v1` | `VLLM_API_KEY` | No key required; high-throughput inference server for production self-hosting |

### Special / Niche

| ID | Display Name | Base URL | API Key Env | Notes |
|----|-------------|----------|-------------|-------|
| `chatgpt` | ChatGPT (Session Auth) | `https://chatgpt.com/backend-api` | `CHATGPT_SESSION_TOKEN` | Session cookie auth, not an API key. Exposes GPT-5.x Codex models (gpt-5.1-codex etc.) that are unavailable via the standard OpenAI API |
| `elevenlabs` | ElevenLabs | `https://api.elevenlabs.io/v1` | `ELEVENLABS_API_KEY` | TTS / voice generation only — has a dedicated `elevenlabs.rs` driver in librefang-runtime. No chat models; appears in the provider list for media capability routing |

---

## Inclusion Criteria

A provider gets its own `.toml` file when it meets **at least one** of:

1. Has a **direct public API** not accessible via OpenRouter
2. Has a **unique endpoint** for a specific workload (e.g. coding plan endpoints)
3. Has a **dedicated driver** (`ApiFormat` beyond generic `OpenAI`)
4. Is a **local/self-hosted** runtime
5. Is a **CLI-based** provider

Providers that only route through `openrouter.ai/api/v1` with `OPENROUTER_API_KEY` are **not** given standalone files — their models are merged into `openrouter.toml` by the sync script. See [scripts/sync-pricing.py](../scripts/sync-pricing.py).

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
python scripts/sync-pricing.py                             # Update prices only
python scripts/sync-pricing.py --create-missing            # Also add new providers
python scripts/sync-pricing.py --dry-run --create-missing  # Preview changes
```

**`--create-missing` routing logic:**

| Condition | Action |
|-----------|--------|
| Provider in `PROVIDER_API` map (has direct API) | Create standalone `.toml` |
| Provider not in `PROVIDER_API` (OpenRouter-only) | Merge into `openrouter.toml` with `openrouter/{provider}/{model}` IDs |
| Provider in `SKIP_PROVIDERS` (morph, aider, kwaipilot, …) | Skip entirely |
| Provider ID starts with `~` (OpenRouter internal routing alias) | Skip entirely |

---

## Validation

```bash
python scripts/validate.py           # Warn on issues
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
