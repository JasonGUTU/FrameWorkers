"""Runtime LLM base abstractions and compatibility exports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from ..config.model_config import ModelRegistry


class MessageRole(str, Enum):
    """Message role types."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class ModelConfig:
    """Configuration for model calls."""

    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False
    timeout: Optional[float] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Chat message structure."""

    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class BaseLLMClient(ABC):
    """Base class shared by all concrete client implementations."""
    _env_initialized: bool = False
    _routing_initialized: bool = False
    _runtime_routing: Dict[str, Any] = {}

    def __init__(
        self,
        default_model: Optional[str] = None,
        config_path: Optional[str] = None,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: str = "medium",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        if not BaseLLMClient._env_initialized:
            # Load .env once per process before reading os.getenv defaults.
            from ..config.config_loader import ConfigLoader

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
        self.model_registry = ModelRegistry()
        self.config_path = config_path
        if config_path:
            self._load_config(config_path)

    def _load_runtime_routing(self) -> Dict[str, Any]:
        """Load user-defined runtime routing config from project root."""
        from ..config.config_loader import ConfigLoader

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
            provider_key_env = routing.get("provider_key_env", {}) if isinstance(routing, dict) else {}
            for provider, key_value in api_keys.items():
                if key_value in (None, ""):
                    continue
                env_name = provider_key_env.get(provider, f"{str(provider).upper()}_API_KEY")
                if not os.getenv(env_name):
                    os.environ[env_name] = str(key_value)

        return routing if isinstance(routing, dict) else {}

    def get_runtime_routing(self) -> Dict[str, Any]:
        """Return cached runtime routing config."""
        return BaseLLMClient._runtime_routing

    def resolve_provider_for_model(self, model: Optional[str]) -> str:
        """Resolve provider using user routing first, then model registry."""
        resolved_model = model or self.model or self.default_model
        if not resolved_model:
            return "openai"

        routing = self.get_runtime_routing()
        model_provider_map = routing.get("model_provider", {}) if isinstance(routing, dict) else {}
        if isinstance(model_provider_map, dict):
            mapped = model_provider_map.get(resolved_model)
            if mapped:
                return str(mapped)

        model_info = self.model_registry.get_model(resolved_model)
        if model_info is not None and model_info.provider:
            return model_info.provider

        default_provider = routing.get("default_provider") if isinstance(routing, dict) else None
        return str(default_provider) if default_provider else "openai"

    def resolve_client_for_provider(self, provider: str) -> str:
        """Resolve client type for provider from routing config."""
        routing = self.get_runtime_routing()
        provider_client = routing.get("provider_client", {}) if isinstance(routing, dict) else {}
        if isinstance(provider_client, dict):
            mapped = provider_client.get(provider)
            if mapped:
                return str(mapped)
        return "openai_sdk" if provider == "openai" else "litellm"

    def _load_config(self, config_path: str):
        from ..config.config_loader import ConfigLoader

        config = ConfigLoader.load(config_path)
        if "default_model" in config:
            self.default_model = config["default_model"]
            self.model = self.default_model
        if "api_keys" in config:
            for provider, key in config["api_keys"].items():
                env_var = f"{provider.upper()}_API_KEY"
                if not os.getenv(env_var):
                    os.environ[env_var] = key

    def _format_messages(
        self, messages: List[Union[Message, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        formatted = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        **(
                            {
                                k: v
                                for k, v in {
                                    "name": msg.name,
                                    "tool_calls": msg.tool_calls,
                                    "tool_call_id": msg.tool_call_id,
                                }.items()
                                if v is not None
                            }
                        ),
                    }
                )
            else:
                formatted.append(msg)
        return formatted

    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        return self.model_registry.list_models(provider=provider)

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        model_info = self.model_registry.get_model(model_id)
        if model_info:
            return {
                "name": model_info.name,
                "provider": model_info.provider,
                "model_id": model_info.model_id,
                "supports_streaming": model_info.supports_streaming,
                "supports_multimodal": model_info.supports_multimodal,
                "max_tokens": model_info.max_tokens,
                "context_window": model_info.context_window,
                "description": model_info.description,
            }
        return None

    @abstractmethod
    def call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def acall(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def stream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Iterator[Dict[str, Any]]:
        pass

    @abstractmethod
    async def astream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
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
    ) -> dict[str, Any]:
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
    ) -> str:
        pass


from .clients.default_client import LLMClient
from .clients.gpt5_client import GPT5ChatClient
from .clients.custom_model import CustomModelClient


__all__ = [
    "BaseLLMClient",
    "CustomModelClient",
    "GPT5ChatClient",
    "LLMClient",
    "Message",
    "MessageRole",
    "ModelConfig",
]
