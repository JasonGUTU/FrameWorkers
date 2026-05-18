#!/usr/bin/env python3
"""B3-naive HunyuanVideo-I2V baseline runner (v2 — sync curl + multiprocessing).

v1 (run_hunyuan_baseline_naive.py) used httpx.AsyncClient + asyncio.gather +
asyncio.Semaphore per case. Hung in production: server-side ``[i2v] done`` events
fired but client-side ``await self.http.post(...)`` never returned, leaving 0
mp4 on disk after 67 min. py-spy showed event loop idle in select; root cause
not pinned but suspected httpx response-stream / keep-alive interaction.

v2 strategy — strip async entirely:
  * Outer driver = ``mp.Process`` per endpoint (one OS process per hunyuan
    endpoint). No shared state, no GIL, no asyncio.
  * Worker = sequential loop over its case bucket.
  * Per-shot inside worker:
      - keyframe: ``fal_client.subscribe`` SYNC → png url → curl download.
      - hunyuan: ``subprocess.run("curl ... /i2v")`` → JSON resp → decode.
  * Each shot writes png + mp4 IMMEDIATELY to disk before moving on. If a shot
    fails (safety filter / timeout / bad response), log + continue with next
    shot. ffmpeg concat at end skips failed shots.
  * 00_done.json marker written at case end (with all_ok / n_succeeded).

Output: ``evals/sub-agents/baseline_30_results/{baseline_creative,baseline_intakeimage}/<case>/``
matching 30_results layout.

Usage:
    python run_hunyuan_baseline_naive_v2.py \
        --hunyuan-endpoints "http://sof1-h200-3:9200,http://sof1-h200-3:9201,..." \
        --infer-steps 50
"""

from __future__ import annotations

import argparse
import base64
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_REPO = Path("/home/zhendong_li/FrameWorkers")
sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")

_SELECTION = _REPO / "evals/sub-agents/e2e_30/selection.json"
_UPLOADS = _REPO / "evals/sub-agents/e2e_30/uploads"
_PROMPT_FILE = (
    _REPO / "evals/sub-agents/baseline_hunyuan_naive_prompts/splitter_system_prompt.txt"
)
_OUTPUT_BASE = _REPO / "evals/sub-agents/baseline_30_results"

_SPLITTER_MODEL = "gemini-2.5-flash"
_SPLITTER_MAX_TOKENS = 65536


def _category_subdir(category: str | None) -> str:
    if category == "cr":
        return "baseline_creative"
    if category == "intake_img":
        return "baseline_intakeimage"
    return "baseline_other"


# ──────────────────────────────────────────────────────────────────────
# Splitter (re-uses framework's LLMClient via asyncio.run wrapping)
# ──────────────────────────────────────────────────────────────────────

def call_splitter(user_goal: str, system_prompt: str) -> list[dict]:
    """Sync wrapper around async LLMClient.chat_json. Single call per case so
    the asyncio.run cost (event loop spin-up) is acceptable."""
    import asyncio
    from inference.clients import LLMClient

    async def _do() -> dict:
        client = LLMClient()
        return await client.chat_json(
            system_prompt=system_prompt,
            user_prompt=f"Brief:\n{user_goal}\n\nSplit into 7-10 shot prompts.",
            model=_SPLITTER_MODEL,
            max_tokens=_SPLITTER_MAX_TOKENS,
        )

    result = asyncio.run(_do())
    if not isinstance(result, dict):
        raise RuntimeError(f"splitter returned non-dict: {type(result).__name__}")
    shots = result.get("shots") or []
    if not isinstance(shots, list) or not (7 <= len(shots) <= 10):
        n = len(shots) if isinstance(shots, list) else "non-list"
        raise RuntimeError(f"splitter emitted {n} shots, expected 7-10")
    return shots


# ──────────────────────────────────────────────────────────────────────
# Keyframe gen via fal_client (SYNC)
# ──────────────────────────────────────────────────────────────────────

def gen_keyframe(prompt: str, upload_ref_bytes: bytes | None) -> bytes:
    """Sync fal_client image gen → png bytes."""
    import fal_client

    api_key = os.getenv("FAL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FAL_API_KEY not set")
    os.environ["FAL_KEY"] = api_key
    image_model = os.getenv("FAL_IMAGE_MODEL", "fal-ai/nano-banana-2").strip().rstrip("/")

    if upload_ref_bytes:
        # nano-banana-2/edit: text + reference images
        ref_b64 = base64.b64encode(upload_ref_bytes).decode("ascii")
        result = fal_client.subscribe(
            "fal-ai/nano-banana-2/edit",
            arguments={
                "prompt": prompt,
                "image_urls": [f"data:image/png;base64,{ref_b64}"],
            },
        )
    else:
        result = fal_client.subscribe(
            image_model,
            arguments={"prompt": prompt},
        )

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"fal returned no images: keys={list(result.keys())}")
    img_url = images[0].get("url")
    if not img_url:
        raise RuntimeError(f"fal image entry missing url: {images[0]}")

    proc = subprocess.run(
        ["curl", "-sS", "--max-time", "60", "-L", img_url],
        capture_output=True, timeout=120,
    )
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(
            f"curl image download failed: rc={proc.returncode} "
            f"stderr={proc.stderr.decode('utf-8','replace')[:200]}"
        )
    return proc.stdout


# ──────────────────────────────────────────────────────────────────────
# Hunyuan i2v via curl subprocess (SYNC, BYPASS httpx)
# ──────────────────────────────────────────────────────────────────────

def gen_hunyuan_video(
    prompt: str,
    keyframe_bytes: bytes,
    hunyuan_endpoint: str,
    infer_steps: int,
    timeout_sec: int = 1800,
) -> bytes:
    """Sync curl POST /i2v → mp4 bytes. timeout_sec is curl --max-time wall cap."""
    body = {
        "prompt": prompt,
        "image_b64": base64.b64encode(keyframe_bytes).decode("ascii"),
        "duration_sec": 5.0,
        "seed": 0,
        "negative_prompt": "",
        "infer_steps": infer_steps,
    }

    body_fd, body_path = tempfile.mkstemp(suffix=".json", prefix="hy_body_")
    resp_fd, resp_path = tempfile.mkstemp(suffix=".json", prefix="hy_resp_")
    try:
        os.close(body_fd)
        os.close(resp_fd)
        with open(body_path, "w") as f:
            json.dump(body, f)

        proc = subprocess.run(
            [
                "curl", "-sS",
                "--max-time", str(timeout_sec),
                "-H", "Content-Type: application/json",
                "--data-binary", f"@{body_path}",
                f"{hunyuan_endpoint}/i2v",
                "-o", resp_path,
            ],
            capture_output=True, text=True, timeout=timeout_sec + 60,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"curl /i2v failed: rc={proc.returncode} stderr={proc.stderr[:300]}"
            )

        with open(resp_path) as f:
            data = json.load(f)
        if "video_b64" not in data:
            raise RuntimeError(
                f"hunyuan response missing video_b64: keys={list(data.keys())}"
            )
        return base64.b64decode(data["video_b64"])
    finally:
        for p in (body_path, resp_path):
            try: os.unlink(p)
            except Exception: pass


# ──────────────────────────────────────────────────────────────────────
# ffmpeg concat
# ──────────────────────────────────────────────────────────────────────

def ffmpeg_concat(shot_paths: list[Path], final_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found")
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
        cmd_re = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", str(final_path),
        ]
        proc2 = subprocess.run(cmd_re, capture_output=True, text=True, timeout=600)
        if proc2.returncode != 0 or not final_path.is_file():
            raise RuntimeError(f"ffmpeg concat failed: {proc2.stderr[-500:]}")


# ──────────────────────────────────────────────────────────────────────
# Per-case sync runner
# ──────────────────────────────────────────────────────────────────────

def run_one_case(case: dict, hunyuan_endpoint: str, infer_steps: int) -> dict:
    name = case["name"]
    category = case.get("category")
    user_goal = case["user_goal"]

    out_dir = _OUTPUT_BASE / _category_subdir(category) / name
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / "00_run.log"
    log_f = open(log_path, "w")

    def lp(msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] [{name}] {msg}"
        log_f.write(line + "\n"); log_f.flush()
        print(line, flush=True)

    case_t0 = time.time()

    # intake_img: load upload as global keyframe ref
    upload_ref_bytes: bytes | None = None
    upload_ref_path: str | None = None
    if category == "intake_img":
        upload_path = _UPLOADS / f"{name}.png"
        if upload_path.is_file():
            upload_ref_bytes = upload_path.read_bytes()
            upload_ref_path = str(upload_path.relative_to(_REPO))

    final_marker = out_dir / "00_done.json"

    try:
        lp(f"START hunyuan={hunyuan_endpoint} infer_steps={infer_steps}")
        if upload_ref_bytes:
            lp(f"  upload_ref={upload_ref_path} ({len(upload_ref_bytes):,}B) → "
               "edit_image with global anchor")
        else:
            lp(f"  text-only keyframes (cr case, no anchor — naive baseline)")

        (out_dir / "00_run_config.json").write_text(json.dumps({
            "case_name": name,
            "category": category,
            "user_goal": user_goal,
            "hunyuan_endpoint": hunyuan_endpoint,
            "infer_steps": infer_steps,
            "splitter_model": _SPLITTER_MODEL,
            "image_model": os.getenv("FAL_IMAGE_MODEL", "fal-ai/nano-banana-2"),
            "upload_ref_used": upload_ref_path,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "driver_version": "v2_sync_curl_mp",
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── Step 1: splitter ────────────────────────────────────────
        lp(f"STEP 1 splitter ({_SPLITTER_MODEL})...")
        t0 = time.time()
        splitter_system = _PROMPT_FILE.read_text(encoding="utf-8")
        shots = call_splitter(user_goal, splitter_system)
        lp(f"  → {len(shots)} shots ({time.time()-t0:.1f}s)")
        (out_dir / "02_splitter_output.json").write_text(
            json.dumps({"shots": shots}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # ── Step 2: render shots SEQUENTIALLY ──────────────────────
        # Server PREDICT_LOCK serializes anyway, so within-case parallelism buys
        # nothing. Sequential = trivially debuggable + each shot persists before
        # the next starts.
        lp(f"STEP 2 render {len(shots)} shots (sequential)...")
        shot_paths: list[Path] = []
        per_shot_records: list[dict] = []
        for i, shot in enumerate(shots, start=1):
            shot_id = shot.get("shot_id") or f"sh_{i:03d}"
            prompt = (shot.get("prompt") or "").strip()
            shot_t0 = time.time()
            shot_record = {"idx": i, "shot_id": shot_id, "prompt": prompt[:200]}
            if not prompt:
                lp(f"  shot {i} ({shot_id}) SKIP empty prompt")
                shot_record["status"] = "SKIP_EMPTY_PROMPT"
                per_shot_records.append(shot_record)
                continue
            try:
                # 2a: keyframe
                lp(f"  shot {i}/{len(shots)} ({shot_id}) keyframe gen "
                   f"({'edit_image+ref' if upload_ref_bytes else 't2i'})...")
                t_kf = time.time()
                kf_bytes = gen_keyframe(prompt, upload_ref_bytes)
                kf_path = out_dir / f"shot_{i:03d}_{shot_id}_keyframe.png"
                kf_path.write_bytes(kf_bytes)
                lp(f"    keyframe → {kf_path.name} ({len(kf_bytes):,}B, "
                   f"{time.time()-t_kf:.1f}s)")

                # 2b: hunyuan i2v
                lp(f"  shot {i}/{len(shots)} ({shot_id}) hunyuan i2v...")
                t_hy = time.time()
                mp4_bytes = gen_hunyuan_video(
                    prompt, kf_bytes, hunyuan_endpoint, infer_steps
                )
                mp4_path = out_dir / f"shot_{i:03d}_{shot_id}.mp4"
                mp4_path.write_bytes(mp4_bytes)
                lp(f"    mp4 → {mp4_path.name} ({len(mp4_bytes):,}B, "
                   f"{time.time()-t_hy:.1f}s)")
                shot_paths.append(mp4_path)
                shot_record["status"] = "OK"
                shot_record["keyframe_bytes"] = len(kf_bytes)
                shot_record["mp4_bytes"] = len(mp4_bytes)
                shot_record["elapsed_sec"] = time.time() - shot_t0
            except Exception as exc:
                err = f"{type(exc).__name__}: {str(exc)[:300]}"
                lp(f"  shot {i} ({shot_id}) FAILED: {err}")
                shot_record["status"] = "FAIL"
                shot_record["error"] = err
                shot_record["elapsed_sec"] = time.time() - shot_t0
            per_shot_records.append(shot_record)

        # save per-shot record
        (out_dir / "03_shot_results.json").write_text(
            json.dumps(per_shot_records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # ── Step 3: ffmpeg concat ────────────────────────────────────
        final_path: Path | None = None
        if shot_paths:
            try:
                lp(f"STEP 3 ffmpeg concat ({len(shot_paths)} mp4s)...")
                final_path = out_dir / "final.mp4"
                ffmpeg_concat(shot_paths, final_path)
                size = final_path.stat().st_size
                lp(f"  → {final_path.name} ({size:,}B)")
            except Exception as exc:
                lp(f"  ffmpeg concat FAILED: {type(exc).__name__}: {str(exc)[:300]}")
                final_path = None
        else:
            lp(f"STEP 3 SKIP — 0 shots succeeded")

        elapsed = time.time() - case_t0
        n_ok = sum(1 for r in per_shot_records if r["status"] == "OK")
        n_total = len(shots)
        all_ok = (n_ok == n_total) and (final_path is not None)
        final_marker.write_text(json.dumps({
            "case_name": name,
            "all_ok": all_ok,
            "elapsed_sec": elapsed,
            "n_shots": n_total,
            "n_succeeded": n_ok,
            "final_mp4": str(final_path.relative_to(_REPO)) if final_path else None,
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        lp(f"DONE all_ok={all_ok} ok={n_ok}/{n_total} elapsed={elapsed:.1f}s")
        return {
            "name": name,
            "status": "DONE" if all_ok else "PARTIAL",
            "n_succeeded": n_ok,
            "n_shots": n_total,
            "elapsed_sec": elapsed,
        }

    except Exception as exc:
        elapsed = time.time() - case_t0
        err = f"{type(exc).__name__}: {exc}"
        lp(f"FATAL {err}")
        log_f.write(traceback.format_exc()); log_f.flush()
        final_marker.write_text(json.dumps({
            "case_name": name,
            "all_ok": False,
            "elapsed_sec": elapsed,
            "error": err,
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"name": name, "status": "FATAL", "error": err, "elapsed_sec": elapsed}
    finally:
        log_f.close()


# ──────────────────────────────────────────────────────────────────────
# Per-endpoint worker (sequential bucket)
# ──────────────────────────────────────────────────────────────────────

def worker_loop(bucket: list[dict], hunyuan_endpoint: str, infer_steps: int,
                result_queue: mp.Queue) -> None:
    """One OS process per endpoint. Process its case bucket sequentially."""
    pid = os.getpid()
    print(f"[v2 worker pid={pid}] starting bucket={[c['name'] for c in bucket]} "
          f"on {hunyuan_endpoint}", flush=True)
    for case in bucket:
        result = run_one_case(case, hunyuan_endpoint, infer_steps)
        result_queue.put(result)
    print(f"[v2 worker pid={pid}] DONE bucket", flush=True)


# ──────────────────────────────────────────────────────────────────────
# Driver entry
# ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hunyuan-endpoints", required=True,
                    help="comma-separated hunyuan endpoint URLs (one per worker)")
    ap.add_argument("--infer-steps", type=int, default=50)
    ap.add_argument("--case-names", default=None,
                    help="comma-separated subset of case names (default = all 20)")
    args = ap.parse_args()

    endpoints = [e.strip().rstrip("/") for e in args.hunyuan_endpoints.split(",") if e.strip()]
    if not endpoints:
        print("ERROR: --hunyuan-endpoints empty", file=sys.stderr)
        return 2

    cases = json.loads(_SELECTION.read_text(encoding="utf-8"))
    cases = [c for c in cases if c.get("category") in ("cr", "intake_img")]
    if args.case_names:
        wanted = set(n.strip() for n in args.case_names.split(",") if n.strip())
        cases = [c for c in cases if c["name"] in wanted]

    print(f"[v2] running {len(cases)} cases across {len(endpoints)} endpoints")
    print(f"[v2] output base: {_OUTPUT_BASE}")

    # Bucket per endpoint (round-robin), each endpoint = one OS process worker
    buckets: list[list[dict]] = [[] for _ in range(len(endpoints))]
    for i, c in enumerate(cases):
        buckets[i % len(endpoints)].append(c)

    print(f"[v2] case bucket per endpoint:")
    for i, b in enumerate(buckets):
        print(f"  {endpoints[i]}: n={len(b)} cases={[c['name'] for c in b]}")

    result_queue: mp.Queue = mp.Queue()
    procs = []
    for i, bucket in enumerate(buckets):
        p = mp.Process(
            target=worker_loop,
            args=(bucket, endpoints[i], args.infer_steps, result_queue),
        )
        p.start()
        procs.append(p)

    print(f"[v2] {len(procs)} workers spawned, waiting...")

    results = []
    expected = sum(len(b) for b in buckets)
    while len(results) < expected:
        try:
            r = result_queue.get(timeout=300)
            results.append(r)
            print(f"[v2] {len(results)}/{expected} {r.get('name')} → {r.get('status')}")
        except Exception:
            # check if any worker died
            dead = [p for p in procs if not p.is_alive()]
            if len(dead) == len(procs):
                print(f"[v2] all workers dead, collected {len(results)}/{expected}")
                break

    for p in procs:
        p.join(timeout=10)
        if p.is_alive():
            p.terminate()

    summary_path = _OUTPUT_BASE / f"00_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps({
        "started_n_cases": expected,
        "n_endpoints": len(endpoints),
        "results": results,
        "n_done": sum(1 for r in results if r.get("status") == "DONE"),
        "n_partial": sum(1 for r in results if r.get("status") == "PARTIAL"),
        "n_fatal": sum(1 for r in results if r.get("status") == "FATAL"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[v2] DONE → summary {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
