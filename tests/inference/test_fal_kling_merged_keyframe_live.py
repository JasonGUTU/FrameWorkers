"""Live fal.ai video call using saved KeyFrame PNGs (opt-in).

Validates the **merge helper** (tests/tooling): two PNGs → ``VideoMaterializer``
horizontal composite (letterboxed for Kling aspect limits) → single
``keyframe_images`` entry → ``FalVideoService`` / Kling. The default pipeline
uses one L3 shot PNG per shot and does not call this merge path.

Enable with ``FW_ENABLE_FAL_VIDEO_MERGED_KEYFRAME_LIVE=1`` plus ``FAL_API_KEY`` /
``FAL_VIDEO_MODEL``. See ``tests/inference/README.md``.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from agents.video.materializer import VideoMaterializer
from inference.generation.fal_helpers import ensure_fal_runtime_env_loaded
from inference.generation.video_generators.service import FalVideoService

# Merge repo-root .env / .env.example so ``FAL_*`` is visible to skipif without manual ``export``.
ensure_fal_runtime_env_loaded()


def _merged_keyframe_live_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_FAL_VIDEO_MERGED_KEYFRAME_LIVE", "").strip() != "1":
        return (
            False,
            "Set FW_ENABLE_FAL_VIDEO_MERGED_KEYFRAME_LIVE=1 to run fal video keyframe live tests.",
        )
    if not os.getenv("FAL_API_KEY", "").strip():
        return False, "FAL_API_KEY is required."
    if not os.getenv("FAL_VIDEO_MODEL", "").strip():
        return False, "FAL_VIDEO_MODEL is required (e.g. from repo .env)."
    return True, ""


_MERGED_LIVE_OK, _MERGED_LIVE_REASON = _merged_keyframe_live_ready()

_CHAR_NAME = "img_char_001_sc_001.png"
_LOC_NAME = "img_loc_001_sc_001.png"


def _resolve_pair_dir(keyframe_agent_or_image_dir: Path) -> Path | None:
    """Workspace stores PNGs under ``.../KeyFrameAgent/image/``; accept that or the agent root."""
    root = keyframe_agent_or_image_dir.resolve()
    direct = root / _CHAR_NAME, root / _LOC_NAME
    if direct[0].is_file() and direct[1].is_file():
        return root
    img = root / "image"
    nested = img / _CHAR_NAME, img / _LOC_NAME
    if nested[0].is_file() and nested[1].is_file():
        return img.resolve()
    return None


def _discover_keyframe_pair_dir() -> Path | None:
    """Pick newest ``workspace_*/.../KeyFrameAgent`` whose root or ``image/`` holds the sc_001 pair."""
    live_root = _repo_root / "Runtime" / "live_e2e_outputs"
    if not live_root.is_dir():
        return None
    candidates = sorted(
        live_root.glob("workspace_*/artifacts/media/KeyFrameAgent"),
        key=lambda p: str(p),
        reverse=True,
    )
    for c in candidates:
        found = _resolve_pair_dir(c)
        if found is not None:
            return found
    return None


def _keyframe_image_dir() -> Path:
    """Directory that **directly** contains the two PNGs (often ``.../KeyFrameAgent/image``)."""
    env = os.getenv("FW_MERGED_KEYFRAME_IMAGE_DIR", "").strip()
    if env:
        root = (_repo_root / env).resolve()
        found = _resolve_pair_dir(root)
        return found if found is not None else root
    preferred = (
        _repo_root
        / "Runtime/live_e2e_outputs/workspace_global_20260403_132858"
        / "artifacts/media/KeyFrameAgent"
    )
    found = _resolve_pair_dir(preferred)
    if found is not None:
        return found
    discovered = _discover_keyframe_pair_dir()
    if discovered is not None:
        return discovered
    return preferred.resolve()


def _load_pair_or_skip() -> tuple[bytes, bytes]:
    base = _keyframe_image_dir()
    char = base / _CHAR_NAME
    loc = base / _LOC_NAME
    if not char.is_file() or not loc.is_file():
        pytest.skip(
            f"Missing keyframe PNGs under {base} (or sibling ``image/`` under KeyFrameAgent) "
            f"(need {_CHAR_NAME} + {_LOC_NAME}). "
            f"Set FW_MERGED_KEYFRAME_IMAGE_DIR or run a live e2e that writes KeyFrameAgent images."
        )
    return char.read_bytes(), loc.read_bytes()


@pytest.mark.skipif(not _MERGED_LIVE_OK, reason=_MERGED_LIVE_REASON)
def test_fal_kling_generate_clip_with_horizontal_merged_dual_keyframe() -> None:
    """Merge helper smoke: two PNGs → one wide composite → single conditioning to Kling."""
    char_png, loc_png = _load_pair_or_skip()

    async def _run() -> bytes:
        merged_list, _summaries, layout = VideoMaterializer._merge_keyframe_images_for_video_api(
            [char_png, loc_png],
            ["scene char anchor", "scene loc anchor"],
        )
        assert layout == "horizontal_merge_2_panels"
        assert len(merged_list) == 1
        merged = merged_list[0]
        assert merged.startswith(b"\x89PNG\r\n\x1a\n")

        svc = FalVideoService()
        try:
            return await svc.generate_clip(
                shot_id="sh_merged_dual_smoke",
                keyframe_images=[merged],
                prompt=(
                    "Cinematic medium shot, watchmaker workshop at night, warm lamp light, "
                    "elderly craftsman at bench, shallow depth of field, slow subtle motion."
                ),
                duration_sec=5.0,
            )
        finally:
            await svc.close()

    clip = asyncio.run(_run())
    assert isinstance(clip, (bytes, bytearray))
    assert len(clip) > 2_000, f"expected non-trivial mp4 bytes, got len={len(clip)}"


def test_merged_keyframe_live_gate_documented() -> None:
    """Always runs: documents that live tests are opt-in (no network)."""
    assert _MERGED_LIVE_REASON or _MERGED_LIVE_OK
