"""Integration tests for the 7 new materializers.

Each test exercises the full ``materializer.materialize(ctx, asset_dict)``
flow using mock services, verifying that:
  - The correct service methods are called with expected arguments
  - MediaAsset list is returned with correct sys_id / extension
  - Asset dict is updated in-place where appropriate
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import pytest

from pydantic import BaseModel


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from agents.base_agent import MaterializeContext
from agents.descriptor import MediaAsset


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_ctx(typed_input: BaseModel, step_id: str = "test_task") -> MaterializeContext:
    """Build a MaterializeContext with a no-op persist callback."""
    return MaterializeContext(
        step_id=step_id,
        typed_input=typed_input,
        persist_binary=lambda asset: f"/mock/{asset.sys_id}.{asset.extension}",
        report_failure=None,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. CompositorMaterializer
# ═══════════════════════════════════════════════════════════════════════════

class _SpyCompositorService:
    def __init__(self):
        self.calls: list[dict] = []

    async def compose(self, *, video_path, audio_path="", subtitle_srts=None, plan=None):
        self.calls.append({
            "video_path": video_path, "audio_path": audio_path,
            "subtitle_srts": list(subtitle_srts or []), "plan": plan,
        })
        return b"composed_mp4_bytes"


class TestCompositorMaterializer:
    def test_produces_one_asset(self):
        from agents.compositor.materializer import CompositorMaterializer
        from agents.compositor.schema import CompositorAgentInput

        svc = _SpyCompositorService()
        mat = CompositorMaterializer(compositor_service=svc)
        inp = CompositorAgentInput(
            video_file_path="/tmp/video.mp4",
            audio_file_path="/tmp/audio.wav",
            subtitle_json_texts=[
                '{"content":{"tracks":[{"srt_text":"1\\n00:00:01,000 --> 00:00:03,000\\nHello\\n"}]}}',
            ],
        )
        asset_dict = {
            "content": {
                "plan": {"subtitle_style": {"font_size": 28}},
                "delivery_asset": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert assets[0].sys_id == "compositor_final"
        assert assets[0].extension == "mp4"
        assert assets[0].data == b"composed_mp4_bytes"
        assert len(svc.calls) == 1
        assert svc.calls[0]["video_path"] == "/tmp/video.mp4"
        srts = svc.calls[0]["subtitle_srts"]
        assert len(srts) == 1
        assert "Hello" in srts[0]

    def test_collects_multiple_tracks_for_bilingual_burn_in(self):
        """Bilingual flow: one tracks-shape artifact (NarratorAgent SRT
        envelope, or legacy subtitle) + one TranslationAgent artifact
        come in through the ``subtitle_tracks`` collection label. The
        materializer must peel the translation's ``translated_payload``
        wrapper and hand both SRT blobs to the compositor service."""
        from agents.compositor.materializer import CompositorMaterializer
        from agents.compositor.schema import CompositorAgentInput

        svc = _SpyCompositorService()
        mat = CompositorMaterializer(compositor_service=svc)
        # First entry: direct tracks-shape (CN) — what NarratorAgent
        # emits via its narrator_srt JSON envelope.
        cn = (
            '{"content":{"tracks":[{"srt_text":'
            '"1\\n00:00:01,000 --> 00:00:03,000\\n你好\\n"}]}}'
        )
        # Second entry: TranslationAgent shape (EN wrapped under
        # content.translated_payload).
        en = (
            '{"content":{"source_language":"zh","target_language":"en",'
            '"translated_payload":{"content":{"tracks":[{"srt_text":'
            '"1\\n00:00:01,000 --> 00:00:03,000\\nHello\\n"}]}}}}'
        )
        inp = CompositorAgentInput(
            video_file_path="/tmp/video.mp4",
            audio_file_path="/tmp/audio.wav",
            subtitle_json_texts=[cn, en],
        )
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, {"content": {"plan": {}}}))

        assert len(assets) == 1
        srts = svc.calls[0]["subtitle_srts"]
        assert len(srts) == 2, f"expected both CN+EN tracks, got {srts!r}"
        joined = "\n".join(srts)
        assert "你好" in joined and "Hello" in joined


# ═══════════════════════════════════════════════════════════════════════════
# 2. TranscriptionMaterializer
# ═══════════════════════════════════════════════════════════════════════════

class _SpyTranscriptionService:
    def __init__(self):
        self.calls: list[str] = []

    async def transcribe(self, media_path):
        from inference.generation.transcription_service import TranscriptionResult, TranscriptSegment
        self.calls.append(media_path)
        return TranscriptionResult(
            language="zh",
            segments=[
                TranscriptSegment(start=0.0, end=2.5, text="你好世界"),
                TranscriptSegment(start=3.0, end=5.0, text="测试转录"),
            ],
            full_text="你好世界 测试转录",
        )


class TestTranscriptionMaterializer:
    def test_pre_generate_seeds_raw_segments_into_input_data(self):
        """STT ran in pre_generate; raw_segments_json_text on input_data
        should contain the serialized ASR output for the LLM to clean up."""
        import json
        from agents.transcription.materializer import TranscriptionMaterializer
        from agents.transcription.schema import TranscriptionAgentInput

        svc = _SpyTranscriptionService()
        mat = TranscriptionMaterializer(transcription_service=svc)
        inp = TranscriptionAgentInput(source_media_path="/tmp/audio.mp3")
        ctx = _make_ctx(inp)
        asyncio.run(mat.pre_generate(ctx, inp))

        assert svc.calls == ["/tmp/audio.mp3"]
        assert inp.raw_segments_json_text, "raw_segments_json_text must be filled"
        payload = json.loads(inp.raw_segments_json_text)
        assert payload["language"] == "zh"
        assert payload["full_text"] == "你好世界 测试转录"
        assert len(payload["segments"]) == 2
        assert payload["segments"][0]["segment_id"] == "seg_001"
        assert payload["segments"][0]["text"] == "你好世界"
        assert payload["segments"][1]["start_time"] == 3.0

    def test_materialize_is_no_op(self):
        """Transcripts are pure-JSON artifacts — materialize emits no
        binary asset and no longer mutates asset_dict (that moved to
        pre_generate)."""
        from agents.transcription.materializer import TranscriptionMaterializer
        from agents.transcription.schema import TranscriptionAgentInput

        svc = _SpyTranscriptionService()
        mat = TranscriptionMaterializer(transcription_service=svc)
        inp = TranscriptionAgentInput(source_media_path="/tmp/audio.mp3")
        asset_dict: dict = {"content": {"segments": ["stub"]}}
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert assets == []
        # STT was NOT invoked — pre_generate owns that call now.
        assert svc.calls == []
        # asset_dict must be untouched by materialize().
        assert asset_dict == {"content": {"segments": ["stub"]}}


# ═══════════════════════════════════════════════════════════════════════════
# 3. StyleTransferMaterializer
# ═══════════════════════════════════════════════════════════════════════════

class _SpyVideoEditService:
    def __init__(self):
        self.style_calls: list[dict] = []
        self.inpaint_calls: list[dict] = []
        self.depth_calls: list[str] = []
        self.track_calls: list[dict] = []

    async def style_transfer(self, *, video_path, prompt, strength=0.7, preserve_motion=True, reference_path=None):
        self.style_calls.append({
            "video_path": video_path, "prompt": prompt,
            "strength": strength, "preserve_motion": preserve_motion,
        })
        return b"stylized_video_bytes"

    async def inpaint(self, *, video_path, mask, prompt, blend_px=8):
        self.inpaint_calls.append({
            "video_path": video_path, "prompt": prompt, "blend_px": blend_px,
        })
        return b"inpainted_video_bytes"

    async def estimate_depth(self, video_path):
        from inference.generation.video_edit_service import DepthMask
        self.depth_calls.append(video_path)
        return DepthMask(foreground=b"fg_mask", background=b"bg_mask")

    async def track_object(self, video_path, description):
        self.track_calls.append({"video_path": video_path, "description": description})
        return b"object_mask"


class TestStyleTransferMaterializer:
    def test_calls_service_and_returns_asset(self):
        from agents.style_transfer.materializer import StyleTransferMaterializer
        from agents.style_transfer.schema import StyleTransferAgentInput

        svc = _SpyVideoEditService()
        mat = StyleTransferMaterializer(video_edit_service=svc)
        inp = StyleTransferAgentInput(
            source_video_path="/tmp/src.mp4",
            style_description="anime",
            style_reference_path="/tmp/ref.jpg",
        )
        asset_dict = {
            "content": {
                "style_spec": {
                    "style_prompt": "anime cel shaded",
                    "style_strength": 0.85,
                    "preserve_motion": True,
                },
                "output_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert assets[0].sys_id == "style_transfer_output"
        assert assets[0].data == b"stylized_video_bytes"
        assert len(svc.style_calls) == 1
        assert svc.style_calls[0]["prompt"] == "anime cel shaded"
        assert svc.style_calls[0]["strength"] == 0.85


# ═══════════════════════════════════════════════════════════════════════════
# 4. InpaintMaterializer — manual mask
# ═══════════════════════════════════════════════════════════════════════════

class TestInpaintMaterializerManual:
    def test_manual_mask(self):
        from agents.inpaint.materializer import InpaintMaterializer
        from agents.inpaint.schema import InpaintAgentInput

        svc = _SpyVideoEditService()
        mat = InpaintMaterializer(video_edit_service=svc)
        inp = InpaintAgentInput(
            source_video_path="/tmp/src.mp4",
            mask_mode="manual",
            mask_path="/tmp/mask.png",
            replacement_description="forest",
        )
        asset_dict = {
            "content": {
                "inpaint_spec": {
                    "mask_mode": "manual",
                    "inpaint_prompt": "lush green forest",
                    "blend_edge_px": 12,
                },
                "output_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert assets[0].sys_id == "inpaint_output"
        assert assets[0].data == b"inpainted_video_bytes"
        assert len(svc.inpaint_calls) == 1
        assert svc.inpaint_calls[0]["blend_px"] == 12
        # No depth or tracking calls for manual mode
        assert svc.depth_calls == []
        assert svc.track_calls == []


class TestInpaintMaterializerDepth:
    def test_depth_background_mode(self):
        from agents.inpaint.materializer import InpaintMaterializer
        from agents.inpaint.schema import InpaintAgentInput

        svc = _SpyVideoEditService()
        mat = InpaintMaterializer(video_edit_service=svc)
        inp = InpaintAgentInput(
            source_video_path="/tmp/src.mp4",
            mask_mode="depth_background",
        )
        asset_dict = {
            "content": {
                "inpaint_spec": {
                    "mask_mode": "depth_background",
                    "inpaint_prompt": "sunset beach",
                    "replacement_description": "beach",
                },
                "output_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        # Depth estimation was called
        assert len(svc.depth_calls) == 1
        assert svc.depth_calls[0] == "/tmp/src.mp4"
        # Inpaint was called
        assert len(svc.inpaint_calls) == 1

    def test_object_track_mode(self):
        from agents.inpaint.materializer import InpaintMaterializer
        from agents.inpaint.schema import InpaintAgentInput

        svc = _SpyVideoEditService()
        mat = InpaintMaterializer(video_edit_service=svc)
        inp = InpaintAgentInput(
            source_video_path="/tmp/src.mp4",
            mask_mode="object_track",
        )
        asset_dict = {
            "content": {
                "inpaint_spec": {
                    "mask_mode": "object_track",
                    "inpaint_prompt": "golden retriever",
                    "replacement_description": "a golden retriever puppy",
                },
                "output_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert len(svc.track_calls) == 1
        assert "golden retriever" in svc.track_calls[0]["description"]


# ═══════════════════════════════════════════════════════════════════════════
# 5. VideoExtendMaterializer
# ═══════════════════════════════════════════════════════════════════════════

class _SpyVideoServiceExtend:
    def __init__(self):
        self.extract_calls: list[str] = []
        self.generate_calls: list[dict] = []

    async def extract_last_frame(self, video_path):
        self.extract_calls.append(video_path)
        return b"last_frame_png_bytes"

    async def generate_clip(self, *, shot_id, keyframe_images, prompt="", duration_sec=0.0, **kw):
        self.generate_calls.append({
            "shot_id": shot_id, "prompt": prompt, "duration": duration_sec,
            "n_images": len(keyframe_images),
        })
        # Return an object with .bytes attribute
        class _R:
            bytes = b"extended_video_bytes"
        return _R()


class TestVideoExtendMaterializer:
    def test_extracts_last_frame_and_generates(self):
        from agents.video_extend.materializer import VideoExtendMaterializer
        from agents.video_extend.schema import VideoExtendAgentInput

        svc = _SpyVideoServiceExtend()
        mat = VideoExtendMaterializer(video_service=svc)
        inp = VideoExtendAgentInput(
            source_video_path="/tmp/clip.mp4",
            continuation_description="walks away",
        )
        asset_dict = {
            "content": {
                "extension_spec": {
                    "continuation_prompt": "Character walks away into sunset",
                    "target_duration_seconds": 5.0,
                },
                "output_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert assets[0].sys_id == "video_extend_output"
        assert assets[0].data == b"extended_video_bytes"
        # Last frame extracted
        assert svc.extract_calls == ["/tmp/clip.mp4"]
        # Generate called with last frame + prompt
        assert len(svc.generate_calls) == 1
        assert svc.generate_calls[0]["n_images"] == 1
        assert "sunset" in svc.generate_calls[0]["prompt"]
        assert svc.generate_calls[0]["duration"] == 5.0


# ═══════════════════════════════════════════════════════════════════════════
# 6. HighlightMaterializer
# ═══════════════════════════════════════════════════════════════════════════

class _SpyVideoServiceClip:
    def __init__(self):
        self.clip_calls: list[dict] = []
        self.concat_called = False

    async def clip_segment(self, video_path, start, end):
        self.clip_calls.append({"path": video_path, "start": start, "end": end})
        return b"clip_bytes"

    async def concat_clips(self, clip_bytes_list):
        self.concat_called = True
        return b"highlight_reel_bytes"


class TestHighlightMaterializer:
    def test_clips_and_concats(self):
        from agents.highlight.materializer import HighlightMaterializer
        from agents.highlight.schema import HighlightAgentInput

        svc = _SpyVideoServiceClip()
        mat = HighlightMaterializer(video_service=svc)
        inp = HighlightAgentInput(
            source_video_path="/tmp/video.mp4",
            criteria="best moments",
        )
        asset_dict = {
            "content": {
                "criteria": "best",
                "clips": [
                    {"clip_id": "clip_001", "start_time": 5.0, "end_time": 12.0, "reason": "A"},
                    {"clip_id": "clip_002", "start_time": 30.0, "end_time": 38.0, "reason": "B"},
                ],
                "compiled_video": {},
            }
        }
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert len(assets) == 1
        assert assets[0].sys_id == "highlight_reel"
        assert assets[0].data == b"highlight_reel_bytes"
        # Two clips extracted
        assert len(svc.clip_calls) == 2
        assert svc.clip_calls[0]["start"] == 5.0
        assert svc.clip_calls[1]["end"] == 38.0
        assert svc.concat_called

    def test_empty_clips_returns_nothing(self):
        from agents.highlight.materializer import HighlightMaterializer
        from agents.highlight.schema import HighlightAgentInput

        svc = _SpyVideoServiceClip()
        mat = HighlightMaterializer(video_service=svc)
        inp = HighlightAgentInput(source_video_path="/tmp/video.mp4")
        asset_dict = {"content": {"clips": [], "compiled_video": {}}}
        ctx = _make_ctx(inp)
        assets = asyncio.run(mat.materialize(ctx, asset_dict))

        assert assets == []


