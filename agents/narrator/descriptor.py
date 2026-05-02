"""NarratorAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import NarratorAgent
from .evaluator import NarratorEvaluator
from .labels import INPUT_LABEL_NARRATION_SCRIPT
from .materializer import (
    NARRATOR_AUDIO_SYS_ID,
    NARRATOR_SEGMENT_TIMING_SYS_ID,
    NARRATOR_SRT_SYS_ID,
    NarratorMaterializer,
)
from .schema import NarratorAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    narration = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_NARRATION_SCRIPT)
    )
    return NarratorAgentInput(
        narration_script_json_text=json.dumps(
            narration.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Four separate captions so downstream consumers can resolve each
    # artifact to the right compositor input label:
    #   - NarratorAgent JSON snapshot → dev/debug, not routed
    #   - aud_narrator_full wav       → audio_package label
    #   - narrator_srt JSON           → subtitle_tracks label (SubtitleAgent shape)
    #   - narrator_segment_timing JSON → segment_timing label (slideshow mode)
    content = output_dict.get("content", {})
    metrics = output_dict.get("metrics", {})
    line_count = metrics.get("line_count", len(content.get("lines", [])))
    seg_count = metrics.get("segment_count", 0)
    total_dur = content.get("total_duration_sec", 0.0)
    language = content.get("language", "") or "und"

    return {
        agent_id: {
            "caption": (
                f"[JSON MANIFEST] Narrator session manifest: "
                f"{line_count} line(s), {seg_count} segment(s), total "
                f"{total_dur:.1f}s. Per-line / per-segment timing. "
                f"Dev/debug view; downstream consumption goes through "
                f"the sibling audio / srt / timing artifacts."
            ),
            "scope": "global",
        },
        NARRATOR_AUDIO_SYS_ID: {
            "caption": (
                f"[BINARY WAV FILE · mime=audio/wav · sys_id "
                f"aud_narrator_full] Narrator voiceover audio bytes "
                f"({total_dur:.1f}s, language={language}). Concatenated "
                f"TTS for an illustrated-storytelling video. Consumed "
                f"by the audio-mix or compositor materializer."
            ),
            "scope": "global",
        },
        NARRATOR_SRT_SYS_ID: {
            "caption": (
                f"[JSON MANIFEST · SRT cues] Narrator subtitle track "
                f"(language={language}): one cue per narration line, "
                f"timed against the narrator audio. Consumed by the "
                f"compositor step as a burn-in subtitle source."
            ),
            "scope": "global",
        },
        NARRATOR_SEGMENT_TIMING_SYS_ID: {
            "caption": (
                f"[JSON MANIFEST] Narrator per-segment timing: "
                f"{seg_count} segment(s) with start / end / duration "
                f"seconds. Used by a slideshow compositor to set how "
                f"long each illustration stays on screen."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> NarratorMaterializer:
    return NarratorMaterializer(audio_service=services["audio_service"])


SPEC = AgentSpec(
    agent_id="NarratorAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_NARRATION_SCRIPT,
            cardinality="single",
            description=(
                "The narration script manifest (JSON) carrying segments and "
                "lines — per-line TTS text plus pause_after_ms. Produced by "
                "the narration step. I TTS each line, concat with per-line "
                "pauses, and emit a full narrator wav plus timed SRT plus "
                "per-segment timing for slideshow alignment."
            ),
        ),
    ],
    output_description=(
        "narrator_voiceover (full wav + timed SRT + per-segment timing) for "
        "an illustrated-storytelling video."
    ),
    purpose_and_trigger=(
        """Render a narration script as a continuous narrator voiceover: per-line TTS concatenated with inter-line pauses, emitted as a full wav + a line-level SRT + a per-segment timing manifest for slideshow alignment. Trigger: user asks for narrated voiceover where the script is line-by-line (not per-shot dialogue). Requires a narration script as upstream input."""
    ),
    input_preamble=(
        "I render the narration script as a continuous narrator voiceover. "
        "I TTS each line individually (so timing is per-line accurate), insert "
        "pauses, and emit a full wav plus a timed SRT plus a per-segment "
        "timing manifest the slideshow compositor uses."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: NarratorAgent(llm_client=llm),
    evaluator_factory=NarratorEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
)
