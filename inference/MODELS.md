# Supported Models

Models recognized out of the box by ``inference``. Provider resolution
consults ``inference_runtime.yaml``'s ``model_provider`` block first; the
built-in table in ``inference/config/model_config.py`` is used as a fallback
when the runtime routing file doesn't cover a model.

## Model Providers

### OpenAI Models

| Model ID | Multimodal | Max Tokens | Context Window |
|----------|------------|------------|----------------|
| `gpt-5` | ✅ | 16384 | 200000 |
| `gpt-5-mini` | ✅ | 16384 | 200000 |
| `gpt-4o` | ✅ | 16384 | 128000 |
| `gpt-4o-mini` | ✅ | 16384 | 128000 |
| `gpt-4-turbo` | ✅ | 4096 | 128000 |
| `gpt-4` | ❌ | 4096 | 8192 |
| `gpt-3.5-turbo` | ❌ | 4096 | 16385 |

### Anthropic Models

| Model ID | Multimodal | Max Tokens | Context Window |
|----------|------------|------------|----------------|
| `claude-3-5-sonnet-20241022` | ✅ | 8192 | 200000 |
| `claude-3-opus-20240229` | ✅ | 4096 | 200000 |
| `claude-3-sonnet-20240229` | ✅ | 4096 | 200000 |
| `claude-3-haiku-20240307` | ✅ | 4096 | 200000 |

### Google Models

| Model ID | Multimodal | Max Tokens | Context Window |
|----------|------------|------------|----------------|
| `google-ai-studio/gemini-2.5-flash` | ✅ | 8192 | 1048576 |
| `gemini-pro` | ✅ | 8192 | 1048576 |
| `gemini-pro-vision` | ✅ | 4096 | 16384 |

### Ollama Models (Local)

| Model ID | Notes |
|----------|-------|
| `llama2` | Via Ollama |
| `llama3` | Via Ollama |
| `mistral` | Via Ollama |
| `codellama` | Via Ollama |

Requires a local Ollama server (default endpoint: `http://localhost:11434`).

## Using Models

### Via Model ID

```python
from inference import LLMClient

client = LLMClient(default_model="gpt-4o")

response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o",  # can override default
)
```

### Via Configuration File

```python
from inference import LLMClient

client = LLMClient(config_path="config/inference_config.yaml")
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Looking Up a Provider

```python
from inference.config import lookup_provider

lookup_provider("gpt-4o")              # "openai"
lookup_provider("claude-3-opus-20240229")  # "anthropic"
lookup_provider("unknown-model")       # None
```

## Model Configuration

Models can be configured via:

1. **Environment variables**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. (or whatever names your `inference_runtime.yaml` maps under `provider_key_env`).
2. **Routing file**: `inference_runtime.yaml` (see `.env.example` + the routing docstring in `base_client.py`).
3. **Per-call override**: pass a `ModelConfig` to `client.call(...)`.

```python
from inference import LLMClient, ModelConfig

client = LLMClient()
config = ModelConfig(temperature=0.9, max_tokens=2000, top_p=0.95)

response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    config=config,
)
```
