"""Live integration tests for 12 sub-agents (10 new + IntakeVideo + IntakeAudio).

Each test creates a real LLMClient, builds realistic typed input,
calls agent.generate() with a real LLM, validates with the evaluator,
and (for media agents) runs the materializer with mock services.

Gate: FW_ENABLE_LIVE_LLM_TESTS=1

Usage:
    source .env
    FW_ENABLE_LIVE_LLM_TESTS=1 python -m pytest tests/agents/test_new_agents_live.py -v -s
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Load .env so API keys are available
from inference.config.config_loader import ConfigLoader
for fname in (".env", ".env.example"):
    env_path = _root / fname
    if env_path.is_file():
        ConfigLoader.load_env_file(str(env_path), override=False)


def _skip_unless_live():
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        pytest.skip("Live LLM test disabled. Set FW_ENABLE_LIVE_LLM_TESTS=1 to run.")


def _make_llm_client():
    from inference.clients import LLMClient
    return LLMClient()


# ── Shared test screenplay fixture ──

_MINI_SCREENPLAY = {
    "content": {
        "scenes": [
            {
                "scene_id": "sc_001",
                "heading": "INT. COFFEE SHOP - MORNING",
                "summary": "Alice meets Bob at a coffee shop.",
                "shots": [
                    {
                        "shot_id": "sh_001",
                        "block_type": "narration",
                        "text": "The morning sun streamed through the window.",
                        "character_name": "Narrator",
                    },
                    {
                        "shot_id": "sh_002",
                        "block_type": "dialogue",
                        "text": "Hi Bob, it's been a while!",
                        "character_name": "Alice",
                        "character_id": "char_001",
                    },
                    {
                        "shot_id": "sh_003",
                        "block_type": "dialogue",
                        "text": "Alice! Great to see you. How have you been?",
                        "character_name": "Bob",
                        "character_id": "char_002",
                    },
                    {
                        "shot_id": "sh_004",
                        "block_type": "action",
                        "text": "They embrace warmly.",
                        "character_name": "",
                    },
                ],
                "scene_end": "They sit down together.",
            }
        ]
    }
}

_MINI_SCREENPLAY_JSON = json.dumps(_MINI_SCREENPLAY, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# 1. TranslationAgent — translate screenplay to English
# ═══════════════════════════════════════════════════════════════════════════

class TestTranslationAgentLive:
    def test_translate_screenplay_zh_to_en(self):
        _skip_unless_live()
        from agents.translation.agent import TranslationAgent
        from agents.translation.schema import TranslationAgentInput
        from agents.translation.evaluator import TranslationEvaluator

        zh_screenplay = json.dumps({
            "content": {
                "scenes": [{
                    "scene_id": "sc_001",
                    "heading": "内景 咖啡店 - 早晨",
                    "summary": "小明在咖啡店遇到了小红。",
                    "shots": [
                        {"shot_id": "sh_001", "block_type": "narration", "text": "清晨的阳光透过窗户洒了进来。", "character_name": "旁白"},
                        {"shot_id": "sh_002", "block_type": "dialogue", "text": "小红，好久不见！", "character_name": "小明"},
                    ]
                }]
            }
        }, ensure_ascii=False, indent=2)

        llm = _make_llm_client()
        agent = TranslationAgent(llm_client=llm)
        inp = TranslationAgentInput(source_json_text=zh_screenplay, target_language="en")

        output = asyncio.run(agent.generate(inp))
        print(f"\n[TranslationAgent] source_language={output.content.source_language}")
        print(f"[TranslationAgent] translated_payload keys: {list(output.content.translated_payload.keys())}")
        print(f"[TranslationAgent] preview: {json.dumps(output.content.translated_payload, ensure_ascii=False)[:200]}...")

        evaluator = TranslationEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert output.content.target_language == "en"
        assert output.content.translated_payload


# ═══════════════════════════════════════════════════════════════════════════
# 2. TranscriptionAgent — LLM post-processing (materializer needs real audio)
# ═══════════════════════════════════════════════════════════════════════════

class TestTranscriptionAgentLive:
    def test_post_process_raw_segments(self):
        """Exercise the LLM cleanup phase with synthetic raw segments
        pre-seeded on ``TranscriptionAgentInput.raw_segments_json_text``
        — same channel the TranscriptionMaterializer.pre_generate hook
        fills with real STT output in production."""
        import json
        _skip_unless_live()
        from agents.transcription.agent import TranscriptionAgent
        from agents.transcription.schema import TranscriptionAgentInput
        from agents.transcription.evaluator import TranscriptionEvaluator

        llm = _make_llm_client()
        agent = TranscriptionAgent(llm_client=llm)
        raw_payload = {
            "language": "en",
            "segments": [
                {"segment_id": "seg_001", "start_time": 0.0, "end_time": 2.5, "text": "um hello everyone welcome to the show"},
                {"segment_id": "seg_002", "start_time": 3.0, "end_time": 5.5, "text": "today we're going to talk about uh artificial intelligence"},
                {"segment_id": "seg_003", "start_time": 6.0, "end_time": 8.0, "text": "let me introduce our guest doctor Sarah Chen"},
                {"segment_id": "seg_004", "start_time": 8.5, "end_time": 11.0, "text": "thank you for having me it's a pleasure to be here"},
            ],
            "full_text": "um hello everyone welcome to the show today we're going to talk about uh artificial intelligence let me introduce our guest doctor Sarah Chen thank you for having me it's a pleasure to be here",
        }
        inp = TranscriptionAgentInput(
            source_media_path="/tmp/sample_audio.wav",
            raw_segments_json_text=json.dumps(raw_payload, ensure_ascii=False),
        )

        output = asyncio.run(agent.generate(inp))

        print(f"\n[TranscriptionAgent] language={output.content.language}")
        print(f"[TranscriptionAgent] {len(output.content.segments)} segments")
        for s in output.content.segments[:5]:
            print(f"  {s.segment_id}: [{s.start_time}-{s.end_time}] {s.text[:60]}")

        evaluator = TranscriptionEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert len(output.content.segments) >= 3


# ═══════════════════════════════════════════════════════════════════════════
# 4. CompositorAgent — plan composition from screenplay + video + audio
# ═══════════════════════════════════════════════════════════════════════════

class TestCompositorAgentLive:
    def test_plan_composition(self):
        _skip_unless_live()
        from agents.compositor.agent import CompositorAgent
        from agents.compositor.schema import CompositorAgentInput
        from agents.compositor.evaluator import CompositorEvaluator

        video_json = json.dumps({
            "content": {
                "scenes": [{"scene_id": "sc_001", "shot_segments": [
                    {"shot_id": "sh_001", "duration_sec": 4.0},
                    {"shot_id": "sh_002", "duration_sec": 3.5},
                    {"shot_id": "sh_003", "duration_sec": 4.0},
                    {"shot_id": "sh_004", "duration_sec": 2.5},
                ]}]
            }
        }, indent=2)

        llm = _make_llm_client()
        agent = CompositorAgent(llm_client=llm)
        inp = CompositorAgentInput(
            screenplay_json_text=_MINI_SCREENPLAY_JSON,
            video_json_text=video_json,
            audio_json_text='{"content": {"scenes": [{"scene_id": "sc_001"}]}}',
        )

        output = asyncio.run(agent.generate(inp))
        plan = output.content.plan
        print(f"\n[CompositorAgent] {len(plan.transitions)} transitions")
        print(f"  resolution={plan.output_resolution}, fps={plan.output_fps}")
        print(f"  color_grade: tone={plan.color_grade.tone}")
        for t in plan.transitions:
            print(f"  {t.from_shot_id} -> {t.to_shot_id}: {t.transition_type} ({t.duration_ms}ms)")

        evaluator = CompositorEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert output.content.delivery_asset.asset_id == "compositor_final"


# ═══════════════════════════════════════════════════════════════════════════
# 5. StyleTransferAgent — plan style transfer
# ═══════════════════════════════════════════════════════════════════════════

class TestStyleTransferAgentLive:
    def test_plan_anime_style(self):
        _skip_unless_live()
        from agents.style_transfer.agent import StyleTransferAgent
        from agents.style_transfer.schema import StyleTransferAgentInput
        from agents.style_transfer.evaluator import StyleTransferEvaluator

        llm = _make_llm_client()
        agent = StyleTransferAgent(llm_client=llm)
        inp = StyleTransferAgentInput(
            source_video_path="/tmp/source.mp4",
            style_description="Studio Ghibli anime style with soft watercolor textures and warm lighting",
        )

        output = asyncio.run(agent.generate(inp))
        spec = output.content.style_spec
        print(f"\n[StyleTransferAgent] style_description: {spec.style_description[:80]}")
        print(f"  style_prompt: {spec.style_prompt[:80]}")
        print(f"  strength={spec.style_strength}, preserve_motion={spec.preserve_motion}")

        evaluator = StyleTransferEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert spec.style_strength > 0


# ═══════════════════════════════════════════════════════════════════════════
# 6. InpaintAgent — plan depth-based background replacement
# ═══════════════════════════════════════════════════════════════════════════

class TestInpaintAgentLive:
    def test_plan_background_replacement(self):
        _skip_unless_live()
        from agents.inpaint.agent import InpaintAgent
        from agents.inpaint.schema import InpaintAgentInput
        from agents.inpaint.evaluator import InpaintEvaluator

        llm = _make_llm_client()
        agent = InpaintAgent(llm_client=llm)
        inp = InpaintAgentInput(
            source_video_path="/tmp/source.mp4",
            mask_mode="depth_background",
            replacement_description="Replace the background with a futuristic cyberpunk city at night with neon lights and rain",
        )

        output = asyncio.run(agent.generate(inp))
        spec = output.content.inpaint_spec
        print(f"\n[InpaintAgent] mask_mode={spec.mask_mode}")
        print(f"  replacement: {spec.replacement_description[:80]}")
        print(f"  inpaint_prompt: {spec.inpaint_prompt[:80]}")
        print(f"  blend_edge_px={spec.blend_edge_px}")

        evaluator = InpaintEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert spec.mask_mode == "depth_background"


# ═══════════════════════════════════════════════════════════════════════════
# 7. VideoExtendAgent — plan video continuation
# ═══════════════════════════════════════════════════════════════════════════

class TestVideoExtendAgentLive:
    def test_plan_continuation(self):
        _skip_unless_live()
        from agents.video_extend.agent import VideoExtendAgent
        from agents.video_extend.schema import VideoExtendAgentInput
        from agents.video_extend.evaluator import VideoExtendEvaluator

        llm = _make_llm_client()
        agent = VideoExtendAgent(llm_client=llm)
        inp = VideoExtendAgentInput(
            source_video_path="/tmp/clip.mp4",
            continuation_description="The character slowly turns to face the camera, smiles, then walks away into the sunset",
        )

        output = asyncio.run(agent.generate(inp))
        spec = output.content.extension_spec
        print(f"\n[VideoExtendAgent] continuation_prompt: {spec.continuation_prompt[:80]}")
        print(f"  motion: {spec.motion_description[:80]}")
        print(f"  duration={spec.target_duration_seconds}s, maintain_style={spec.maintain_style}")

        evaluator = VideoExtendEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert spec.target_duration_seconds > 0


# ═══════════════════════════════════════════════════════════════════════════
# 8. VideoAnalysisAgent — analyze a real video file (no text-description fallback)
# ═══════════════════════════════════════════════════════════════════════════

_VIDEO_ANALYSIS_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "process-flow-visualizer"
    / "test-assets"
    / "video_analysis_input.mp4"
)


class TestVideoAnalysisAgentLive:
    def test_analyze_real_video(self):
        """End-to-end VideoAnalysisAgent against a real video file.

        This test **requires** a real ``.mp4`` on disk. VideoAnalysisAgent
        does video analysis (scene detection + per-scene visual description
        + entities) — there is no text-description fallback. The input
        schema rejects non-existent paths and non-video MIME types, and the
        LLM client raises if the file is missing; a clean failure is the
        intended behavior when the fixture is absent.
        """
        _skip_unless_live()
        if not _VIDEO_ANALYSIS_FIXTURE.is_file():
            pytest.skip(
                f"video fixture missing: {_VIDEO_ANALYSIS_FIXTURE} "
                f"(required — this agent analyzes real video bytes only)"
            )

        from agents.video_analysis.agent import VideoAnalysisAgent
        from agents.video_analysis.schema import VideoAnalysisAgentInput
        from agents.video_analysis.evaluator import VideoAnalysisEvaluator

        llm = _make_llm_client()
        agent = VideoAnalysisAgent(llm_client=llm)
        inp = VideoAnalysisAgentInput(
            source_video_path=str(_VIDEO_ANALYSIS_FIXTURE)
        )

        output = asyncio.run(agent.generate(inp))

        print(f"\n[VideoAnalysisAgent] title: {output.content.video_summary.title}")
        print(f"  summary: {output.content.video_summary.summary[:100]}")
        print(f"  {len(output.content.scenes)} scenes:")
        for s in output.content.scenes:
            print(f"    {s.scene_id}: [{s.start_time}-{s.end_time}] {s.description[:60]}")

        # Structural checks
        evaluator = VideoAnalysisEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"

        # Content-level sanity: the LLM actually looked at video bytes if
        # it produced a non-trivial summary and at least one scene. If the
        # video never reached Gemini (e.g. the OpenAI-compat bridge dropped
        # the data URL), the LLM would likely return an empty/refusal shape.
        assert output.content.video_summary.summary.strip(), (
            "empty summary — suggests the video bytes never reached the model"
        )
        assert len(output.content.scenes) >= 1, (
            "no scenes detected — suggests the video bytes never reached the model"
        )
        assert len(output.content.scenes) >= 2


# ═══════════════════════════════════════════════════════════════════════════
# 9. HighlightAgent — select highlights based on analysis
# ═══════════════════════════════════════════════════════════════════════════

class TestHighlightAgentLive:
    def test_select_highlights(self):
        _skip_unless_live()
        from agents.highlight.agent import HighlightAgent
        from agents.highlight.schema import HighlightAgentInput
        from agents.highlight.evaluator import HighlightEvaluator

        analysis_json = json.dumps({
            "content": {
                "video_summary": {"title": "Park Morning", "summary": "A morning walk in the park", "genre": "lifestyle", "duration_seconds": 120.0},
                "scenes": [
                    {"scene_id": "scene_001", "start_time": 0.0, "end_time": 30.0, "description": "Wide shot of sunrise over the lake with golden reflections", "mood": "serene", "entities": ["lake", "sun"]},
                    {"scene_id": "scene_002", "start_time": 30.0, "end_time": 55.0, "description": "A heron takes flight from the water, dramatic slow motion", "mood": "dramatic", "entities": ["heron", "water"]},
                    {"scene_id": "scene_003", "start_time": 55.0, "end_time": 75.0, "description": "Children playing on a swing set, laughing", "mood": "joyful", "entities": ["children", "swing"]},
                    {"scene_id": "scene_004", "start_time": 75.0, "end_time": 95.0, "description": "Close-up of dew drops on flower petals", "mood": "contemplative", "entities": ["flowers", "dew"]},
                    {"scene_id": "scene_005", "start_time": 95.0, "end_time": 120.0, "description": "Panoramic sunset view from the hilltop", "mood": "majestic", "entities": ["sunset", "hill"]},
                ],
            }
        }, ensure_ascii=False, indent=2)

        llm = _make_llm_client()
        agent = HighlightAgent(llm_client=llm)
        inp = HighlightAgentInput(
            source_video_path="/tmp/video.mp4",
            analysis_json_text=analysis_json,
            criteria="most visually stunning and emotionally impactful moments",
        )

        output = asyncio.run(agent.generate(inp))
        print(f"\n[HighlightAgent] criteria: {output.content.criteria}")
        print(f"  {len(output.content.clips)} clips selected:")
        for c in output.content.clips:
            print(f"    {c.clip_id}: [{c.start_time}-{c.end_time}] score={c.score:.2f} — {c.reason[:60]}")

        evaluator = HighlightEvaluator()
        errors = evaluator.check_structure(output)
        assert errors == [], f"Structural errors: {errors}"
        assert len(output.content.clips) >= 2


# ═══════════════════════════════════════════════════════════════════════════
# 11. IntakeVideoAgent — video caption generation
# ═══════════════════════════════════════════════════════════════════════════

class TestIntakeVideoAgentLive:
    def test_generate_video_caption(self):
        """IntakeVideoAgent relies on a multimodal video LLM.
        We test the LLM call path using rework_notes to describe the video.
        Gemini rejects empty/invalid video bytes ('Unsupported file URI type'),
        so we generate a minimal-but-valid 1s black mp4 via ffmpeg — content
        doesn't matter because the rework note carries the actual description.
        """
        _skip_unless_live()
        import subprocess
        import tempfile
        from agents.intake.intake_video.agent import IntakeVideoAgent
        from agents.intake.intake_video.schema import IntakeVideoInput
        from agents.intake.intake_video.evaluator import IntakeVideoEvaluator

        llm = _make_llm_client()
        agent = IntakeVideoAgent(llm_client=llm)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            video_path = tmp.name
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=1",
             "-t", "1", "-pix_fmt", "yuv420p", "-movflags", "+faststart", video_path],
            check=True, capture_output=True,
        )
        try:
            inp = IntakeVideoInput(raw_video_path=video_path)

            output = asyncio.run(agent.generate(inp, rework_notes=(
                "The video attachment is unavailable. Based on metadata: "
                "30-second clip of a golden retriever playing fetch on a sunny beach, "
                "waves in the background. Produce a visual_summary from this description."
            )))

            print(f"\n[IntakeVideoAgent] visual_summary: {output.content.visual_summary}")
            print(f"  video_asset.uri: {output.content.video_asset.uri}")

            evaluator = IntakeVideoEvaluator()
            errors = evaluator.check_structure(output)
            assert errors == [], f"Structural errors: {errors}"
            assert output.content.video_asset.uri == video_path
            assert len(output.content.visual_summary) > 10
        finally:
            import os as _os
            _os.path.isfile(video_path) and _os.unlink(video_path)


