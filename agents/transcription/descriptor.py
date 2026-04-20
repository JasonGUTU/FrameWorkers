"""TranscriptionAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import TranscriptionAgent
from .evaluator import TranscriptionEvaluator
from .labels import INPUT_LABEL_SOURCE_MEDIA
from .materializer import TranscriptionMaterializer
from .schema import TranscriptionAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    entry = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_MEDIA)
    )
    return TranscriptionAgentInput(
        source_media_path=entry.path,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    lang = content.get("language", "?")
    seg_count = len(content.get("segments", []))
    return {
        agent_id: {
            "caption": (
                f"Transcript ({lang}): {seg_count} segment(s) with "
                f"timestamps. Speech-to-text from source media. Usable "
                f"as the 'timed source text' input to a downstream subtitle step, or "
                f"as the 'source text' input to a downstream translation step."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> TranscriptionMaterializer:
    return TranscriptionMaterializer(
        transcription_service=services["transcription_service"]
    )


SPEC = AgentSpec(
    agent_id="TranscriptionAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_MEDIA,
            cardinality="single",
            description=(
                "An audio or video file to transcribe. Accepts any format "
                "supported by the transcription service (mp3, wav, mp4, "
                "etc.). The file path is passed directly to the STT "
                "service."
            ),
        ),
    ],
    output_description=(
        "transcript (timestamped segments + full text + detected language). "
        "Shape is compatible with SubtitleAgent's 'timed source text' slot "
        "— SubtitleAgent can consume me the same way it consumes a "
        "screenplay."
    ),
    purpose_and_routing=(
        """Speech-to-text on an existing video's audio track, producing timestamped transcript segments. Trigger: existing-video flow needing subtitles or translation, with no screenplay available."""
    ),
    input_preamble=(
        "I transcribe audio/video files into timestamped text."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: TranscriptionAgent(llm_client=llm),
    evaluator_factory=TranscriptionEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "transcription_service": lambda ctx: __import__(
            "inference.generation",
            fromlist=["select_transcription_service"],
        ).select_transcription_service(),
    },
    materializer_factory=materializer_factory,
)
