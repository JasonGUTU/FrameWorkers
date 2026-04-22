"""Replay the CompositorAgent demo purely offline from the checked-in bundle.

The bundle at ``process-flow-visualizer/test-assets/compositor_demo/`` is
the output of ``scripts/gen_compositor_demo.py`` (which does call live
fal.ai + OpenRouter APIs). This test does NOT call any live API — it
just takes the already-produced video clip + final audio mix + subtitle
SRT + the LLM's saved composition plan, feeds them straight into
``CompositorService.compose``, and checks that the FFmpeg mux / burn /
color-grade step still produces a valid MP4. That closes the loop so
the demo remains reproducible without spending more API credit.

Skipped when:
  - the bundle hasn't been generated yet (fresh checkout, no assets),
  - ffmpeg is not on PATH.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

import pytest


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_ROOT = _resolve_project_root()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


_DEMO = _ROOT / "process-flow-visualizer" / "test-assets" / "compositor_demo"
_VIDEO_DIR = _DEMO / "03_video"
_AUDIO_DIR = _DEMO / "07_audio_mix"
_SUBTITLE_DIR = _DEMO / "08_subtitle"
_COMPOSITOR_DIR = _DEMO / "09_compositor"


def _find_final_video() -> Path | None:
    if not _VIDEO_DIR.is_dir():
        return None
    # Prefer the concatenated final clip; fall back to any .mp4.
    for name in ("clip_final.mp4", "final.mp4"):
        p = _VIDEO_DIR / name
        if p.is_file():
            return p
    mp4s = sorted(_VIDEO_DIR.glob("*.mp4"))
    return mp4s[0] if mp4s else None


def _find_final_audio() -> Path | None:
    if not _AUDIO_DIR.is_dir():
        return None
    for name in ("aud_final.wav", "final_audio.wav", "output_final_audio.wav"):
        p = _AUDIO_DIR / name
        if p.is_file():
            return p
    wavs = sorted(_AUDIO_DIR.glob("*.wav"))
    return wavs[0] if wavs else None


def _find_srt() -> Path | None:
    if not _SUBTITLE_DIR.is_dir():
        return None
    p = _SUBTITLE_DIR / "subtitle.srt"
    return p if p.is_file() else None


def _find_compositor_plan() -> dict | None:
    pkg = _COMPOSITOR_DIR / "package.json"
    if not pkg.is_file():
        return None
    data = json.loads(pkg.read_text(encoding="utf-8"))
    return data.get("content", {}).get("plan", {}) or None


_BUNDLE_MISSING_REASON = None
if not _DEMO.is_dir():
    _BUNDLE_MISSING_REASON = f"demo bundle not generated: {_DEMO}"
elif shutil.which("ffmpeg") is None:
    _BUNDLE_MISSING_REASON = "ffmpeg not found on PATH"
else:
    # Skip unless the full replay inputs are present.
    _missing = [
        n for n, p in [
            ("final video clip", _find_final_video()),
            ("final audio mix",  _find_final_audio()),
            ("subtitle.srt",     _find_srt()),
            ("compositor plan",  _find_compositor_plan()),
        ] if p is None
    ]
    if _missing:
        _BUNDLE_MISSING_REASON = (
            "demo bundle incomplete (run scripts/gen_compositor_demo.py "
            f"first) — missing: {', '.join(_missing)}"
        )

pytestmark = pytest.mark.skipif(
    _BUNDLE_MISSING_REASON is not None,
    reason=_BUNDLE_MISSING_REASON or "",
)


def test_bundle_has_all_required_assets():
    assert _find_final_video() is not None, \
        "final concatenated video clip missing under 03_video/"
    assert _find_final_audio() is not None, \
        "final mixed audio missing under 07_audio_mix/"
    assert _find_srt() is not None, \
        "subtitle.srt missing under 08_subtitle/"
    assert _find_compositor_plan() is not None, \
        "compositor package.json plan missing under 09_compositor/"


def test_screenplay_seed_is_plan_a_compliant():
    """The seed screenplay must carry estimated_duration_seconds so Music
    and Ambience can read it — this is the Plan A contract."""
    seed = _DEMO / "01_screenplay_seed.json"
    data = json.loads(seed.read_text(encoding="utf-8"))
    scenes = data.get("content", {}).get("scenes", [])
    assert scenes, "seed has no scenes"
    for s in scenes:
        d = s.get("estimated_duration_seconds", 0.0)
        assert d > 0, f"scene {s.get('scene_id')} missing estimated_duration_seconds"


def test_compositor_materializer_replays_from_bundle(tmp_path):
    """Feed the already-produced video + audio + SRT + saved LLM plan
    straight into CompositorService.compose and verify it produces a
    non-trivial MP4.

    This is the purely deterministic half of the pipeline. It exercises
    the FFmpeg subtitle burn-in, eq color grading, and audio mux paths
    without depending on any remote API.
    """
    from inference.generation.compositor_service import CompositorService

    video_path = _find_final_video()
    audio_path = _find_final_audio()
    srt_path = _find_srt()
    plan = _find_compositor_plan()

    assert video_path and audio_path and srt_path and plan

    svc = CompositorService()
    out_bytes = asyncio.run(svc.compose(
        video_path=str(video_path),
        audio_path=str(audio_path),
        subtitle_srts=[srt_path.read_text(encoding="utf-8")],
        plan=plan,
    ))

    assert out_bytes, "CompositorService.compose returned empty bytes"
    # A successfully muxed MP4 with burnt subtitles is easily hundreds of
    # KB. Anything under ~10 KB is almost certainly a mock / fallback.
    assert len(out_bytes) > 10_000, (
        f"output mp4 is suspiciously small ({len(out_bytes)} bytes) — "
        "FFmpeg likely fell back to raw-copy of the input video"
    )

    # Double-check the mp4 magic header so we didn't get a text error
    # blob. MP4 box headers start at offset 4 with "ftyp".
    assert out_bytes[4:8] == b"ftyp", \
        f"output is not a valid mp4 (missing ftyp box): head={out_bytes[:16]!r}"

    # Save into tmp_path for manual inspection if this test is run with -s.
    out_path = tmp_path / "replay_final.mp4"
    out_path.write_bytes(out_bytes)
    print(f"\n[replay] wrote {len(out_bytes)} bytes to {out_path}")


def test_compositor_plan_mentions_the_four_shots():
    """Sanity — the LLM plan should cover our four-shot screenplay."""
    plan = _find_compositor_plan()
    transitions = plan.get("transitions", []) if plan else []
    # 4 shots => at most 3 transitions.
    assert 1 <= len(transitions) <= 3, (
        f"expected 1-3 transitions for a 4-shot screenplay, got {len(transitions)}"
    )
    shot_ids = {t.get("from_shot_id") for t in transitions} | {t.get("to_shot_id") for t in transitions}
    assert "sh_001" in shot_ids or "sh_002" in shot_ids, \
        "transitions reference unexpected shot_ids"
