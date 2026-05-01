"""MusicAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_audio_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import MusicAgent
from .evaluator import MusicEvaluator
from .labels import (
    INPUT_LABEL_CREATIVE_BRIEF,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_VIDEO_ANALYSIS,
)
from .materializer import MUSIC_FILM_SYS_ID, MusicMaterializer
from .schema import MusicAgentInput


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
    return MusicAgentInput(
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
    # Caption role: let a downstream audio-mix step discover BGM cues.
    # Content (mood free-text keywords) lives in the JSON payload, NOT
    # in caption. See MEMORY:feedback_caption_role_not_content.
    cues = output_dict.get("content", {}).get("cues", [])
    caps: dict = {
        agent_id: {
            "caption": (
                f"Background music pack (JSON manifest): {len(cues)} "
                f"cue(s). Carries the LLM-chosen mood for the film-wide "
                f"BGM underlay. Consumed by the audio-mix step's LLM "
                f"for mix planning."
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
                "The screenplay — I read its overall mood/tone "
                "(genre / tone_keywords / per-shot descriptive text) "
                "to pick a film-wide music style."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "A scene-level video-analysis report — scenes with mood "
                "and a video_summary.genre. I aggregate scene moods into "
                "a single film-wide mood."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            optional=True,
            description=(
                "The user's verbatim natural-language brief for the "
                "whole pipeline (auto-persisted from chat / text upload). "
                "Often the most direct mood signal — the user names "
                "instruments / atmosphere directly ('gentle slow piano "
                "score', 'tense orchestral theme', 'lullaby BGM'). "
                "Read alongside [screenplay] / [video_analysis]; any "
                "one of the three is enough."
            ),
        ),
    ],
    output_description="music_cue (one film-wide background music track).",
    purpose_and_trigger=(
        """Generate ONE film-wide background music track. All three inputs (screenplay, video_analysis, creative_brief) are individually optional — at least one must carry a usable mood signal. Trigger: include only when the user explicitly mentions music / BGM / score / soundtrack in the goal (e.g. 'add some music', 'with orchestral theme', 'piano score under narrator'). Silence is the default — do not include unless the goal warrants."""
    ),
    input_preamble=(
        "I generate one global background music track for the whole film. "
        "I pick the mood from any available content source — screenplay, "
        "video analysis, or the user's brief — whichever is wired up."
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
