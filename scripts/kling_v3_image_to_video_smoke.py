#!/usr/bin/env python3
"""Kling v3 image-to-video smoke test (validates FAL_VIDEO_MODEL=fal-ai/kling-video/v3/...).

Exercises the same call path as VideoAgent's materializer: builds a
ShotSemanticContext with a motion hint, runs through
``FalVideoService._compose_prompt``, lets ``_kling_duration_enum`` snap
to v3's ``{3, 5, 10, 15}`` enum, and downloads the resulting mp4.

Costs fal credits: ~$0.112/sec (audio off) or ~$0.168/sec (audio on).

Environment loaded from repo ``.env`` via ``ensure_fal_runtime_env_loaded``:
``FAL_API_KEY`` (required), ``FAL_VIDEO_MODEL`` (required; should be a
``fal-ai/kling-video/v3/...`` slug for this script to be meaningful).

Examples::

    # 3s, audio off, default image  →  Runtime/kling_v3_smoke_3s_<ts>.mp4
    python scripts/kling_v3_image_to_video_smoke.py

    # 15s, audio off  →  validates the new v3 upper bound
    python scripts/kling_v3_image_to_video_smoke.py --duration 15

    # 5s, audio on (Kling bakes dialogue + foley into the mp4)
    python scripts/kling_v3_image_to_video_smoke.py --duration 5 --audio

    # custom image + output path
    python scripts/kling_v3_image_to_video_smoke.py \\
      -i path/to/start_frame.png -o Runtime/my_smoke.mp4
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
from inference.generation.video_generators.types import ShotSemanticContext


_DEFAULT_IMAGE = (
    _REPO_ROOT
    / "_workspaces/workspace_global_20260509_153139"
    / "artifacts/media/IllustrationAgent/image"
    / "step_2_d7df2bc3_illustration_seg_001.png"
)
_DEFAULT_MOTION_HINT = (
    "slow push-in, subject turns head gently from left to right then back, "
    "shoulders relaxed, breathing visible"
)


async def _run(args: argparse.Namespace) -> int:
    ensure_fal_runtime_env_loaded()
    if not (os.getenv("FAL_API_KEY") or "").strip():
        print("ERROR: FAL_API_KEY not set in env or .env.", file=sys.stderr)
        return 2
    model = (os.getenv("FAL_VIDEO_MODEL") or "").strip()
    if not model:
        print("ERROR: FAL_VIDEO_MODEL not set in env or .env.", file=sys.stderr)
        return 2
    if "/v3/" not in model and "/o3/" not in model:
        print(
            f"WARN: FAL_VIDEO_MODEL={model!r} is not a v3/o3 endpoint; this "
            "smoke script targets Kling v3-only behaviour (3s/15s enum). "
            "Proceeding anyway.",
            file=sys.stderr,
        )

    img_path = Path(args.image)
    if not img_path.is_file():
        print(f"ERROR: image not found: {img_path}", file=sys.stderr)
        return 2
    png = img_path.read_bytes()

    out_path = args.output
    if out_path is None:
        runtime = _REPO_ROOT / "Runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        out_path = runtime / (
            f"kling_v3_smoke_{int(args.duration)}s_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )

    ctx = ShotSemanticContext(
        shot_id="v3_smoke",
        shot_type=args.shot_type,
        visual_goal=args.visual_goal,
        action_focus=args.action_focus,
        video_motion_hints=[args.motion],
        framing_notes="hold the framing of the still; minimal subject movement",
        dialogue_text=args.dialogue,
        emotion_hint=args.emotion,
        language=args.language,
    )

    print("FAL_VIDEO_MODEL:", model)
    print("image:", img_path, "bytes:", len(png))
    print(f"duration={args.duration}s  audio={args.audio}")
    motion_preview = args.motion if len(args.motion) <= 100 else args.motion[:97] + "..."
    print("motion:", motion_preview)

    svc = FalVideoService()
    try:
        result = await svc.generate_clip(
            shot_id="v3_smoke",
            keyframe_images=[png],
            semantic_context=ctx,
            duration_sec=float(args.duration),
            generate_audio=args.audio,
        )
        mp4 = result.bytes
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
    head = mp4[:12]
    print("OK: wrote", out_path, "size_bytes=", len(mp4))
    print("mp4 head:", head)
    if b"ftyp" in head:
        print("mp4 container: valid (ftyp atom present)")
    print(
        "resolved duration enum:",
        repr(result.resolved_payload.get("duration")),
    )
    return 0


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Kling v3 image-to-video smoke test (requires "
            "FAL_VIDEO_MODEL=fal-ai/kling-video/v3/...)."
        )
    )
    p.add_argument(
        "-i", "--image", type=Path, default=_DEFAULT_IMAGE,
        help="Input PNG path (default: a stock illustration from _workspaces).",
    )
    p.add_argument(
        "--motion", default=_DEFAULT_MOTION_HINT,
        help="Motion hint string; becomes the prompt prefix via _compose_prompt.",
    )
    p.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output mp4 path (default: Runtime/kling_v3_smoke_<dur>s_<ts>.mp4 — gitignored).",
    )
    p.add_argument(
        "--duration", type=float, default=3.0,
        help="Clip duration in seconds. Kling v3 accepts {3, 5, 10, 15}; "
             "off-enum values get snapped to nearest.",
    )
    p.add_argument(
        "--audio", action="store_true",
        help="Enable generate_audio (Kling bakes dialogue+foley into mp4). "
             "Default off (cheaper).",
    )
    p.add_argument(
        "--dialogue", default="",
        help="Dialogue line spoken on-camera. Empty = action shot (no speech, "
             "only foley/ambient audio when --audio is on).",
    )
    p.add_argument(
        "--emotion", default="",
        help="Delivery tone for dialogue (calm / urgent / warm / sad / etc.). "
             "Only meaningful when --dialogue is set.",
    )
    p.add_argument(
        "--language", default="",
        help="BCP-47 / ISO language code for all voiced content (e.g. 'zh', "
             "'en'). Without this Kling falls back to its English training "
             "prior on action shots even when --dialogue is Chinese.",
    )
    p.add_argument(
        "--shot-type", default="close-up",
        help="Shot type tag (close-up / medium / wide / etc.).",
    )
    p.add_argument(
        "--visual-goal",
        default=(
            "Maintain the character's pose and expression from the input still; "
            "introduce only a subtle camera push-in and a small head turn."
        ),
        help="High-level visual intent for the shot.",
    )
    p.add_argument(
        "--action-focus", default="slight head turn left to right, eyes following",
        help="Per-shot action focus (drives foley generation when --audio is on).",
    )
    args = p.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
