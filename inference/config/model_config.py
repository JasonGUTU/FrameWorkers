"""Model → provider lookup used as a fallback for LLM provider resolution.

The primary mechanism for mapping a ``model_id`` to a provider is the
``model_provider`` block inside ``inference_runtime.yaml``. This table is
consulted only when the runtime routing file doesn't cover a model —
typically in dev / CI without a local routing file. Add entries here for
any model you want to work "out of the box" without configuration.
"""

from __future__ import annotations

from typing import Optional

_MODEL_PROVIDER: dict[str, str] = {
    # OpenAI
    "gpt-5": "openai",
    "gpt-5-mini": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4-turbo": "openai",
    "gpt-4": "openai",
    "gpt-3.5-turbo": "openai",
    # Anthropic
    "claude-3-5-sonnet-20241022": "anthropic",
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    # Google (AI Studio)
    "google-ai-studio/gemini-2.5-flash": "google",
    "gemini-pro": "google",
    "gemini-pro-vision": "google",
    # Ollama (local)
    "llama2": "ollama",
    "llama3": "ollama",
    "mistral": "ollama",
    "codellama": "ollama",
}


def lookup_provider(model_id: Optional[str]) -> Optional[str]:
    """Return the provider for ``model_id`` from the built-in table, or ``None`` if unknown."""
    if not model_id:
        return None
    return _MODEL_PROVIDER.get(model_id)
