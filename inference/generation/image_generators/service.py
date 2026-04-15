"""Reusable image backend services for agents."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from typing import Any

import httpx

from .._mock_data import MOCK_PNG
from ..fal_helpers import (
    LazyHttpxClientMixin,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
    require_fal_model_var,
)
from .types import ImageResult, ImageSemanticContext

logger = logging.getLogger(__name__)

_DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# Prompt templating — owned entirely by the inference layer.
#
# These strings are the **only** fal/Gemini-flavored image prompt templating
# in the codebase. Agent-layer materializers never see them; they just pack
# a language-neutral ``ImageSemanticContext`` and let the service render it.
# ---------------------------------------------------------------------------

# Prepended to image-edit prompts. The reference image already encodes the
# global visual style, so the instruction tells the model to preserve
# subject identity while applying the text-described changes.
_EDIT_INSTRUCTION_PREFIX = (
    "Edit the attached reference to match the text below; keep subject identity "
    "recognizable; apply lighting, framing, pose, and environment as described.\n\n"
)


class ImageService(LazyHttpxClientMixin):
    """Image generation + editing service backed by OpenRouter.

    Callers pass either:

    * ``semantic_context``: an ``ImageSemanticContext`` describing the
      image in model-neutral language. The service is responsible for
      turning it into a backend-specific text prompt.
    * ``prompt``: a pre-composed text prompt string (legacy / direct
      path, used by callers that build prompts themselves — e.g. the
      UniVA keyframe materializer, which inherits its prompts from an
      upstream LLM step).

    When both are provided, ``semantic_context`` takes precedence.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = _DEFAULT_OPENROUTER_BASE_URL,
        timeout: float = 120.0,
        retry_base_delay: float = 2.0,
        retry_max_delay: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("INFERENCE_IMAGE_MODEL", "")
        if not self.model:
            raise RuntimeError(
                "No image model configured. Set INFERENCE_IMAGE_MODEL in .env "
                "(e.g. google/gemini-2.5-flash-image)"
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self._http: httpx.AsyncClient | None = None

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[Layer1] Generating image: %.100s...", composed)
        messages = [{"role": "user", "content": composed}]
        image_bytes = await self._call_and_extract_image(messages, composed)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        refs = [reference_images] if isinstance(reference_images, bytes) else list(reference_images)
        logger.info("[Layer2/3] Editing image (refs=%d): %.100s...", len(refs), composed)

        content_parts: list[dict[str, Any]] = []
        for ref_bytes in refs:
            b64 = base64.b64encode(ref_bytes).decode()
            content_parts.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        content_parts.append({"type": "text", "text": composed})
        messages = [{"role": "user", "content": content_parts}]
        image_bytes = await self._call_and_extract_image(messages, composed)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    # ------------------------------------------------------------------
    # Semantic context → text prompt
    #
    # The two methods below own every fal/Gemini-flavored string that
    # used to live in ``agents/keyframe/materializer.py``. They are the
    # single place in the codebase that knows how to render a
    # ``ImageSemanticContext`` into a wire-format prompt. Subclasses
    # (Fal, Mock) inherit this behavior unchanged.
    # ------------------------------------------------------------------

    @staticmethod
    def _compose_generate_prompt(ctx: ImageSemanticContext) -> str:
        """Render a semantic context into a text-to-image prompt.

        Includes the full style suffix — this path has no reference
        image to carry global style, so every cue has to be spelled out
        in text.
        """
        parts: list[str] = []
        if ctx.prompt_summary:
            parts.append(ctx.prompt_summary)
        tail = ImageService._compose_style_suffix(
            style_notes=ctx.style_notes,
            must_avoid=ctx.must_avoid,
            include_visual_style=True,
        )
        if tail:
            parts.append(tail)
        return "".join(parts)

    @staticmethod
    def _compose_edit_prompt(ctx: ImageSemanticContext) -> str:
        """Render a semantic context into an image-edit prompt.

        Prepends the edit instruction that preserves subject identity,
        and **omits** the ``Visual style:`` block because the reference
        image already encodes the global look. ``Do NOT use:`` still
        applies — style refs don't express avoidance.
        """
        parts: list[str] = [_EDIT_INSTRUCTION_PREFIX]
        if ctx.prompt_summary:
            parts.append(ctx.prompt_summary)
        tail = ImageService._compose_style_suffix(
            style_notes=ctx.style_notes,
            must_avoid=ctx.must_avoid,
            include_visual_style=False,
        )
        if tail:
            parts.append(tail)
        return "".join(parts)

    @staticmethod
    def _compose_style_suffix(
        *,
        style_notes: list[str],
        must_avoid: list[str],
        include_visual_style: bool,
    ) -> str:
        """Build the trailing style chunk shared by generate + edit paths.

        Format: ``"\\nVisual style: a; b. Do NOT use: x; y."`` — the
        leading newline separates the suffix from the body summary so
        the model sees a clear section break. Empty input → empty
        suffix (no stray whitespace).
        """
        chunks: list[str] = []
        if include_visual_style and style_notes:
            chunks.append("Visual style: " + "; ".join(style_notes) + ".")
        if must_avoid:
            chunks.append("Do NOT use: " + "; ".join(must_avoid) + ".")
        if not chunks:
            return ""
        return "\n" + " ".join(chunks)

    async def _call_and_extract_image(
        self,
        messages: list[dict[str, Any]],
        prompt_for_log: str,
    ) -> bytes:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages}

        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self.http.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                images = msg.get("images", [])
                if not images:
                    text_content = msg.get("content", "")
                    raise RuntimeError(
                        f"No image returned from {self.model}. Text response: {text_content[:300]}"
                    )
                img_url = images[0].get("image_url", {}).get("url", "")
                if not img_url.startswith("data:image"):
                    raise RuntimeError(f"Unexpected image format from {self.model}: {img_url[:100]}")
                _, b64_data = img_url.split(",", 1)
                image_bytes = base64.b64decode(b64_data)
                logger.info(
                    "Image generated (%d bytes, attempt %d) for: %.80s...",
                    len(image_bytes),
                    attempt,
                    prompt_for_log,
                )
                return image_bytes
            except (
                httpx.HTTPStatusError,
                httpx.TimeoutException,
                httpx.ConnectError,
                RuntimeError,
            ) as exc:
                delay = min(self.retry_base_delay * (2 ** (attempt - 1)), self.retry_max_delay)
                logger.warning(
                    "Image generation attempt %d failed: %s — retrying in %.1fs",
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)


class MockImageService(ImageService):
    """Mock image service that returns a tiny placeholder PNG."""

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[MockImageService] Placeholder for: %.80s...", composed)
        return ImageResult(bytes=MOCK_PNG, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[MockImageService] Placeholder edit for: %.80s...", composed)
        return ImageResult(bytes=MOCK_PNG, resolved_prompt=composed)


class FalImageService(ImageService):
    """Image generation/editing service backed by fal.ai."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.model = require_fal_model_var("FAL_IMAGE_MODEL", explicit=model)
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

    async def generate_image(
        self,
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_generate_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        logger.info("[fal.ai] Generating image with model=%s", self.model)
        result = await fal_subscribe(self._api_key, self.model, {"prompt": composed})
        image_url = extract_fal_media_url(result, media_type="image")
        image_bytes = await http_download_bytes(self.http, image_url)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str = "",
        *,
        semantic_context: ImageSemanticContext | None = None,
    ) -> ImageResult:
        composed = (
            self._compose_edit_prompt(semantic_context)
            if semantic_context is not None
            else prompt
        )
        refs = [reference_images] if isinstance(reference_images, bytes) else list(reference_images)
        if not refs:
            raise ValueError("reference_images cannot be empty for fal edit_image")

        if self._is_nano_banana2_base_model(self.model):
            # fal-ai/nano-banana-2/edit expects image_urls (list), not image_url.
            image_urls = [
                f"data:image/png;base64,{base64.b64encode(r).decode('utf-8')}" for r in refs
            ]
            edit_model = "fal-ai/nano-banana-2/edit"
            logger.info("[fal.ai] Editing image with model=%s", edit_model)
            result = await fal_subscribe(
                self._api_key, edit_model, {"prompt": composed, "image_urls": image_urls}
            )
        else:
            image_url = f"data:image/png;base64,{base64.b64encode(refs[0]).decode('utf-8')}"
            result = await fal_subscribe(
                self._api_key, self.model, {"prompt": composed, "image_url": image_url}
            )
        out_url = extract_fal_media_url(result, media_type="image")
        image_bytes = await http_download_bytes(self.http, out_url)
        return ImageResult(bytes=image_bytes, resolved_prompt=composed)

    @staticmethod
    def _is_nano_banana2_base_model(model: str) -> bool:
        return model.rstrip("/") == "fal-ai/nano-banana-2"
