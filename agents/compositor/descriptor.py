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
    INPUT_LABEL_ILLUSTRATION_SEQUENCE,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_SEGMENT_TIMING,
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

    # Slideshow mode — an illustrated-storytelling chain routes its
    # IllustrationAgent output (one image artifact per segment) through
    # the [illustration_sequence] collection label, and NarratorAgent's
    # segment_timing JSON through [segment_timing]. We sort the image
    # paths by their embedded ``seg_NNN`` token so the materializer
    # iterates them in render order (InputResolver does not guarantee
    # collection-label ordering).
    illustration_entries = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_ILLUSTRATION_SEQUENCE)
    )
    illustration_image_paths = _sort_image_paths_by_segment(
        [e.path for e in illustration_entries if e.path]
    )

    timing = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SEGMENT_TIMING)
    )
    segment_timing_json_text = (
        json.dumps(timing.payload, ensure_ascii=False, indent=2)
        if timing.payload else ""
    )

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
        illustration_image_paths=illustration_image_paths,
        segment_timing_json_text=segment_timing_json_text,
    )


def _sort_image_paths_by_segment(paths: list[str]) -> list[str]:
    """Order illustration paths by their embedded ``seg_NNN`` token.

    IllustrationMaterializer writes each image as
    ``illustration_seg_NNN.png`` via sys_id, so the segment order is
    recoverable from the filename without re-fetching captions. Paths
    without a parseable segment token sink to the end in their original
    relative order.
    """
    import re
    _SEG_RE = re.compile(r"seg_(\d+)")

    def _key(p: str) -> tuple[int, int, str]:
        m = _SEG_RE.search(p)
        if m:
            return (0, int(m.group(1)), p)
        return (1, 0, p)

    return sorted(paths, key=_key)


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
            optional=True,
            description=(
                "Assembled video's JSON manifest — scenes, "
                "shot_segments, per-clip timing. LLM reads this to "
                "plan transitions and grade against the video "
                "structure. Targets the JSON/manifest artifact "
                "specifically, NOT the mp4 file. Optional because "
                "illustrated-storytelling flows produce an image "
                "sequence instead (see illustration_sequence); exactly "
                "one of {video_package, illustration_sequence} must be "
                "present."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_FILE,
            cardinality="single",
            optional=True,
            description=(
                "The final assembled mp4 video file on disk (binary "
                "artifact, mime=video/mp4). Materializer reads its "
                "path and passes it to ffmpeg for composition. "
                "Targets the mp4 binary specifically, NOT the JSON "
                "manifest. Optional — absent on illustrated-storytelling "
                "flows where there is no assembled mp4 to mux (the "
                "video track is rendered from illustration_sequence "
                "images)."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_ILLUSTRATION_SEQUENCE,
            cardinality="collection",
            optional=True,
            description=(
                "Ordered per-segment still illustrations (png images) "
                "for an illustrated-storytelling / audiobook-with-"
                "pictures video. Present only on illustrated-"
                "storytelling flows produced by an illustration step; "
                "mutually exclusive with video_package / video_file. "
                "Every image is burned as one slide whose on-screen "
                "duration is driven by segment_timing."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_SEGMENT_TIMING,
            cardinality="single",
            optional=True,
            description=(
                "Per-segment timing manifest (JSON: "
                "``content.segment_timings = [{segment_id, start_sec, "
                "end_sec, duration_sec, line_ids}, ...]``). Produced by "
                "the narrator step on illustrated-storytelling flows. "
                "Required whenever illustration_sequence is present — "
                "tells the compositor how long each illustration stays "
                "on screen so the image sequence aligns with the "
                "narrator audio."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AUDIO_PACKAGE,
            cardinality="single",
            optional=True,
            description=(
                "Final-audio-mix JSON envelope (planning manifest; "
                "carries no audio asset fields — the wav is a separate "
                "binary artifact). Optional — present iff an audio-mix "
                "step ran. Targets the JSON/manifest artifact "
                "specifically, NOT the wav file."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_AUDIO_FILE,
            cardinality="single",
            optional=True,
            description=(
                "The final mixed wav audio file on disk (binary "
                "artifact, mime=audio/wav). Optional — present iff "
                "an audio-mix step ran. Materializer muxes this onto "
                "the video via ffmpeg. Targets the wav binary, NOT "
                "the JSON descriptor."
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
                "(e.g. a source-language SRT + a translated SRT, both "
                "burned simultaneously)."
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
