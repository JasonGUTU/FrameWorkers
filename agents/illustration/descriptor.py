"""IllustrationAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_image_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import IllustrationAgent
from .evaluator import IllustrationEvaluator
from .labels import INPUT_LABEL_NARRATION_SCRIPT
from .materializer import IllustrationMaterializer
from .schema import IllustrationAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    narration = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_NARRATION_SCRIPT)
    )
    return IllustrationAgentInput(
        narration_script_json_text=json.dumps(
            narration.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # JSON snapshot caption describes the manifest's role (list of images).
    # Each individual image also gets its own caption under its sys_id so
    # a downstream compositor step can find the full ordered illustration
    # set by semantic-typed label resolution.
    content = output_dict.get("content", {})
    illustrations = content.get("illustrations", [])
    count = len(illustrations)

    caps: dict = {
        agent_id: {
            "caption": (
                f"Illustration manifest (JSON): {count} image(s) aligned to "
                f"narration segments. Consumed by the compositor step when "
                f"assembling an illustrated-storytelling slideshow."
            ),
            "scope": "global",
        },
    }

    for i, entry in enumerate(illustrations, start=1):
        if not isinstance(entry, dict):
            continue
        seg_id = entry.get("segment_id") or f"seg_{i:03d}"
        sys_id = f"illustration_{seg_id}"
        caps[sys_id] = {
            "caption": (
                f"Illustration image (png) for narration segment {seg_id} "
                f"(order {i}/{count}). One frame of an illustrated-"
                f"storytelling video; consumed by the compositor step as "
                f"part of the image sequence that fills the video track."
            ),
            "scope": "global",
        }

    return caps


def materializer_factory(services: dict) -> IllustrationMaterializer:
    return IllustrationMaterializer(image_service=services["image_service"])


SPEC = AgentSpec(
    agent_id="IllustrationAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_NARRATION_SCRIPT,
            cardinality="single",
            description=(
                "The narration script manifest (JSON) carrying segments "
                "with per-segment image_prompt and a cross-segment "
                "overall_style art-style anchor. Produced by the narration "
                "step. I generate one illustration per segment, using the "
                "first image as a visual style reference for the rest."
            ),
        ),
    ],
    output_description=(
        "illustration_manifest (one png image per narration segment, "
        "aligned by segment_id, with cross-segment style consistency)."
    ),
    purpose_and_trigger=(
        """Generate one illustration per segment described in a narration script — uses the first generated image as a visual style reference for the rest to keep cross-segment style consistency. Trigger: user asks for an illustrated audiobook / picture-book / story-time slideshow video where each narrated segment gets its own still image. Requires a narration script as upstream input."""
    ),
    input_preamble=(
        "I produce one illustration per narration segment. I read the "
        "upstream narration script and generate images with cross-segment "
        "style consistency via a first-frame-as-anchor strategy."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: IllustrationAgent(llm_client=llm),
    evaluator_factory=IllustrationEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"image_service": lambda ctx: select_image_service()},
    materializer_factory=materializer_factory,
)
