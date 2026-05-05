"""Tests for the 10 new sub-agents added in the capability expansion.

Each agent is tested for:
  1. Schema — output model round-trips correctly, defaults are sane
  2. Evaluator — check_structure catches missing/invalid fields, passes valid output
  3. Descriptor — build_input produces correct typed input from resolved artifacts,
     build_captions returns well-formed caption dict
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


# ═══════════════════════════════════════════════════════════════════════════
# TranslationAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestTranslationAgent:
    def test_schema_defaults(self):
        from agents.translation.schema import TranslationAgentInput, TranslationAgentOutput
        inp = TranslationAgentInput()
        assert inp.source_json_text == ""
        assert inp.target_language == "en"
        out = TranslationAgentOutput()
        assert out.content.source_language == ""
        assert out.content.translated_payload == {}
        assert out.metrics.has_payload is False

    def test_schema_round_trip(self):
        from agents.translation.schema import TranslationAgentOutput
        data = {
            "content": {
                "source_language": "zh",
                "target_language": "en",
                "translated_payload": {"scene_id": "sc_001", "dialogue": "Hello world"},
            },
        }
        out = TranslationAgentOutput.model_validate(data)
        assert out.content.source_language == "zh"
        assert out.content.translated_payload["dialogue"] == "Hello world"

    def test_evaluator_passes_valid_output(self):
        from agents.translation.schema import TranslationAgentOutput
        from agents.translation.evaluator import TranslationEvaluator
        data = {
            "content": {
                "source_language": "zh",
                "target_language": "en",
                "translated_payload": {"content": {"scenes": [{"dialogue": "Hello"}]}},
            },
        }
        out = TranslationAgentOutput.model_validate(data)
        evaluator = TranslationEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_empty_fields(self):
        from agents.translation.schema import TranslationAgentOutput
        from agents.translation.evaluator import TranslationEvaluator
        out = TranslationAgentOutput()
        evaluator = TranslationEvaluator()
        errors = evaluator.check_structure(out)
        assert len(errors) >= 3  # source_language, target_language, translated_payload

    def test_evaluator_catches_empty_payload(self):
        from agents.translation.schema import TranslationAgentOutput
        from agents.translation.evaluator import TranslationEvaluator
        data = {
            "content": {
                "source_language": "zh",
                "target_language": "en",
                "translated_payload": {},
            },
        }
        out = TranslationAgentOutput.model_validate(data)
        evaluator = TranslationEvaluator()
        errors = evaluator.check_structure(out)
        assert any("payload" in e for e in errors)

    def test_descriptor_build_input(self):
        from agents.translation.descriptor import build_input
        resolved = {
            "source_text": {
                "caption": "Screenplay in Chinese",
                "scope": "global",
                "path": "/tmp/screenplay.json",
                "mime": "application/json",
                "payload": {"content": {"scenes": [{"dialogue": "你好"}]}, "target_language": "en"},
            }
        }
        inp = build_input("task_001", resolved)
        assert inp.target_language == "en"
        assert "你好" in inp.source_json_text

    def test_descriptor_build_captions(self):
        from agents.translation.descriptor import build_captions
        output_dict = {
            "content": {
                "source_language": "zh",
                "target_language": "en",
                "translated_text": "Hello",
            },
        }
        caps = build_captions("TranslationAgent", output_dict)
        assert "TranslationAgent" in caps
        assert "zh" in caps["TranslationAgent"]["caption"]
        assert "en" in caps["TranslationAgent"]["caption"]


# ═══════════════════════════════════════════════════════════════════════════
# TranscriptionAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestTranscriptionAgent:
    def test_schema_defaults(self):
        from agents.transcription.schema import TranscriptionAgentInput, TranscriptionAgentOutput
        inp = TranscriptionAgentInput()
        assert inp.source_media_path == ""
        out = TranscriptionAgentOutput()
        assert out.content.segments == []

    def test_evaluator_passes_valid_output(self):
        from agents.transcription.schema import TranscriptionAgentOutput
        from agents.transcription.evaluator import TranscriptionEvaluator
        data = {
            "content": {
                "language": "zh",
                "segments": [
                    {"segment_id": "seg_001", "start_time": 0.0, "end_time": 3.5, "speaker": "Speaker_1", "text": "你好世界", "confidence": 0.95},
                    {"segment_id": "seg_002", "start_time": 4.0, "end_time": 7.0, "speaker": "Speaker_2", "text": "你好", "confidence": 0.88},
                ],
                "full_text": "[Speaker_1]: 你好世界 [Speaker_2]: 你好",
            }
        }
        out = TranscriptionAgentOutput.model_validate(data)
        evaluator = TranscriptionEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_overlapping_segments(self):
        from agents.transcription.schema import TranscriptionAgentOutput
        from agents.transcription.evaluator import TranscriptionEvaluator
        data = {
            "content": {
                "language": "en",
                "segments": [
                    {"segment_id": "seg_001", "start_time": 0.0, "end_time": 5.0, "text": "A", "confidence": 0.9},
                    {"segment_id": "seg_002", "start_time": 3.0, "end_time": 7.0, "text": "B", "confidence": 0.9},
                ],
                "full_text": "A B",
            }
        }
        out = TranscriptionAgentOutput.model_validate(data)
        evaluator = TranscriptionEvaluator()
        errors = evaluator.check_structure(out)
        assert any("overlaps" in e for e in errors)

    def test_evaluator_catches_end_before_start(self):
        from agents.transcription.schema import TranscriptionAgentOutput
        from agents.transcription.evaluator import TranscriptionEvaluator
        data = {
            "content": {
                "language": "en",
                "segments": [
                    {"segment_id": "seg_001", "start_time": 5.0, "end_time": 3.0, "text": "bad", "confidence": 0.9},
                ],
                "full_text": "bad",
            }
        }
        out = TranscriptionAgentOutput.model_validate(data)
        evaluator = TranscriptionEvaluator()
        errors = evaluator.check_structure(out)
        assert any("end_time" in e for e in errors)

    def test_descriptor_build_input(self):
        from agents.transcription.descriptor import build_input
        resolved = {
            "source_media": {
                "caption": "Video file", "scope": "global",
                "path": "/tmp/video.mp4", "mime": "video/mp4", "payload": None,
            },
        }
        inp = build_input("task_001", resolved)
        assert inp.source_media_path == "/tmp/video.mp4"


# ═══════════════════════════════════════════════════════════════════════════
# CompositorAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestCompositorAgent:
    def test_schema_defaults(self):
        from agents.compositor.schema import CompositorAgentInput, CompositorAgentOutput
        inp = CompositorAgentInput()
        assert inp.screenplay_json_text == ""
        out = CompositorAgentOutput()
        assert out.content.plan.output_resolution == "1920x1080"
        assert out.content.plan.output_fps == 30

    def test_evaluator_passes_valid_output(self):
        from agents.compositor.schema import CompositorAgentOutput
        from agents.compositor.evaluator import CompositorEvaluator
        data = {
            "content": {
                "plan": {
                    "color_grade": {"brightness": 0.0, "contrast": 0.05, "saturation": 0.0, "tone": "warm"},
                    "subtitle_style": {"font_size": 24, "font_color": "#FFFFFF", "outline_color": "#000000", "position": "bottom", "burn_in": True},
                    "output_resolution": "1920x1080",
                    "output_fps": 30,
                    "output_format": "mp4",
                },
                "delivery_asset": {"asset_id": "compositor_final", "uri": "placeholder", "format": "mp4"},
            }
        }
        out = CompositorAgentOutput.model_validate(data)
        evaluator = CompositorEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_bad_resolution(self):
        from agents.compositor.schema import CompositorAgentOutput
        from agents.compositor.evaluator import CompositorEvaluator
        data = {
            "content": {
                "plan": {"output_resolution": "fullhd", "output_fps": 30},
                "delivery_asset": {"asset_id": "compositor_final"},
            }
        }
        out = CompositorAgentOutput.model_validate(data)
        evaluator = CompositorEvaluator()
        errors = evaluator.check_structure(out)
        assert any("resolution" in e for e in errors)

    def test_evaluator_catches_wrong_asset_id(self):
        from agents.compositor.schema import CompositorAgentOutput
        from agents.compositor.evaluator import CompositorEvaluator
        data = {
            "content": {
                "plan": {"output_resolution": "1920x1080", "output_fps": 30},
                "delivery_asset": {"asset_id": "wrong_id"},
            }
        }
        out = CompositorAgentOutput.model_validate(data)
        evaluator = CompositorEvaluator()
        errors = evaluator.check_structure(out)
        assert any("compositor_final" in e for e in errors)

    def test_descriptor_build_input(self):
        from agents.compositor.descriptor import build_input
        # video_file / audio_file labels carry the binary paths; the
        # sibling video_package / audio_package labels carry the JSON
        # manifest payloads. CompositorAgent now reads them independently.
        resolved = {
            "screenplay": {"caption": "SP", "scope": "global", "path": "", "mime": "application/json", "payload": {"content": {}}},
            "video_package": {"caption": "VP", "scope": "global", "path": "", "mime": "application/json", "payload": {"content": {}}},
            "video_file": {"caption": "VF", "scope": "global", "path": "/tmp/v.mp4", "mime": "video/mp4", "payload": None},
            "audio_package": {"caption": "AP", "scope": "global", "path": "", "mime": "application/json", "payload": {"content": {}}},
            "audio_file": {"caption": "AF", "scope": "global", "path": "/tmp/a.wav", "mime": "audio/wav", "payload": None},
            "subtitle_tracks": {"caption": "ST", "scope": "global", "path": "", "mime": "application/json", "payload": {"tracks": []}},
        }
        inp = build_input("task_001", resolved)
        assert "content" in inp.screenplay_json_text
        assert inp.video_file_path == "/tmp/v.mp4"
        assert inp.audio_file_path == "/tmp/a.wav"


# ═══════════════════════════════════════════════════════════════════════════
# StyleTransferAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestStyleTransferAgent:
    def test_schema_defaults(self):
        from agents.style_transfer.schema import StyleTransferAgentInput, StyleTransferAgentOutput
        inp = StyleTransferAgentInput()
        assert inp.source_video_path == ""
        out = StyleTransferAgentOutput()
        assert out.content.style_spec.style_strength == 0.7
        assert out.content.style_spec.preserve_motion is True

    def test_evaluator_passes_valid_output(self):
        from agents.style_transfer.schema import StyleTransferAgentOutput
        from agents.style_transfer.evaluator import StyleTransferEvaluator
        data = {
            "content": {
                "style_spec": {
                    "style_description": "Japanese anime style with cel shading and vibrant colors",
                    "style_prompt": "anime cel-shaded vibrant colors sharp outlines studio ghibli inspired",
                    "preserve_motion": True,
                    "style_strength": 0.85,
                },
                "output_video": {"asset_id": "style_transfer_output", "uri": "placeholder", "format": "mp4"},
            }
        }
        out = StyleTransferAgentOutput.model_validate(data)
        evaluator = StyleTransferEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_empty_prompt(self):
        from agents.style_transfer.schema import StyleTransferAgentOutput
        from agents.style_transfer.evaluator import StyleTransferEvaluator
        data = {
            "content": {
                "style_spec": {"style_description": "anime", "style_prompt": "", "style_strength": 0.8},
                "output_video": {"asset_id": "style_transfer_output"},
            }
        }
        out = StyleTransferAgentOutput.model_validate(data)
        evaluator = StyleTransferEvaluator()
        errors = evaluator.check_structure(out)
        assert any("style_prompt" in e and "empty" in e for e in errors)

    def test_evaluator_catches_wrong_asset_id(self):
        from agents.style_transfer.schema import StyleTransferAgentOutput
        from agents.style_transfer.evaluator import StyleTransferEvaluator
        data = {
            "content": {
                "style_spec": {"style_description": "x", "style_prompt": "long enough prompt for the model", "style_strength": 0.8},
                "output_video": {"asset_id": "wrong"},
            }
        }
        out = StyleTransferAgentOutput.model_validate(data)
        evaluator = StyleTransferEvaluator()
        errors = evaluator.check_structure(out)
        assert any("style_transfer_output" in e for e in errors)

    def test_descriptor_build_input(self):
        from agents.style_transfer.descriptor import build_input
        resolved = {
            "source_video": {"caption": "Source", "scope": "global", "path": "/tmp/src.mp4", "mime": "video/mp4", "payload": None},
            "style_reference": {"caption": "Oil painting with warm tones", "scope": "global", "path": "/tmp/ref.jpg", "mime": "image/jpeg", "payload": None},
        }
        inp = build_input("task_001", resolved)
        assert inp.source_video_path == "/tmp/src.mp4"
        assert inp.style_reference_path == "/tmp/ref.jpg"
        assert "Oil painting" in inp.style_description


# ═══════════════════════════════════════════════════════════════════════════
# InpaintAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestInpaintAgent:
    def test_schema_defaults(self):
        from agents.inpaint.schema import InpaintAgentInput, InpaintAgentOutput
        inp = InpaintAgentInput()
        assert inp.mask_mode == "manual"
        out = InpaintAgentOutput()
        assert out.content.inpaint_spec.blend_edge_px == 8

    def test_evaluator_passes_valid_output(self):
        from agents.inpaint.schema import InpaintAgentOutput
        from agents.inpaint.evaluator import InpaintEvaluator
        data = {
            "content": {
                "inpaint_spec": {
                    "mask_mode": "depth_background",
                    "replacement_description": "Replace the background with a cyberpunk cityscape",
                    "inpaint_prompt": "cyberpunk cityscape neon lights rain reflections night sky detailed buildings",
                    "preserve_unmasked": True,
                    "blend_edge_px": 12,
                },
                "output_video": {"asset_id": "inpaint_output", "uri": "placeholder"},
            }
        }
        out = InpaintAgentOutput.model_validate(data)
        evaluator = InpaintEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_invalid_mask_mode(self):
        from agents.inpaint.schema import InpaintAgentOutput
        from agents.inpaint.evaluator import InpaintEvaluator
        data = {
            "content": {
                "inpaint_spec": {
                    "mask_mode": "auto_magic",
                    "replacement_description": "something",
                    "inpaint_prompt": "long enough prompt for model",
                },
                "output_video": {"asset_id": "inpaint_output"},
            }
        }
        out = InpaintAgentOutput.model_validate(data)
        evaluator = InpaintEvaluator()
        errors = evaluator.check_structure(out)
        assert any("mask_mode" in e for e in errors)

    def test_evaluator_all_four_mask_modes_valid(self):
        from agents.inpaint.schema import InpaintAgentOutput
        from agents.inpaint.evaluator import InpaintEvaluator
        evaluator = InpaintEvaluator()
        for mode in ("manual", "depth_foreground", "depth_background", "object_track"):
            data = {
                "content": {
                    "inpaint_spec": {
                        "mask_mode": mode,
                        "replacement_description": "Replace with forest",
                        "inpaint_prompt": "lush green forest sunlight through trees",
                    },
                    "output_video": {"asset_id": "inpaint_output"},
                }
            }
            out = InpaintAgentOutput.model_validate(data)
            errors = evaluator.check_structure(out)
            mask_errors = [e for e in errors if "mask_mode" in e]
            assert mask_errors == [], f"mask_mode={mode} should be valid"

    def test_descriptor_build_input_depth_mode(self):
        from agents.inpaint.descriptor import build_input
        resolved = {
            "source_video": {"caption": "Src", "scope": "global", "path": "/tmp/v.mp4", "mime": "video/mp4", "payload": None},
            "mask": {"caption": "Replace background", "scope": "global", "path": "", "mime": "",
                     "payload": {"mask_mode": "depth_background", "replacement_description": "sunset beach"}},
        }
        inp = build_input("task_001", resolved)
        assert inp.mask_mode == "depth_background"
        assert inp.replacement_description == "sunset beach"


# ═══════════════════════════════════════════════════════════════════════════
# VideoExtendAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestVideoExtendAgent:
    def test_schema_defaults(self):
        from agents.video_extend.schema import VideoExtendAgentInput, VideoExtendAgentOutput
        inp = VideoExtendAgentInput()
        assert inp.source_video_path == ""
        out = VideoExtendAgentOutput()
        assert out.content.extension_spec.target_duration_seconds == 5.0

    def test_evaluator_passes_valid_output(self):
        from agents.video_extend.schema import VideoExtendAgentOutput
        from agents.video_extend.evaluator import VideoExtendEvaluator
        data = {
            "content": {
                "extension_spec": {
                    "continuation_prompt": "The character turns and walks through the doorway into a brightly lit room",
                    "target_duration_seconds": 5.0,
                    "maintain_style": True,
                    "motion_description": "Camera follows character through door, gentle push-in",
                },
                "output_video": {"asset_id": "video_extend_output", "uri": "placeholder"},
            }
        }
        out = VideoExtendAgentOutput.model_validate(data)
        evaluator = VideoExtendEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_excessive_duration(self):
        from agents.video_extend.schema import VideoExtendAgentOutput
        from agents.video_extend.evaluator import VideoExtendEvaluator
        data = {
            "content": {
                "extension_spec": {
                    "continuation_prompt": "A long continuation scene",
                    "target_duration_seconds": 60.0,
                    "motion_description": "Static camera",
                },
                "output_video": {"asset_id": "video_extend_output"},
            }
        }
        out = VideoExtendAgentOutput.model_validate(data)
        evaluator = VideoExtendEvaluator()
        errors = evaluator.check_structure(out)
        assert any("30s" in e for e in errors)

    def test_evaluator_catches_empty_motion(self):
        from agents.video_extend.schema import VideoExtendAgentOutput
        from agents.video_extend.evaluator import VideoExtendEvaluator
        data = {
            "content": {
                "extension_spec": {
                    "continuation_prompt": "Character walks away from camera into the distance",
                    "target_duration_seconds": 5.0,
                    "motion_description": "",
                },
                "output_video": {"asset_id": "video_extend_output"},
            }
        }
        out = VideoExtendAgentOutput.model_validate(data)
        evaluator = VideoExtendEvaluator()
        errors = evaluator.check_structure(out)
        assert any("motion_description" in e for e in errors)

    def test_descriptor_build_input_dumps_instruction_payload_as_json(self):
        from agents.video_extend.descriptor import build_input
        resolved = {
            "source_video": {
                "caption": "User-uploaded video reference.",
                "scope": "global", "path": "/tmp/clip.mp4", "mime": "video/mp4",
                "payload": None,
            },
            "continuation_instruction": {
                "caption": "User-submitted creative brief (32 chars). ...",
                "scope": "global", "path": "/tmp/brief.json",
                "mime": "application/json",
                "payload": {"content": {"text": "Character walks out the door"}},
            },
        }
        inp = build_input("task_001", resolved)
        assert inp.source_video_path == "/tmp/clip.mp4"
        assert "door" in inp.continuation_description
        assert "content" in inp.continuation_description

    def test_descriptor_build_input_falls_back_to_instruction_caption(self):
        from agents.video_extend.descriptor import build_input
        resolved = {
            "source_video": {
                "caption": "Source video clip.",
                "scope": "global", "path": "/tmp/clip.mp4", "mime": "video/mp4",
                "payload": None,
            },
            "continuation_instruction": {
                "caption": "Extend 5 seconds: character walks away.",
                "scope": "global", "path": "/tmp/brief.txt",
                "mime": "text/plain", "payload": None,
            },
        }
        inp = build_input("task_001", resolved)
        assert inp.source_video_path == "/tmp/clip.mp4"
        assert inp.continuation_description == "Extend 5 seconds: character walks away."

    def test_descriptor_build_input_empty_when_no_instruction(self):
        from agents.video_extend.descriptor import build_input
        resolved = {
            "source_video": {
                "caption": "Source video clip.",
                "scope": "global", "path": "/tmp/clip.mp4", "mime": "video/mp4",
                "payload": None,
            },
        }
        inp = build_input("task_001", resolved)
        assert inp.source_video_path == "/tmp/clip.mp4"
        assert inp.continuation_description == ""


# ═══════════════════════════════════════════════════════════════════════════
# VideoAnalysisAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestVideoAnalysisAgent:
    def test_schema_defaults(self):
        """Input REJECTS empty path (validator enforces a real video file).

        Output still has sane defaults for empty construction.
        """
        import pytest
        from pydantic import ValidationError
        from agents.video_analysis.schema import VideoAnalysisAgentInput, VideoAnalysisAgentOutput
        with pytest.raises(ValidationError):
            VideoAnalysisAgentInput()
        out = VideoAnalysisAgentOutput()
        assert out.content.scenes == []

    def test_evaluator_passes_valid_output(self):
        from agents.video_analysis.schema import VideoAnalysisAgentOutput
        from agents.video_analysis.evaluator import VideoAnalysisEvaluator
        data = {
            "content": {
                "video_summary": {"title": "Morning Walk", "summary": "A person walks through a park at sunrise.", "genre": "documentary", "language": "en", "duration_seconds": 45.0},
                "scenes": [
                    {"scene_id": "scene_001", "start_time": 0.0, "end_time": 20.0, "description": "Wide shot of park at sunrise with dew on grass", "setting": "Park", "mood": "peaceful", "entities": ["person", "trees"]},
                    {"scene_id": "scene_002", "start_time": 20.0, "end_time": 45.0, "description": "Close-up of person smiling", "setting": "Park bench", "mood": "happy", "entities": ["person"]},
                ],
            }
        }
        out = VideoAnalysisAgentOutput.model_validate(data)
        evaluator = VideoAnalysisEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_overlapping_scenes(self):
        from agents.video_analysis.schema import VideoAnalysisAgentOutput
        from agents.video_analysis.evaluator import VideoAnalysisEvaluator
        data = {
            "content": {
                "video_summary": {"title": "T", "summary": "S", "genre": "g"},
                "scenes": [
                    {"scene_id": "scene_001", "start_time": 0.0, "end_time": 20.0, "description": "A"},
                    {"scene_id": "scene_002", "start_time": 15.0, "end_time": 30.0, "description": "B"},
                ],
            }
        }
        out = VideoAnalysisAgentOutput.model_validate(data)
        evaluator = VideoAnalysisEvaluator()
        errors = evaluator.check_structure(out)
        assert any("overlaps" in e for e in errors)

    def test_evaluator_catches_non_increasing_scene_ids(self):
        from agents.video_analysis.schema import VideoAnalysisAgentOutput
        from agents.video_analysis.evaluator import VideoAnalysisEvaluator
        data = {
            "content": {
                "video_summary": {"title": "T", "summary": "S", "genre": "g"},
                "scenes": [
                    {"scene_id": "scene_002", "start_time": 0.0, "end_time": 10.0, "description": "A"},
                    {"scene_id": "scene_001", "start_time": 10.0, "end_time": 20.0, "description": "B"},
                ],
            }
        }
        out = VideoAnalysisAgentOutput.model_validate(data)
        evaluator = VideoAnalysisEvaluator()
        errors = evaluator.check_structure(out)
        assert any("increasing" in e for e in errors)

    def test_descriptor_build_input(self):
        """VideoAnalysisAgentInput validates path exists + is video/* mime.

        Use a real tempfile with .mp4 suffix so the validator passes.
        """
        import tempfile
        from agents.video_analysis.descriptor import build_input
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
            resolved = {
                "source_video": {
                    "caption": "Video", "scope": "global",
                    "path": tmp.name, "mime": "video/mp4", "payload": None,
                },
            }
            inp = build_input("task_001", resolved)
            assert inp.source_video_path == tmp.name

    def test_descriptor_build_captions(self):
        from agents.video_analysis.descriptor import build_captions
        output_dict = {
            "content": {
                "video_summary": {"title": "City Walk", "genre": "vlog"},
                "scenes": [{"scene_id": "scene_001"}, {"scene_id": "scene_002"}],
            }
        }
        caps = build_captions("VideoAnalysisAgent", output_dict)
        cap = caps["VideoAnalysisAgent"]["caption"]
        # Caption carries role + scene count. Content (title, genre) lives
        # in payload, never in caption. See MEMORY:feedback_caption_role_not_content.
        assert "2 scene(s)" in cap
        assert "City Walk" not in cap
        assert "vlog" not in cap


# ═══════════════════════════════════════════════════════════════════════════
# HighlightAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestHighlightAgent:
    def test_schema_defaults(self):
        from agents.highlight.schema import HighlightAgentInput, HighlightAgentOutput
        inp = HighlightAgentInput()
        assert inp.criteria == ""
        out = HighlightAgentOutput()
        assert out.content.clips == []

    def test_evaluator_passes_valid_output(self):
        from agents.highlight.schema import HighlightAgentOutput
        from agents.highlight.evaluator import HighlightEvaluator
        data = {
            "content": {
                "criteria": "most visually interesting moments",
                "clips": [
                    {"clip_id": "clip_001", "start_time": 5.0, "end_time": 12.0, "reason": "Beautiful sunrise shot", "score": 0.95},
                    {"clip_id": "clip_002", "start_time": 30.0, "end_time": 38.0, "reason": "Dynamic action sequence", "score": 0.88},
                ],
                "compiled_video": {"asset_id": "highlight_reel", "uri": "placeholder"},
            }
        }
        out = HighlightAgentOutput.model_validate(data)
        evaluator = HighlightEvaluator()
        errors = evaluator.check_structure(out)
        assert errors == []

    def test_evaluator_catches_overlapping_clips(self):
        from agents.highlight.schema import HighlightAgentOutput
        from agents.highlight.evaluator import HighlightEvaluator
        data = {
            "content": {
                "criteria": "best",
                "clips": [
                    {"clip_id": "clip_001", "start_time": 5.0, "end_time": 15.0, "reason": "A", "score": 0.9},
                    {"clip_id": "clip_002", "start_time": 10.0, "end_time": 20.0, "reason": "B", "score": 0.8},
                ],
                "compiled_video": {"asset_id": "highlight_reel"},
            }
        }
        out = HighlightAgentOutput.model_validate(data)
        evaluator = HighlightEvaluator()
        errors = evaluator.check_structure(out)
        assert any("overlaps" in e for e in errors)

    def test_evaluator_catches_too_short_clip(self):
        from agents.highlight.schema import HighlightAgentOutput
        from agents.highlight.evaluator import HighlightEvaluator
        data = {
            "content": {
                "criteria": "best",
                "clips": [
                    {"clip_id": "clip_001", "start_time": 5.0, "end_time": 5.5, "reason": "Quick", "score": 0.7},
                ],
                "compiled_video": {"asset_id": "highlight_reel"},
            }
        }
        out = HighlightAgentOutput.model_validate(data)
        evaluator = HighlightEvaluator()
        errors = evaluator.check_structure(out)
        assert any("short" in e for e in errors)

    def test_descriptor_build_captions(self):
        from agents.highlight.descriptor import build_captions
        output_dict = {
            "content": {
                "criteria": "action scenes",
                "clips": [
                    {"start_time": 5.0, "end_time": 15.0},
                    {"start_time": 30.0, "end_time": 40.0},
                ],
            }
        }
        caps = build_captions("HighlightAgent", output_dict)
        assert "2 clip(s)" in caps["HighlightAgent"]["caption"]
        assert "20.0s" in caps["HighlightAgent"]["caption"]


# ═══════════════════════════════════════════════════════════════════════════
# Cross-agent registry check
# ═══════════════════════════════════════════════════════════════════════════

class TestNewAgentsInRegistry:
    """Verify all new agents are properly registered."""

    EXPECTED_NEW_AGENTS = [
        "TranslationAgent",
        "CompositorAgent",
        "StyleTransferAgent",
        "VideoExtendAgent",
        "VideoAnalysisAgent",
        "HighlightAgent",
    ]

    def test_all_new_agents_in_registry(self):
        from agents import AGENT_REGISTRY
        for agent_id in self.EXPECTED_NEW_AGENTS:
            assert agent_id in AGENT_REGISTRY, f"{agent_id} missing from AGENT_REGISTRY"

    def test_all_new_agents_have_catalog_entry(self):
        from agents import AGENT_REGISTRY
        for agent_id in self.EXPECTED_NEW_AGENTS:
            desc = AGENT_REGISTRY[agent_id]
            assert desc.catalog_entry, f"{agent_id} has empty catalog_entry"
            assert agent_id in desc.catalog_entry

    def test_all_new_agents_have_input_needs_description(self):
        from agents import AGENT_REGISTRY
        for agent_id in self.EXPECTED_NEW_AGENTS:
            desc = AGENT_REGISTRY[agent_id]
            assert desc.input_needs_description, f"{agent_id} has empty input_needs_description"

    def test_all_new_descriptors_use_resolved_artifacts(self):
        """Ensure new agents follow the resolved_artifacts convention."""
        import inspect
        from agents import AGENT_REGISTRY
        for agent_id in self.EXPECTED_NEW_AGENTS:
            desc = AGENT_REGISTRY[agent_id]
            sig = inspect.signature(desc.build_input)
            params = list(sig.parameters.keys())
            assert len(params) >= 2, f"{agent_id}.build_input needs at least 2 params"

    def test_total_registry_count(self):
        # Floor guard against accidental mass un-registration. Update this
        # number on intentional agent restructures; the specific critical
        # set is enforced by ``test_all_new_agents_in_registry`` above.
        from agents import AGENT_REGISTRY
        assert len(AGENT_REGISTRY) >= 18, f"Expected >=18 agents, got {len(AGENT_REGISTRY)}"
