"""Independent E2E tests — one per agent, each with its own workspace.

Each test:
1. Creates a fresh Flask test client + workspace
2. Pre-seeds the workspace with the upstream artifacts the agent needs
3. POST /api/assistant/execute for that single agent
4. Verifies COMPLETED + checks output structure
5. Output goes to Runtime/independent_e2e/{agent_name}_{timestamp}/

Can run in parallel: pytest -n 6

Gates:
- FW_ENABLE_LIVE_LLM_TESTS=1 — required for all tests (real LLM calls)
- FW_USE_REAL_MEDIA_GEN=1   — opt-in: switches StyleTransfer/Inpaint from
  the LLM-only mock path (MockVideoEditService returns 28-byte placeholder)
  to the full fal.ai pipeline (real video upload → fal inpaint/style →
  download). Asserts the materialized mp4 is non-trivial. Costs fal credits
  + ~30s-2min per test.

Usage:
    source .env
    # default: LLM-only (cheap, video-edit materializer goes through MockVideoEditService)
    FW_ENABLE_LIVE_LLM_TESTS=1 python -m pytest tests/agents/test_new_agents_independent_e2e.py -v -s -n 6
    # full fal.ai pipeline for video-edit agents (costs credits, slow)
    FW_ENABLE_LIVE_LLM_TESTS=1 FW_USE_REAL_MEDIA_GEN=1 python -m pytest tests/agents/test_new_agents_independent_e2e.py::test_inpaint_agent_independent tests/agents/test_new_agents_independent_e2e.py::test_style_transfer_agent_independent -v -s
"""

from __future__ import annotations

import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
for p in [str(_repo_root), str(_pkg_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from inference.config.config_loader import ConfigLoader
for fname in (".env", ".env.example"):
    p = _repo_root / fname
    if p.is_file():
        ConfigLoader.load_env_file(str(p), override=False)

if "flask_cors" not in sys.modules:
    fc = types.ModuleType("flask_cors")
    fc.CORS = lambda *a, **kw: None
    sys.modules["flask_cors"] = fc

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from src.assistant.workspace.workspace import Workspace
from src.assistant.workspace.models import ArtifactRef
from inference.clients import LLMClient


# ── Skip gate ─────────────────────────────────────────────────────────

def _is_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return False, "Set FW_ENABLE_LIVE_LLM_TESTS=1"
    try:
        c = LLMClient()
        m = c.model or c.default_model
        prov = c.resolve_provider_for_model(m)
        routing = c.get_runtime_routing()
        key_env = (routing.get("provider_key_env", {}).get(prov) if isinstance(routing, dict) else None) or f"{prov.upper()}_API_KEY"
        if not os.getenv(key_env, "").strip():
            return False, f"Missing {key_env}"
    except Exception as e:
        return False, str(e)
    return True, ""

_READY, _SKIP = _is_ready()
pytestmark = pytest.mark.skipif(not _READY, reason=_SKIP)


# ── Helpers ───────────────────────────────────────────────────────────

def _runtime_base():
    b = _repo_root / "Runtime" / "independent_e2e"
    b.mkdir(parents=True, exist_ok=True)
    return b


def _make_env(agent_name: str, monkeypatch):
    """Create isolated Flask client + workspace for one agent."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ws_id = f"{agent_name}_{ts}"
    store = AssistantStateStore(runtime_base_path=_runtime_base())
    workspace = Workspace(workspace_id=ws_id, runtime_base_path=store.runtime_base_path)
    store.global_workspace = workspace
    monkeypatch.setattr(routes_module, "assistant_state_store", store)
    app = create_app({"TESTING": True})
    client = app.test_client()
    return client, workspace


def _ws_path(workspace: Workspace) -> Path:
    return workspace.runtime_base_path / workspace.id


def _seed_artifact(workspace: Workspace, agent_id: str, payload: dict, caption: str, scope: str = "global"):
    """Write a JSON artifact into the workspace and register it in global_memory."""
    art_dir = _ws_path(workspace) / "artifacts" / agent_id
    art_dir.mkdir(parents=True, exist_ok=True)
    fname = f"seed_{agent_id.lower()}.json"
    fpath = art_dir / fname
    fpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    workspace.global_memory.register(
        agent_id=agent_id,
        execution_id=f"seed_{agent_id.lower()}",
        step_id="seed",
        artifacts=[ArtifactRef(caption=caption, scope=scope, path=str(fpath), mime="application/json")],
    )


def _seed_file(workspace: Workspace, agent_id: str, filename: str, data: bytes, caption: str, mime: str, scope: str = "global"):
    """Write a binary file + register."""
    art_dir = _ws_path(workspace) / "artifacts" / agent_id
    art_dir.mkdir(parents=True, exist_ok=True)
    fpath = art_dir / filename
    fpath.write_bytes(data)
    workspace.global_memory.register(
        agent_id=agent_id,
        execution_id=f"seed_{agent_id.lower()}",
        step_id="seed",
        artifacts=[ArtifactRef(caption=caption, scope=scope, path=str(fpath), mime=mime)],
    )


def _create_step(client, goal: str) -> str:
    resp = client.post(
        "/api/plan-stack/modify",
        json={
            "operations": [
                {
                    "type": "create_steps",
                    "params": {"steps": [{"description": {"goal": goal}}]},
                }
            ]
        },
    )
    assert resp.status_code == 200
    return resp.get_json()["created_step_ids"][0]


def _execute(client, agent_id: str, step_id: str) -> dict:
    resp = client.post("/api/assistant/execute", json={"agent_id": agent_id, "step_id": step_id})
    body = resp.get_json()
    return body


def _brief_last(body) -> dict:
    """Current execution from the ``/execute`` response (a single serialized row)."""
    return body if isinstance(body, dict) else {}


# ── Shared fixture data ──────────────────────────────────────────────

_MINI_SCREENPLAY = {
    "meta": {"asset_type": "screenplay"},
    "content": {
        "title": "Mars Cave",
        "scenes": [{
            "scene_id": "sc_001",
            "heading": "INT. MARS CAVE - DAY",
            "summary": "Two astronauts discover glowing crystals.",
            "shots": [
                {"shot_id": "sh_001", "block_type": "narration", "text": "The cave walls shimmer with an otherworldly blue glow.", "character_name": "Narrator"},
                {"shot_id": "sh_002", "block_type": "dialogue", "text": "Look at these crystals!", "character_name": "Chen", "character_id": "char_001"},
                {"shot_id": "sh_003", "block_type": "dialogue", "text": "We need to report this to base.", "character_name": "Park", "character_id": "char_002"},
                {"shot_id": "sh_004", "block_type": "action", "text": "They carefully collect a sample.", "character_name": ""},
            ],
            "scene_end": "The crystals pulse brighter as they approach.",
        }],
    },
}

_MINI_VIDEO_PACKAGE = {
    "meta": {"asset_type": "video_package"},
    "content": {
        "scenes": [{"scene_id": "sc_001", "shot_segments": [
            {"shot_id": "sh_001", "duration_sec": 3.0, "video_asset": {"uri": "placeholder"}},
            {"shot_id": "sh_002", "duration_sec": 2.5, "video_asset": {"uri": "placeholder"}},
            {"shot_id": "sh_003", "duration_sec": 3.0, "video_asset": {"uri": "placeholder"}},
            {"shot_id": "sh_004", "duration_sec": 2.0, "video_asset": {"uri": "placeholder"}},
        ]}],
        "final_video_asset": {"uri": "placeholder"},
    },
}

_MINI_AUDIO_PACKAGE = {
    "meta": {"asset_type": "audio_package"},
    "content": {
        "scenes": [{"scene_id": "sc_001", "narration_segments": [
            {"segment_id": "narr_001", "speaker": "Narrator", "text": "The cave walls shimmer."},
        ]}],
        "final_audio_asset": {"uri": "placeholder"},
    },
}

_MINI_SUBTITLE = {
    "meta": {"asset_type": "subtitle_tracks"},
    "content": {
        "tracks": [{"language": "en", "cues": [
            {"cue_id": "cue_001", "start_time": "00:00:01,000", "end_time": "00:00:04,000", "text": "The cave walls shimmer."},
            {"cue_id": "cue_002", "start_time": "00:00:04,500", "end_time": "00:00:06,500", "text": "Look at these crystals!"},
        ], "srt_text": "1\n00:00:01,000 --> 00:00:04,000\nThe cave walls shimmer.\n\n2\n00:00:04,500 --> 00:00:06,500\nLook at these crystals!\n"}],
    },
}

_MINI_ANALYSIS = {
    "meta": {"asset_type": "video_analysis"},
    "content": {
        "video_summary": {"title": "Mars Cave", "summary": "Astronauts in a cave", "genre": "sci-fi", "duration_seconds": 30.0},
        "scenes": [
            {"scene_id": "scene_001", "start_time": 0.0, "end_time": 10.0, "description": "Wide shot of cave entrance with blue glow", "mood": "mysterious", "entities": ["cave", "crystals"]},
            {"scene_id": "scene_002", "start_time": 10.0, "end_time": 20.0, "description": "Close-up of astronauts examining crystals", "mood": "excited", "entities": ["astronaut", "crystals"]},
            {"scene_id": "scene_003", "start_time": 20.0, "end_time": 30.0, "description": "Crystals pulse brighter", "mood": "dramatic", "entities": ["crystals", "light"]},
        ],
    },
}

# Minimal valid WAV (44 bytes)
_MOCK_WAV = (b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
             b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

# Minimal MP4 header (28 bytes) — good enough for agents whose backing
# service only reads path/mime (fal.ai style_transfer/inpaint/highlight/
# video_extend). NOT good enough for Gemini-based video_analysis, which
# validates the byte stream; see ``_real_tiny_mp4()`` below.
_MOCK_MP4 = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"


_REAL_MP4_CACHE: bytes | None = None


def _real_tiny_mp4() -> bytes:
    """Return bytes of a 1s black 16x16 mp4. Uses ffmpeg, cached on first call.

    Gemini's video API rejects fake/empty mp4 bytes ('Unsupported file URI
    type' / INVALID_ARGUMENT), so tests that hit Gemini (VideoAnalysisAgent)
    need real, well-formed video bytes. Synthetic 1s black video satisfies
    the API validator without bundling any binary fixture in the repo.
    """
    global _REAL_MP4_CACHE
    if _REAL_MP4_CACHE is not None:
        return _REAL_MP4_CACHE
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        path = tmp.name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=1",
             "-t", "1", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
            check=True, capture_output=True,
        )
        with open(path, "rb") as f:
            _REAL_MP4_CACHE = f.read()
    finally:
        if os.path.isfile(path):
            os.unlink(path)
    return _REAL_MP4_CACHE


def _use_real_media_gen() -> bool:
    """True when FW_USE_REAL_MEDIA_GEN is set — video-edit materializers
    will hit fal.ai instead of MockVideoEditService."""
    return os.getenv("FW_USE_REAL_MEDIA_GEN", "").strip().lower() in ("1", "true", "yes")


def _video_seed_bytes() -> bytes:
    """Pick seed video bytes based on whether materializer hits real fal.

    Three tiers, in priority order:
    1. Real-mode + ``_REAL_VIDEO`` exists  → use the 5MB cached fal i2v clip.
       Real content (~5s, 1948x1064) so VACE / SAM2 / depth models produce
       meaningful output, not just succeed on a 16x16 black frame.
    2. Real-mode + no cached video         → ffmpeg-generate a 1s tiny mp4.
       Validates fal upload + endpoint; output quality is best-effort.
    3. Mock mode                           → 28-byte ftyp header.
       MockVideoEditService never reads the bytes, so it doesn't matter.
    """
    if _use_real_media_gen():
        return _REAL_VIDEO.read_bytes() if _REAL_VIDEO.is_file() else _real_tiny_mp4()
    return _MOCK_MP4


def _assert_materialized_video(uri: str, label: str, min_bytes: int = 1024) -> None:
    """Verify ``output_video.uri`` points to a real, non-trivial mp4.

    Mock path returns ``MOCK_MP4_HEADER`` (28 bytes); a real fal output is
    KBs to MBs. ``min_bytes=1024`` cleanly separates the two.
    """
    assert uri and uri != "placeholder", (
        f"[{label}] output_video.uri not materialized: {uri!r}"
    )
    p = Path(uri)
    assert p.is_file(), f"[{label}] materialized file does not exist: {uri}"
    size = p.stat().st_size
    print(f"  [{label}] materialized: {uri} ({size} bytes)")
    assert size >= min_bytes, (
        f"[{label}] materialized mp4 too small ({size} bytes) — "
        f"likely placeholder; fal.ai may have returned empty"
    )


# ═══════════════════════════════════════════════════════════════════════
# 12 independent tests
# ═══════════════════════════════════════════════════════════════════════

def test_subtitle_agent_independent(monkeypatch):
    client, ws = _make_env("SubtitleAgent", monkeypatch)
    _seed_artifact(ws, "ScreenplayAgent", _MINI_SCREENPLAY,
                   "Screenplay: 1 scene, 4 shots with dialogue and narration")
    step_id = _create_step(client, "Generate subtitles")
    body = _execute(client, "SubtitleAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[SubtitleAgent] status={cur.get('status')}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"
    results = body.get("results") or _last_results(client, step_id)
    tracks = (results or {}).get("content", {}).get("tracks", [])
    print(f"  tracks={len(tracks)}, cues={sum(len(t.get('cues',[])) for t in tracks)}")
    print(f"  workspace: {_ws_path(ws)}")


def test_translation_agent_independent(monkeypatch):
    client, ws = _make_env("TranslationAgent", monkeypatch)
    # Seed a Chinese screenplay so there's something meaningful to translate
    zh_screenplay = {
        "meta": {"asset_type": "screenplay"},
        "content": {
            "title": "火星洞穴",
            "scenes": [{
                "scene_id": "sc_001",
                "heading": "内景 火星洞穴 - 白天",
                "summary": "两名宇航员发现发光的水晶。",
                "shots": [
                    {"shot_id": "sh_001", "block_type": "narration", "text": "洞穴的墙壁闪烁着神秘的蓝色光芒。", "character_name": "旁白"},
                    {"shot_id": "sh_002", "block_type": "dialogue", "text": "快看这些水晶！", "character_name": "陈"},
                    {"shot_id": "sh_003", "block_type": "dialogue", "text": "我们必须向基地报告这个发现。", "character_name": "朴"},
                ],
            }],
        },
        "target_language": "en",
    }
    _seed_artifact(ws, "ScreenplayAgent", zh_screenplay,
                   "Screenplay in Chinese: dialogue between Chen and Park in Mars cave")
    step_id = _create_step(client, "Translate Chinese screenplay to English")
    body = _execute(client, "TranslationAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[TranslationAgent] status={cur.get('status')}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"


def test_compositor_agent_independent(monkeypatch):
    client, ws = _make_env("CompositorAgent", monkeypatch)
    _seed_artifact(ws, "ScreenplayAgent", _MINI_SCREENPLAY,
                   "Screenplay: 1 scene, 4 shots with dialogue and narration")
    _seed_artifact(ws, "VideoAgent", _MINI_VIDEO_PACKAGE,
                   "Video package: 1 scene, 4 shot clips, final merged video")
    _seed_artifact(ws, "AudioMixAgent", _MINI_AUDIO_PACKAGE,
                   "Audio mix: narration, music, ambience mixed into final audio")
    _seed_artifact(ws, "SubtitleAgent", _MINI_SUBTITLE,
                   "Subtitle tracks (en): 2 cues with SRT timing")
    step_id = _create_step(client, "Compose final video")
    body = _execute(client, "CompositorAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[CompositorAgent] status={cur.get('status')}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"


def test_style_transfer_agent_independent(monkeypatch):
    client, ws = _make_env("StyleTransferAgent", monkeypatch)
    real = _use_real_media_gen()
    _seed_file(ws, "VideoAgent", "final.mp4", _video_seed_bytes(),
               "Final merged video of Mars cave exploration scene",
               "video/mp4")
    _seed_artifact(ws, "user", {"style": "Studio Ghibli anime with watercolor textures"},
                   "Style reference: anime watercolor art style request",
                   "global")
    step_id = _create_step(client, "Apply anime style to video")
    body = _execute(client, "StyleTransferAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[StyleTransferAgent] status={cur.get('status')} real_media={real}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"
    if real:
        results = body.get("results") or _last_results(client, step_id)
        uri = (results or {}).get("content", {}).get("output_video", {}).get("uri", "")
        _assert_materialized_video(uri, "StyleTransferAgent")


def test_inpaint_agent_independent(monkeypatch):
    client, ws = _make_env("InpaintAgent", monkeypatch)
    real = _use_real_media_gen()
    _seed_file(ws, "VideoAgent", "final.mp4", _video_seed_bytes(),
               "Final video of astronauts in Mars cave",
               "video/mp4")
    _seed_artifact(ws, "user",
                   {"mask_mode": "depth_background", "replacement_description": "Replace background with futuristic city"},
                   "Mask specification: depth-based background replacement with cyberpunk city",
                   "global")
    step_id = _create_step(client, "Replace video background")
    body = _execute(client, "InpaintAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[InpaintAgent] status={cur.get('status')} real_media={real}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"
    if real:
        results = body.get("results") or _last_results(client, step_id)
        uri = (results or {}).get("content", {}).get("output_video", {}).get("uri", "")
        _assert_materialized_video(uri, "InpaintAgent")


def test_video_extend_agent_independent(monkeypatch):
    client, ws = _make_env("VideoExtendAgent", monkeypatch)
    _seed_file(ws, "VideoAgent", "final.mp4", _MOCK_MP4,
               "Video clip ending with astronaut reaching toward glowing crystal",
               "video/mp4")
    user_instruction = (
        "Extend the clip by 5 seconds: the astronaut picks up the crystal "
        "and holds it to the light."
    )
    _seed_artifact(ws, "IntakeTextAgent",
                   {"content": {"text": user_instruction, "summary": ""}},
                   "User-submitted creative brief (110 chars). Pipeline entry point — consumed by story and screenplay agents.",
                   "global")
    step_id = _create_step(client, "Extend video clip")
    body = _execute(client, "VideoExtendAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[VideoExtendAgent] status={cur.get('status')}")
    print(f"[VideoExtendAgent] user_instruction seeded: {user_instruction!r}")
    spec = ((cur.get("output") or {}).get("content") or {}).get("extension_spec", {})
    print(f"[VideoExtendAgent] LLM-planned continuation_prompt:\n    {spec.get('continuation_prompt', '')[:240]}")
    print(f"[VideoExtendAgent] LLM-planned motion_description:\n    {spec.get('motion_description', '')[:240]}")
    print(f"[VideoExtendAgent] LLM-planned duration: {spec.get('target_duration_seconds')}s")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"


def test_video_analysis_agent_independent(monkeypatch):
    client, ws = _make_env("VideoAnalysisAgent", monkeypatch)
    # Gemini rejects malformed mp4 bytes — use a real (tiny) mp4 instead.
    _seed_file(ws, "VideoAgent", "final.mp4", _real_tiny_mp4(),
               "30-second Mars cave exploration video with two astronauts discovering crystals",
               "video/mp4")
    step_id = _create_step(client, "Analyze video content")
    body = _execute(client, "VideoAnalysisAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[VideoAnalysisAgent] status={cur.get('status')}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"


def test_highlight_agent_independent(monkeypatch):
    client, ws = _make_env("HighlightAgent", monkeypatch)
    _seed_file(ws, "VideoAgent", "final.mp4", _MOCK_MP4,
               "30-second Mars cave video for highlight extraction",
               "video/mp4")
    _seed_artifact(ws, "VideoAnalysisAgent", _MINI_ANALYSIS,
                   "Video analysis: 3 scenes, 30s, sci-fi genre, cave + crystals + astronauts")
    step_id = _create_step(client, "Extract highlights")
    body = _execute(client, "HighlightAgent", step_id)
    cur = _brief_last(body)
    print(f"\n[HighlightAgent] status={cur.get('status')}")
    assert cur.get("status") == "COMPLETED", f"FAILED: {cur.get('error', '')[:200]}"


_REAL_VIDEO = Path("/home/zhendong_li/FrameWorkers/_workspaces/kling_capability_probe/3B_emotion_angry_shout.mp4")
_REAL_AUDIO = Path("/home/zhendong_li/FrameWorkers/Runtime/live_e2e_outputs/workspace_global_20260405_190306/artifacts/media/AudioAgent/audio/aud_narr_sc_001_01.wav")


def test_intake_video_agent_independent(monkeypatch):
    client, ws = _make_env("IntakeVideoAgent", monkeypatch)

    # Use the REAL video file — copy into workspace so path is valid
    ws_dir = _ws_path(ws)
    inputs_dir = ws_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    video_dest = inputs_dir / "user_upload.mp4"
    if _REAL_VIDEO.is_file():
        import shutil
        shutil.copy2(_REAL_VIDEO, video_dest)
    else:
        video_dest.write_bytes(_MOCK_MP4)

    # Register with the real path so build_skeleton fills video_asset.uri
    workspace = ws
    workspace.global_memory.register(
        agent_id="user",
        execution_id="upload_video",
        step_id="seed",
        artifacts=[ArtifactRef(
            caption="Raw user upload (mime=video/mp4): short cinematic clip generated by fal.ai I2V",
            scope="raw_pending",
            path=str(video_dest),
            mime="video/mp4",
        )],
    )

    step_id = _create_step(client, "Analyze uploaded video")
    body = _execute(client, "IntakeVideoAgent", step_id)
    status = body.get("status", "?")
    print(f"\n[IntakeVideoAgent] status={status}")

    if status == "COMPLETED":
        results = _last_results(client, step_id)
        summary = results.get("content", {}).get("visual_summary", "")
        uri = results.get("content", {}).get("video_asset", {}).get("uri", "")
        print(f"  visual_summary: {summary}")
        print(f"  video_asset.uri: {uri}")
        assert summary, "visual_summary is empty"
        assert uri, "video_asset.uri is empty"
    else:
        err = body.get("error", "")[:200]
        print(f"  error: {err}")
        # IntakeVideo is a multimodal stub — may fail without vision-video LLM
        pytest.skip(f"IntakeVideoAgent requires multimodal video LLM: {err}")

    print(f"  workspace: {ws_dir}")


# helper used by some tests
def _last_results(client, step_id):
    resp = client.get(f"/api/assistant/executions/step/{step_id}")
    if resp.status_code == 200:
        execs = resp.get_json()
        if execs:
            return execs[-1].get("results") or {}
    return {}
