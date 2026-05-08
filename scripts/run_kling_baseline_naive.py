#!/usr/bin/env python3
"""B3-naive Kling baseline runner.

Pipeline:
  1. Read user_goal of a named case from
     ``evals/director_routing/eval_cases_v4500_balanced.json``
  2. Read the splitter system_prompt from
     ``evals/sub-agents/baseline_kling_naive_prompts/splitter_system_prompt.txt``
  3. ONE Gemini-3-pro-preview chat_json call → ``{"shots": [{...}, ...]}``
  4. For each shot, call Kling t2v
     (``fal-ai/kling-video/v2.6/pro/text-to-video``) and save shot_NNN.mp4
  5. ``ffmpeg concat`` all shot mp4 → ``final.mp4``

No character anchor, no music, no ambience, no subtitle — that's framework's
job, not baseline's. Run output goes under
``evals/sub-agents/baseline_<case>_kling_naive_<UTC ts>/``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")
# Force Kling t2v model for this baseline (i2v is the codebase default).
os.environ["FAL_VIDEO_MODEL"] = (
    "fal-ai/kling-video/v2.6/pro/text-to-video"
)
# Ensure real fal calls (not mock).
os.environ.setdefault("FW_USE_REAL_MEDIA_GEN", "1")

from inference.clients import LLMClient  # noqa: E402
from inference.generation.video_generators.service import (  # noqa: E402
    FalVideoService,
)
from inference.generation.video_generators.types import (  # noqa: E402
    ShotSemanticContext,
)


_CASES_FILE = _REPO / "evals/director_routing/eval_cases_v4500_balanced.json"
_PROMPT_FILE = (
    _REPO
    / "evals/sub-agents/baseline_kling_naive_prompts/splitter_system_prompt.txt"
)
_OUTPUT_BASE = _REPO / "evals/sub-agents"

_SPLITTER_MODEL = "gemini-3-pro-preview"
_SPLITTER_MAX_TOKENS = 65536


def _load_case(case_name: str) -> dict:
    cases = json.loads(_CASES_FILE.read_text())
    for c in cases:
        if c.get("name") == case_name:
            return c
    raise KeyError(f"case {case_name!r} not in {_CASES_FILE}")


async def _split_brief_into_shots(
    user_goal: str, system_prompt: str
) -> list[dict]:
    client = LLMClient()
    user_prompt = (
        f"Brief:\n{user_goal}\n\nSplit into 7-10 shot prompts."
    )
    result = await client.chat_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=_SPLITTER_MODEL,
        max_tokens=_SPLITTER_MAX_TOKENS,
    )
    if not isinstance(result, dict):
        raise RuntimeError(
            f"splitter returned non-dict: {type(result).__name__}"
        )
    shots = result.get("shots") or []
    if not isinstance(shots, list) or not (7 <= len(shots) <= 10):
        raise RuntimeError(
            f"splitter emitted {len(shots) if isinstance(shots, list) else 'non-list'} "
            f"shots, expected 7-10. raw={result}"
        )
    return shots


async def _render_one_shot(
    svc: FalVideoService, shot: dict, idx: int, out_dir: Path
) -> Path:
    shot_id = shot.get("shot_id") or f"sh_{idx:03d}"
    prompt = (shot.get("prompt") or "").strip()
    duration_sec = float(shot.get("duration_sec", 5) or 5)
    if duration_sec not in (5.0, 10.0):
        duration_sec = 10.0 if duration_sec > 5.5 else 5.0

    semantic_ctx = ShotSemanticContext(
        shot_id=shot_id,
        visual_goal=prompt,
        action_focus="",
    )
    print(
        f"[baseline] [{idx}/{idx}] shot {shot_id} duration={duration_sec}s"
        f" prompt='{prompt[:80]}...'"
    )
    t0 = time.time()
    result = await svc.generate_clip(
        shot_id=shot_id,
        keyframe_images=[],  # t2v: no anchor
        semantic_context=semantic_ctx,
        duration_sec=duration_sec,
    )
    elapsed = time.time() - t0
    if not result.bytes:
        raise RuntimeError(
            f"shot {shot_id}: Kling t2v returned empty bytes"
        )
    out_path = out_dir / f"shot_{idx:03d}_{shot_id}.mp4"
    out_path.write_bytes(result.bytes)
    print(
        f"[baseline]   → {out_path.name} ({len(result.bytes):,} bytes, {elapsed:.1f}s)"
    )
    return out_path


def _ffmpeg_concat(shot_paths: list[Path], final_path: Path) -> None:
    """ffmpeg concat protocol: write a concat list file then concat -c copy."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")
    list_file = final_path.parent / "_concat_list.txt"
    with list_file.open("w") as fh:
        for p in shot_paths:
            fh.write(f"file '{p.absolute()}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(final_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0 or not final_path.is_file():
        # concat -c copy can fail if codecs don't perfectly match. Fall
        # back to re-encoding (slower but always works).
        print(
            "[baseline] concat -c copy failed, falling back to re-encode..."
        )
        cmd_reencode = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac",
            str(final_path),
        ]
        proc2 = subprocess.run(
            cmd_reencode, capture_output=True, text=True, timeout=600,
        )
        if proc2.returncode != 0 or not final_path.is_file():
            tail = (proc2.stderr or "")[-500:]
            raise RuntimeError(
                f"ffmpeg concat (re-encode) also failed: {tail}"
            )


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, help="case name in eval_cases_v4500_balanced.json")
    ap.add_argument(
        "--run-name",
        default=None,
        help="output dir name; default = baseline_<case>_kling_naive_<UTC ts>",
    )
    args = ap.parse_args()

    case = _load_case(args.case)
    user_goal = case["user_goal"]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_name = args.run_name or f"baseline_{args.case}_kling_naive_{timestamp}"
    out_dir = _OUTPUT_BASE / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[baseline] case={args.case}  out_dir={out_dir}")
    print(f"[baseline] splitter_model={_SPLITTER_MODEL}  max_tokens={_SPLITTER_MAX_TOKENS}")
    print(f"[baseline] kling_model={os.environ['FAL_VIDEO_MODEL']}")
    print(f"[baseline] user_goal: {user_goal}")
    print()

    # Persist run config.
    (out_dir / "00_run_config.json").write_text(json.dumps({
        "case": args.case,
        "run_name": run_name,
        "user_goal": user_goal,
        "splitter_model": _SPLITTER_MODEL,
        "splitter_max_tokens": _SPLITTER_MAX_TOKENS,
        "splitter_prompt_file": str(_PROMPT_FILE.relative_to(_REPO)),
        "kling_model": os.environ["FAL_VIDEO_MODEL"],
        "kling_generate_audio_default": True,  # FalVideoService default
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Step 1: split brief ────────────────────────────────────────
    splitter_system = _PROMPT_FILE.read_text()
    print("[baseline] STEP 1: calling splitter (Gemini 3 pro)...")
    t0 = time.time()
    shots = await _split_brief_into_shots(user_goal, splitter_system)
    print(f"[baseline]   → {len(shots)} shots emitted ({time.time()-t0:.1f}s)")

    (out_dir / "02_splitter_output.json").write_text(
        json.dumps({"shots": shots}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("=== shot prompts ===")
    for s in shots:
        print(f"  [{s.get('shot_id','?')}] {s.get('duration_sec','?')}s  {s.get('prompt','')[:100]}")
    print()

    # ── Step 2: render all shots via Kling t2v in PARALLEL ─────────
    # Per memory:feedback_video_gen_must_parallel — N-shot Kling calls
    # must use asyncio.gather, not sequential. Semaphore(8) caps fal
    # concurrency to a rate-limit-safe ceiling.
    print(f"[baseline] STEP 2: rendering {len(shots)} shots via Kling t2v "
          f"(parallel, Semaphore=8)...")
    svc = FalVideoService()
    sem = asyncio.Semaphore(8)

    async def _gen_with_sem(shot: dict, idx: int) -> Path:
        async with sem:
            return await _render_one_shot(svc, shot, idx, out_dir)

    t_step2 = time.time()
    shot_paths: list[Path] = await asyncio.gather(
        *[_gen_with_sem(shot, i) for i, shot in enumerate(shots, start=1)]
    )
    print(f"[baseline]   → {len(shot_paths)} shot mp4 saved "
          f"({time.time()-t_step2:.1f}s wall — vs sequential would be sum-of-shots)")

    # ── Step 3: concat ──────────────────────────────────────────────
    final_path = out_dir / "final.mp4"
    print(f"[baseline] STEP 3: ffmpeg concat → {final_path.name}")
    _ffmpeg_concat(shot_paths, final_path)
    final_size = final_path.stat().st_size
    print(f"[baseline]   → {final_path} ({final_size:,} bytes)")

    # ffprobe duration sanity
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final_path)],
        capture_output=True, text=True, timeout=10,
    )
    dur = (proc.stdout or "").strip()
    print(f"[baseline]   final duration: {dur}s")

    print()
    print(f"[baseline] DONE. all artifacts in {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
