"""MusicAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import MusicAgent
from .evaluator import MusicEvaluator
from .labels import INPUT_LABEL_SCREENPLAY, INPUT_LABEL_VIDEO_ANALYSIS
from .materializer import MUSIC_FILM_SYS_ID, MusicMaterializer
from .schema import MusicAgentInput


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    screenplay = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SCREENPLAY)
    )
    analysis = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_ANALYSIS)
    )
    return MusicAgentInput(
        screenplay_json_text=json.dumps(
            screenplay.payload, ensure_ascii=False, indent=2
        ) if screenplay.payload else "",
        video_analysis_json_text=json.dumps(
            analysis.payload, ensure_ascii=False, indent=2
        ) if analysis.payload else "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: let a downstream audio-mix step discover BGM cues.
    # Content (mood free-text keywords) lives in the JSON payload, NOT
    # in caption. See MEMORY:feedback_caption_role_not_content.
    cues = output_dict.get("content", {}).get("cues", [])
    caps: dict = {
        agent_id: {
            "caption": (
                f"Background music pack (JSON manifest): {len(cues)} "
                f"cue(s). Carries mood + duration target for the "
                f"film-wide BGM underlay. Consumed by the audio-mix step's "
                f"LLM for mix planning."
            ),
            "scope": "global",
        },
    }
    if cues:
        caps[MUSIC_FILM_SYS_ID] = {
            "caption": (
                "Background music audio track (wav) — film-wide "
                "music underlay. Consumed by a downstream audio-mix step for "
                "merging with dialogue / ambience tracks."
            ),
            "scope": "global",
        }
    return caps


def materializer_factory(services: dict) -> MusicMaterializer:
    return MusicMaterializer(audio_service=services["audio_service"])


SPEC = AgentSpec(
    agent_id="MusicAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SCREENPLAY,
            cardinality="single",
            optional=True,
            description=(
                "The screenplay — I read its overall mood/tone to pick a "
                "film-wide music style and count spoken words + action "
                "shots across every scene to size a single global cue. "
                "Present on newly-created films; absent on existing-video "
                "edit flows — in that case route a video_analysis "
                "artifact instead."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "A scene-level video-analysis report — scenes with mood "
                "+ video_summary.duration_seconds. Present on existing-"
                "video edit flows where there is no screenplay; the "
                "agent derives overall mood from the scene moods and "
                "uses video_summary.duration_seconds as the cue duration "
                "target. At least one of {screenplay, video_analysis} "
                "must be supplied."
            ),
        ),
    ],
    output_description="music_cue (one film-wide background music track).",
    purpose_and_routing=(
        """Generate ONE film-wide background music track. Trigger: cinematic default for any newly-created film deliverable (unless user specifies ambience-only), or user explicitly requests music / BGM / soundtrack / score on an existing video."""
    ),
    input_preamble=(
        "I generate one global background music track for the whole film. "
        "I prefer a screenplay when available (rich mood + shot counts) "
        "and fall back to a scene-level video analysis (mood + duration) "
        "on existing-video edit flows."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: MusicAgent(llm_client=llm),
    evaluator_factory=MusicEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
)
