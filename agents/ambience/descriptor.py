"""AmbienceAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import AmbienceAgent
from .evaluator import AmbienceEvaluator
from .labels import INPUT_LABEL_SCREENPLAY, INPUT_LABEL_VIDEO_ANALYSIS
from .materializer import AMBIENCE_FILM_SYS_ID, AmbienceMaterializer
from .schema import AmbienceAgentInput


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    screenplay = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SCREENPLAY)
    )
    analysis = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_ANALYSIS)
    )
    return AmbienceAgentInput(
        screenplay_json_text=json.dumps(
            screenplay.payload, ensure_ascii=False, indent=2
        ) if screenplay.payload else "",
        video_analysis_json_text=json.dumps(
            analysis.payload, ensure_ascii=False, indent=2
        ) if analysis.payload else "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: let a downstream audio-mix step discover ambience
    # tracks. Content (per-bed descriptions) lives in the JSON payload,
    # NOT in caption. See MEMORY:feedback_caption_role_not_content.
    beds = output_dict.get("content", {}).get("beds", [])
    caps: dict = {
        agent_id: {
            "caption": (
                f"Ambience pack (JSON manifest): {len(beds)} bed(s). "
                f"Carries description + duration target for the "
                f"film-wide room-tone underlay. Consumed by "
                f"the audio-mix step's LLM for mix planning."
            ),
            "scope": "global",
        },
    }
    if beds:
        caps[AMBIENCE_FILM_SYS_ID] = {
            "caption": (
                "Ambient room-tone audio track (wav) — film-wide "
                "atmospheric underlay. Consumed by a downstream audio-mix step "
                "for merging with dialogue / music tracks."
            ),
            "scope": "global",
        }
    return caps


def materializer_factory(services: dict) -> AmbienceMaterializer:
    return AmbienceMaterializer(audio_service=services["audio_service"])


SPEC = AgentSpec(
    agent_id="AmbienceAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SCREENPLAY,
            cardinality="single",
            optional=True,
            description=(
                "The screenplay — I read the dominant location(s) to "
                "pick a continuous room-tone underlay, and count spoken "
                "words + action shots across every scene to size a "
                "single global bed. Present on newly-created films; "
                "absent on existing-video edit flows — in that case "
                "route a video_analysis artifact instead."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "A scene-level video-analysis report — scenes with "
                "setting / mood + video_summary.duration_seconds. Present "
                "on existing-video edit flows where there is no "
                "screenplay; the agent derives dominant environment from "
                "scenes[*].setting and uses "
                "video_summary.duration_seconds as the bed duration "
                "target. At least one of {screenplay, video_analysis} "
                "must be supplied."
            ),
        ),
    ],
    output_description=(
        "ambience_bed (one film-wide room-tone underlay)."
    ),
    purpose_and_routing=(
        """Generate ONE film-wide ambient sound bed (room tone / environmental underlay). Trigger: cinematic default alongside music for newly-created films (unless user specifies music-only), or user asks for atmospheric beds (rain, wind, crowd, room tone) on existing video."""
    ),
    input_preamble=(
        "I generate one global ambient room-tone underlay that covers "
        "the entire film. I prefer a screenplay when available and "
        "fall back to a scene-level video analysis (mood + duration) "
        "on existing-video edit flows."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: AmbienceAgent(llm_client=llm),
    evaluator_factory=AmbienceEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
)
