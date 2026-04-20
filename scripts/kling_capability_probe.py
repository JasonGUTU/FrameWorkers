#!/usr/bin/env python3
"""Kling v2.6 Pro capability probe — single 10s call, ``generate_audio=True``.

Purpose: empirical test of what Kling 2.6 Pro I2V actually produces when the
prompt explicitly requests (a) character dialogue with lip-sync, (b) in-frame
subtitle text, (c) background music, (d) environmental foley. The prompt is
bilingual: English scene description + Chinese dialogue line in quotes, to
probe Kling's Chinese-speech capability (if any).

Bypasses ``FalVideoService`` because the current service layer does NOT pass
``generate_audio`` through on the single-anchor path (service.py:475-480 only
handles dual-anchor). This script constructs the fal ``arguments`` dict
directly so the flag is always set and the raw fal response is printed for
inspection (audio track URLs, subtitle fields, etc. would show up in
``result.keys()`` beyond ``video``).

Duration is pinned to 10 (Kling's upper quantum — 20s single-call is not
possible on this model). **Costs fal credits (~$0.50 for one 10s v2.6 Pro
call).** Run once, listen/watch the output.

Example::

    python scripts/kling_capability_probe.py
    python scripts/kling_capability_probe.py -i path/to/start.png
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import httpx

from inference.generation.fal_helpers import (
    ensure_fal_runtime_env_loaded,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
)


_DEFAULT_IMAGE = (
    _REPO_ROOT
    / "Runtime/intake_e2e_outputs/workspace_e2e_text_only_20260413_225626"
    / "artifacts/media/KeyFrameAgent/image/task_1_4e2d5e30_img_char_001_global.png"
)

# English scene skeleton + Chinese dialogue in quotes. The four capability
# probes are labeled inline so we can correlate "model did / didn't do X"
# with a specific clause when reviewing the output.
_DEFAULT_PROMPT = (
    # --- Scene + character ---
    "A middle-aged man in a dark sweater sits by a window inside a quiet "
    "coffee shop during daytime, warm soft light on his face. He faces the "
    "camera directly, medium close-up. "
    # --- Probe #1: dialogue + lip-sync (Chinese) ---
    "He clearly speaks aloud in Mandarin Chinese the line: "
    "\u300c\u6b22\u8fce\u6765\u5230 FrameWorkers\u3002\u300d "
    "His lips move in visible sync with each syllable. "
    # --- Probe #2: on-screen subtitle (matching the line) ---
    "At the bottom of the frame, a clean white subtitle caption reads: "
    "\u300c\u6b22\u8fce\u6765\u5230 FrameWorkers\u300d. "
    # --- Probe #3: background music ---
    "Background music: soft jazz piano, low volume, plays continuously. "
    # --- Probe #4: ambient + foley ---
    "Ambient sound: quiet cafe chatter in the distance, occasional gentle "
    "cup clinks, espresso machine hiss. After speaking, he lifts his "
    "coffee cup and takes a small sip; the cup makes a soft clink when it "
    "touches the saucer."
)


async def _run(args: argparse.Namespace) -> int:
    ensure_fal_runtime_env_loaded()

    api_key = (os.getenv("FAL_API_KEY") or "").strip()
    if not api_key:
        print("ERROR: FAL_API_KEY not set.", file=sys.stderr)
        return 2

    model = (args.model or os.getenv("FAL_VIDEO_MODEL") or "").strip()
    if not model:
        print("ERROR: FAL_VIDEO_MODEL not set and --model not passed.", file=sys.stderr)
        return 2
    if "kling-video/v2.6/pro" not in model:
        print(
            f"WARNING: model={model!r} does not look like Kling v2.6 Pro; "
            "probe results may not reflect that SKU.",
            file=sys.stderr,
        )

    img_path = Path(args.image)
    if not img_path.is_file():
        print("ERROR: start-frame image not found:", img_path, file=sys.stderr)
        return 2
    png = img_path.read_bytes()
    b64 = base64.b64encode(png).decode("utf-8")
    image_data_url = f"data:image/png;base64,{b64}"

    duration_enum = "10" if float(args.duration) > 5.5 else "5"

    # Direct fal arguments — includes generate_audio which the service layer
    # currently doesn't pass on single-anchor calls.
    arguments: dict[str, object] = {
        "prompt": args.prompt,
        "start_image_url": image_data_url,
        "duration": duration_enum,
        "generate_audio": True,
    }

    # Output locations
    runtime_dir = _REPO_ROOT / "_workspaces" / "kling_capability_probe"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_mp4 = args.output or (runtime_dir / f"kling_probe_{ts}.mp4")
    out_mp4 = Path(out_mp4)
    out_json = out_mp4.with_suffix(".fal_response.json")
    out_prompt = out_mp4.with_suffix(".prompt.txt")

    # Redact the image data URL before logging — it's multi-MB base64 and
    # pollutes the audit file.
    args_for_audit = dict(arguments)
    args_for_audit["start_image_url"] = f"<base64 png, {len(png)} bytes>"

    print("=" * 60)
    print("Kling v2.6 Pro capability probe")
    print("=" * 60)
    print(f"model:       {model}")
    print(f"start frame: {img_path} ({len(png)} bytes)")
    print(f"duration:    {duration_enum}s (requested {args.duration}s)")
    print(f"generate_audio: True")
    print(f"output mp4:  {out_mp4}")
    print("-" * 60)
    print("PROMPT:")
    print(args.prompt)
    print("-" * 60)
    print("arguments (redacted):", json.dumps(args_for_audit, ensure_ascii=False, indent=2))
    print("=" * 60)
    print("submitting to fal.ai (this costs credits; ~$0.50 for Kling 2.6 Pro 10s)...")
    print("=" * 60, flush=True)

    try:
        result = await fal_subscribe(api_key, model, arguments)
    except Exception as exc:
        print("ERROR from fal_subscribe:", type(exc).__name__, exc, file=sys.stderr)
        return 3

    print("fal response keys:", list(result.keys()))
    print("fal full response (trimmed):")
    # Trim any inline base64 for pretty-print
    pretty = _trim_response_for_print(result)
    print(json.dumps(pretty, ensure_ascii=False, indent=2)[:4000])
    print("-" * 60)

    # Save the full raw response (useful to spot audio / subtitle extras)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("raw fal response saved:", out_json)

    # Save the effective prompt for reproducibility
    out_prompt.write_text(args.prompt, encoding="utf-8")
    print("effective prompt saved:", out_prompt)

    # Try to extract the video URL
    try:
        video_url = extract_fal_media_url(result, media_type="video")
    except Exception as exc:
        print("ERROR extracting video url:", exc, file=sys.stderr)
        return 4

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            mp4 = await http_download_bytes(client, video_url)
        except Exception as exc:
            print("ERROR downloading mp4:", type(exc).__name__, exc, file=sys.stderr)
            return 5

    out_mp4.write_bytes(mp4)
    print(f"video saved: {out_mp4}  ({len(mp4):,} bytes)")
    print()
    print("=" * 60)
    print("NEXT: play the mp4 and listen for:")
    print("  [1] Chinese dialogue \u300c\u6b22\u8fce\u6765\u5230 FrameWorkers\u300d spoken + lip-sync")
    print("  [2] On-screen subtitle text showing the same line")
    print("  [3] Background jazz piano music")
    print("  [4] Cafe ambient + cup / espresso foley")
    print("Also check the .fal_response.json for non-video track fields.")
    print("=" * 60)
    return 0


def _trim_response_for_print(obj):
    """Truncate obvious base64 fields for console printing."""
    if isinstance(obj, dict):
        return {k: _trim_response_for_print(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_trim_response_for_print(v) for v in obj]
    if isinstance(obj, str) and obj.startswith("data:") and len(obj) > 200:
        return f"<data URL, {len(obj)} chars>"
    return obj


def main() -> None:
    p = argparse.ArgumentParser(description="Kling v2.6 Pro capability probe.")
    p.add_argument(
        "-i",
        "--image",
        type=Path,
        default=_DEFAULT_IMAGE,
        help="Start-frame PNG (default: bundled Joseph global portrait).",
    )
    p.add_argument(
        "--prompt",
        default=_DEFAULT_PROMPT,
        help="Override the capability-probe prompt (default: bilingual probe).",
    )
    p.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output mp4 path (default: _workspaces/kling_capability_probe/kling_probe_<ts>.mp4)",
    )
    p.add_argument(
        "--duration", type=float, default=10.0,
        help="Requested duration in seconds; Kling quantizes to 5 or 10 (default 10).",
    )
    p.add_argument(
        "--model", default=None,
        help="Override FAL_VIDEO_MODEL for this run.",
    )
    args = p.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
