"""BriefEnricherAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import BriefEnricherAgent
from .labels import INPUT_LABEL_IMAGE_DESCRIPTIONS, INPUT_LABEL_IMAGE_FILES, INPUT_LABEL_RAW_BRIEF
from .schema import BriefEnricherInput
from .evaluator import BriefEnricherEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_RAW_BRIEF)
    )
    images = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_IMAGE_DESCRIPTIONS)
    )
    image_files = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_IMAGE_FILES)
    )
    image_payloads = [img.payload or {} for img in images]
    # image_paths come from the PNG file entries (matched by [image_files]),
    # NOT from the JSON descriptor entries (which have path=*.json).
    image_paths = [f.path for f in image_files if f.path]
    return BriefEnricherInput(
        raw_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
        image_payloads_json_text=json.dumps(
            image_payloads, ensure_ascii=False, indent=2
        ),
        image_paths=image_paths,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    caps: dict = {}
    # The enriched brief itself — StoryAgent should prefer this over
    # IntakeTextAgent's raw brief because of the "Supersedes" phrasing.
    caps[agent_id] = {
        "caption": (
            "Enriched creative brief with visual reference descriptions "
            "integrated. Supersedes the raw user brief for story "
            "generation — contains the user's original concept plus "
            "detailed visual descriptions of uploaded reference images."
        ),
        "scope": "global",
    }
    # Role-specific caption entries for each classified image.
    # The ``path`` key triggers ArtifactWriter's external-ref registration
    # so the image file gets a NEW artifact entry with a role-specific
    # caption (e.g. "Global character reference image") that
    # InputResolver can match precisely to labels like
    # [character_reference] / [location_reference].
    image_paths = content.get("image_paths", [])
    for cls in content.get("image_classifications", []):
        if not isinstance(cls, dict):
            continue
        idx = cls.get("image_index", -1)
        role = cls.get("role", "general")
        if 0 <= idx < len(image_paths):
            caps[f"ref_{role}_{idx}"] = {
                "caption": (
                    f"Global {role} reference image. Visual identity "
                    f"anchor for downstream keyframe generation."
                ),
                "scope": "global",
                "path": image_paths[idx],
                "mime": "image/png",
            }
    return caps


CATALOG_ENTRY = (
    "BriefEnricherAgent\n"
    "  - Input: raw creative brief + uploaded image descriptions\n"
    "  - Output: enriched brief with visual details woven in + image role classifications\n"
    "  - Purpose: Merge image visual descriptions into the text brief so downstream\n"
    "    story/screenplay generation matches the uploaded reference images."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="BriefEnricherAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: BriefEnricherAgent(llm_client=llm),
    evaluator_factory=BriefEnricherEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I merge visual descriptions from uploaded reference images into "
        "the user's creative brief so that downstream story generation "
        "creates characters / locations / props that MATCH the uploaded "
        "images.\n\n"
        f"[{INPUT_LABEL_RAW_BRIEF}] (single)\n"
        "The raw creative brief — the user's text describing the story "
        "or video concept. This is typically the output of "
        "IntakeTextAgent. Choose the single most recent text brief.\n\n"
        f"[{INPUT_LABEL_IMAGE_DESCRIPTIONS}] (collection)\n"
        "The JSON descriptor artifacts from IntakeImageAgent. Each "
        "entry's payload contains a visual_description of the uploaded "
        "image. Match by caption mentioning 'reference image' and "
        "mime=application/json. Include every processed image upload.\n\n"
        f"[{INPUT_LABEL_IMAGE_FILES}] (collection)\n"
        "The actual uploaded image FILES (PNG/JPG) registered by "
        "IntakeImageAgent. Each entry's path points directly to the "
        "image file on disk (not a JSON descriptor). Match by "
        "mime=image/*. Include every uploaded image file."
    ),
)
