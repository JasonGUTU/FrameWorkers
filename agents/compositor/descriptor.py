"""CompositorAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import CompositorAgent
from .evaluator import CompositorEvaluator
from .labels import (
    INPUT_LABEL_AUDIO_FILE,
    INPUT_LABEL_AUDIO_PACKAGE,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_SUBTITLE_TRACKS,
    INPUT_LABEL_VIDEO_FILE,
    INPUT_LABEL_VIDEO_PACKAGE,
)
from .materializer import CompositorMaterializer
from .schema import CompositorAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    screenplay = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SCREENPLAY)
    )
    video_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_PACKAGE)
    )
    video_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_FILE)
    )
    audio_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_AUDIO_PACKAGE)
    )
    audio_file = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_AUDIO_FILE)
    )
    subtitle_entries = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_SUBTITLE_TRACKS)
    )
    subtitle_json_texts = [
        json.dumps(e.payload, ensure_ascii=False, indent=2)
        for e in subtitle_entries
        if e.payload
    ]

    return CompositorAgentInput(
        screenplay_json_text=json.dumps(
            screenplay.payload or {}, ensure_ascii=False, indent=2
        ),
        video_json_text=json.dumps(
            video_pkg.payload or {}, ensure_ascii=False, indent=2
        ) if video_pkg.payload else "",
        audio_json_text=json.dumps(
            audio_pkg.payload or {}, ensure_ascii=False, indent=2
        ) if audio_pkg.payload else "",
        subtitle_json_texts=subtitle_json_texts,
        # Binary artifact paths come from their dedicated ``*_file``
        # labels, NOT from the sibling ``*_package`` entries — the
        # InputResolver routes mp4/wav files into ``*_file`` and JSON
        # manifests into ``*_package`` based on each label's description.
        video_file_path=video_file.path or "",
        audio_file_path=audio_file.path or "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    plan = content.get("plan", {})
    transitions = len(plan.get("transitions", []))
    res = plan.get("output_resolution", "?")
    return {
        agent_id: {
            "caption": (
                f"Final composited video ({res}): {transitions} "
                f"transition(s), audio mix, subtitle burn-in. Ready for "
                f"delivery."
            ),
            "scope": "global",
        },
        "compositor_final": {
            "caption": (
                "Final delivered video binary (mp4) — the complete "
                "composited output with transitions, audio mix, and "
                "(optional) subtitle burn-in. Terminal deliverable of "
                "the creative pipeline."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> CompositorMaterializer:
    return CompositorMaterializer(
        compositor_service=services["compositor_service"]
    )


SPEC = AgentSpec(
    agent_id="CompositorAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SCREENPLAY,
            cardinality="single",
            optional=True,
            description=(
                "Optional screenplay for scene/shot structure context — "
                "present on newly-created films, absent on existing-video "
                "edit flows (style transfer / video extend / highlight / "
                "transcription+subtitle). When absent the agent plans the "
                "composition from the video_package alone."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_PACKAGE,
            cardinality="single",
            description=(
                "VideoAgent's JSON manifest — scenes, shot_segments, "
                "per-clip timing. LLM reads this to plan transitions "
                "and grade against the video structure. Targets the "
                "JSON/manifest artifact specifically, NOT the mp4 file."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_FILE,
            cardinality="single",
            description=(
                "The final assembled mp4 video file on disk (binary "
                "artifact, mime=video/mp4). Materializer reads its "
                "path and passes it to ffmpeg for composition. "
                "Targets the mp4 binary specifically, NOT the JSON "
                "manifest."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AUDIO_PACKAGE,
            cardinality="single",
            optional=True,
            description=(
                "AudioMixAgent's JSON envelope (planning manifest; "
                "carries no audio asset fields — the wav is a separate "
                "binary artifact). Optional — present iff AudioMixAgent "
                "ran. Targets the JSON/manifest artifact specifically, "
                "NOT the wav file."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AUDIO_FILE,
            cardinality="single",
            optional=True,
            description=(
                "The final mixed wav audio file on disk (binary "
                "artifact, mime=audio/wav). Optional — present iff "
                "AudioMixAgent ran. Materializer muxes this onto the "
                "video via ffmpeg. Targets the wav binary, NOT the "
                "JSON descriptor."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_SUBTITLE_TRACKS,
            cardinality="collection",
            optional=True,
            description=(
                "Optional subtitle artifacts (SRT cues) to burn into the "
                "video. Zero, one, or many — resolver routes every "
                "subtitle-shaped artifact here so bilingual / "
                "multilingual flows can supply one artifact per language "
                "(e.g. SubtitleAgent source-lang SRT + TranslationAgent "
                "translated SRT, both burned simultaneously)."
            ),
        ),
    ],
    output_description=(
        "final_video (composited MP4 with audio, subtitles, transitions)."
    ),
    purpose_and_routing=(
        """Final deliverable: mux video + final audio + subtitle tracks into a single polished mp4. Terminal step that produces the fully composited output."""
    ),
    input_preamble=(
        "I compose the final deliverable video by muxing video clips "
        "with audio tracks, burning subtitles, adding transitions "
        "between shots, and applying color grading."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: CompositorAgent(llm_client=llm),
    evaluator_factory=CompositorEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "compositor_service": lambda ctx: __import__(
            "inference.generation", fromlist=["select_compositor_service"]
        ).select_compositor_service(),
    },
    materializer_factory=materializer_factory,
)
