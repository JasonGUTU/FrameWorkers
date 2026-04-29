"""Model → provider lookup used as a fallback for LLM provider resolution.

The primary mechanism for mapping a ``model_id`` to a provider is the
``model_provider`` block inside ``inference_runtime.yaml``. This table is
consulted only when the runtime routing file doesn't cover a model —
typically in dev / CI without a local routing file. Add entries here for
any model you want to work "out of the box" without configuration.
"""

from __future__ import annotations

from typing import Optional

# Kept intentionally short — the canonical map lives in
# ``inference_runtime.yaml``. Only list model ids the project actually
# uses (or might flip to without a config change).
_MODEL_PROVIDER: dict[str, str] = {
    # OpenAI (GPT-5 family is the opt-in alternative to the default Gemini
    # routing; the other GPT-4/3.5 ids were dropped from this table because
    # no caller references them.)
    "gpt-5": "openai",
    "gpt-5-mini": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    # Google (Gemini) — the default LLM for the whole project
    # (``INFERENCE_DEFAULT_MODEL`` in ``.env``). Routed via cf_aig provider
    # (CF AI Gateway native-Gemini Worker, google_genai client_type) per
    # ``inference_runtime.yaml``; the bare ``gemini-2.5-flash`` id is what
    # google.genai SDK accepts. The legacy ``gemini-pro`` /
    # ``gemini-pro-vision`` ids were removed — Google deprecated them in
    # 2024 and no caller references them.
    "gemini-2.5-flash": "cf_aig",
}


def lookup_provider(model_id: Optional[str]) -> Optional[str]:
    """Return the provider for ``model_id`` from the built-in table, or ``None`` if unknown."""
    if not model_id:
        return None
    return _MODEL_PROVIDER.get(model_id)
