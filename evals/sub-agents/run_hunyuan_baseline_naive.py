#!/usr/bin/env python3
"""B3-naive HunyuanVideo-I2V baseline runner.

Mirrors ``scripts/run_kling_baseline_naive.py`` but with:
  * Hunyuan i2v video backend (self-hosted FastAPI on H200).
  * Per-shot keyframe generated text-to-image via FalImageService
    (nano-banana-2) — Hunyuan-I2V requires a conditioning frame.
  * Splitter LLM = ``gemini-2.5-flash`` (matches the agent-pipeline
    experiment's text model, not the Kling baseline's gemini-3-pro).
  * Reads cases from ``evals/sub-agents/e2e_30/selection.json``
    (10 cr + 10 intake_img, 20 total). Skips ``storytelling`` cases.

Pipeline per case:
  1. Read user_goal of the named case from selection.json.
  2. ONE Gemini-2.5-flash chat_json call → ``{"shots": [{...}, ...]}``.
  3. For each shot: (a) FalImageService.generate_image(prompt) → keyframe png;
                    (b) HunyuanVideoService.generate_clip(keyframe, prompt) → mp4.
  4. ``ffmpeg concat`` all shot mp4 → ``final.mp4``.

No character anchor / music / subtitle / multi-scene continuity — that is
framework's job, not baseline's. Per-case run output:
``evals/sub-agents/baseline_hunyuan_naive_<case>_<UTC ts>/``

Two modes:
  (a) ``--case <name>`` runs ONE case on a single ``--hunyuan-endpoint``.
  (b) ``--all`` runs all 20 cr+intake_img cases distributed across
      ``--hunyuan-endpoints`` CSV (round-robin); within an endpoint cases
      run sequentially, across endpoints in parallel.
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
from typing import Any

_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")
os.environ.setdefault("FW_USE_REAL_MEDIA_GEN", "1")
# Force Hunyuan video backend (the global default may be fal/kling).
os.environ["FW_VIDEO_BACKEND"] = "hunyuan"

from inference.clients import LLMClient  # noqa: E402
from inference.generation.image_generators.service import (  # noqa: E402
    FalImageService,
)
from inference.generation.video_generators.service import (  # noqa: E402
    HunyuanVideoService,
)
from inference.generation.video_generators.types import (  # noqa: E402
    ShotSemanticContext,
)


_SELECTION = _REPO / "evals/sub-agents/e2e_30/selection.json"
_UPLOADS = _REPO / "evals/sub-agents/e2e_30/uploads"
_PROMPT_FILE = (
    _REPO / "evals/sub-agents/baseline_hunyuan_naive_prompts/splitter_system_prompt.txt"
)
_OUTPUT_BASE = _REPO / "evals/sub-agents"

_SPLITTER_MODEL = "gemini-2.5-flash"
_SPLITTER_MAX_TOKENS = 65536


# ──────────────────────────────────────────────────────────────────────
# Splitter (Gemini 2.5 Flash → list[shot])
# ──────────────────────────────────────────────────────────────────────

async def _split_brief_into_shots(
    user_goal: str, system_prompt: str
) -> list[dict]:
    client = LLMClient()
    user_prompt = f"Brief:\n{user_goal}\n\nSplit into 7-10 shot prompts."
    result = await client.chat_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=_SPLITTER_MODEL,
        max_tokens=_SPLITTER_MAX_TOKENS,
    )
    if not isinstance(result, dict):
        raise RuntimeError(f"splitter returned non-dict: {type(result).__name__}")
    shots = result.get("shots") or []
    if not isinstance(shots, list) or not (7 <= len(shots) <= 10):
        n = len(shots) if isinstance(shots, list) else "non-list"
        raise RuntimeError(
            f"splitter emitted {n} shots, expected 7-10. raw={result}"
        )
    return shots


# ──────────────────────────────────────────────────────────────────────
# Per-shot render: text → keyframe png → hunyuan i2v mp4
# ──────────────────────────────────────────────────────────────────────

async def _render_one_shot(
    img_svc: FalImageService,
    vid_svc: HunyuanVideoService,
    shot: dict,
    idx: int,
    out_dir: Path,
    upload_ref_bytes: bytes | None = None,
) -> Path:
    shot_id = shot.get("shot_id") or f"sh_{idx:03d}"
    prompt = (shot.get("prompt") or "").strip()
    if not prompt:
        raise RuntimeError(f"shot {shot_id}: empty prompt")

    # Hunyuan-I2V is 5s only; ignore splitter's duration.
    duration_sec = 5.0

    # intake_img case: feed user's uploaded reference image to nano-banana-2/edit
    # so identity persists across shots. cr cases have upload_ref_bytes=None and
    # use plain text-to-image (no anchor — that's the baseline's "no-character-
    # consistency" property which the framework's KeyFrameAgent improves on).
    print(
        f"[baseline] [{idx}] {shot_id} keyframe "
        f"({'edit_image+upload_ref' if upload_ref_bytes else 'generate_image t2i'}): "
        f"'{prompt[:80]}...'"
    )
    t0 = time.time()
    if upload_ref_bytes:
        img_result = await img_svc.edit_image(
            reference_images=upload_ref_bytes,
            prompt=prompt,
        )
    else:
        img_result = await img_svc.generate_image(prompt=prompt)
    if not img_result.bytes:
        raise RuntimeError(f"shot {shot_id}: keyframe gen returned empty bytes")
    kf_path = out_dir / f"shot_{idx:03d}_{shot_id}_keyframe.png"
    kf_path.write_bytes(img_result.bytes)
    print(
        f"[baseline]   keyframe → {kf_path.name} "
        f"({len(img_result.bytes):,} bytes, {time.time()-t0:.1f}s)"
    )

    print(f"[baseline] [{idx}] {shot_id} hunyuan i2v ({duration_sec}s) ...")
    t1 = time.time()
    semantic_ctx = ShotSemanticContext(
        shot_id=shot_id, visual_goal=prompt, action_focus=""
    )
    vid_result = await vid_svc.generate_clip(
        shot_id=shot_id,
        keyframe_images=[img_result.bytes],
        semantic_context=semantic_ctx,
        duration_sec=duration_sec,
    )
    if not vid_result.bytes:
        raise RuntimeError(f"shot {shot_id}: hunyuan returned empty bytes")
    mp4_path = out_dir / f"shot_{idx:03d}_{shot_id}.mp4"
    mp4_path.write_bytes(vid_result.bytes)
    print(
        f"[baseline]   mp4 → {mp4_path.name} "
        f"({len(vid_result.bytes):,} bytes, {time.time()-t1:.1f}s)"
    )
    return mp4_path


# ──────────────────────────────────────────────────────────────────────
# ffmpeg concat
# ──────────────────────────────────────────────────────────────────────

def _ffmpeg_concat(shot_paths: list[Path], final_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")
    list_file = final_path.parent / "_concat_list.txt"
    with list_file.open("w") as fh:
        for p in shot_paths:
            fh.write(f"file '{p.absolute()}'\n")
    cmd_copy = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(final_path),
    ]
    proc = subprocess.run(cmd_copy, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0 or not final_path.is_file():
        # codec mismatch fallback: re-encode (always works)
        print("[baseline] concat -c copy failed, falling back to re-encode...")
        cmd_re = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", str(final_path),
        ]
        proc2 = subprocess.run(cmd_re, capture_output=True, text=True, timeout=600)
        if proc2.returncode != 0 or not final_path.is_file():
            tail = (proc2.stderr or "")[-500:]
            raise RuntimeError(f"ffmpeg concat (re-encode) also failed: {tail}")


# ──────────────────────────────────────────────────────────────────────
# Run one case end-to-end on one hunyuan endpoint
# ──────────────────────────────────────────────────────────────────────

def _category_subdir(category: str | None) -> str:
    """Map case category to baseline output subdir, mirroring 30_results layout.

    All baseline outputs live under ``baseline_30_results/`` to keep the
    sub-agents/ root tidy — sibling to 30_results/, easy to diff side by side.
    """
    base = "baseline_30_results"
    if category == "cr":
        return f"{base}/baseline_creative"
    if category == "intake_img":
        return f"{base}/baseline_intakeimage"
    return f"{base}/baseline_other"


async def run_one_case(
    case: dict,
    hunyuan_endpoint: str,
    splitter_system_prompt: str,
    *,
    infer_steps: int = 50,
    out_root: Path = _OUTPUT_BASE,
) -> dict:
    name = case["name"]
    category = case.get("category")
    user_goal = case["user_goal"]
    out_dir = out_root / _category_subdir(category) / name
    out_dir.mkdir(parents=True, exist_ok=True)

    # intake_img: feed user's upload as global reference for every keyframe gen.
    # Matches main framework's decision to use the upload as char_001 anchor —
    # without this, intake_img cases would be unfair (text-only baseline vs
    # image-conditioned framework). cr cases have no upload, baseline stays
    # text-only — which is the actual property the framework improves on.
    upload_ref_bytes: bytes | None = None
    upload_ref_path: str | None = None
    if category == "intake_img":
        candidate = _UPLOADS / f"{name}.png"
        if candidate.is_file():
            upload_ref_bytes = candidate.read_bytes()
            upload_ref_path = str(candidate.relative_to(_REPO))

    final_marker = out_dir / "00_done.json"
    case_t0 = time.time()
    log_lines: list[str] = []

    def lp(msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] [{name}] {msg}"
        print(line, flush=True)
        log_lines.append(line)

    try:
        lp(f"START hunyuan_endpoint={hunyuan_endpoint} infer_steps={infer_steps}")
        lp(f"  user_goal: {user_goal[:120]}{'...' if len(user_goal)>120 else ''}")
        if upload_ref_bytes:
            lp(f"  upload_ref: {upload_ref_path} ({len(upload_ref_bytes):,} bytes) "
               f"→ used as global keyframe reference (nano-banana-2/edit)")
        elif category == "intake_img":
            lp(f"  WARNING intake_img case but upload not found at {_UPLOADS}/{name}.png — "
               f"falling back to text-only keyframes")
        else:
            lp(f"  text-only keyframes (no upload, no char anchor — naive baseline)")
        (out_dir / "00_run_config.json").write_text(json.dumps({
            "case_name": name,
            "category": category,
            "user_goal": user_goal,
            "hunyuan_endpoint": hunyuan_endpoint,
            "infer_steps": infer_steps,
            "splitter_model": _SPLITTER_MODEL,
            "splitter_max_tokens": _SPLITTER_MAX_TOKENS,
            "splitter_prompt_file": str(_PROMPT_FILE.relative_to(_REPO)),
            "image_model": os.getenv("FAL_IMAGE_MODEL", "<unset>"),
            "upload_ref_used": upload_ref_path,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── Step 1: split brief ──────────────────────────────────────
        lp("STEP 1 splitter (gemini-2.5-flash)…")
        t0 = time.time()
        shots = await _split_brief_into_shots(user_goal, splitter_system_prompt)
        lp(f"  → {len(shots)} shots ({time.time()-t0:.1f}s)")
        (out_dir / "02_splitter_output.json").write_text(
            json.dumps({"shots": shots}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # ── Step 2: render each shot (keyframe + i2v) ────────────────
        # Within a case all shots share ONE hunyuan endpoint; server
        # PREDICT_LOCK serializes anyway, so client-side concurrency
        # buys little. Sem=4 caps fal/CF image-gen concurrency to be
        # safe (nano-banana-2 has its own rate limits).
        lp(f"STEP 2 render {len(shots)} shots (img→i2v sequential at server)…")
        img_svc = FalImageService()
        vid_svc = HunyuanVideoService(endpoint_url=hunyuan_endpoint, infer_steps=infer_steps)
        sem = asyncio.Semaphore(4)

        async def _gen_with_sem(shot: dict, idx: int) -> Path | Exception:
            async with sem:
                try:
                    return await _render_one_shot(
                        img_svc, vid_svc, shot, idx, out_dir,
                        upload_ref_bytes=upload_ref_bytes,
                    )
                except Exception as exc:
                    lp(f"  shot {idx} ({shot.get('shot_id','?')}) FAILED: "
                       f"{type(exc).__name__}: {str(exc)[:200]}")
                    return exc

        t_step2 = time.time()
        outcomes = await asyncio.gather(
            *[_gen_with_sem(shot, i) for i, shot in enumerate(shots, start=1)],
            return_exceptions=False,  # _gen_with_sem catches internally
        )
        shot_paths: list[Path] = [o for o in outcomes if isinstance(o, Path)]
        n_failed = len(outcomes) - len(shot_paths)
        lp(f"  → {len(shot_paths)}/{len(shots)} mp4 saved "
           f"({n_failed} failed) ({time.time()-t_step2:.1f}s wall)")
        if not shot_paths:
            raise RuntimeError(f"all {len(shots)} shots failed; no mp4 to concat")

        # ── Step 3: concat ───────────────────────────────────────────
        final_path = out_dir / "final.mp4"
        lp(f"STEP 3 ffmpeg concat → {final_path.name}")
        _ffmpeg_concat(shot_paths, final_path)
        final_size = final_path.stat().st_size

        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(final_path)],
            capture_output=True, text=True, timeout=10,
        )
        dur = (proc.stdout or "").strip()
        lp(f"  → {final_path.name} ({final_size:,} bytes, duration={dur}s)")

        elapsed = time.time() - case_t0
        final_marker.write_text(json.dumps({
            "case_name": name, "all_ok": True, "elapsed_sec": elapsed,
            "n_shots": len(shots), "final_mp4_bytes": final_size,
            "final_duration_sec": dur,
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2), encoding="utf-8")
        (out_dir / "00_run.log").write_text("\n".join(log_lines), encoding="utf-8")
        lp(f"DONE elapsed={elapsed:.1f}s")
        return {"name": name, "status": "DONE", "elapsed_sec": elapsed,
                "out_dir": str(out_dir)}

    except Exception as exc:
        elapsed = time.time() - case_t0
        lp(f"FATAL {type(exc).__name__}: {exc}")
        import traceback
        log_lines.append(traceback.format_exc())
        (out_dir / "00_run.log").write_text("\n".join(log_lines), encoding="utf-8")
        final_marker.write_text(json.dumps({
            "case_name": name, "all_ok": False, "elapsed_sec": elapsed,
            "error": f"{type(exc).__name__}: {exc}",
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2), encoding="utf-8")
        return {"name": name, "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_sec": elapsed, "out_dir": str(out_dir)}


# ──────────────────────────────────────────────────────────────────────
# Multi-case driver: distribute cases across endpoints
# ──────────────────────────────────────────────────────────────────────

async def run_many_cases(
    cases: list[dict],
    hunyuan_endpoints: list[str],
    splitter_system_prompt: str,
    *,
    infer_steps: int,
    out_root: Path,
) -> list[dict]:
    """Round-robin cases to endpoints; within an endpoint sequential, across parallel."""
    n_eps = len(hunyuan_endpoints)
    buckets: list[list[dict]] = [[] for _ in range(n_eps)]
    for i, c in enumerate(cases):
        buckets[i % n_eps].append(c)
    for i, b in enumerate(buckets):
        print(f"[baseline] bucket {i} (ep={hunyuan_endpoints[i]}) "
              f"n={len(b)}: {[c['name'] for c in b]}")

    async def worker(bucket: list[dict], ep: str) -> list[dict]:
        results = []
        for case in bucket:
            r = await run_one_case(
                case, ep, splitter_system_prompt,
                infer_steps=infer_steps, out_root=out_root,
            )
            results.append(r)
        return results

    all_results = await asyncio.gather(
        *[worker(buckets[i], hunyuan_endpoints[i]) for i in range(n_eps)],
        return_exceptions=True,
    )
    flat = []
    for r in all_results:
        if isinstance(r, Exception):
            flat.append({"status": "WORKER_EXCEPTION", "error": str(r)})
        else:
            flat.extend(r)
    return flat


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def _load_cases(target_categories: tuple[str, ...] = ("cr", "intake_img")) -> list[dict]:
    data = json.loads(_SELECTION.read_text(encoding="utf-8"))
    return [c for c in data if c.get("category") in target_categories]


async def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--case", help="single case name (for one-off run)")
    g.add_argument("--all", action="store_true",
                   help="run all 20 cr+intake_img cases distributed across endpoints")
    ap.add_argument("--hunyuan-endpoint",
                    help="single Hunyuan endpoint URL (--case mode)")
    ap.add_argument("--hunyuan-endpoints",
                    help="comma-separated Hunyuan endpoint URLs (--all mode)")
    ap.add_argument("--infer-steps", type=int, default=50)
    ap.add_argument("--out-root", default=str(_OUTPUT_BASE))
    args = ap.parse_args()

    splitter_system = _PROMPT_FILE.read_text(encoding="utf-8")
    out_root = Path(args.out_root)

    if args.case:
        if not args.hunyuan_endpoint:
            print("ERROR: --case requires --hunyuan-endpoint", file=sys.stderr)
            return 2
        cases = _load_cases()
        match = [c for c in cases if c["name"] == args.case]
        if not match:
            print(f"ERROR: case {args.case!r} not in selection.json (cr+intake_img)",
                  file=sys.stderr)
            return 2
        result = await run_one_case(
            match[0], args.hunyuan_endpoint.rstrip("/"),
            splitter_system,
            infer_steps=args.infer_steps, out_root=out_root,
        )
        summary_path = out_root / f"baseline_hunyuan_naive_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[baseline] DONE summary → {summary_path}")
        return 0 if result["status"] == "DONE" else 1

    # --all mode
    if not args.hunyuan_endpoints:
        print("ERROR: --all requires --hunyuan-endpoints (comma-separated)",
              file=sys.stderr)
        return 2
    endpoints = [e.strip().rstrip("/") for e in args.hunyuan_endpoints.split(",") if e.strip()]
    if not endpoints:
        print("ERROR: --hunyuan-endpoints parsed empty", file=sys.stderr)
        return 2
    cases = _load_cases()
    print(f"[baseline] running {len(cases)} cases across {len(endpoints)} endpoints")

    results = await run_many_cases(
        cases, endpoints, splitter_system,
        infer_steps=args.infer_steps, out_root=out_root,
    )

    summary_path = out_root / f"baseline_hunyuan_naive_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps({
        "n_cases": len(cases),
        "n_endpoints": len(endpoints),
        "results": results,
        "n_done": sum(1 for r in results if r.get("status") == "DONE"),
        "n_fail": sum(1 for r in results if r.get("status") != "DONE"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[baseline] DONE summary → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
