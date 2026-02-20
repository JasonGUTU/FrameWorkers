"""Image generation service — OpenRouter + Gemini 2.5 Flash Image.

Three-layer keyframe generation (all layers use the SAME model & endpoint):
  Layer 1 (Global anchors)  → ``generate_image()``  — text → image
  Layer 2 (Scene anchors)   → ``edit_image()``       — reference image + text → image
  Layer 3 (Shot keyframes)  → ``edit_image()``       — reference image(s) + text → image

Backend: ``google/gemini-2.5-flash-image`` via OpenRouter ``/chat/completions``.
Images are returned in the non-standard ``message.images[]`` field as
``data:image/png;base64,…`` data URIs.

Called by Assistant as a post-processing step **after** KeyFrameAgent's
JSON plan passes the quality gate.  Flow:

    KeyFrameAgent (LLM plan)
        → Evaluator (quality gate)
        → ImageService.generate_image() / edit_image()   ← this module
        → AssetManager.save_binary()
        → update ``image_asset.uri`` in the asset dict

This service is independent of any agent — agents plan, services execute.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "google/gemini-2.5-flash-image"
_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


class ImageService:
    """Image generation + editing service backed by OpenRouter (Gemini).

    - ``generate_image`` — text → image  (Layer 1 global anchors).
    - ``edit_image``     — image(s) + text → image  (Layer 2 scene / Layer 3 shot).

    Both methods call the same ``/chat/completions`` endpoint.  Gemini
    natively supports multimodal input (reference images) and image output,
    so **no fallback** is needed — Layer 2/3 edits work out of the box.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 120.0,
        retry_base_delay: float = 2.0,
        retry_max_delay: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self._http: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # HTTP client management
    # ------------------------------------------------------------------

    @property
    def http(self) -> httpx.AsyncClient:
        """Lazy-init a reusable async HTTP client."""
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def close(self) -> None:
        """Shut down the HTTP client."""
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    # ------------------------------------------------------------------
    # Layer 1: Text → Image
    # ------------------------------------------------------------------

    async def generate_image(self, prompt: str) -> bytes:
        """Generate an image from a text prompt.

        Used for **Layer 1 global anchors** — no reference image.

        Args:
            prompt: Image generation prompt.

        Returns:
            Raw PNG image bytes.
        """
        logger.info("[Layer1] Generating image: %.100s…", prompt)

        messages = [{"role": "user", "content": prompt}]
        return await self._call_and_extract_image(messages, prompt)

    # ------------------------------------------------------------------
    # Layer 2 / 3: Reference Image(s) + Text → Image
    # ------------------------------------------------------------------

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str,
    ) -> bytes:
        """Edit / adapt reference image(s) using text instructions.

        Used for:
          - **Layer 2** (scene anchors): single global anchor → scene-adapted.
          - **Layer 3** (shot keyframes): one or more scene anchors → shot.

        Gemini natively accepts multiple input images as vision content,
        so all references are passed together.

        Args:
            reference_images: One ``bytes`` object or a list of ``bytes``.
            prompt:           Edit instruction.

        Returns:
            Raw PNG image bytes of the edited result.
        """
        if isinstance(reference_images, bytes):
            refs = [reference_images]
        else:
            refs = list(reference_images)

        logger.info(
            "[Layer2/3] Editing image (refs=%d): %.100s…", len(refs), prompt
        )

        # Build multimodal content: image(s) first, then text instruction
        content_parts: list[dict] = []
        for ref_bytes in refs:
            b64 = base64.b64encode(ref_bytes).decode()
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                }
            )
        content_parts.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content_parts}]
        return await self._call_and_extract_image(messages, prompt)

    # ------------------------------------------------------------------
    # Internal: call OpenRouter and extract image from response
    # ------------------------------------------------------------------

    async def _call_and_extract_image(
        self,
        messages: list[dict],
        prompt_for_log: str,
    ) -> bytes:
        """Send a chat completion request and extract the first image.

        Retries **indefinitely** with exponential backoff (capped at
        ``retry_max_delay``) until Gemini returns an image.  Transient
        empty-response failures are common under high concurrency.

        OpenRouter's Gemini image model returns images in a non-standard
        field ``message.images[]`` as ``data:image/png;base64,…`` URIs.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }

        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self.http.post(url, headers=headers, json=payload)
                resp.raise_for_status()

                data = resp.json()

                # Extract image from message.images[]
                msg = data.get("choices", [{}])[0].get("message", {})
                images = msg.get("images", [])

                if not images:
                    text_content = msg.get("content", "")
                    raise RuntimeError(
                        f"No image returned from {self.model}. "
                        f"Text response: {text_content[:300]}"
                    )

                img_url = images[0].get("image_url", {}).get("url", "")
                if not img_url.startswith("data:image"):
                    raise RuntimeError(
                        f"Unexpected image format from {self.model}: "
                        f"{img_url[:100]}"
                    )

                # Parse data URI: data:image/png;base64,<data>
                _, b64_data = img_url.split(",", 1)
                image_bytes = base64.b64decode(b64_data)

                logger.info(
                    "Image generated (%d bytes, attempt %d) for: %.80s…",
                    len(image_bytes),
                    attempt,
                    prompt_for_log,
                )
                return image_bytes

            except (httpx.HTTPStatusError, httpx.TimeoutException,
                    httpx.ConnectError, RuntimeError) as exc:
                delay = min(
                    self.retry_base_delay * (2 ** (attempt - 1)),
                    self.retry_max_delay,
                )
                logger.warning(
                    "Image generation attempt %d failed: %s — "
                    "retrying in %.1fs",
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)


# =====================================================================
#  Mock service — returns a 1x1 transparent PNG placeholder
# =====================================================================

# Minimal valid 1×1 transparent PNG (67 bytes).
_MOCK_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MockImageService(ImageService):
    """Mock backend that returns a tiny placeholder PNG.

    Use with ``--debug`` to skip real Gemini API calls during testing.
    All three layers (global, scene, shot) return the same 1×1 PNG.
    """

    async def generate_image(self, prompt: str) -> bytes:
        logger.info("[MockImageService] Placeholder for: %.80s…", prompt)
        return _MOCK_PNG

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str,
    ) -> bytes:
        logger.info("[MockImageService] Placeholder edit for: %.80s…", prompt)
        return _MOCK_PNG
