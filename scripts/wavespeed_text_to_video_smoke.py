#!/usr/bin/env python3
"""WaveSpeed **text-to-video** smoke test (no reference images).

Uses ``WavespeedVideoService.generate_clip`` with empty ``keyframe_images`` — same
shape as ``scripts/fal_text_to_video_smoke.py`` but hits WaveSpeed.ai (UniVA-style
Seedance T2V defaults).

**Costs WaveSpeed credits.** Default duration maps to 5s or 10s (see
``WavespeedVideoService``).

Environment (repo-root ``.env`` merge via ``ensure_fal_runtime_env_loaded``):

- ``WAVESPEED_API_KEY`` (required)
- ``FW_VIDEO_BACKEND`` — optional; this script constructs ``WavespeedVideoService``
  directly (no need to set for the smoke script)
- ``WAVESPEED_VIDEO_PROVIDER`` — default ``bytedance``
- ``WAVESPEED_VIDEO_T2V_MODEL`` — default ``seedance-v1-pro-t2v-480p``
- ``WAVESPEED_T2V_PROMPT`` — optional default when ``--prompt`` omitted

Examples::

    python scripts/wavespeed_text_to_video_smoke.py
    python scripts/wavespeed_text_to_video_smoke.py --prompt "A cat on a windowsill." -o /tmp/ws_t2v.mp4
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
from inference.generation.video_generators.service import WavespeedVideoService

_DEFAULT_PROMPT = (
    "Simple test clip: a red balloon floats slowly against a clear blue sky, soft daylight."
)


async def _run(args: argparse.Namespace) -> int:
    ensure_fal_runtime_env_loaded()
    if not (os.getenv("WAVESPEED_API_KEY") or "").strip():
        print(
            "ERROR: WAVESPEED_API_KEY not set (set in repo-root .env or environment).",
            file=sys.stderr,
        )
        return 2

    prompt = (args.prompt or "").strip() or _DEFAULT_PROMPT

    out_path = args.output
    if out_path is None:
        runtime = _REPO_ROOT / "Runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        out_path = runtime / f"wavespeed_t2v_smoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    print("WAVESPEED_VIDEO_PROVIDER:", (os.getenv("WAVESPEED_VIDEO_PROVIDER") or "bytedance").strip())
    print("WAVESPEED_VIDEO_T2V_MODEL:", (os.getenv("WAVESPEED_VIDEO_T2V_MODEL") or "seedance-v1-pro-t2v-480p").strip())
    print("duration_sec:", args.duration)
    print("prompt:", prompt if len(prompt) <= 120 else prompt[:117] + "...")

    svc = WavespeedVideoService()
    try:
        mp4 = await svc.generate_clip(
            shot_id="ws_t2v_smoke",
            keyframe_images=[],
            prompt=prompt,
            duration_sec=float(args.duration),
        )
    except Exception as exc:
        print("ERROR: WaveSpeed call failed:", type(exc).__name__, exc, file=sys.stderr)
        return 3
    finally:
        await svc.close()

    if not mp4 or len(mp4) < 64:
        print("ERROR: response payload too small to be a valid mp4.", file=sys.stderr)
        return 4

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(mp4)
    print("OK: wrote", out_path, "size_bytes=", len(mp4))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="WaveSpeed text-to-video smoke (prompt only).")
    parser.add_argument(
        "--prompt",
        default=os.getenv("WAVESPEED_T2V_PROMPT", _DEFAULT_PROMPT),
        help="Text prompt (default: WAVESPEED_T2V_PROMPT env or built-in short test).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output .mp4 path (default: Runtime/wavespeed_t2v_smoke_<timestamp>.mp4).",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Requested duration in seconds (maps to 5 or 10 for Seedance-style models).",
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
