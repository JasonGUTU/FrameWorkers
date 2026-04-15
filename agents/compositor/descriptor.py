"""CompositorAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import CompositorAgent
from .labels import (
    INPUT_LABEL_VIDEO_PACKAGE,
    INPUT_LABEL_AUDIO_PACKAGE,
    INPUT_LABEL_SUBTITLE_TRACKS,
    INPUT_LABEL_SCREENPLAY,
)
from .schema import CompositorAgentInput
from .evaluator import CompositorEvaluator
from .materializer import CompositorMaterializer


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
    audio_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_AUDIO_PACKAGE)
    )
    subtitle = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SUBTITLE_TRACKS)
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
        subtitle_json_text=json.dumps(
            subtitle.payload or {}, ensure_ascii=False, indent=2
        ) if subtitle.payload else "",
        video_file_path=video_pkg.path,
        audio_file_path=audio_pkg.path,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    plan = content.get("plan", {})
    transitions = len(plan.get("transitions", []))
    res = plan.get("output_resolution", "?")
    return {
        agent_id: {
            "caption": (
                f"Final composited video ({res}): {transitions} transition(s), "
                f"audio mix, subtitle burn-in. Ready for delivery."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> CompositorMaterializer:
    return CompositorMaterializer(compositor_service=services["compositor_service"])


CATALOG_ENTRY = (
    "CompositorAgent\n"
    "  - Input: a video artifact (required) + optional audio mix + optional subtitle tracks "
    "+ optional screenplay (for transition/color-grade hints).\n"
    "  - Output: final_video (composited MP4 with audio, subtitles, transitions).\n"
    "  - Purpose: Mux video + audio, burn subtitles, add transitions, apply color grade — "
    "produce a single deliverable MP4. Run me as the LAST step ONLY when the user wants a "
    "fully composited deliverable that combines video with audio and/or subtitles. SKIP me "
    "when the deliverable is itself a single-track artifact (e.g. only subtitles, only style-"
    "transferred video, only inpainted video, only a transcript) — in those cases the "
    "single-track artifact IS the final output."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="CompositorAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: CompositorAgent(llm_client=llm),
    evaluator_factory=CompositorEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "compositor_service": lambda ctx: __import__("inference.generation", fromlist=["select_compositor_service"]).select_compositor_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I compose the final deliverable video by muxing video clips with "
        "audio tracks, burning subtitles, adding transitions between shots, "
        "and applying color grading.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay for scene/shot structure context.\n\n"
        f"[{INPUT_LABEL_VIDEO_PACKAGE}] (single)\n"
        "The video package with per-shot clips and timing.\n\n"
        f"[{INPUT_LABEL_AUDIO_PACKAGE}] (single)\n"
        "The audio package with narration, music, ambience, and final mix.\n\n"
        f"[{INPUT_LABEL_SUBTITLE_TRACKS}] (single)\n"
        "Optional subtitle tracks (SRT cues) to burn into the video."
    ),
)
