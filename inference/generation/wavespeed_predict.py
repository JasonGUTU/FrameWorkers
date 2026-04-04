"""Async WaveSpeed.ai prediction API (text-to-video / image-to-video).

Used by ``WavespeedVideoService``. Logic mirrors UniVA ``utils/wavespeed_api`` but
uses ``httpx`` and async polling so it fits the inference stack without importing
the ``univa`` subtree (inference must not depend on other top-level packages).
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

WAVESPEED_API_BASE = "https://api.wavespeed.ai/api/v3"


async def wavespeed_download_video(client: httpx.AsyncClient, url: str) -> bytes:
    resp = await client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


async def wavespeed_poll_until_done(
    client: httpx.AsyncClient,
    api_key: str,
    request_id: str,
    *,
    poll_interval_sec: float = 2.0,
    timeout_sec: float = 300.0,
) -> str:
    """Poll prediction status; return first output URL when completed."""
    headers = {"Authorization": f"Bearer {api_key}"}
    result_url = f"{WAVESPEED_API_BASE}/predictions/{request_id}/result"
    deadline = time.monotonic() + timeout_sec

    while time.monotonic() < deadline:
        resp = await client.get(result_url, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        data = body.get("data") or {}
        status = data.get("status")
        if status == "completed":
            outputs = data.get("outputs") or []
            if not outputs or not isinstance(outputs[0], str):
                raise RuntimeError(f"WaveSpeed completed but no output URL: {data!r}")
            return outputs[0]
        if status == "failed":
            err = data.get("error", "unknown")
            raise RuntimeError(f"WaveSpeed prediction failed: {err}")
        await asyncio.sleep(poll_interval_sec)

    raise TimeoutError(
        f"WaveSpeed prediction {request_id!r} did not complete within {timeout_sec}s"
    )


async def wavespeed_submit_text_to_video(
    client: httpx.AsyncClient,
    api_key: str,
    *,
    provider: str,
    model: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    duration: int = 5,
    seed: int = -1,
) -> str:
    url = f"{WAVESPEED_API_BASE}/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload: dict[str, Any] = {
        "aspect_ratio": aspect_ratio,
        "duration": int(duration),
        "prompt": prompt,
        "seed": seed,
    }
    resp = await client.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(
            f"WaveSpeed T2V submit failed HTTP {resp.status_code}: {resp.text[:500]}"
        )
    data = resp.json().get("data") or {}
    request_id = data.get("id")
    if not request_id:
        raise RuntimeError(f"WaveSpeed T2V missing request id: {resp.text[:500]}")
    logger.info("WaveSpeed T2V submitted request_id=%s", request_id)
    return str(request_id)


async def wavespeed_submit_image_to_video(
    client: httpx.AsyncClient,
    api_key: str,
    *,
    provider: str,
    model: str,
    prompt: str,
    image_png_or_jpeg: bytes,
    duration: int = 5,
    seed: int | None = None,
) -> str:
    url = f"{WAVESPEED_API_BASE}/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    mime = "png" if image_png_or_jpeg[:8] == b"\x89PNG\r\n\x1a\n" else "jpeg"
    b64 = base64.b64encode(image_png_or_jpeg).decode("ascii")
    if seed is None:
        seed = int(time.time())
    payload: dict[str, Any] = {
        "duration": int(duration),
        "image": f"data:image/{mime};base64,{b64}",
        "prompt": prompt,
        "seed": seed,
    }
    resp = await client.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(
            f"WaveSpeed I2V submit failed HTTP {resp.status_code}: {resp.text[:500]}"
        )
    data = resp.json().get("data") or {}
    request_id = data.get("id")
    if not request_id:
        raise RuntimeError(f"WaveSpeed I2V missing request id: {resp.text[:500]}")
    logger.info("WaveSpeed I2V submitted request_id=%s", request_id)
    return str(request_id)
