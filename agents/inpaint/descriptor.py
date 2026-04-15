"""InpaintAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import InpaintAgent
from .labels import INPUT_LABEL_SOURCE_VIDEO, INPUT_LABEL_MASK
from .schema import InpaintAgentInput
from .evaluator import InpaintEvaluator
from .materializer import InpaintMaterializer


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

    # Infer mask_mode and replacement_description from mask entry
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
    content = output_dict.get("content", {})
    spec = content.get("inpaint_spec", {})
    mode = spec.get("mask_mode", "?")
    desc = spec.get("replacement_description", "")
    return {
        agent_id: {
            "caption": (
                f"Inpainted video ({mode} mask): {desc}. "
                f"Object replacement / depth-based edit applied."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> InpaintMaterializer:
    return InpaintMaterializer(video_edit_service=services["video_edit_service"])


CATALOG_ENTRY = (
    "InpaintAgent\n"
    "  - Input: a source-video artifact + a replacement / removal instruction text "
    "(e.g. '去掉路人', 'remove watermark', 'replace background with beach').\n"
    "  - Output: inpainted_video (source video with the masked region replaced).\n"
    "  - Purpose: Video inpainting / object removal / object replacement. Supports manual "
    "masks, depth-based segmentation, and object tracking. Need both an ingested source "
    "video AND a user instruction text before I can run. The output is itself a finished "
    "video — no further composition needed unless the user also wants subtitles or style "
    "transfer chained on top."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="InpaintAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: InpaintAgent(llm_client=llm),
    evaluator_factory=InpaintEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_edit_service": lambda ctx: __import__("inference.generation", fromlist=["select_video_edit_service"]).select_video_edit_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I perform video inpainting / object replacement. I support "
        "multiple mask modes: manual mask, depth-based foreground/"
        "background separation, and object tracking.\n\n"
        f"[{INPUT_LABEL_SOURCE_VIDEO}] (single)\n"
        "The source video to edit.\n\n"
        f"[{INPUT_LABEL_MASK}] (single)\n"
        "Mask specification. For manual mode, provide an explicit mask "
        "image/video. For depth/object modes, the caption or payload "
        "should describe mask_mode and what to replace. Payload may "
        "contain: mask_mode (manual|depth_foreground|depth_background|"
        "object_track), replacement_description (what to paint)."
    ),
)
