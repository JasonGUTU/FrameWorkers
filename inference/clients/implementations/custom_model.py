"""Custom model client (e.g., Ollama)."""

from __future__ import annotations

import os
from typing import Optional

from .default_client import LLMClient


class CustomModelClient(LLMClient):
    """Client for self-hosted/custom models, especially Ollama."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        super().__init__(default_model=default_model, config_path=config_path)
        self.base_url = base_url
        self.api_key = api_key
        if "ollama" in base_url.lower() or "localhost" in base_url.lower():
            self._setup_ollama()

    def _setup_ollama(self) -> None:
        try:
            import litellm  # noqa: F401

            os.environ["OLLAMA_API_BASE"] = self.base_url
        except ImportError:
            pass

    def register_custom_model(
        self,
        model_id: str,
        name: str,
        provider: str = "custom",
        supports_streaming: bool = True,
        supports_multimodal: bool = False,
        max_tokens: Optional[int] = None,
        context_window: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        from ...config.model_config import ModelInfo

        model_info = ModelInfo(
            name=name,
            provider=provider,
            model_id=model_id,
            supports_streaming=supports_streaming,
            supports_multimodal=supports_multimodal,
            max_tokens=max_tokens,
            context_window=context_window,
            description=description or f"Custom model: {name}",
        )
        self.model_registry.register_model(model_info)

