"""Default LLM client implementation."""

from __future__ import annotations

import json
import os
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from openai import AsyncOpenAI

from ..base_client import BaseLLMClient, Message, ModelConfig

try:
    import litellm  # noqa: F401
    from litellm import acompletion, astream, completion, stream

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMClient(BaseLLMClient):
    """Unified client with provider-based automatic routing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._openai_client: Optional[AsyncOpenAI] = None

    def _ensure_litellm(self) -> None:
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is not installed. Please install it with: pip install litellm"
            )

    def _resolve_provider(self, model: Optional[str]) -> str:
        return self.resolve_provider_for_model(model)

    def _resolve_model_and_client(self, model: Optional[str]) -> tuple[str, str, str]:
        resolved_model = model or self.model or self.default_model or "gpt-3.5-turbo"
        provider = self._resolve_provider(resolved_model)
        client_type = self.resolve_client_for_provider(provider)
        return resolved_model, provider, client_type

    def _provider_env_name(self, provider: str, category: str) -> Optional[str]:
        routing = self.get_runtime_routing()
        if category == "api_key":
            mapped = routing.get("provider_key_env", {}).get(provider) if isinstance(routing, dict) else None
            return str(mapped) if mapped else f"{provider.upper()}_API_KEY"
        if category == "base_url":
            mapped = routing.get("provider_base_url_env", {}).get(provider) if isinstance(routing, dict) else None
            return str(mapped) if mapped else f"{provider.upper()}_BASE_URL"
        return None

    @property
    def client(self) -> AsyncOpenAI:
        if self._openai_client is None:
            key_env_name = self._provider_env_name("openai", "api_key") or "OPENAI_API_KEY"
            base_url_env_name = self._provider_env_name("openai", "base_url") or "OPENAI_BASE_URL"
            self._openai_client = AsyncOpenAI(
                api_key=self._api_key or os.getenv(key_env_name),
                base_url=self._base_url or os.getenv(base_url_env_name),
            )
        return self._openai_client

    def _build_call_params(
        self,
        model: str,
        config: Optional[ModelConfig],
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        model_info = self.model_registry.get_model(model)
        provider = self._resolve_provider(model)
        if config:
            params.update(
                {
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                    or (model_info.max_tokens if model_info else None),
                    "top_p": config.top_p,
                    "frequency_penalty": config.frequency_penalty,
                    "presence_penalty": config.presence_penalty,
                    "stop": config.stop,
                    "stream": config.stream,
                    "timeout": config.timeout,
                }
            )
            if config.custom_headers:
                params["extra_headers"] = config.custom_headers
            if config.extra_params:
                params.update(config.extra_params)
            if config.api_key:
                os.environ[f"{provider.upper()}_API_KEY"] = config.api_key
            if config.base_url:
                params["api_base"] = config.base_url
        params.update(kwargs)
        return {k: v for k, v in params.items() if v is not None}

    @staticmethod
    def _format_response(response: Any) -> Dict[str, Any]:
        if hasattr(response, "model_dump"):
            return response.model_dump()
        if hasattr(response, "dict"):
            return response.dict()
        if isinstance(response, dict):
            return response
        return {
            "choices": getattr(response, "choices", []),
            "usage": getattr(response, "usage", {}),
            "model": getattr(response, "model", ""),
            "id": getattr(response, "id", ""),
        }

    @staticmethod
    def _format_chunk(chunk: Any) -> Dict[str, Any]:
        if hasattr(chunk, "model_dump"):
            return chunk.model_dump()
        if hasattr(chunk, "dict"):
            return chunk.dict()
        if isinstance(chunk, dict):
            return chunk
        return {
            "choices": getattr(chunk, "choices", []),
            "model": getattr(chunk, "model", ""),
            "id": getattr(chunk, "id", ""),
        }

    @staticmethod
    def _parse_json_text(raw: str) -> dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM response is not valid JSON: {exc}") from exc

    @staticmethod
    def _extract_assistant_text(response: Dict[str, Any]) -> str:
        choices = response.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "".join(text_parts)
        return ""

    def _build_openai_chat_kwargs(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int],
        reasoning_effort: Optional[str],
        json_mode: bool,
        client_type: str,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        is_gpt5_family = client_type == "gpt5_sdk" or model.startswith("gpt-5")
        if resolved_max_tokens is not None:
            # GPT-5 chat completion uses max_completion_tokens.
            kwargs["max_completion_tokens" if is_gpt5_family else "max_tokens"] = resolved_max_tokens

        resolved_reasoning_effort = (
            reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        )
        if is_gpt5_family and resolved_reasoning_effort:
            kwargs["reasoning_effort"] = resolved_reasoning_effort
        return kwargs

    def call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        self._ensure_litellm()
        resolved_model = model or self.default_model
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(resolved_model, config, **kwargs)
        response = completion(model=resolved_model, messages=formatted_messages, **call_params)
        return self._format_response(response)

    async def acall(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        self._ensure_litellm()
        resolved_model = model or self.default_model
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(resolved_model, config, **kwargs)
        response = await acompletion(
            model=resolved_model, messages=formatted_messages, **call_params
        )
        return self._format_response(response)

    def stream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Iterator[Dict[str, Any]]:
        self._ensure_litellm()
        resolved_model = model or self.default_model
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(
            resolved_model, config, stream=True, **kwargs
        )
        for chunk in stream(
            model=resolved_model, messages=formatted_messages, **call_params
        ):
            yield self._format_chunk(chunk)

    async def astream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        self._ensure_litellm()
        resolved_model = model or self.default_model
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(
            resolved_model, config, stream=True, **kwargs
        )
        async for chunk in astream(
            model=resolved_model, messages=formatted_messages, **call_params
        ):
            yield self._format_chunk(chunk)

    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> dict[str, Any]:
        resolved_model, _provider, client_type = self._resolve_model_and_client(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if client_type in {"openai_sdk", "gpt5_sdk"}:
            request_kwargs = self._build_openai_chat_kwargs(
                model=resolved_model,
                messages=messages,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                json_mode=True,
                client_type=client_type,
            )
            response = await self.client.chat.completions.create(**request_kwargs)
            raw = response.choices[0].message.content or "{}"
            return self._parse_json_text(raw)

        # Provider routes configured to LiteLLM.
        self._ensure_litellm()
        litellm_kwargs: Dict[str, Any] = {}
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            litellm_kwargs["max_tokens"] = resolved_max_tokens
        if reasoning_effort is not None:
            litellm_kwargs["reasoning_effort"] = reasoning_effort
        elif self.reasoning_effort:
            litellm_kwargs["reasoning_effort"] = self.reasoning_effort

        try:
            response = await acompletion(
                model=resolved_model,
                messages=messages,
                response_format={"type": "json_object"},
                **litellm_kwargs,
            )
        except Exception:
            # Some providers don't support response_format; retry without it.
            response = await acompletion(
                model=resolved_model,
                messages=messages,
                **litellm_kwargs,
            )

        raw = self._extract_assistant_text(self._format_response(response)) or "{}"
        return self._parse_json_text(raw)

    async def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        resolved_model, _provider, client_type = self._resolve_model_and_client(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if client_type in {"openai_sdk", "gpt5_sdk"}:
            request_kwargs = self._build_openai_chat_kwargs(
                model=resolved_model,
                messages=messages,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                json_mode=False,
                client_type=client_type,
            )
            response = await self.client.chat.completions.create(**request_kwargs)
            return response.choices[0].message.content or ""

        self._ensure_litellm()
        litellm_kwargs: Dict[str, Any] = {}
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            litellm_kwargs["max_tokens"] = resolved_max_tokens
        if reasoning_effort is not None:
            litellm_kwargs["reasoning_effort"] = reasoning_effort
        elif self.reasoning_effort:
            litellm_kwargs["reasoning_effort"] = self.reasoning_effort

        response = await acompletion(
            model=resolved_model,
            messages=messages,
            **litellm_kwargs,
        )
        return self._extract_assistant_text(self._format_response(response))
