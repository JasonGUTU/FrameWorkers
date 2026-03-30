"""Default LLM client implementation."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from openai import AsyncOpenAI

from ..base.base_client import BaseLLMClient, Message, ModelConfig
from ..json_parse_diag import describe_json_decode_error

try:
    # NOTE: LiteLLM's public symbols have changed across versions.
    # Import the module only; call `litellm.*` at runtime to avoid hard failures
    # when optional helpers are renamed/removed.
    import litellm  # type: ignore  # noqa: F401

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMClient(BaseLLMClient):
    """Unified client with provider-based automatic routing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._openai_clients: Dict[str, AsyncOpenAI] = {}

    def _ensure_litellm(self) -> None:
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is not installed. Please install it with: pip install litellm"
            )

    def _resolve_provider(self, model: Optional[str]) -> str:
        return self.resolve_provider_for_model(model)

    def _canonicalize_model(self, model: Optional[str]) -> str:
        resolved_model = model or self.model or self.default_model or "gpt-3.5-turbo"
        model_info = self.model_registry.get_model(resolved_model)
        if model_info and model_info.model_id:
            return model_info.model_id
        return resolved_model

    def _resolve_model_and_client(self, model: Optional[str]) -> tuple[str, str, str]:
        resolved_model = self._canonicalize_model(model)
        provider = self._resolve_provider(resolved_model)
        client_type = self.resolve_client_for_provider(provider)
        return resolved_model, provider, client_type

    def _provider_env_name(self, provider: str, category: str) -> Optional[str]:
        routing = self.get_runtime_routing()
        if category == "api_key":
            mapped = (
                routing.get("provider_key_env", {}).get(provider)
                if isinstance(routing, dict)
                else None
            )
            return str(mapped) if mapped else f"{provider.upper()}_API_KEY"
        if category == "base_url":
            mapped = (
                routing.get("provider_base_url_env", {}).get(provider)
                if isinstance(routing, dict)
                else None
            )
            return str(mapped) if mapped else f"{provider.upper()}_BASE_URL"
        return None

    def _provider_default_headers(self, provider: str) -> Dict[str, str]:
        """Resolve provider default headers from runtime routing config."""
        routing = self.get_runtime_routing()
        provider_headers = (
            routing.get("provider_default_headers", {})
            if isinstance(routing, dict)
            else {}
        )
        raw_headers = (
            provider_headers.get(provider, {})
            if isinstance(provider_headers, dict)
            else {}
        )
        if not isinstance(raw_headers, dict):
            return {}
        # Keep only string headers for OpenAI default_headers.
        return {str(k): str(v) for k, v in raw_headers.items() if v is not None}

    def _get_openai_client(self, provider: str) -> AsyncOpenAI:
        if provider not in self._openai_clients:
            key_env_name = self._provider_env_name(provider, "api_key")
            base_url_env_name = self._provider_env_name(provider, "base_url")
            default_headers = self._provider_default_headers(provider)
            self._openai_clients[provider] = AsyncOpenAI(
                api_key=self._api_key or os.getenv(key_env_name or "OPENAI_API_KEY"),
                base_url=self._base_url or os.getenv(base_url_env_name or "OPENAI_BASE_URL"),
                default_headers=default_headers or None,
            )
        return self._openai_clients[provider]

    @property
    def client(self) -> AsyncOpenAI:
        """Backward-compatible default OpenAI client accessor."""
        return self._get_openai_client("openai")

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
    def _parse_json_object_strict(raw: str) -> dict[str, Any]:
        """
        Parse **chat_json** responses: one JSON object only, no fence-stripping or substring recovery.
        Call sites must use provider JSON mode (``response_format`` / OpenAI json_mode); failures surface here.
        """
        text = (raw or "").strip()
        if not text:
            raise ValueError("chat_json: empty model content (expected a JSON object)")
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            diag = describe_json_decode_error(text, exc)
            # Optional diagnostics: dump raw model output to disk for post-mortem.
            # This is off by default to avoid leaking prompts/outputs.
            if os.getenv("FW_JSON_DIAG_DUMP", "").strip().lower() in {"1", "true", "yes", "on"}:
                dump_dir = os.getenv("FW_JSON_DIAG_DUMP_DIR", "").strip() or "Runtime/debug/json_parse_failures"
                try:
                    p = Path(dump_dir)
                    if not p.is_absolute():
                        p = Path.cwd() / p
                    p.mkdir(parents=True, exist_ok=True)
                    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                    out_path = p / f"chat_json_invalid_{ts}.txt"
                    out_path.write_text(
                        "=== raw (strip) ===\n"
                        + text
                        + "\n\n=== error ===\n"
                        + f"{exc}\n\n=== diag ===\n"
                        + diag
                        + "\n",
                        encoding="utf-8",
                    )
                except Exception:
                    # Never hide the underlying parse failure.
                    pass
            raise ValueError(
                f"chat_json: model output is not valid JSON: {exc}; {diag}"
            ) from exc
        if not isinstance(obj, dict):
            raise ValueError("chat_json: root JSON value must be an object")
        return obj

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
            kwargs["max_completion_tokens" if is_gpt5_family else "max_tokens"] = (
                resolved_max_tokens
            )

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
        resolved_model = self._canonicalize_model(model or self.default_model)
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(resolved_model, config, **kwargs)
        response = litellm.completion(
            model=resolved_model, messages=formatted_messages, **call_params
        )
        return self._format_response(response)

    async def acall(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        self._ensure_litellm()
        resolved_model = self._canonicalize_model(model or self.default_model)
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(resolved_model, config, **kwargs)
        response = await litellm.acompletion(
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
        resolved_model = self._canonicalize_model(model or self.default_model)
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(
            resolved_model, config, stream=True, **kwargs
        )
        for chunk in litellm.stream(
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
        resolved_model = self._canonicalize_model(model or self.default_model)
        formatted_messages = self._format_messages(messages)
        call_params = self._build_call_params(
            resolved_model, config, stream=True, **kwargs
        )
        async for chunk in litellm.astream(
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
        resolved_model, provider, client_type = self._resolve_model_and_client(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if client_type in {"openai_sdk", "gpt5_sdk"}:
            openai_client = self._get_openai_client(provider)
            request_kwargs = self._build_openai_chat_kwargs(
                model=resolved_model,
                messages=messages,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                json_mode=True,
                client_type=client_type,
            )
            response = await openai_client.chat.completions.create(**request_kwargs)
            raw = response.choices[0].message.content or ""
            return self._parse_json_object_strict(raw)

        # Provider routes configured to LiteLLM — require JSON mode; no silent fallback without it.
        self._ensure_litellm()
        litellm_kwargs: Dict[str, Any] = {}
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            litellm_kwargs["max_tokens"] = resolved_max_tokens
        if reasoning_effort is not None:
            litellm_kwargs["reasoning_effort"] = reasoning_effort
        elif self.reasoning_effort:
            litellm_kwargs["reasoning_effort"] = self.reasoning_effort

        response = await litellm.acompletion(
            model=resolved_model,
            messages=messages,
            response_format={"type": "json_object"},
            **litellm_kwargs,
        )

        raw = self._extract_assistant_text(self._format_response(response)) or ""
        return self._parse_json_object_strict(raw)

    async def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        resolved_model, provider, client_type = self._resolve_model_and_client(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if client_type in {"openai_sdk", "gpt5_sdk"}:
            openai_client = self._get_openai_client(provider)
            request_kwargs = self._build_openai_chat_kwargs(
                model=resolved_model,
                messages=messages,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                json_mode=False,
                client_type=client_type,
            )
            response = await openai_client.chat.completions.create(**request_kwargs)
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

        response = await litellm.acompletion(
            model=resolved_model,
            messages=messages,
            **litellm_kwargs,
        )
        return self._extract_assistant_text(self._format_response(response))
