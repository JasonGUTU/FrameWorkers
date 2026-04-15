"""TranscriptionAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import TranscriptionAgent
from .labels import INPUT_LABEL_SOURCE_MEDIA
from .schema import TranscriptionAgentInput
from .evaluator import TranscriptionEvaluator
from .materializer import TranscriptionMaterializer


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
                f"Transcript ({lang}): {seg_count} segment(s) with timestamps. "
                f"Speech-to-text from source media."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> TranscriptionMaterializer:
    return TranscriptionMaterializer(transcription_service=services["transcription_service"])


CATALOG_ENTRY = (
    "TranscriptionAgent\n"
    "  - Input: any media artifact containing speech (an ingested audio file or video file).\n"
    "  - Output: transcript (timestamped segments + full text + detected language + "
    "speaker attribution).\n"
    "  - Purpose: Speech-to-text. The transcript can be a deliverable on its own (when the "
    "user just wants 'transcribe this'), or feed downstream translation / subtitle generation "
    "for existing-media workflows that have no screenplay. Run me whenever the user asks to "
    "transcribe, translate audio/video, or add subtitles to an existing video lacking a script."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="TranscriptionAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: TranscriptionAgent(llm_client=llm),
    evaluator_factory=TranscriptionEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "transcription_service": lambda ctx: __import__("inference.generation", fromlist=["select_transcription_service"]).select_transcription_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I transcribe audio/video files into timestamped text with speaker "
        "attribution.\n\n"
        f"[{INPUT_LABEL_SOURCE_MEDIA}] (single)\n"
        "An audio or video file to transcribe. Accepts any format supported "
        "by the transcription service (mp3, wav, mp4, etc.). The file path "
        "is passed directly to the STT service."
    ),
)
