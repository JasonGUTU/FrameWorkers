"""LLM client wrapper — unified interface for calling language models.

Supports OpenAI-compatible APIs.  All LLM agents route through this client
so that model, reasoning_effort, retries, and JSON-only enforcement are
centralized.

GPT-5 API notes:
  - Uses ``max_completion_tokens`` (not ``max_tokens``).
  - Uses ``reasoning_effort`` (minimal / low / medium / high) instead of
    ``temperature``.
  - ``response_format: {"type": "json_object"}`` is supported.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """Async wrapper around OpenAI chat completions (GPT-5)."""

    def __init__(
        self,
        model: str = "gpt-5",
        max_tokens: int = 65536,
        reasoning_effort: str = "medium",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self._api_key = api_key
        self._base_url = base_url
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-init the OpenAI client (avoids crash when no API key at import)."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._api_key or os.getenv("OPENAI_API_KEY"),
                base_url=self._base_url or os.getenv("OPENAI_BASE_URL"),
            )
        return self._client

    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> dict[str, Any]:
        """Send a chat request and parse the response as JSON.

        Raises ValueError if the response is not valid JSON.
        """
        response = await self.client.chat.completions.create(
            model=model or self.model,
            max_completion_tokens=max_tokens or self.max_tokens,
            reasoning_effort=reasoning_effort or self.reasoning_effort,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = response.choices[0]
        finish_reason = choice.finish_reason
        raw = choice.message.content or "{}"

        # Log token usage for diagnostics
        usage = response.usage
        if usage:
            details = getattr(usage, "completion_tokens_details", None)
            reasoning_tokens = getattr(details, "reasoning_tokens", 0) if details else 0
            output_tokens = usage.completion_tokens - reasoning_tokens
            logger.info(
                "LLM usage: prompt=%d, completion=%d "
                "(reasoning=%d + output=%d), total=%d | "
                "finish_reason=%s",
                usage.prompt_tokens,
                usage.completion_tokens,
                reasoning_tokens,
                output_tokens,
                usage.total_tokens,
                finish_reason,
            )

        # Detect truncation: if finish_reason is "length", the output was
        # cut short by max_completion_tokens.  For reasoning models this is
        # especially common because reasoning tokens count toward the limit.
        if finish_reason == "length":
            logger.warning(
                "LLM response TRUNCATED (finish_reason=length). "
                "max_completion_tokens=%d may be too low. "
                "Raw tail: …%s",
                max_tokens or self.max_tokens,
                raw[-200:],
            )

        logger.debug("LLM raw response (first 500 chars): %s", raw[:500])
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("LLM returned invalid JSON: %s", raw[:200])
            raise ValueError(f"LLM response is not valid JSON: {exc}") from exc

    async def chat_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        """Send a chat request and return plain text."""
        response = await self.client.chat.completions.create(
            model=model or self.model,
            max_completion_tokens=max_tokens or self.max_tokens,
            reasoning_effort=reasoning_effort or self.reasoning_effort,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
