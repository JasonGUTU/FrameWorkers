"""Shared helpers for fal.ai-backed media services (subscribe + HTTP download)."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


async def fal_subscribe(api_key: str, model_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run ``fal_client.subscribe`` with ``FAL_KEY`` set for this process."""
    if not api_key:
        raise RuntimeError("FAL_API_KEY is required for fal.ai services")
    try:
        import fal_client
    except ImportError as exc:
        raise RuntimeError("fal-client is required. Install with `pip install fal-client`.") from exc

    previous = os.getenv("FAL_KEY")
    os.environ["FAL_KEY"] = api_key
    try:
        result = await asyncio.to_thread(
            fal_client.subscribe,
            model_id,
            arguments=arguments,
            with_logs=False,
        )
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected fal.ai response type: {type(result).__name__}")
        return result
    finally:
        if previous is None:
            os.environ.pop("FAL_KEY", None)
        else:
            os.environ["FAL_KEY"] = previous


async def http_download_bytes(client: httpx.AsyncClient, url: str) -> bytes:
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.content
