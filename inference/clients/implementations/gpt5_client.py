"""GPT-5 specific client implementation."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .default_client import LLMClient


class GPT5ChatClient(LLMClient):
    """LLMClient variant that uses GPT-5 specific request fields."""

    DEFAULT_GPT5_MODEL = "gpt-5"

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
            "model": model or self.model or self.DEFAULT_GPT5_MODEL,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            request_kwargs["max_completion_tokens"] = resolved_max_tokens
        resolved_reasoning_effort = (
            reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        )
        if resolved_reasoning_effort:
            request_kwargs["reasoning_effort"] = resolved_reasoning_effort
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
            "model": model or self.model or self.DEFAULT_GPT5_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            request_kwargs["max_completion_tokens"] = resolved_max_tokens
        resolved_reasoning_effort = (
            reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        )
        if resolved_reasoning_effort:
            request_kwargs["reasoning_effort"] = resolved_reasoning_effort
        response = await self.client.chat.completions.create(**request_kwargs)
        return response.choices[0].message.content or ""
