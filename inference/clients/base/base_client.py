"""LLM base abstractions for all client implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List, Optional

from ...config.model_config import lookup_provider


class BaseLLMClient(ABC):
    """Base class shared by all concrete client implementations.

    Concrete subclasses implement three async entry points:

      * ``acall`` — low-level chat completion; used by callers that need
        raw messages + provider-specific kwargs (multimodal, response_format).
      * ``chat_json`` — JSON-mode structured output; parses + validates.
      * ``chat_text`` — plain-text response.

    All three honor the runtime provider routing loaded from
    ``inference_runtime.yaml`` / built-in ``_MODEL_PROVIDER`` table.
    """

    _env_initialized: bool = False
    _routing_initialized: bool = False
    _runtime_routing: Dict[str, Any] = {}

    def __init__(
        self,
        default_model: Optional[str] = None,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: str = "medium",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        if not BaseLLMClient._env_initialized:
            from ...config.config_loader import ConfigLoader

            ConfigLoader.load_env_file()
            BaseLLMClient._env_initialized = True
        if not BaseLLMClient._routing_initialized:
            BaseLLMClient._runtime_routing = self._load_runtime_routing()
            BaseLLMClient._routing_initialized = True

        self.default_model = (
            model
            or default_model
            or os.getenv("INFERENCE_DEFAULT_MODEL", "gpt-3.5-turbo")
        )
        self.model = self.default_model
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self._api_key = api_key
        self._base_url = base_url

    def _load_runtime_routing(self) -> Dict[str, Any]:
        """Load user-defined runtime routing config from project root."""
        from ...config.config_loader import ConfigLoader

        config_path = os.getenv("INFERENCE_RUNTIME_CONFIG")
        if not config_path:
            config_path = (
                ConfigLoader.find_file_upwards("inference_runtime.yaml")
                or ConfigLoader.find_file_upwards("inference_runtime.yml")
            )
        if not config_path:
            return {}

        config = ConfigLoader.load(config_path, use_env=True)
        routing = config.get("routing", {}) if isinstance(config, dict) else {}
        api_keys = config.get("api_keys", {}) if isinstance(config, dict) else {}

        if isinstance(api_keys, dict):
            provider_key_env = (
                routing.get("provider_key_env", {}) if isinstance(routing, dict) else {}
            )
            for provider, key_value in api_keys.items():
                if key_value in (None, ""):
                    continue
                # Skip unresolved ``${VAR}`` placeholders — ConfigLoader
                # leaves the literal text when the source env var is unset,
                # and writing that into os.environ pollutes downstream
                # SDKs that probe env vars by name.
                key_str = str(key_value)
                if key_str.startswith("${") and key_str.endswith("}"):
                    continue
                env_name = provider_key_env.get(
                    provider, f"{str(provider).upper()}_API_KEY"
                )
                if not os.getenv(env_name):
                    os.environ[env_name] = key_str

        return routing if isinstance(routing, dict) else {}

    def get_runtime_routing(self) -> Dict[str, Any]:
        """Return cached runtime routing config."""
        return BaseLLMClient._runtime_routing

    def resolve_provider_for_model(self, model: Optional[str]) -> str:
        """Resolve provider: runtime routing > built-in table > runtime default > "openai"."""
        resolved_model = model or self.model or self.default_model
        if not resolved_model:
            return "openai"

        routing = self.get_runtime_routing()
        model_provider_map = (
            routing.get("model_provider", {}) if isinstance(routing, dict) else {}
        )
        if isinstance(model_provider_map, dict):
            mapped = model_provider_map.get(resolved_model)
            if mapped:
                return str(mapped)

        builtin = lookup_provider(resolved_model)
        if builtin:
            return builtin

        default_provider = (
            routing.get("default_provider") if isinstance(routing, dict) else None
        )
        return str(default_provider) if default_provider else "openai"

    def resolve_client_for_provider(self, provider: str) -> str:
        """Resolve client type for provider from routing config."""
        routing = self.get_runtime_routing()
        provider_client = (
            routing.get("provider_client", {}) if isinstance(routing, dict) else {}
        )
        if isinstance(provider_client, dict):
            mapped = provider_client.get(provider)
            if mapped:
                return str(mapped)
        return "openai_sdk" if provider == "openai" else "litellm"

    @abstractmethod
    async def acall(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Low-level async chat completion.

        ``messages`` is a list of OpenAI-format dicts (``{role, content}``).
        Extra kwargs (``response_format``, tools, etc.) flow through to the
        underlying SDK call.
        """
        pass

    @abstractmethod
    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        media_attachments: Optional[List[Dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """Generate a JSON response.

        ``media_attachments`` is an optional list of dicts with keys:
          - ``type``: ``"image"`` | ``"audio"`` | ``"video"``
          - ``path``: absolute file path
        When provided, the user message becomes a multimodal content array
        with the text + inline media (base64-encoded data URLs).
        """
        pass

    @abstractmethod
    async def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        media_attachments: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        pass
