"""InpaintAgent descriptor — built from a single AgentSpec.

⚠ INTENTIONALLY_UNREGISTERED
This descriptor is NOT added to ``AGENT_REGISTRY`` in ``agents/__init__.py``.
The agent code is complete (agent / schema / evaluator / materializer) but the
product has deliberately not exposed video-inpainting functionality; the
Director will therefore never route to InpaintAgent. To enable: import
``DESCRIPTOR`` in ``agents/__init__.py`` and add ``_inpaint_desc`` to the
registry list.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import InpaintAgent
from .evaluator import InpaintEvaluator
from .labels import INPUT_LABEL_MASK, INPUT_LABEL_SOURCE_VIDEO
from .materializer import InpaintMaterializer
from .schema import InpaintAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )
    mask = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_MASK)
    )

    mask_mode = "manual"
    replacement_desc = ""
    if mask.payload:
        mask_mode = mask.payload.get("mask_mode", "manual")
        replacement_desc = mask.payload.get("replacement_description", "")
    elif mask.caption:
        replacement_desc = mask.caption

    return InpaintAgentInput(
        source_video_path=video.path,
        mask_mode=mask_mode,
        mask_path=mask.path,
        replacement_description=replacement_desc,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: signal "inpaint output video" + mask_mode (closed
    # enum, helps consumers that care about segmentation vs depth).
    # Content (replacement_description free text) lives in the JSON
    # payload, NOT in caption.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    spec = content.get("inpaint_spec", {})
    mode = spec.get("mask_mode", "?")
    return {
        agent_id: {
            "caption": (
                f"Inpainted video (mask_mode={mode}): object-removal / "
                f"region-replacement edit applied. Structured manifest — "
                f"see payload for the replacement specification."
            ),
            "scope": "global",
        },
        "inpaint_output": {
            "caption": (
                "Inpainted video binary (mp4) — output of object-removal "
                "or region-replacement edit. Can be re-ingested by "
                "downstream video agents (analysis / style transfer / "
                "extension / compositing)."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> InpaintMaterializer:
    return InpaintMaterializer(video_edit_service=services["video_edit_service"])


SPEC = AgentSpec(
    agent_id="InpaintAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_VIDEO,
            cardinality="single",
            description=(
                "The source video FILE on disk to edit — a binary "
                "mp4 artifact (mime=video/mp4) whose actual bytes the "
                "materializer feeds to the inpaint video model. "
                "This label targets the mp4 binary specifically, NOT "
                "any JSON/manifest video_package artifact that may "
                "coexist."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_MASK,
            cardinality="single",
            description=(
                "Mask specification. For manual mode, provide an explicit "
                "mask image/video. For depth/object modes, the caption or "
                "payload should describe mask_mode and what to replace. "
                "Payload may contain: mask_mode (manual | depth_foreground "
                "| depth_background | object_track), "
                "replacement_description (what to paint)."
            ),
        ),
    ],
    output_description=(
        "inpainted_video (source video with the masked region replaced)."
    ),
    purpose_and_trigger=(
        "Video inpainting / object removal / object replacement. Supports "
        "manual masks, depth-based segmentation, and object tracking. "
        "Need both an ingested source video AND a user instruction text "
        "before I can run. The output is itself a finished video and is "
        "the deliverable by default — no further composition needed unless "
        "the user explicitly asks for additional treatments on top."
    ),
    input_preamble=(
        "I perform video inpainting / object replacement. I support "
        "multiple mask modes: manual mask, depth-based foreground / "
        "background separation, and object tracking."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: InpaintAgent(llm_client=llm),
    evaluator_factory=InpaintEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_edit_service": lambda ctx: __import__(
            "inference.generation", fromlist=["select_video_edit_service"]
        ).select_video_edit_service(),
    },
    materializer_factory=materializer_factory,
)
