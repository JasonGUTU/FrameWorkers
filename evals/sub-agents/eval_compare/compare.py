#!/usr/bin/env python3
"""Side-by-side comparison: framework e2e mp4 vs B3-naive Kling baseline mp4.

Runs purely with ffprobe / ffmpeg + an optional Gemini-3 vision judge —
no ML dependencies required (CLIP / face-rec) so the script works in
the bare frameworkers conda env.

Metrics computed on each mp4:
  - total_duration_sec       (ffprobe)
  - resolution               (ffprobe; ``WxH`` string)
  - has_audio_track          (ffprobe; bool)
  - audio_lufs_integrated    (ffmpeg loudnorm pass-1 analysis; -∞ when silent)
  - audio_lufs_range         (ffmpeg loudnorm; LRA, dB)
  - audio_true_peak_db       (ffmpeg loudnorm; max true peak)
  - shot_segment_count       (estimated from metadata/dir; best-effort)
  - filesize_bytes
  - subtitle_burnin_present  (Gemini-3 vision check on 1 sampled frame; only
                              when --use-llm-judge is passed; otherwise None)

Optional Gemini judge (--use-llm-judge):
  - character_consistency_score  : 0..10, "do all sampled frames depict the
                                   same protagonist?"  (1 LLM call per video)

Usage::

    python compare.py \\
        --framework-mp4 path/to/framework_final.mp4 \\
        --baseline-mp4  path/to/baseline_final.mp4 \\
        --case cr_001 \\
        --out-dir /home/zhendong_li/FrameWorkers/evals/sub-agents/compare_cr_001/

Writes ``comparison_report.json`` and ``comparison_report.md`` under
``--out-dir``.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")


# ── Basic ffprobe ────────────────────────────────────────────────────


def _ffprobe_field(mp4_path: Path, *args: str) -> str:
    cmd = ["ffprobe", "-v", "error", *args, str(mp4_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return (proc.stdout or "").strip()


def duration_sec(mp4_path: Path) -> float | None:
    out = _ffprobe_field(
        mp4_path,
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
    )
    try:
        return float(out)
    except ValueError:
        return None


def resolution(mp4_path: Path) -> str | None:
    out = _ffprobe_field(
        mp4_path,
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
    )
    parts = out.replace(",", "x").strip()
    return parts or None


def has_audio_track(mp4_path: Path) -> bool:
    out = _ffprobe_field(
        mp4_path,
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
    )
    return "audio" in out


def filesize_bytes(mp4_path: Path) -> int:
    return mp4_path.stat().st_size


# ── Audio LUFS via ffmpeg loudnorm pass-1 ───────────────────────────


_LUFS_FIELDS = ("input_i", "input_lra", "input_tp", "input_thresh")


def measure_lufs(mp4_path: Path) -> dict[str, float | None]:
    """Run ffmpeg loudnorm pass-1 in print_format=json and parse the JSON."""
    if not has_audio_track(mp4_path):
        return {k: None for k in _LUFS_FIELDS}
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats",
        "-i", str(mp4_path),
        "-af", "loudnorm=I=-23:LRA=11:TP=-1.5:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    err = proc.stderr or ""
    # Loudnorm prints a JSON block at the end of stderr.
    match = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.DOTALL)
    if not match:
        return {k: None for k in _LUFS_FIELDS}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {k: None for k in _LUFS_FIELDS}
    out: dict[str, float | None] = {}
    for f in _LUFS_FIELDS:
        v = data.get(f)
        try:
            out[f] = float(v) if v not in (None, "", "-inf") else None
        except (TypeError, ValueError):
            out[f] = None
    return out


# ── Shot-segment count heuristic ────────────────────────────────────


def shot_segment_count(mp4_dir: Path) -> int | None:
    """Count shot mp4 siblings (baseline) or shot_segments[] in JSON manifest
    (framework). Best-effort: returns None when neither signal is present.
    """
    # Baseline: shot_NNN_*.mp4 siblings
    siblings = list(mp4_dir.glob("shot_*.mp4"))
    if siblings:
        return len(siblings)
    # Framework: look for the splitter_output (baseline only) OR for the
    # video_package JSON with shot_segments under workspace tree.
    for candidate in mp4_dir.glob("**/VideoAgent/*.json"):
        try:
            d = json.loads(candidate.read_text())
            scenes = d.get("content", {}).get("scenes", []) or []
            n = sum(len(s.get("shot_segments", []) or []) for s in scenes)
            if n > 0:
                return n
        except Exception:
            continue
    return None


# ── Optional Gemini-3 vision judge ──────────────────────────────────


def _extract_frames(
    mp4_path: Path, n: int, out_dir: Path
) -> list[Path]:
    dur = duration_sec(mp4_path) or 0
    if dur <= 0:
        return []
    epsilon = min(0.5, dur * 0.05)
    if n == 1:
        timestamps = [dur / 2.0]
    else:
        step = (dur - 2 * epsilon) / (n - 1)
        timestamps = [epsilon + i * step for i in range(n)]
    out: list[Path] = []
    for i, ts in enumerate(timestamps, start=1):
        out_path = out_dir / f"frame_{i:03d}.png"
        proc = subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", str(mp4_path),
             "-vframes", "1", "-q:v", "2", str(out_path)],
            capture_output=True, check=False, text=True, timeout=30,
        )
        if proc.returncode == 0 and out_path.is_file():
            out.append(out_path)
    return out


_JUDGE_SYSTEM = (
    "You evaluate whether sampled frames from a SINGLE video depict the "
    "SAME protagonist with consistent appearance (face, hair, costume, "
    "body) across all frames. Score 0-10 (0=every frame is a different "
    "person, 10=identical protagonist throughout). Also detect if "
    "subtitle text is burned into the bottom portion of any frame.\n\n"
    "Output strict JSON: {\"character_consistency_score\": <int 0-10>, "
    "\"reasoning\": \"<one sentence>\", \"subtitle_burnin_present\": <bool>}"
)


async def llm_judge(
    mp4_path: Path, n_frames: int = 6, model: str = "gemini-3-pro-preview"
) -> dict[str, Any]:
    from inference.clients import LLMClient  # local import to keep optional

    with tempfile.TemporaryDirectory(prefix="fw_judge_") as tmp:
        frames = _extract_frames(mp4_path, n_frames, Path(tmp))
        if not frames:
            return {"character_consistency_score": None,
                    "reasoning": "could not extract frames",
                    "subtitle_burnin_present": None}
        media = [{"type": "image", "path": str(p)} for p in frames]
        client = LLMClient()
        result = await client.chat_json(
            system_prompt=_JUDGE_SYSTEM,
            user_prompt=(
                f"Sampled {len(frames)} evenly-spaced frames from one video. "
                "Score character consistency and detect burnt-in subtitles."
            ),
            model=model,
            max_tokens=32768,
            media_attachments=media,
        )
        return result if isinstance(result, dict) else {
            "character_consistency_score": None,
            "reasoning": f"unexpected reply: {result}",
            "subtitle_burnin_present": None,
        }


# ── Per-mp4 collector + report writer ──────────────────────────────


def metrics_for_mp4(mp4_path: Path, hint_dir: Path | None = None) -> dict:
    out: dict[str, Any] = {
        "path": str(mp4_path),
        "duration_sec": duration_sec(mp4_path),
        "resolution": resolution(mp4_path),
        "has_audio_track": has_audio_track(mp4_path),
        "filesize_bytes": filesize_bytes(mp4_path),
    }
    out["audio_lufs"] = measure_lufs(mp4_path)
    if hint_dir is not None:
        out["shot_segment_count"] = shot_segment_count(hint_dir)
    return out


def render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Comparison report — case `{report['case']}`")
    lines.append("")
    lines.append(f"- generated: `{report['timestamp']}`")
    lines.append("")
    lines.append("## Per-mp4 metrics")
    lines.append("")
    lines.append("| metric | framework | baseline |")
    lines.append("|---|---|---|")
    f = report["framework"]
    b = report["baseline"]

    def _fmt(v: Any, unit: str = "") -> str:
        if v is None:
            return "—"
        if isinstance(v, float):
            return f"{v:.2f}{unit}"
        return f"{v}{unit}"

    rows: list[tuple[str, Any, Any]] = [
        ("duration_sec",        f.get("duration_sec"),    b.get("duration_sec")),
        ("resolution",          f.get("resolution"),      b.get("resolution")),
        ("has_audio_track",     f.get("has_audio_track"), b.get("has_audio_track")),
        ("filesize_bytes",      f.get("filesize_bytes"),  b.get("filesize_bytes")),
        ("shot_segment_count",  f.get("shot_segment_count"), b.get("shot_segment_count")),
        ("audio_lufs.input_i (LUFS)",  f.get("audio_lufs", {}).get("input_i"), b.get("audio_lufs", {}).get("input_i")),
        ("audio_lufs.input_lra (LRA)", f.get("audio_lufs", {}).get("input_lra"), b.get("audio_lufs", {}).get("input_lra")),
        ("audio_lufs.input_tp (dBTP)", f.get("audio_lufs", {}).get("input_tp"), b.get("audio_lufs", {}).get("input_tp")),
    ]
    for name, fv, bv in rows:
        lines.append(f"| {name} | {_fmt(fv)} | {_fmt(bv)} |")

    if "judge" in report:
        lines.append("")
        lines.append("## Gemini-3 vision judge (per video)")
        lines.append("")
        lines.append("| metric | framework | baseline |")
        lines.append("|---|---|---|")
        jf = report["judge"]["framework"]
        jb = report["judge"]["baseline"]
        lines.append(f"| character_consistency_score (0-10) | {_fmt(jf.get('character_consistency_score'))} | {_fmt(jb.get('character_consistency_score'))} |")
        lines.append(f"| subtitle_burnin_present | {_fmt(jf.get('subtitle_burnin_present'))} | {_fmt(jb.get('subtitle_burnin_present'))} |")
        lines.append("")
        lines.append("### Judge reasoning")
        lines.append(f"- **framework**: {jf.get('reasoning','—')}")
        lines.append(f"- **baseline**:  {jb.get('reasoning','—')}")

    return "\n".join(lines) + "\n"


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--framework-mp4", required=True)
    ap.add_argument("--baseline-mp4", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--use-llm-judge", action="store_true")
    args = ap.parse_args()

    fw = Path(args.framework_mp4)
    bl = Path(args.baseline_mp4)
    if not fw.is_file():
        print(f"FATAL: framework mp4 not found: {fw}")
        return 2
    if not bl.is_file():
        print(f"FATAL: baseline mp4 not found: {bl}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[compare] case={args.case}")
    print(f"[compare] framework: {fw}")
    print(f"[compare] baseline:  {bl}")
    print()

    print("[compare] computing per-mp4 metrics (ffprobe + ffmpeg loudnorm)...")
    fw_metrics = metrics_for_mp4(fw, hint_dir=fw.parent)
    bl_metrics = metrics_for_mp4(bl, hint_dir=bl.parent)

    report: dict[str, Any] = {
        "case": args.case,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "framework": fw_metrics,
        "baseline": bl_metrics,
    }

    if args.use_llm_judge:
        print("[compare] running Gemini-3 vision judge on each mp4 (~$0.05)...")
        judge_fw = await llm_judge(fw)
        judge_bl = await llm_judge(bl)
        report["judge"] = {"framework": judge_fw, "baseline": judge_bl}

    (out_dir / "comparison_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    md = render_md(report)
    (out_dir / "comparison_report.md").write_text(md, encoding="utf-8")
    print()
    print("=== comparison_report.md ===")
    print(md)
    print(f"[compare] DONE → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
