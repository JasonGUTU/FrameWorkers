"""Shared helpers for fal.ai-backed media services (subscribe + HTTP download).

Also hosts a small ``LazyHttpxClientMixin`` that media services use to share
the same lazy-init / re-open / close lifecycle for an ``httpx.AsyncClient``.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class LazyHttpxClientMixin:
    """Mixin providing a lazily-created ``httpx.AsyncClient``.

    Hosts must set ``self.timeout: float`` and initialise
    ``self._http: httpx.AsyncClient | None = None`` in ``__init__``.
    """

    timeout: float
    _http: Optional[httpx.AsyncClient]

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def close(self) -> None:
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()

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
    """Run ``fal_client.subscribe`` with ``FAL_KEY`` set for this process.

    Hardened against silent indefinite hangs: passes ``start_timeout`` and
    ``client_timeout`` so a stuck queue / dead worker raises rather than
    blocking forever. Logs queue state transitions (Queued → InProgress →
    Completed) at INFO so prod ops can see what fal is doing.

    Timeouts are configurable via env (queue waits on big video models like
    VACE can legitimately exceed 5 minutes; absolute upper bound prevents
    runaway):
      FW_FAL_START_TIMEOUT  — max seconds to wait for Queued → InProgress (default 900)
      FW_FAL_CLIENT_TIMEOUT — total wall-clock cap (default 1800)
    """
    if not api_key:
        raise RuntimeError("FAL_API_KEY is required for fal.ai services")
    try:
        import fal_client
    except ImportError as exc:
        raise RuntimeError("fal-client is required. Install with `pip install fal-client`.") from exc

    start_timeout = float(os.getenv("FW_FAL_START_TIMEOUT", "900"))
    client_timeout = float(os.getenv("FW_FAL_CLIENT_TIMEOUT", "1800"))

    last_state: dict[str, str] = {"v": ""}

    def _on_queue_update(status: Any) -> None:
        cur = type(status).__name__
        if cur != last_state["v"]:
            logger.info("[fal:%s] queue state -> %s", model_id, cur)
            last_state["v"] = cur

    previous = os.getenv("FAL_KEY")
    os.environ["FAL_KEY"] = api_key
    try:
        result = await asyncio.to_thread(
            fal_client.subscribe,
            model_id,
            arguments=arguments,
            with_logs=False,
            on_queue_update=_on_queue_update,
            start_timeout=start_timeout,
            client_timeout=client_timeout,
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


def extract_fal_media_url(result: dict[str, Any], *, media_type: str) -> str:
    """Extract a media URL from a fal.ai response.

    fal.ai endpoints expose the generated artifact under a few different
    shapes depending on model and modality. Tries them in this order:

    1. ``result["<media>s"]``: list of dicts with ``url`` (plural form
       used by multi-output image/video endpoints)
    2. ``result["<media>"]``: single dict with ``url`` (most video/audio
       endpoints)
    3. ``result["<media>_file"]``: dict with ``url`` (used by some fal
       TTS endpoints — only meaningful for audio, harmless otherwise)
    4. ``result["<media>_url"]`` or ``result["url"]``: bare string URL

    Raises ``RuntimeError`` listing the response keys if nothing matches.
    """
    plural = f"{media_type}s"
    items = result.get(plural)
    if isinstance(items, list) and items:
        first = items[0]
        if isinstance(first, dict):
            url = first.get("url")
            if isinstance(url, str) and url:
                return url

    obj = result.get(media_type)
    if isinstance(obj, dict):
        url = obj.get("url")
        if isinstance(url, str) and url:
            return url

    file_obj = result.get(f"{media_type}_file")
    if isinstance(file_obj, dict):
        url = file_obj.get("url")
        if isinstance(url, str) and url:
            return url

    url_field = result.get(f"{media_type}_url") or result.get("url")
    if isinstance(url_field, dict):
        url = url_field.get("url")
        if isinstance(url, str) and url:
            return url
    if isinstance(url_field, str) and url_field:
        return url_field

    raise RuntimeError(
        f"No {media_type} URL found in fal.ai response keys={list(result.keys())}"
    )
