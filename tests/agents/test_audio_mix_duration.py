"""E2E regression: AudioMixMaterializer respects max(narration_actual, music_target, ambience_target).

User-facing invariant (from CLAUDE.md discussion 2026-04-14):
  对话时长以实际为准；音乐/环境音时长以 screenplay 估计为准；
  允许 music/ambience 长于 dialogue；dialogue 短的轨道用静音 pad 上去。

Implementation uses ``ffmpeg ... amix=duration=longest``, which pads
every input track with silence up to the longest input's length.
Needs real ffmpeg on PATH — skipped if missing.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe required for end-to-end mix test",
)


def _sine_wav(duration_sec: float, freq: int) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out = tmp.name
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-t", str(duration_sec),
         "-i", f"sine=frequency={freq}:sample_rate=44100",
         "-c:a", "pcm_s16le", out],
        capture_output=True, check=True,
    )
    data = Path(out).read_bytes()
    os.unlink(out)
    return data


def _probe_duration(wav_bytes: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes); tmp.flush()
        path = tmp.name
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    os.unlink(path)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def test_audio_mix_pads_narration_to_music_ambience_length():
    """Scene 1 narration (2s) is padded to 8s when music+ambience target 8s.

    Two scenes; final = concat of scene mixes = 13s. Each scene's mix
    equals the longest of (narration-actual, music-target, ambience-target),
    which is what the user asked for.
    """
    from agents.audio_mix.materializer import AudioMixMaterializer
    from agents.audio_mix.schema import AudioMixAgentInput
    from agents.base_agent import MaterializeContext
    from inference.generation.audio_generators.service import AudioService

    tmp = Path(tempfile.mkdtemp(prefix="fw_mixtest_"))
    try:
        paths = {
            "narr_s1_a": tmp / "narr_s1_a.wav", "narr_s1_b": tmp / "narr_s1_b.wav",
            "music_s1":  tmp / "music_s1.wav",  "amb_s1":    tmp / "amb_s1.wav",
            "narr_s2":   tmp / "narr_s2.wav",
            "music_s2":  tmp / "music_s2.wav",  "amb_s2":    tmp / "amb_s2.wav",
        }
        paths["narr_s1_a"].write_bytes(_sine_wav(1.0, 440))
        paths["narr_s1_b"].write_bytes(_sine_wav(1.0, 660))
        paths["music_s1"].write_bytes(_sine_wav(8.0, 220))
        paths["amb_s1"].write_bytes(_sine_wav(8.0, 110))
        paths["narr_s2"].write_bytes(_sine_wav(3.0, 880))
        paths["music_s2"].write_bytes(_sine_wav(5.0, 330))
        paths["amb_s2"].write_bytes(_sine_wav(5.0, 165))

        screenplay = {"content": {"scenes": [
            {"scene_id": "sc_001", "shots": [{"shot_id": "sh_001"}, {"shot_id": "sh_002"}]},
            {"scene_id": "sc_002", "shots": [{"shot_id": "sh_003"}]},
        ]}}
        narration = {"content": {"segments": [
            {"segment_id": "narr_001", "linked_shot_id": "sh_001",
             "audio_asset": {"uri": str(paths["narr_s1_a"])}},
            {"segment_id": "narr_002", "linked_shot_id": "sh_002",
             "audio_asset": {"uri": str(paths["narr_s1_b"])}},
            {"segment_id": "narr_003", "linked_shot_id": "sh_003",
             "audio_asset": {"uri": str(paths["narr_s2"])}},
        ]}}
        music = {"content": {"cues": [
            {"scene_id": "sc_001", "audio_asset": {"uri": str(paths["music_s1"])}},
            {"scene_id": "sc_002", "audio_asset": {"uri": str(paths["music_s2"])}},
        ]}}
        ambience = {"content": {"beds": [
            {"scene_id": "sc_001", "audio_asset": {"uri": str(paths["amb_s1"])}},
            {"scene_id": "sc_002", "audio_asset": {"uri": str(paths["amb_s2"])}},
        ]}}

        typed = AudioMixAgentInput(
            screenplay_json_text=json.dumps(screenplay),
            narration_json_text=json.dumps(narration),
            music_json_text=json.dumps(music),
            ambience_json_text=json.dumps(ambience),
        )
        asset_dict = {"content": {
            "scene_mixes": [
                {"scene_id": "sc_001", "mix_asset": {"asset_id": "aud_mix_sc_001", "uri": "placeholder", "format": "wav"}},
                {"scene_id": "sc_002", "mix_asset": {"asset_id": "aud_mix_sc_002", "uri": "placeholder", "format": "wav"}},
            ],
            "final_audio": {"asset_id": "aud_final", "uri": "placeholder", "format": "wav"},
        }}

        ctx = MaterializeContext(
            step_id="test", typed_input=typed,
            persist_binary=lambda a: f"mock://{a.sys_id}",
            report_failure=None,
        )
        mat = AudioMixMaterializer(audio_service=AudioService(client=None, tts_model="tts-1"))
        results = asyncio.run(mat.materialize(ctx, asset_dict))

        by_id = {r.sys_id: _probe_duration(r.data) for r in results}
        tol = 0.5
        assert abs(by_id["aud_mix_sc_001"] - 8.0) < tol, by_id
        assert abs(by_id["aud_mix_sc_002"] - 5.0) < tol, by_id
        assert abs(by_id["aud_final"] - 13.0) < tol, by_id
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_audio_mix_final_duration_is_max_not_min():
    """Inverse guard: if narration >> music/ambience, final stretches to narration."""
    from agents.audio_mix.materializer import AudioMixMaterializer
    from agents.audio_mix.schema import AudioMixAgentInput
    from agents.base_agent import MaterializeContext
    from inference.generation.audio_generators.service import AudioService

    tmp = Path(tempfile.mkdtemp(prefix="fw_mixtest_"))
    try:
        narr_path = tmp / "narr.wav"; narr_path.write_bytes(_sine_wav(6.0, 440))
        music_path = tmp / "music.wav"; music_path.write_bytes(_sine_wav(2.0, 220))
        amb_path = tmp / "amb.wav"; amb_path.write_bytes(_sine_wav(2.0, 110))

        screenplay = {"content": {"scenes": [
            {"scene_id": "sc_001", "shots": [{"shot_id": "sh_001"}]},
        ]}}
        narration = {"content": {"segments": [
            {"segment_id": "narr_001", "linked_shot_id": "sh_001",
             "audio_asset": {"uri": str(narr_path)}},
        ]}}
        music = {"content": {"cues": [
            {"scene_id": "sc_001", "audio_asset": {"uri": str(music_path)}},
        ]}}
        ambience = {"content": {"beds": [
            {"scene_id": "sc_001", "audio_asset": {"uri": str(amb_path)}},
        ]}}

        typed = AudioMixAgentInput(
            screenplay_json_text=json.dumps(screenplay),
            narration_json_text=json.dumps(narration),
            music_json_text=json.dumps(music),
            ambience_json_text=json.dumps(ambience),
        )
        asset_dict = {"content": {
            "scene_mixes": [
                {"scene_id": "sc_001", "mix_asset": {"asset_id": "aud_mix_sc_001", "uri": "placeholder", "format": "wav"}},
            ],
            "final_audio": {"asset_id": "aud_final", "uri": "placeholder", "format": "wav"},
        }}
        ctx = MaterializeContext(
            step_id="test", typed_input=typed,
            persist_binary=lambda a: f"mock://{a.sys_id}",
            report_failure=None,
        )
        mat = AudioMixMaterializer(audio_service=AudioService(client=None, tts_model="tts-1"))
        results = asyncio.run(mat.materialize(ctx, asset_dict))

        by_id = {r.sys_id: _probe_duration(r.data) for r in results}
        # Narration 6s > music/ambience 2s ⇒ mix and final stretch to 6s
        assert abs(by_id["aud_mix_sc_001"] - 6.0) < 0.5, by_id
        assert abs(by_id["aud_final"] - 6.0) < 0.5, by_id
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
