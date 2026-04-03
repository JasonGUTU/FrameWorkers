from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def _resolve_agents_project_root() -> Path:
    env_root = os.getenv("FRAMEWORKERS_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "agents" / "__init__.py").exists():
            return candidate

    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent

    raise RuntimeError(
        "Cannot locate project root containing agents/__init__.py. "
        "Set FRAMEWORKERS_ROOT to override."
    )


_project_root = _resolve_agents_project_root()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


from agents.audio.materializer import AudioMaterializer
from agents.contracts import ArtifactRefV2, InputBundleV2
from agents.keyframe.materializer import KeyframeMaterializer
from agents.video.materializer import VideoMaterializer
from inference.generation.audio_generators.service import AudioService
from inference.generation.video_generators.service import FalVideoService
from inference.generation.video_generators.service import VideoService


class _CaptureVideoService:
    def __init__(self) -> None:
        self.generate_calls: list[dict] = []

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes],
        prompt: str,
        duration_sec: float,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs,
    ) -> bytes:
        self.generate_calls.append(
            {
                "shot_id": shot_id,
                "keyframe_images": list(keyframe_images),
                "prompt": prompt,
                "kwargs": dict(kwargs),
            }
        )
        return b"clip"

    async def assemble_scene(
        self,
        *,
        scene_id: str,
        clip_bytes_list: list[bytes],
        transitions: list[dict],
    ) -> bytes:
        return b"scene"

    async def assemble_final(self, *, scene_bytes_list: list[bytes]) -> bytes:
        return b"final_video"


class _CaptureAudioService:
    def __init__(self) -> None:
        self.mux_calls: list[dict] = []

    async def generate_speech(self, text: str, *, voice: str | None = None) -> bytes:
        return b"speech"

    async def generate_music(self, *, mood: str, duration_sec: float, scene_id: str = "", **kwargs) -> bytes:
        return b"music"

    async def generate_ambience(
        self,
        *,
        description: str,
        duration_sec: float,
        scene_id: str = "",
        **kwargs,
    ) -> bytes:
        return b"ambience"

    async def mix_scene_audio(
        self,
        *,
        narration_bytes_list: list[bytes],
        music_bytes: bytes | None = None,
        ambience_bytes: bytes | None = None,
        scene_id: str = "",
        duration_sec: float = 0.0,
    ) -> bytes:
        return b"scene_mix"

    async def assemble_final(self, *, scene_mix_bytes_list: list[bytes]) -> bytes:
        return b"final_audio"

    async def mux_audio_with_video(self, *, video_bytes: bytes, audio_bytes: bytes) -> bytes:
        self.mux_calls.append({"video_bytes": video_bytes, "audio_bytes": audio_bytes})
        return b"muxed_video"


class _CaptureImageService:
    async def generate_image(self, prompt: str) -> bytes:
        return f"gen:{prompt}".encode("utf-8")

    async def edit_image(self, reference_images, prompt: str) -> bytes:
        return f"edit:{prompt}".encode("utf-8")


class _FalVideoServiceSpy(FalVideoService):
    def __init__(self, fail_multi: bool, structured_constraints_field: str | None = None) -> None:
        super().__init__(
            api_key="test",
            model="fal-ai/test-model",
            structured_constraints_field=structured_constraints_field,
        )
        self.fail_multi = fail_multi
        self.submitted: list[dict] = []

    async def _submit(self, arguments: dict[str, object]) -> dict[str, object]:
        self.submitted.append(arguments)
        if self.fail_multi and "image_urls" in arguments:
            raise RuntimeError("image_urls not supported")
        return {"video_url": "https://example.com/video.mp4"}

    async def _download_binary(self, url: str) -> bytes:
        return f"video:{url}".encode("utf-8")


def _bundle_from_assets(task_id: str, assets: dict[str, object]) -> InputBundleV2:
    artifacts = [
        ArtifactRefV2(
            artifact_id=f"art_{semantic_type}",
            semantic_type=semantic_type,
            payload=payload,
        )
        for semantic_type, payload in assets.items()
    ]
    return InputBundleV2(
        task_id=task_id,
        artifacts=artifacts,
        context={"resolved_inputs": dict(assets)},
    )


def test_video_materializer_uses_keyframe_images_for_clip_generation(monkeypatch):
    monkeypatch.setenv("FW_ENABLE_PROP_PIPELINE", "1")
    with tempfile.TemporaryDirectory() as tmp_dir:
        kf1 = Path(tmp_dir) / "kf1.png"
        kf2 = Path(tmp_dir) / "kf2.png"
        kf1.write_bytes(b"kf_image_1")
        kf2.write_bytes(b"kf_image_2")

        video_service = _CaptureVideoService()
        materializer = VideoMaterializer(video_service=video_service)
        asset_dict = {
            "content": {
                "scenes": [
                    {
                        "scene_id": "sc_001",
                        "shot_segments": [
                            {
                                "shot_id": "sh_001",
                                "estimated_duration_sec": 2.0,
                                "video_asset": {"format": "mp4"},
                            }
                        ],
                        "transition_plan": [],
                        "scene_clip_asset": {"format": "mp4"},
                    }
                ],
                "final_video_asset": {"format": "mp4"},
            }
        }
        assets = {
            "storyboard": {
                "content": {
                    "scenes": [
                        {
                            "scene_id": "sc_001",
                            "scene_consistency_pack": {
                                "location_lock": {
                                    "location_id": "loc_001",
                                    "time_of_day": "NIGHT",
                                    "environment_notes": [
                                        "Rain-soaked street with reflective neon lights."
                                    ],
                                },
                                "style_lock": {
                                    "global_style_notes": [
                                        "Moody cinematic contrast with cool highlights."
                                    ],
                                    "must_avoid": [
                                        "Flat lighting and washed-out colors."
                                    ],
                                },
                            },
                            "shots": [
                                {
                                    "shot_id": "sh_001",
                                    "shot_type": "medium",
                                    "visual_goal": "Show the character entering frame.",
                                    "action_focus": "Character walks in from left.",
                                    "characters_in_frame": ["char_001"],
                                    "camera": {
                                        "angle": "eye_level",
                                        "movement": "pan",
                                        "framing_notes": "Follow the character into center frame.",
                                    },
                                    "keyframe_plan": {
                                        "keyframe_notes": [
                                            "Entrance silhouette at frame left.",
                                            "Character reaches center frame.",
                                        ]
                                    },
                                }
                            ],
                        }
                    ]
                }
            },
            "keyframes": {
                "content": {
                    "scenes": [
                        {
                            "scene_id": "sc_001",
                            "shots": [
                                {
                                    "shot_id": "sh_001",
                                    "keyframes": [
                                        {
                                            "image_asset": {"uri": str(kf1)},
                                            "prompt_summary": "wide establishing frame",
                                        },
                                        {
                                            "image_asset": {"uri": str(kf2)},
                                            "prompt_summary": "character enters from left",
                                        },
                                    ],
                                }
                            ],
                        }
                    ]
                }
            },
        }

        input_bundle_v2 = _bundle_from_assets("task_1", assets)
        asyncio.run(materializer.materialize("task_1", asset_dict, input_bundle_v2))

    assert len(video_service.generate_calls) == 1
    call = video_service.generate_calls[0]
    assert call["shot_id"] == "sh_001"
    assert call["keyframe_images"] == [b"kf_image_1", b"kf_image_2"]
    assert "Keyframe policy: keyframe anchors are for stability/consistency only" in call["prompt"]
    assert "Show the character entering frame." in call["prompt"]
    assert "Character walks in from left." in call["prompt"]
    assert "Characters in frame: char_001" in call["prompt"]
    assert "Scene context: location_id=loc_001, time_of_day=NIGHT" in call["prompt"]
    assert "Scene environment notes: Rain-soaked street with reflective neon lights." in call["prompt"]
    assert "Scene style notes: Moody cinematic contrast with cool highlights." in call["prompt"]
    assert "Scene must avoid: Flat lighting and washed-out colors." in call["prompt"]
    assert "Follow the character into center frame." in call["prompt"]
    assert "Anchor images: 2" in call["prompt"]
    assert "Task focus: in this scene, complete this shot action: Character walks in from left." in call["prompt"]
    constraints = call["kwargs"].get("consistency_constraints", {})
    assert constraints.get("consistency_type") == "entity_anchor_constraints"
    assert constraints.get("keyframe_role") == "stability_and_consistency_only"
    assert constraints.get("characters_in_frame") == ["char_001"]
    assert constraints.get("scene_context", {}).get("location_id") == "loc_001"
    assert constraints.get("scene_context", {}).get("time_of_day") == "NIGHT"
    assert "wide establishing frame" in constraints.get("keyframe_prompt_summaries", [])


def test_keyframe_materializer_returns_assets_without_local_progress_snapshots(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp_dir:
        progress_dir = Path(tmp_dir) / "progress"
        monkeypatch.setenv("FW_KEYFRAME_PROGRESS_SAVE", "1")
        monkeypatch.setenv("FW_KEYFRAME_PROGRESS_DIR", str(progress_dir))
        monkeypatch.setenv("FW_KEYFRAME_PROGRESS_RUN_TAG", "unit")

        materializer = KeyframeMaterializer(image_service=_CaptureImageService())
        asset_dict = {
            "content": {
                "global_anchors": {
                    "characters": [
                        {
                            "entity_id": "char_001",
                            "prompt_summary": "global character prompt",
                            "image_asset": {"format": "png"},
                        }
                    ],
                    "locations": [
                        {
                            "entity_id": "loc_001",
                            "prompt_summary": "global location prompt",
                            "image_asset": {"format": "png"},
                        }
                    ],
                },
                "scenes": [
                    {
                        "scene_id": "sc_001",
                        "stability_keyframes": {
                            "characters": [
                                {
                                    "entity_id": "char_001",
                                    "prompt_summary": "scene character prompt",
                                    "image_asset": {"format": "png"},
                                }
                            ],
                            "locations": [
                                {
                                    "entity_id": "loc_001",
                                    "prompt_summary": "scene location prompt",
                                    "image_asset": {"format": "png"},
                                }
                            ],
                        },
                        "shots": [
                            {
                                "shot_id": "sh_001",
                                "keyframes": [
                                    {
                                        "prompt_summary": "shot prompt",
                                        "constraints_applied": {
                                            "characters_in_frame": ["char_001"],
                                        },
                                        "image_asset": {"format": "png"},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        }

        media_assets = asyncio.run(
            materializer.materialize(
                "task_test",
                asset_dict,
                InputBundleV2(task_id="task_test"),
            )
        )

        assert len(media_assets) >= 1
        run_dir = progress_dir / "task_test" / "unit"
        # Keyframe materializer should not write local progress snapshots.
        assert not run_dir.exists()


def test_audio_materializer_mixes_final_delivery_video():
    with tempfile.TemporaryDirectory() as tmp_dir:
        final_video_path = Path(tmp_dir) / "video.mp4"
        final_video_path.write_bytes(b"final_video")

        audio_service = _CaptureAudioService()
        materializer = AudioMaterializer(audio_service=audio_service)
        asset_dict = {
            "content": {
                "scenes": [
                    {
                        "scene_id": "sc_001",
                        "scene_duration_sec": 3.0,
                        "narration_segments": [
                            {
                                "segment_id": "narr_001",
                                "speaker": "Narrator",
                                "text": "hello world",
                                "audio_asset": {"format": "wav"},
                            }
                        ],
                        "music_cue": {
                            "mood": "calm",
                            "start_sec": 0.0,
                            "end_sec": 3.0,
                            "audio_asset": {},
                        },
                        "ambience_bed": {
                            "description": "wind",
                            "start_sec": 0.0,
                            "end_sec": 3.0,
                            "audio_asset": {},
                        },
                        "mix": {"audio_asset": {}},
                    }
                ],
                "final_audio_asset": {},
                "final_delivery_asset": {},
            }
        }
        assets = {
            "video": {
                "content": {
                    "final_video_asset": {
                        "uri": str(final_video_path),
                    }
                }
            }
        }

        input_bundle_v2 = _bundle_from_assets("task_1", assets)
        media_assets = asyncio.run(materializer.materialize("task_1", asset_dict, input_bundle_v2))

    ids = {m.sys_id for m in media_assets}
    assert "aud_final" in ids
    assert "delivery_final" in ids
    assert len(audio_service.mux_calls) == 1
    assert audio_service.mux_calls[0]["video_bytes"] == b"final_video"
    assert audio_service.mux_calls[0]["audio_bytes"] == b"final_audio"


class _KlingFalVideoSpy(FalVideoService):
    def __init__(self) -> None:
        super().__init__(
            api_key="test",
            model="fal-ai/kling-video/v2.6/pro/image-to-video",
        )
        self.submitted: list[dict] = []

    async def _submit(self, arguments: dict[str, object]) -> dict[str, object]:
        self.submitted.append(arguments)
        return {"video": {"url": "https://example.com/video.mp4"}}

    async def _download_binary(self, url: str) -> bytes:
        return f"video:{url}".encode("utf-8")


def test_fal_video_service_kling_maps_start_end_and_duration_enum():
    svc = _KlingFalVideoSpy()
    out = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"img1", b"img2"],
            prompt="prompt",
            duration_sec=2.0,
        )
    )
    assert out.startswith(b"video:https://example.com/")
    assert len(svc.submitted) == 1
    arg = svc.submitted[0]
    assert arg["duration"] == "5"
    assert arg["start_image_url"].startswith("data:image/png;base64,")
    assert arg["end_image_url"].startswith("data:image/png;base64,")
    assert "image_urls" not in arg
    assert "fps" not in arg


def test_fal_video_service_uses_multi_image_payload_when_supported():
    svc = _FalVideoServiceSpy(fail_multi=False)
    out = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"img1", b"img2"],
            prompt="prompt",
            duration_sec=2.0,
        )
    )
    assert out.startswith(b"video:https://example.com/")
    assert len(svc.submitted) == 1
    assert "image_urls" in svc.submitted[0]
    assert "image_url" not in svc.submitted[0]


def test_fal_video_service_raises_when_multi_image_payload_rejected():
    svc = _FalVideoServiceSpy(fail_multi=True)
    try:
        asyncio.run(
            svc.generate_clip(
                shot_id="sh_001",
                keyframe_images=[b"img1", b"img2"],
                prompt="prompt",
                duration_sec=2.0,
            )
        )
        raise AssertionError("Expected RuntimeError for rejected image_urls payload")
    except RuntimeError as exc:
        assert "image_urls not supported" in str(exc)
    assert len(svc.submitted) == 1
    assert "image_urls" in svc.submitted[0]


def test_fal_video_service_includes_structured_constraints_when_configured():
    svc = _FalVideoServiceSpy(
        fail_multi=False,
        structured_constraints_field="consistency_constraints",
    )
    out = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"img1"],
            prompt="prompt",
            duration_sec=2.0,
            consistency_constraints={
                "consistency_type": "entity_anchor_constraints",
                "characters_in_frame": ["char_001"],
            },
        )
    )
    assert out.startswith(b"video:https://example.com/")
    assert len(svc.submitted) == 1
    assert "consistency_constraints" in svc.submitted[0]
    assert svc.submitted[0]["consistency_constraints"]["consistency_type"] == "entity_anchor_constraints"


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe required for video concat duration check",
)
def test_video_service_assemble_scene_concatenates_real_mp4_duration():
    def _make_clip(duration_sec: float, out_path: Path) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s=320x240:d={duration_sec}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def _probe_duration(path: Path) -> float:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return float(proc.stdout.strip())

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        c1 = tmp / "c1.mp4"
        c2 = tmp / "c2.mp4"
        merged = tmp / "merged.mp4"
        _make_clip(1.0, c1)
        _make_clip(1.0, c2)

        service = VideoService()
        merged_bytes = asyncio.run(
            service.assemble_scene(
                scene_id="sc_001",
                clip_bytes_list=[c1.read_bytes(), c2.read_bytes()],
                transitions=[],
            )
        )
        merged.write_bytes(merged_bytes)

        d1 = _probe_duration(c1)
        d2 = _probe_duration(c2)
        dm = _probe_duration(merged)
        assert dm >= (d1 + d2) - 0.2


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe required for audio-video mux duration check",
)
def test_audio_service_mux_keeps_video_duration_when_audio_is_short():
    def _make_video(duration_sec: float, out_path: Path) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=size=320x240:rate=24:duration={duration_sec}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def _make_audio(duration_sec: float, out_path: Path) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=r=44100:cl=mono:d={duration_sec}",
                "-c:a",
                "pcm_s16le",
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def _probe_duration(path: Path) -> float:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return float(proc.stdout.strip())

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        video_path = tmp / "v.mp4"
        audio_path = tmp / "a.wav"
        muxed_path = tmp / "out.mp4"
        _make_video(2.0, video_path)
        _make_audio(0.1, audio_path)

        service = AudioService()
        out_bytes = asyncio.run(
            service.mux_audio_with_video(
                video_bytes=video_path.read_bytes(),
                audio_bytes=audio_path.read_bytes(),
            )
        )
        muxed_path.write_bytes(out_bytes)

        dv = _probe_duration(video_path)
        dm = _probe_duration(muxed_path)
        assert dm >= dv - 0.15
