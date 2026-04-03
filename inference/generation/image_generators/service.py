"""Reusable image backend services for agents."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from typing import Any

import httpx

from ..fal_helpers import fal_subscribe, http_download_bytes, require_fal_model_var

logger = logging.getLogger(__name__)

_DEFAULT_IMAGE_MODEL = "google/gemini-2.5-flash-image"
_DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class ImageService:
    """Image generation + editing service backed by OpenRouter."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_IMAGE_MODEL,
        base_url: str = _DEFAULT_OPENROUTER_BASE_URL,
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

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def generate_image(self, prompt: str) -> bytes:
        logger.info("[Layer1] Generating image: %.100s...", prompt)
        messages = [{"role": "user", "content": prompt}]
        return await self._call_and_extract_image(messages, prompt)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str,
    ) -> bytes:
        refs = [reference_images] if isinstance(reference_images, bytes) else list(reference_images)
        logger.info("[Layer2/3] Editing image (refs=%d): %.100s...", len(refs), prompt)

        content_parts: list[dict[str, Any]] = []
        for ref_bytes in refs:
            b64 = base64.b64encode(ref_bytes).decode()
            content_parts.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        content_parts.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content_parts}]
        return await self._call_and_extract_image(messages, prompt)

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


_MOCK_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MockImageService(ImageService):
    """Mock image service that returns a tiny placeholder PNG."""

    async def generate_image(self, prompt: str) -> bytes:
        logger.info("[MockImageService] Placeholder for: %.80s...", prompt)
        return _MOCK_PNG

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str,
    ) -> bytes:
        logger.info("[MockImageService] Placeholder edit for: %.80s...", prompt)
        return _MOCK_PNG


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

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def generate_image(self, prompt: str) -> bytes:
        logger.info("[fal.ai] Generating image with model=%s", self.model)
        result = await self._submit({"prompt": prompt})
        image_url = self._extract_image_url(result)
        return await self._download_binary(image_url)

    async def edit_image(
        self,
        reference_images: bytes | list[bytes],
        prompt: str,
    ) -> bytes:
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
            result = await self._submit_model(edit_model, {"prompt": prompt, "image_urls": image_urls})
        else:
            image_url = f"data:image/png;base64,{base64.b64encode(refs[0]).decode('utf-8')}"
            result = await self._submit_model(self.model, {"prompt": prompt, "image_url": image_url})
        out_url = self._extract_image_url(result)
        return await self._download_binary(out_url)

    @staticmethod
    def _is_nano_banana2_base_model(model: str) -> bool:
        return model.rstrip("/") == "fal-ai/nano-banana-2"

    async def _submit(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return await self._submit_model(self.model, arguments)

    async def _submit_model(self, model_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return await fal_subscribe(self._api_key, model_id, arguments)

    async def _download_binary(self, url: str) -> bytes:
        return await http_download_bytes(self.http, url)

    @staticmethod
    def _extract_image_url(result: dict[str, Any]) -> str:
        images = result.get("images")
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                url = first.get("url")
                if isinstance(url, str) and url:
                    return url

        image_obj = result.get("image")
        if isinstance(image_obj, dict):
            url = image_obj.get("url")
            if isinstance(url, str) and url:
                return url

        direct_url = result.get("image_url")
        if isinstance(direct_url, str) and direct_url:
            return direct_url

        raise RuntimeError(f"No image URL found in fal.ai response keys={list(result.keys())}")
