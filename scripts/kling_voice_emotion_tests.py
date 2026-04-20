#!/usr/bin/env python3
"""Kling v2.6 Pro follow-up probes: voice consistency across shots + emotion control.

Runs four sequential fal calls (same start frame, `generate_audio=True`, 10s each):

  Test #1 — Voice consistency across shots (same character, DIFFERENT lines):
    1A: Line "这块表我修了三年了。" — neutral delivery
    1B: Line "请坐下来喝杯茶吧。"  — neutral delivery
    → listen whether the voice sounds like the *same person*.

  Test #3 — Emotion control (same character, same WARNING line, different tone):
    3A: Soft / calm / whispered delivery
    3B: Angry / shouted / terrified delivery
    → listen whether the two deliveries differ in emotion/volume/tempo.

Each call costs ~$0.50 on Kling v2.6 Pro 10s → ~$2 total. Outputs land in
``_workspaces/kling_capability_probe/<test_label>.mp4`` with an adjacent
``.audio.wav`` extracted for quicker listening.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
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


_START_FRAME = (
    _REPO_ROOT
    / "Runtime/intake_e2e_outputs/workspace_e2e_text_only_20260413_225626"
    / "artifacts/media/KeyFrameAgent/image/task_1_4e2d5e30_img_char_001_global.png"
)

_OUT_DIR = _REPO_ROOT / "_workspaces" / "kling_capability_probe"

# Scene anchor used by every prompt so the only variable is line / emotion.
_SCENE = (
    "A middle-aged watchmaker in his workshop faces the camera directly, "
    "medium close-up, warm interior light. "
)

_TESTS: list[dict[str, str]] = [
    # ------------------------------------------------------------------
    # Test #1 — Voice consistency across shots. SAME start frame, SAME
    # character description, DIFFERENT lines, DIFFERENT semantic content
    # so Kling can't reuse the earlier audio. If both deliveries sound
    # like the same person, cross-shot voice consistency is usable.
    # ------------------------------------------------------------------
    {
        "label": "1A_voice_consistency_line_A",
        "prompt": (
            _SCENE
            + "He speaks clearly in Mandarin Chinese the line: "
            "\u300c\u8fd9\u5757\u8868\u6211\u4fee\u4e86\u4e09\u5e74\u4e86\u3002\u300d "  # 「这块表我修了三年了。」
            "His lips move in visible sync with each syllable. "
            "Natural neutral tone, calm and matter-of-fact."
        ),
        "listen_for": (
            "Voice timbre + speaker identity. Chinese line: "
            "\u300c\u8fd9\u5757\u8868\u6211\u4fee\u4e86\u4e09\u5e74\u4e86\u3002\u300d"
        ),
    },
    {
        "label": "1B_voice_consistency_line_B",
        "prompt": (
            _SCENE
            + "He speaks clearly in Mandarin Chinese the line: "
            "\u300c\u8bf7\u5750\u4e0b\u6765\u559d\u676f\u8336\u5427\u3002\u300d "  # 「请坐下来喝杯茶吧。」
            "His lips move in visible sync with each syllable. "
            "Natural neutral tone, calm and matter-of-fact."
        ),
        "listen_for": (
            "Same voice timbre as 1A? Chinese line: "
            "\u300c\u8bf7\u5750\u4e0b\u6765\u559d\u676f\u8336\u5427\u3002\u300d"
        ),
    },
    # ------------------------------------------------------------------
    # Test #3 — Emotion control. SAME start frame, SAME line, sharply
    # different emotional direction. If both deliveries sound tonally
    # identical, prompt-level emotion control does not work.
    # ------------------------------------------------------------------
    {
        "label": "3A_emotion_soft_calm",
        "prompt": (
            _SCENE
            + "He speaks the line quietly and calmly, in a soft low voice, "
            "almost whispering with a gentle gentle tone and slow pace: "
            "\u300c\u522b\u8fc7\u6765\uff0c\u73b0\u5728\u4e0d\u8981\u8fc7\u6765\u3002\u300d "  # 「别过来，现在不要过来。」
            "His lips move in visible sync with each syllable."
        ),
        "listen_for": (
            "Soft / quiet / whispered delivery? Chinese line: "
            "\u300c\u522b\u8fc7\u6765\uff0c\u73b0\u5728\u4e0d\u8981\u8fc7\u6765\u3002\u300d"
        ),
    },
    {
        "label": "3B_emotion_angry_shout",
        "prompt": (
            _SCENE
            + "He SHOUTS the line loudly with intense fear and fury, raised "
            "voice cracking, desperate and urgent: "
            "\u300c\u522b\u8fc7\u6765\uff01\u73b0\u5728\u4e0d\u8981\u8fc7\u6765\uff01\u300d "  # 「别过来！现在不要过来！」
            "His lips move in visible sync with each syllable."
        ),
        "listen_for": (
            "Loud / shouted / urgent delivery? Chinese line: "
            "\u300c\u522b\u8fc7\u6765\uff01\u73b0\u5728\u4e0d\u8981\u8fc7\u6765\uff01\u300d"
        ),
    },
]


def _ffprobe_audio_summary(mp4_path: Path) -> dict[str, str]:
    try:
        proc = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "a:0",
                "-show_entries",
                "stream=codec_name,sample_rate,channels,duration",
                "-of", "json",
                str(mp4_path),
            ],
            capture_output=True, text=True, check=True, timeout=15,
        )
        data = json.loads(proc.stdout or "{}")
        streams = data.get("streams") or []
        return streams[0] if streams else {}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def _extract_audio_wav(mp4_path: Path) -> Path:
    wav = mp4_path.with_suffix(".audio.wav")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(mp4_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100",
            str(wav),
        ],
        capture_output=True, check=False, timeout=60,
    )
    return wav


async def _run_one(
    *,
    api_key: str,
    model: str,
    image_data_url: str,
    start_frame_size: int,
    label: str,
    prompt: str,
    listen_for: str,
) -> dict[str, object]:
    out_mp4 = _OUT_DIR / f"{label}.mp4"
    out_prompt = _OUT_DIR / f"{label}.prompt.txt"
    out_response = _OUT_DIR / f"{label}.fal_response.json"

    arguments: dict[str, object] = {
        "prompt": prompt,
        "start_image_url": image_data_url,
        "duration": "10",
        "generate_audio": True,
    }

    print(f"\n{'=' * 60}\n[{label}]\n{'=' * 60}")
    print("prompt:", prompt)
    print("-" * 60)
    print("submitting to fal.ai...", flush=True)

    try:
        result = await fal_subscribe(api_key, model, arguments)
    except Exception as exc:
        print(f"[{label}] ERROR from fal_subscribe:", type(exc).__name__, exc, file=sys.stderr)
        return {"label": label, "status": "submit_failed", "error": str(exc)}

    out_response.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    out_prompt.write_text(prompt, encoding="utf-8")
    print(f"[{label}] fal response keys:", list(result.keys()))

    try:
        video_url = extract_fal_media_url(result, media_type="video")
    except Exception as exc:
        print(f"[{label}] ERROR extracting video url:", exc, file=sys.stderr)
        return {"label": label, "status": "extract_failed", "error": str(exc)}

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            mp4 = await http_download_bytes(client, video_url)
        except Exception as exc:
            print(f"[{label}] ERROR downloading:", type(exc).__name__, exc, file=sys.stderr)
            return {"label": label, "status": "download_failed", "error": str(exc)}

    out_mp4.write_bytes(mp4)
    audio_summary = _ffprobe_audio_summary(out_mp4)
    wav = _extract_audio_wav(out_mp4)
    print(
        f"[{label}] OK: wrote {out_mp4.name} ({len(mp4):,} B); "
        f"audio_stream={audio_summary}; wav={wav.name}"
    )
    return {
        "label": label,
        "status": "ok",
        "mp4": str(out_mp4),
        "wav": str(wav),
        "size_bytes": len(mp4),
        "audio_stream": audio_summary,
        "listen_for": listen_for,
    }


async def _main_async() -> int:
    ensure_fal_runtime_env_loaded()
    api_key = (os.getenv("FAL_API_KEY") or "").strip()
    model = (os.getenv("FAL_VIDEO_MODEL") or "").strip()
    if not api_key or not model:
        print("ERROR: FAL_API_KEY / FAL_VIDEO_MODEL not set.", file=sys.stderr)
        return 2
    if "kling-video/v2.6/pro" not in model:
        print(f"WARNING: model={model!r} is not Kling v2.6 Pro; results may differ.", file=sys.stderr)

    if not _START_FRAME.is_file():
        print("ERROR: start frame missing:", _START_FRAME, file=sys.stderr)
        return 2
    png = _START_FRAME.read_bytes()
    b64 = base64.b64encode(png).decode("utf-8")
    image_data_url = f"data:image/png;base64,{b64}"

    _OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"model:       {model}")
    print(f"start frame: {_START_FRAME} ({len(png):,} bytes)")
    print(f"output dir:  {_OUT_DIR}")
    print(f"tests:       {len(_TESTS)}  (~$0.50 each → ~${0.5 * len(_TESTS):.2f} total)")
    print(f"started:     {datetime.now().isoformat(timespec='seconds')}")

    results: list[dict[str, object]] = []
    for spec in _TESTS:
        r = await _run_one(
            api_key=api_key,
            model=model,
            image_data_url=image_data_url,
            start_frame_size=len(png),
            label=spec["label"],
            prompt=spec["prompt"],
            listen_for=spec["listen_for"],
        )
        results.append(r)

    summary_path = _OUT_DIR / f"voice_emotion_tests_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'=' * 60}\nALL TESTS DONE — summary: {summary_path}\n{'=' * 60}")
    print("\nWhat to listen for (compare pairs side-by-side):")
    print("  Test #1 — VOICE CONSISTENCY:")
    print("    Listen to  1A_voice_consistency_line_A.audio.wav")
    print("    Then to    1B_voice_consistency_line_B.audio.wav")
    print("    Question: Does it sound like the SAME speaker?")
    print("")
    print("  Test #3 — EMOTION CONTROL:")
    print("    Listen to  3A_emotion_soft_calm.audio.wav")
    print("    Then to    3B_emotion_angry_shout.audio.wav")
    print("    Question: Is the delivery tonally DIFFERENT (volume/urgency/pace)?")

    return 0 if all(r.get("status") == "ok" for r in results) else 1


def main() -> None:
    raise SystemExit(asyncio.run(_main_async()))


if __name__ == "__main__":
    main()
