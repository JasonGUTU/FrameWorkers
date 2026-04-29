"""Default LLM client implementation."""

from __future__ import annotations

import base64
import json
import logging
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from ..base.base_client import BaseLLMClient
from ..json_parse_diag import describe_json_decode_error

logger = logging.getLogger(__name__)


def _build_multimodal_user_content(
    user_prompt: str,
    media_attachments: List[Dict[str, str]],
) -> list[dict]:
    """Build an OpenAI-compatible multimodal content array.

    Converts ``media_attachments`` (list of ``{type, path}``) into the
    appropriate OpenAI-compat content parts alongside the text prompt.

    ``type`` values:

    - ``"image"``: sent as ``{"type": "image_url", "image_url": {"url":
      "data:image/*;base64,..."}}``. Gemini OpenAI-compat endpoint decodes
      the inline image natively.
    - ``"audio"``: sent as ``{"type": "input_audio", "input_audio": {"data":
      b64, "format": "wav|mp3|..."}}``. This is the standard OpenAI Realtime
      audio input format, also supported by Gemini's OpenAI-compat bridge.
    - ``"video"``: sent as ``{"type": "image_url", "image_url": {"url":
      "data:video/*;base64,..."}}``. This is **Gemini's documented OpenAI-
      compat extension** — Google's OpenAI-compat bridge recognizes video/*
      MIME types in the ``image_url`` data URL and routes them to Gemini's
      native inline-video path. The OpenAI spec itself does not define a
      video content part; this shape only works against Gemini (direct or
      via Cloudflare AI Gateway's /compat endpoint).
      NOTE: Gemini caps inline multimedia at ~20 MB per request. Larger
      videos must use the File API (not yet wired here).

    Caller contract: every ``{path}`` MUST point to an existing file whose
    MIME matches its declared ``type``. A missing file or a type/MIME
    mismatch raises — this function does NOT silently skip media, because
    a silent skip would let a downstream "video analysis" call succeed
    while actually sending only the text prompt (a historical footgun).
    """
    parts: list[dict] = []

    # Add media first so LLM "sees/hears" before reading the prompt
    for att in media_attachments:
        media_type = att.get("type", "")
        file_path = att.get("path", "")

        if not file_path:
            raise ValueError(
                f"media attachment of type={media_type!r} has no path"
            )
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"media attachment path does not exist: {file_path!r} "
                f"(declared type={media_type!r})"
            )

        mime = mimetypes.guess_type(file_path)[0] or ""

        if media_type == "image":
            if mime and not mime.startswith("image/"):
                raise ValueError(
                    f"media type=image but file MIME is {mime!r} (path={file_path!r})"
                )
            mime = mime or "image/png"
            with open(file_path, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })

        elif media_type == "audio":
            if mime and not mime.startswith("audio/"):
                raise ValueError(
                    f"media type=audio but file MIME is {mime!r} (path={file_path!r})"
                )
            mime = mime or "audio/wav"
            # Normalize x-wav → wav, mpeg → mp3 for API compatibility
            audio_fmt = mime.split("/")[-1]
            if audio_fmt in ("x-wav", "x-wave"):
                audio_fmt = "wav"
            elif audio_fmt == "mpeg":
                audio_fmt = "mp3"
            with open(file_path, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            parts.append({
                "type": "input_audio",
                "input_audio": {"data": b64, "format": audio_fmt},
            })

        elif media_type == "video":
            if mime and not mime.startswith("video/"):
                raise ValueError(
                    f"media type=video but file MIME is {mime!r} (path={file_path!r}) — "
                    f"VideoAnalysisAgent requires a real video/* file, not an image or audio."
                )
            mime = mime or "video/mp4"
            size = os.path.getsize(file_path)
            if size > 20 * 1024 * 1024:
                raise ValueError(
                    f"video file {file_path!r} is {size} bytes > 20 MB — exceeds "
                    f"Gemini's inline multimedia cap. Use a shorter clip or switch "
                    f"to Gemini's File API (not yet wired)."
                )
            with open(file_path, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            # Gemini-documented OpenAI-compat extension: data URL with video/*
            # MIME inside image_url is routed to Gemini's native inline-video input.
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })

        else:
            raise ValueError(
                f"unsupported media attachment type: {media_type!r} "
                f"(supported: image / audio / video)"
            )

    # Add text prompt last
    parts.append({"type": "text", "text": user_prompt})

    return parts

try:
    # NOTE: LiteLLM's public symbols have changed across versions.
    # Import the module only; call `litellm.*` at runtime to avoid hard failures
    # when optional helpers are renamed/removed.
    import litellm  # type: ignore  # noqa: F401

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


def _parse_data_url(url: str) -> tuple[bytes, str]:
    """``data:<mime>;base64,<payload>`` → ``(bytes, mime)``."""
    if not url.startswith("data:"):
        raise ValueError(f"expected data: URL, got {url[:40]!r}")
    header, _, payload = url[5:].partition(",")
    if ";base64" not in header:
        raise ValueError(f"expected base64 data: URL, got header={header!r}")
    mime = header.split(";", 1)[0]
    return base64.b64decode(payload), mime


def _openai_messages_to_genai(messages: List[Dict[str, Any]]):
    """Convert OpenAI-format messages → ``(system_instruction, contents)``
    for ``google.genai`` ``generate_content``.

    Last system message wins (matches OpenAI semantics where there is
    typically one system message). User parts (text + multimodal) are
    flattened into a single ``Content(role="user", parts=[...])``.
    """
    from google.genai import types

    system_instruction: Optional[str] = None
    user_parts: list = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "system":
            if isinstance(content, str):
                system_instruction = content
            elif isinstance(content, list):
                texts = [
                    p.get("text", "")
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                ]
                system_instruction = "".join(texts)
            continue

        if role == "user":
            if isinstance(content, str):
                user_parts.append(types.Part.from_text(text=content))
            elif isinstance(content, list):
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    ptype = part.get("type")
                    if ptype == "text":
                        user_parts.append(
                            types.Part.from_text(text=part.get("text", ""))
                        )
                    elif ptype == "image_url":
                        url = (part.get("image_url") or {}).get("url", "")
                        data, mime = _parse_data_url(url)
                        user_parts.append(
                            types.Part.from_bytes(data=data, mime_type=mime)
                        )
                    elif ptype == "input_audio":
                        audio = part.get("input_audio") or {}
                        data = base64.b64decode(audio.get("data", ""))
                        fmt = audio.get("format", "wav")
                        user_parts.append(
                            types.Part.from_bytes(data=data, mime_type=f"audio/{fmt}")
                        )
                    else:
                        raise ValueError(
                            f"google_genai: unsupported content part type: {ptype!r}"
                        )
            else:
                raise ValueError(
                    f"google_genai: unsupported user content type: {type(content).__name__}"
                )
            continue

        if role == "assistant":
            # Multi-turn assistant priors aren't used in this codebase;
            # if a caller starts using them, route as role="model".
            if isinstance(content, str) and content:
                user_parts.append(types.Part.from_text(text=content))
            continue

        raise ValueError(f"google_genai: unsupported message role: {role!r}")

    contents = (
        [types.Content(role="user", parts=user_parts)] if user_parts else []
    )
    return system_instruction, contents


def _genai_response_to_openai_dict(response: Any, model: str) -> Dict[str, Any]:
    """Wrap a ``google.genai`` response in the OpenAI ``chat.completions``
    shape so downstream ``_format_response`` / ``_extract_assistant_text``
    paths keep working unchanged."""
    text = getattr(response, "text", "") or ""
    usage_meta = getattr(response, "usage_metadata", None)
    usage: Dict[str, Any] = {}
    if usage_meta is not None:
        usage = {
            "prompt_tokens": getattr(usage_meta, "prompt_token_count", 0) or 0,
            "completion_tokens": getattr(usage_meta, "candidates_token_count", 0)
            or 0,
            "total_tokens": getattr(usage_meta, "total_token_count", 0) or 0,
        }
    return {
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": usage,
        "model": model,
        "id": "",
    }


class LLMClient(BaseLLMClient):
    """Unified client with provider-based automatic routing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._openai_clients: Dict[str, AsyncOpenAI] = {}
        self._genai_clients: Dict[str, Any] = {}

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

    def _get_genai_client(self, provider: str):
        """Lazy-construct a ``google.genai.Client`` per provider.

        Uses ``provider_key_env`` / ``provider_base_url_env`` from
        ``inference_runtime.yaml`` to resolve which env vars hold the
        API key + custom gateway base URL.
        """
        if provider not in self._genai_clients:
            from google import genai

            key_env_name = self._provider_env_name(provider, "api_key")
            base_url_env_name = self._provider_env_name(provider, "base_url")
            api_key = self._api_key or os.getenv(key_env_name or "GEMINI_API_KEY")
            base_url = self._base_url or os.getenv(base_url_env_name or "")
            client_kwargs: Dict[str, Any] = {}
            if api_key:
                client_kwargs["api_key"] = api_key
            if base_url:
                client_kwargs["http_options"] = {"base_url": base_url}
            self._genai_clients[provider] = genai.Client(**client_kwargs)
        return self._genai_clients[provider]

    def _build_genai_config(
        self,
        *,
        system_instruction: Optional[str],
        max_tokens: Optional[int],
        json_mode: bool,
    ):
        from google.genai import types

        config_kwargs: Dict[str, Any] = {}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"
        resolved_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        if resolved_max_tokens is not None:
            config_kwargs["max_output_tokens"] = resolved_max_tokens
        return types.GenerateContentConfig(**config_kwargs)

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
    def _parse_json_object_strict(raw: str) -> dict[str, Any]:
        """
        Parse **chat_json** responses: one JSON object only.
        Call sites must use provider JSON mode (``response_format`` / OpenAI json_mode).
        """
        text = (raw or "").strip()
        if not text:
            raise ValueError("chat_json: empty model content (expected a JSON object)")
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            # Local repair pass — fixes the common LLM-JSON drift modes
            # Gemini-class models produce on long structured outputs:
            # trailing commas, unquoted keys, unescaped inner quotes in
            # string values, and CJK confusable substitutions for ASCII
            # delimiters. No LLM cost; runs in milliseconds.
            try:
                from json_repair import loads as _repair_loads
                repaired = _repair_loads(text)
                if isinstance(repaired, dict):
                    return repaired
            except Exception:
                # Repair raised on hopeless input — fall through to the
                # strict-error path below so the caller sees the original
                # JSONDecodeError with diagnostics.
                pass
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

    async def acall(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Async raw chat completion that honors provider routing.

        Mirrors ``chat_json``'s three-branch dispatch:
          * ``openai_sdk`` / ``gpt5_sdk``: call
            ``AsyncOpenAI.chat.completions.create`` directly so multimodal
            messages and ``response_format`` flow through the OpenAI SDK.
          * ``google_genai``: call ``google.genai`` async path (cf_aig
            provider via the CF AI Gateway native-Gemini Worker).
          * Anything else: fall back to litellm.
        """
        resolved_model, provider, client_type = self._resolve_model_and_client(model)

        if client_type in {"openai_sdk", "gpt5_sdk"}:
            openai_client = self._get_openai_client(provider)
            # Translate optional kwargs into OpenAI-SDK-shaped request kwargs.
            # ``_build_openai_chat_kwargs`` already handles the gpt-5
            # max_completion_tokens vs max_tokens split and reasoning_effort.
            # Anything else (response_format, tools, etc.) flows through via
            # the kwargs catch-all below.
            local_kwargs = dict(kwargs)
            max_tokens_resolved: Optional[int] = local_kwargs.pop(
                "max_tokens", None
            )
            reasoning_effort_resolved: Optional[str] = local_kwargs.pop(
                "reasoning_effort", None
            )
            request_kwargs = self._build_openai_chat_kwargs(
                model=resolved_model,
                messages=messages,
                max_tokens=max_tokens_resolved,
                reasoning_effort=reasoning_effort_resolved,
                # ``acall`` does NOT force JSON mode — callers (e.g.
                # IntakeImageAgent) may pass ``response_format`` themselves
                # via the kwargs catch-all.
                json_mode=False,
                client_type=client_type,
            )
            request_kwargs.update(local_kwargs)
            response = await openai_client.chat.completions.create(**request_kwargs)
            return self._format_response(response)

        if client_type == "google_genai":
            genai_client = self._get_genai_client(provider)
            system_instruction, contents = _openai_messages_to_genai(messages)
            response_format = kwargs.get("response_format")
            json_mode = (
                isinstance(response_format, dict)
                and response_format.get("type") == "json_object"
            )
            config = self._build_genai_config(
                system_instruction=system_instruction,
                max_tokens=kwargs.get("max_tokens"),
                json_mode=json_mode,
            )
            response = await genai_client.aio.models.generate_content(
                model=resolved_model,
                contents=contents,
                config=config,
            )
            return _genai_response_to_openai_dict(response, resolved_model)

        # Non-OpenAI-SDK providers — fall back to litellm.
        self._ensure_litellm()
        response = await litellm.acompletion(
            model=resolved_model,
            messages=messages,
            **{k: v for k, v in kwargs.items() if v is not None},
        )
        return self._format_response(response)

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
        resolved_model, provider, client_type = self._resolve_model_and_client(model)

        if media_attachments:
            user_content = _build_multimodal_user_content(user_prompt, media_attachments)
        else:
            user_content = user_prompt

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # One full LLM invocation returning raw string. The transient
        # 3-try retry for empty content is internal here so the outer
        # parse-retry doesn't multiply by 3.
        async def _invoke_once() -> str:
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
                # Transient provider hiccups (rate-limit backoff, gateway
                # flap, content filter) sometimes cause the model to
                # return an empty ``message.content`` or no ``choices``
                # at all. Retry up to 2 extra times — the second call
                # usually succeeds because the upstream backend has
                # cleared whatever transient issue caused the first miss.
                last_err: str = ""
                for _attempt in range(3):
                    response = await openai_client.chat.completions.create(**request_kwargs)
                    choices = getattr(response, "choices", None) or []
                    if not choices:
                        last_err = "model returned empty choices"
                        continue
                    msg = getattr(choices[0], "message", None)
                    if msg is None:
                        last_err = "model returned empty message"
                        continue
                    raw = (getattr(msg, "content", None) or "").strip()
                    if raw:
                        return raw
                    last_err = "model returned empty content"
                raise ValueError(
                    f"chat_json: {last_err} (after 3 attempts)"
                )

            if client_type == "google_genai":
                genai_client = self._get_genai_client(provider)
                system_instruction, contents = _openai_messages_to_genai(messages)
                config = self._build_genai_config(
                    system_instruction=system_instruction,
                    max_tokens=max_tokens,
                    json_mode=True,
                )
                last_err = ""
                for _attempt in range(3):
                    response = await genai_client.aio.models.generate_content(
                        model=resolved_model,
                        contents=contents,
                        config=config,
                    )
                    raw = (getattr(response, "text", "") or "").strip()
                    if raw:
                        return raw
                    last_err = "model returned empty content"
                raise ValueError(f"chat_json: {last_err} (after 3 attempts)")

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
            return self._extract_assistant_text(self._format_response(response)) or ""

        # Parse-retry loop: ``_parse_json_object_strict`` already tries
        # ``json-repair`` locally for trailing commas / unescaped quotes
        # / CJK confusable substitutions. If that still fails, retry the
        # LLM call once — a fresh sampling path usually clears the
        # drift (different token choices avoid the same mistake).
        for _parse_attempt in range(2):
            raw = await _invoke_once()
            try:
                return self._parse_json_object_strict(raw)
            except ValueError:
                if _parse_attempt == 0:
                    logger.warning(
                        "chat_json: parse failed after json-repair fallback; retrying LLM call once"
                    )
                    continue
                raise
        # Unreachable: either returned above or re-raised on 2nd attempt.
        raise RuntimeError("chat_json: parse-retry loop exited without result")

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
        resolved_model, provider, client_type = self._resolve_model_and_client(model)

        if media_attachments:
            user_content = _build_multimodal_user_content(user_prompt, media_attachments)
        else:
            user_content = user_prompt

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
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

        if client_type == "google_genai":
            genai_client = self._get_genai_client(provider)
            system_instruction, contents = _openai_messages_to_genai(messages)
            config = self._build_genai_config(
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                json_mode=False,
            )
            response = await genai_client.aio.models.generate_content(
                model=resolved_model,
                contents=contents,
                config=config,
            )
            return getattr(response, "text", "") or ""

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
