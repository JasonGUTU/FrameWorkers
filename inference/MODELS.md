# Supported Models

This document lists all supported models in the Inference module.

## Model Providers

### OpenAI Models

| Model ID | Name | Multimodal | Max Tokens | Context Window |
|----------|------|------------|------------|----------------|
| `gpt-4o` | GPT-4o | ✅ | 16384 | 128000 |
| `gpt-4o-mini` | GPT-4o Mini | ✅ | 16384 | 128000 |
| `gpt-4-turbo` | GPT-4 Turbo | ✅ | 4096 | 128000 |
| `gpt-4` | GPT-4 | ❌ | 4096 | 8192 |
| `gpt-3.5-turbo` | GPT-3.5 Turbo | ❌ | 4096 | 16385 |

### Anthropic Models

| Model ID | Name | Multimodal | Max Tokens | Context Window |
|----------|------|------------|------------|----------------|
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet | ✅ | 8192 | 200000 |
| `claude-3-opus-20240229` | Claude 3 Opus | ✅ | 4096 | 200000 |
| `claude-3-sonnet-20240229` | Claude 3 Sonnet | ✅ | 4096 | 200000 |
| `claude-3-haiku-20240307` | Claude 3 Haiku | ✅ | 4096 | 200000 |

### Google Models

| Model ID | Name | Multimodal | Max Tokens | Context Window |
|----------|------|------------|------------|----------------|
| `google-ai-studio/gemini-2.5-flash` | Gemini 2.5 Flash | ✅ | 8192 | 1048576 |
| `gemini-pro-vision` | Gemini Pro Vision | ✅ | 4096 | 16384 |

`gemini-pro` is kept as a compatibility alias and is automatically canonicalized to `google-ai-studio/gemini-2.5-flash`.

### Ollama Models (Local/Custom)

| Model ID | Name | Multimodal | Notes |
|----------|------|------------|-------|
| `llama2` | Llama 2 | ❌ | Via Ollama |
| `llama3` | Llama 3 | ❌ | Via Ollama |
| `mistral` | Mistral | ❌ | Via Ollama |
| `codellama` | Code Llama | ❌ | Via Ollama |

**Note**: Ollama models require a local Ollama server running. Default endpoint: `http://localhost:11434`

## Using Models

### Via Model ID

```python
from inference import LLMClient

client = LLMClient(default_model="gpt-4o")

response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o"  # Can override default
)
```

### Via Configuration File

```python
from inference import LLMClient

client = LLMClient(config_path="config/inference_config.yaml")

# Uses default_model from config
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Listing Available Models

```python
from inference import ModelRegistry

registry = ModelRegistry()

# List all models
all_models = registry.list_models()

# List by provider
openai_models = registry.list_models(provider="openai")
anthropic_models = registry.list_models(provider="anthropic")

# Get model info
model_info = registry.get_model("gpt-4o")
print(model_info.name)
print(model_info.supports_multimodal)
```

## Custom Models

You can register custom models:

```python
from inference import CustomModelClient, ModelInfo

client = CustomModelClient()

client.register_custom_model(
    model_id="my-custom-model",
    name="My Custom Model",
    provider="custom",
    supports_streaming=True,
    supports_multimodal=False,
    max_tokens=4096,
    context_window=8192
)
```

## Model Configuration

Models can be configured via:

1. **Environment Variables**: Set API keys as environment variables
2. **Configuration File**: Use `inference_config.yaml`
3. **Code**: Pass `ModelConfig` object to calls

Example:

```python
from inference import LLMClient, ModelConfig

client = LLMClient()

config = ModelConfig(
    temperature=0.9,
    max_tokens=2000,
    top_p=0.95
)

response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    config=config
)
```
