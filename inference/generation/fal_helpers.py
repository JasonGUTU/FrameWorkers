"""Shared helpers for fal.ai-backed media services (subscribe + HTTP download)."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import httpx

_FAL_ENV_MERGED = False


def ensure_fal_runtime_env_loaded() -> None:
    """Merge FrameWorkers repo-root ``.env`` then ``.env.example`` (**missing** keys only).

    Resolved relative to this file so fal services see the same defaults regardless of
    ``cwd``. Fal image/video model IDs come only from ``FAL_IMAGE_MODEL`` /
    ``FAL_VIDEO_MODEL`` (after merge), not from Python literals in ``Fal*Service``.
    """
    global _FAL_ENV_MERGED
    if _FAL_ENV_MERGED:
        return
    from inference.config.config_loader import ConfigLoader

    # inference/generation/fal_helpers.py -> repo root is parents[2]
    repo_root = Path(__file__).resolve().parents[2]
    for fname in (".env", ".env.example"):
        path = repo_root / fname
        if path.is_file():
            ConfigLoader.load_env_file(str(path), override=False)
    _FAL_ENV_MERGED = True


def require_fal_model_var(env_name: str, *, explicit: str | None) -> str:
    """Resolve a fal model id from ``explicit`` or ``os.environ[env_name]``."""
    ensure_fal_runtime_env_loaded()
    resolved = (explicit or os.getenv(env_name) or "").strip()
    if not resolved:
        raise RuntimeError(
            f"{env_name} is not set. Define it in the project `.env` "
            f"(see `.env.example`) or pass model=... to the service constructor."
        )
    return resolved


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
