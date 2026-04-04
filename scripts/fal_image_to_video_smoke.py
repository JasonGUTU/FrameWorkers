#!/usr/bin/env python3
"""Minimal fal **image-to-video** smoke test (same path as VideoAgent / ``FAL_VIDEO_MODEL``).

Reads a local PNG, calls ``FalVideoService.generate_clip`` with one keyframe (data URL
internally). **Costs fal credits.**

Environment: ``FAL_API_KEY``, ``FAL_VIDEO_MODEL`` (from repo ``.env`` merge).

Example::

    python scripts/fal_image_to_video_smoke.py \\
      -i Runtime/live_e2e_outputs/workspace_global_20260403_221709/artifacts/media/KeyFrameAgent/image/img_sh_001_kf_001.png
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from inference.generation.fal_helpers import ensure_fal_runtime_env_loaded
from inference.generation.video_generators.service import FalVideoService

_DEFAULT_IMAGE = (
    _REPO_ROOT
    / "Runtime/live_e2e_outputs/workspace_global_20260403_221709"
    / "artifacts/media/KeyFrameAgent/image/img_sh_001_kf_001.png"
)
_DEFAULT_PROMPT = "Cinematic subtle motion, same composition; soft natural movement only."


async def _run(args: argparse.Namespace) -> int:
    ensure_fal_runtime_env_loaded()
    if not (os.getenv("FAL_API_KEY") or "").strip():
        print("ERROR: FAL_API_KEY not set.", file=sys.stderr)
        return 2
    model = (os.getenv("FAL_VIDEO_MODEL") or "").strip()
    if not model:
        print("ERROR: FAL_VIDEO_MODEL not set.", file=sys.stderr)
        return 2

    img_path = Path(args.image)
    if not img_path.is_file():
        print("ERROR: image not found:", img_path, file=sys.stderr)
        return 2
    png = img_path.read_bytes()
    prompt = (args.prompt or "").strip() or _DEFAULT_PROMPT

    out_path = args.output
    if out_path is None:
        runtime = _REPO_ROOT / "Runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        out_path = runtime / f"fal_i2v_smoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    print("FAL_VIDEO_MODEL:", model)
    print("image:", img_path, "bytes:", len(png))
    print("prompt:", prompt if len(prompt) <= 100 else prompt[:97] + "...")

    svc = FalVideoService()
    try:
        mp4 = await svc.generate_clip(
            shot_id="i2v_smoke",
            keyframe_images=[png],
            prompt=prompt,
            duration_sec=float(args.duration),
        )
    except Exception as exc:
        print("ERROR:", type(exc).__name__, exc, file=sys.stderr)
        return 3
    finally:
        await svc.close()

    if not mp4 or len(mp4) < 64:
        print("ERROR: payload too small.", file=sys.stderr)
        return 4

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(mp4)
    print("OK: wrote", out_path, "size_bytes=", len(mp4))
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="fal image-to-video smoke (FAL_VIDEO_MODEL).")
    p.add_argument(
        "-i",
        "--image",
        type=Path,
        default=_DEFAULT_IMAGE,
        help="Input PNG path.",
    )
    p.add_argument("--prompt", default=_DEFAULT_PROMPT)
    p.add_argument("-o", "--output", type=Path, default=None)
    p.add_argument("--duration", type=float, default=5.0)
    args = p.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
