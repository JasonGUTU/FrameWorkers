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
    # Caption role: this artifact IS an SRT-shaped subtitle source
    # ready for direct compositor burn-in (each segment carries
    # start/end timestamps + text, exactly the shape an SRT cue
    # needs). The phrase ``SRT-shaped subtitle artifact`` is what
    # InputResolver matches against CompositorAgent's [subtitle_tracks]
    # label description — earlier wording ``input to a downstream
    # subtitle step`` was read by the LLM resolver as "needs a
    # SubtitleAgent in between" and dropped the routing.
    # See MEMORY:feedback_caption_role_not_content (count metric only,
    # no per-line text inserted).
    content = output_dict.get("content", {})
    lang = content.get("language", "?")
    seg_count = len(content.get("segments", []))
    return {
        agent_id: {
            "caption": (
                f"Transcript ({lang}): {seg_count} timestamped segment(s). "
                f"SRT-shaped subtitle artifact — ready for direct "
                f"burn-in by a compositor's subtitle track (each "
                f"segment is one SRT cue with start/end seconds + "
                f"text). Also usable as the 'source text' input to a "
                f"translation step when bilingual subtitles are needed."
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
        "Each segment carries start/end timestamps and per-segment text, "
        "making it a drop-in 'timed source text' artifact suitable for "
        "subtitle burn-in or for translation into another language while "
        "preserving the segment timing."
    ),
    purpose_and_trigger=(
        """Speech-to-text on an existing video's audio track — produces timestamped transcript segments matching what's actually heard. Trigger: a deliverable needs a subtitle / caption track or a translation source and a screenplay document is not available (e.g. user uploaded a video with spoken content; transcribe its audio for downstream subtitling or translation)."""
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
