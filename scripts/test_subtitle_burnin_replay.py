#!/usr/bin/env python3
"""Replay CompositorAgent's subtitle burn-in path against an existing run.

Bypasses the plan stack entirely. Reads:
  - the assembled video (clip_final.mp4 from a prior VideoAgent run)
  - the final-mix audio (aud_final.wav from a prior AudioMixAgent run)
  - the transcript JSON (segments → SRT) from a prior TranscriptionAgent run

Calls ``CompositorService.compose()`` directly with the SRT inline. No
fal/Kling/audio gen calls. Used to validate the subtitle-source caption
fix on TranscriptionAgent without re-rendering video.

Output: <run_dir>/replay_subtitle_burnin.mp4
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")

from inference.generation.compositor_service import CompositorService  # noqa: E402


def _seconds_to_srt_timestamp(s: float) -> str:
    """``32.06`` → ``"00:00:32,060"`` (SRT format)."""
    if s < 0:
        s = 0.0
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    whole = int(s % 60)
    millis = int(round((s - int(s)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{h:02d}:{m:02d}:{whole:02d},{millis:03d}"


def _segments_to_srt(segments: list[dict]) -> str:
    """Convert ``[{start_time, end_time, text}, ...]`` → SRT body."""
    lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        start = float(seg.get("start_time", 0) or 0)
        end = float(seg.get("end_time", 0) or 0)
        text = (seg.get("text") or "").strip()
        if end <= start or not text:
            continue
        lines.append(str(i))
        lines.append(
            f"{_seconds_to_srt_timestamp(start)} --> "
            f"{_seconds_to_srt_timestamp(end)}"
        )
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--run-dir",
        default=str(
            _REPO / "evals/sub-agents/e2e_samurai_20260506_222914"
        ),
        help="Top-level run dir containing workspace_global_*/artifacts/...",
    )
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        print(f"FATAL: run dir not found: {run_dir}")
        return 2

    # Find the workspace dir (the one workspace_global_* under run_dir).
    ws_candidates = sorted(run_dir.glob("workspace_global_*"))
    if not ws_candidates:
        print(f"FATAL: no workspace_global_* under {run_dir}")
        return 2
    ws = ws_candidates[0]
    print(f"[replay] workspace: {ws}")

    # Locate the three artifacts we need.
    video_glob = list(
        ws.glob("artifacts/media/VideoAgent/video/*_clip_final.mp4")
    )
    audio_glob = list(
        ws.glob("artifacts/media/AudioMixAgent/audio/*_aud_final.wav")
    )
    transcript_glob = list(ws.glob("artifacts/TranscriptionAgent/*.json"))

    if not video_glob:
        print(f"FATAL: no clip_final.mp4 under {ws}")
        return 3
    if not audio_glob:
        print(f"FATAL: no aud_final.wav under {ws}")
        return 3
    if not transcript_glob:
        print(f"FATAL: no transcript JSON under {ws}")
        return 3

    video_path = video_glob[0]
    audio_path = audio_glob[0]
    transcript_path = transcript_glob[0]
    print(f"[replay] video      : {video_path.name}")
    print(f"[replay] audio      : {audio_path.name}")
    print(f"[replay] transcript : {transcript_path.name}")

    # Build SRT from transcript segments.
    transcript = json.loads(transcript_path.read_text())
    segments = transcript.get("content", {}).get("segments", []) or []
    srt_body = _segments_to_srt(segments)
    if not srt_body.strip():
        print("FATAL: transcript has no usable segments")
        return 4
    print(f"[replay] SRT cues   : {sum(1 for ln in srt_body.splitlines() if '-->' in ln)}")
    print()
    print("=== generated SRT body ===")
    print(srt_body)
    print("=== end SRT ===")
    print()

    # Compose with the (just-fixed) CompositorService — exercises A3
    # subtitle font_color normalize + font_size/margin scale alongside
    # the actual subtitle burn-in.
    plan = {
        "output_resolution": "1920x1080",
        "fps": 30,
        "subtitle_style": {
            "font_size": 24,
            "font_color": "#FFFFFF",
            "outline_color": "#000000",
            "font_name": "Noto Sans CJK SC",
        },
    }

    svc = CompositorService()
    print("[replay] calling CompositorService.compose() ...")
    out_bytes = await svc.compose(
        video_path=str(video_path),
        audio_path=str(audio_path),
        subtitle_srts=[srt_body],
        plan=plan,
    )

    out_path = run_dir / "replay_subtitle_burnin.mp4"
    out_path.write_bytes(out_bytes)
    print(f"[replay] DONE → {out_path} ({len(out_bytes):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
