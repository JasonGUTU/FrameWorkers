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
    """Default client: LiteLLM for completion, OpenAI chat for json/text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._openai_client: Optional[AsyncOpenAI] = None

    def _ensure_litellm(self) -> None:
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is not installed. Please install it with: pip install litellm"
            )

    @property
    def client(self) -> AsyncOpenAI:
        if self._openai_client is None:
            self._openai_client = AsyncOpenAI(
                api_key=self._api_key or os.getenv("OPENAI_API_KEY"),
                base_url=self._base_url or os.getenv("OPENAI_BASE_URL"),
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
                provider = model_info.provider if model_info else "openai"
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
        request_kwargs: Dict[str, Any] = {
            "model": model or self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            request_kwargs["max_tokens"] = resolved_max_tokens
        response = await self.client.chat.completions.create(**request_kwargs)
        raw = response.choices[0].message.content or "{}"
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
        request_kwargs: Dict[str, Any] = {
            "model": model or self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            request_kwargs["max_tokens"] = resolved_max_tokens
        response = await self.client.chat.completions.create(**request_kwargs)
        return response.choices[0].message.content or ""
