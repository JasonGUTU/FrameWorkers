"""AmbienceAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import AmbienceAgent
from .evaluator import AmbienceEvaluator
from .labels import (
    INPUT_LABEL_CREATIVE_BRIEF,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_VIDEO_ANALYSIS,
)
from .materializer import AMBIENCE_FILM_SYS_ID, AmbienceMaterializer
from .schema import AmbienceAgentInput


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    screenplay = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SCREENPLAY)
    )
    analysis = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_ANALYSIS)
    )
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    return AmbienceAgentInput(
        screenplay_json_text=json.dumps(
            screenplay.payload, ensure_ascii=False, indent=2
        ) if screenplay.payload else "",
        video_analysis_json_text=json.dumps(
            analysis.payload, ensure_ascii=False, indent=2
        ) if analysis.payload else "",
        creative_brief_json_text=json.dumps(
            brief.payload, ensure_ascii=False, indent=2
        ) if brief.payload else "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: let a downstream audio-mix step discover ambience
    # tracks. Content (per-bed descriptions) lives in the JSON payload,
    # NOT in caption. See MEMORY:feedback_caption_role_not_content.
    beds = output_dict.get("content", {}).get("beds", [])
    caps: dict = {
        agent_id: {
            "caption": (
                f"[JSON MANIFEST] Ambience planning metadata: "
                f"{len(beds)} bed(s) carrying the LLM-chosen "
                f"description for the film-wide room-tone underlay. "
                f"Read by the audio-mix LLM for mix planning."
            ),
            "scope": "global",
        },
    }
    if beds:
        caps[AMBIENCE_FILM_SYS_ID] = {
            "caption": (
                "[BINARY WAV FILE · mime=audio/wav · sys_id "
                "aud_amb_film] Ambient room-tone audio bytes for the "
                "film-wide atmospheric underlay. Consumed by the "
                "audio-mix materializer via ffmpeg."
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
                "The screenplay — I read the dominant location(s) "
                "across scenes[*] to pick a continuous room-tone "
                "underlay."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "A scene-level video-analysis report — scenes with "
                "setting / mood. I aggregate scenes[*].setting into a "
                "single dominant environment."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            optional=True,
            description=(
                "The user's verbatim natural-language brief for the "
                "whole pipeline (auto-persisted from chat / text upload). "
                "Often the most direct environment signal — the user "
                "names locations / weather / atmosphere directly "
                "('rainy-night city street', 'jungle ambience', 'cafe "
                "interior'). Read alongside [screenplay] / "
                "[video_analysis]; any one of the three is enough."
            ),
        ),
    ],
    output_description=(
        "ambience_bed (one film-wide room-tone underlay)."
    ),
    purpose_and_trigger=(
        """Generate ONE film-wide ambient sound bed (room tone / environmental underlay). All three inputs (screenplay, video_analysis, creative_brief) are individually optional — at least one must carry a usable environment signal. Trigger: include only when the user explicitly mentions ambient / atmospheric / environmental sound in the goal (e.g. 'add ambient sounds', 'layer in rain + traffic', 'jungle ambience'). Silence is the default — do not include unless the goal warrants."""
    ),
    input_preamble=(
        "I generate one global ambient room-tone underlay that covers "
        "the entire film. I pick the environment from any available "
        "content source — screenplay, video analysis, or the user's "
        "brief — whichever is wired up."
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
