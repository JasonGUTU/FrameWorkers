"""Custom model client (e.g., Ollama)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterator, List, Optional, Union

import requests

from .default_client import LLMClient
from ..base_client import Message, ModelConfig


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

    def call_ollama(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        resolved_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": resolved_model,
            "messages": self._format_messages(messages),
            "stream": False,
        }
        if config:
            if config.temperature is not None:
                payload.setdefault("options", {})["temperature"] = config.temperature
            if config.max_tokens:
                payload.setdefault("options", {})["num_predict"] = config.max_tokens
        payload.update(kwargs)
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=config.timeout if config else 60.0,
        )
        response.raise_for_status()
        return response.json()

    def stream_ollama(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Iterator[Dict[str, Any]]:
        resolved_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": resolved_model,
            "messages": self._format_messages(messages),
            "stream": True,
        }
        if config:
            if config.temperature is not None:
                payload.setdefault("options", {})["temperature"] = config.temperature
            if config.max_tokens:
                payload.setdefault("options", {})["num_predict"] = config.max_tokens
        payload.update(kwargs)
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=config.timeout if config else 60.0,
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            try:
                yield json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue

    def list_ollama_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []

    def pull_ollama_model(self, model_name: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300.0,
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
