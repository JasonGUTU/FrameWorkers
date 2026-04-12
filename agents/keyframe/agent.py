"""KeyFrameAgent — full keyframes-package generation from a screenplay JSON text blob.

Input:  KeyFrameAgentInput (``screenplay_json_text`` + user-uploaded
        character / location / style reference image lists)
Output: KeyFrameAgentOutput (KeyframesPackage with L1 global_anchors,
        per-scene L2 stability_keyframes, per-shot L3 keyframes with
        prompt_summary + video_motion_hint, plus top-level ``style_notes``
        and ``must_avoid`` mirrored from the screenplay)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives the
upstream screenplay as an indented JSON text blob and produces the complete
KeyFrameAgentOutput in a single pass. See CLAUDE.md §7 (Postel's Law at the
agent layer) for the rationale: zero Python-side string-keyed access on
the upstream screenplay; the LLM is the sole consumer of its shape.

History note: a prior version of this agent was "skeleton-first with
1 global + N per-scene parallel LLM calls" to dodge single-call timeouts
on long screenplays. That optimization required walking the upstream
screenplay dict by key in Python (``sp.get("content").get("scenes")``
etc.) to build the skeleton and scene-level prompts — a direct violation
of CLAUDE.md §7. It was discarded in favour of a single full LLM call.
If single-call timeouts become a real problem in practice, the path back
is to re-introduce parallel calls BUT each call must still consume the
opaque ``screenplay_json_text`` (with a "focus on scene X" directive),
NEVER a Python-parsed dict.

Output contract: all content-level invariants (entity ids, scene/shot
ids, L1/L2/L3 layering, prop_NNN format, keyframe_count==1, mirroring
style_lock/must_avoid from the screenplay, …) are owned by the LLM via
the template + system prompt and enforced by KeyframeEvaluator's
structural checks. Rework surfaces any drift instead of a silent
Python-side patch-up. ``recompute_metrics`` does NOT rewrite any
LLM-authored field — it only derives summary counts. User-uploaded
reference images are pre-filled into ``global_anchors.image_asset.uri``
as a final Python pass AFTER the LLM call (these are runtime-assigned
file paths that the LLM cannot know).
"""

from __future__ import annotations

import logging
from typing import Any

from ..base_agent import BaseAgent
from .schema import KeyFrameAgentInput, KeyFrameAgentOutput

logger = logging.getLogger(__name__)


KEYFRAMES_OUTPUT_TEMPLATE = """{
  "content": {
    "style_notes": ["<screenplay scene_consistency_pack.style_lock.global_style_notes, merged+deduped across scenes>"],
    "must_avoid": ["<screenplay scene_consistency_pack.style_lock.must_avoid, merged+deduped across scenes>"],
    "global_anchors": {
      "characters": [
        {
          "entity_type": "character",
          "entity_id": "char_001",
          "purpose": "identity_anchor",
          "keyframe_id": "kf_global_char_001",
          "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
          "prompt_summary": "<L1 canonical character look: standalone t2i, 2-6 short sentences, no location>",
          "image_generation_prompt": ""
        }
      ],
      "locations": [
        {
          "entity_type": "location",
          "entity_id": "loc_001",
          "purpose": "style_anchor",
          "keyframe_id": "kf_global_loc_001",
          "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
          "prompt_summary": "<L1 canonical location look: environment ONLY, no characters/people, 2-6 short sentences>",
          "image_generation_prompt": ""
        }
      ],
      "props": [
        {
          "entity_type": "prop",
          "entity_id": "prop_001",
          "purpose": "prop_anchor",
          "keyframe_id": "kf_global_prop_001",
          "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
          "prompt_summary": "<L1 canonical prop look: standalone t2i, 2-6 short sentences>",
          "image_generation_prompt": ""
        }
      ]
    },
    "scenes": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "source": {
          "screenplay_asset_id": "<from screenplay meta.asset_id if present, else empty string>",
          "screenplay_scene_id": "sc_001"
        },
        "stability_keyframes": {
          "characters": [
            {
              "entity_type": "character",
              "entity_id": "char_001",
              "purpose": "scene_adaptation",
              "keyframe_id": "kf_char_001_sc_001",
              "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
              "prompt_summary": "<L2 short edit delta vs global anchor — light / pose / environment only>",
              "image_generation_prompt": ""
            }
          ],
          "locations": [
            {
              "entity_type": "location",
              "entity_id": "loc_001",
              "purpose": "scene_adaptation",
              "keyframe_id": "kf_loc_001_sc_001",
              "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
              "prompt_summary": "<L2 short edit delta vs global anchor>",
              "image_generation_prompt": ""
            }
          ],
          "props": [
            {
              "entity_type": "prop",
              "entity_id": "prop_001",
              "purpose": "scene_adaptation",
              "keyframe_id": "kf_prop_001_sc_001",
              "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
              "prompt_summary": "<L2 short edit delta vs global anchor>",
              "image_generation_prompt": ""
            }
          ]
        },
        "shots": [
          {
            "shot_id": "sh_001",
            "order": 1,
            "source": {"source_shot_id": "sh_001"},
            "keyframes": [
              {
                "keyframe_id": "kf_001",
                "order": 1,
                "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"},
                "prompt_summary": "<L3 one frozen frame: 2-6 short sentences, no sound/edit/dialogue/music meta>",
                "video_motion_hint": "<1-3 sentences of subtle I2V motion only; do NOT duplicate still text>",
                "image_generation_prompt": ""
              }
            ]
          }
        ]
      }
    ]
  }
}"""


class KeyFrameAgent(BaseAgent[KeyFrameAgentInput, KeyFrameAgentOutput]):

    async def generate(
        self,
        input_data: KeyFrameAgentInput,
        *,
        rework_notes: str = "",
    ) -> KeyFrameAgentOutput:
        """Single full-output LLM call from the screenplay JSON text blob.

        After the LLM returns, a Python pass wires user-uploaded
        reference images into the L1 global_anchors so the materializer
        can use them directly instead of running t2i.
        """
        output = await self._llm_fill_full(input_data, rework_notes)
        self._prefill_reference_images(output, input_data)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are KeyFrameAgent: read a screenplay and produce three "
            "layers of STATIC image prompts plus a top-level style mirror.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream screenplay as a RAW JSON TEXT "
            "BLOB inside the user message. Do NOT assume specific field "
            "names in advance. READ the JSON, understand whatever shape "
            "it happens to have, and extract the elements you need. "
            "Typical fields you may encounter include content.scenes[] "
            "with each scene containing a scene_consistency_pack "
            "(location_lock, character_locks, props_lock, style_lock) "
            "and shots[] (with shot_id, shot_type, visual_goal, "
            "action_focus, characters_in_frame, props_in_frame, "
            "keyframe_plan, camera) — but the exact names and nesting "
            "may vary. Reason from the text, not from assumed keys.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. Use empty string for unknowns, never null. Your "
            "output will be validated against a strict Pydantic "
            "schema.\n\n"
            "=== LAYERING (CRITICAL) ===\n"
            "L1 — ``global_anchors``: one entry per UNIQUE character, "
            "location, and prop across the whole screenplay. This is a "
            "standalone t2i prompt — the canonical physical look of that "
            "entity in isolation. STRICT: location prompts must describe "
            "ONLY the environment/place — NEVER include characters or "
            "people. Avoid pasting global style paragraphs (the backend "
            "re-injects style).\n"
            "L2 — per-scene ``stability_keyframes``: for each scene, one "
            "entry per character / location / prop that appears in that "
            "scene. This is a SHORT edit delta vs the global anchor — "
            "light / environment / pose only. Do not dump full style "
            "lists.\n"
            "L3 — per-shot ``keyframes``: EXACTLY ONE keyframe per shot. "
            "``prompt_summary`` is one frozen visual frame (no sound / "
            "edit / dialogue / music meta). ``video_motion_hint`` is "
            "1-3 sentences of subtle I2V motion only; never duplicate "
            "still text into the motion hint.\n"
            "Every ``prompt_summary`` (L1, L2, L3) must be 2-6 short "
            "English sentences and non-empty.\n\n"
            "=== TOP-LEVEL STYLE MIRROR ===\n"
            "Mirror ``style_notes`` and ``must_avoid`` into the "
            "content's top-level arrays:\n"
            "  * style_notes: collect "
            "scene_consistency_pack.style_lock.global_style_notes from "
            "EVERY scene in the screenplay, merge, dedupe (same text "
            "after whitespace normalization → drop duplicates), "
            "preserve first-seen order.\n"
            "  * must_avoid: same treatment for "
            "scene_consistency_pack.style_lock.must_avoid.\n"
            "The materializer reads these two lists directly and will "
            "NOT walk the screenplay — so whatever you put here is what "
            "the image generation service sees.\n\n"
            "=== ID CONVENTIONS ===\n"
            "character/location/prop entity_ids: reuse the screenplay's "
            "exact ids (char_001, loc_001, prop_001 style). If a scene's "
            "consistency_pack doesn't list an entity but the shots inside "
            "reference its id, include it anyway.\n"
            "scene_id: reuse the screenplay's scene_id verbatim.\n"
            "scene.order: 1, 2, 3, … matching the screenplay's scene "
            "order.\n"
            "source.screenplay_scene_id: same as scene_id.\n"
            "source.screenplay_asset_id: copy from screenplay top-level "
            "meta.asset_id if present, else empty string.\n"
            "shot_id: reuse the screenplay's shot_id verbatim "
            "(sh_NNN style, globally sequential across the whole "
            "screenplay).\n"
            "shot.order: 1, 2, 3, … restarting at 1 inside each scene.\n"
            "keyframe_id (L1): kf_global_{entity_id}.\n"
            "keyframe_id (L2): kf_{entity_id}_{scene_id}.\n"
            "keyframe_id (L3): kf_001, kf_002, … GLOBALLY sequential "
            "across the whole package (3-digit zero-padded), one per "
            "shot.\n"
            "All ``image_asset.asset_id``: empty string — the "
            "materializer fills it.\n"
            "All ``image_asset.uri``: 'placeholder' — the materializer "
            "fills it.\n"
            "All ``image_generation_prompt``: empty string — the "
            "materializer fills it after calling the image service.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "Every shot MUST have exactly ONE keyframe in its L3 "
            "keyframes list (keyframe_count == 1). Every prompt_summary "
            "(L1, L2, L3) MUST be non-empty. stability_keyframes' "
            "character / location / prop lists may be empty if the "
            "scene has none of that kind.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: KeyFrameAgentInput) -> str:
        return (
            "Read the upstream screenplay below and produce a complete "
            "keyframes package (L1 global_anchors, L2 per-scene "
            "stability_keyframes, L3 per-shot keyframes, plus top-level "
            "style_notes / must_avoid mirrored from the screenplay).\n\n"
            "=== SCREENPLAY (raw JSON — read the shape before writing) ===\n"
            f"{input_data.screenplay_json_text}\n"
            "=== END SCREENPLAY ===\n\n"
            "Produce the full keyframes package JSON in EXACTLY this "
            "shape:\n\n"
            f"{KEYFRAMES_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> KeyFrameAgentOutput:
        return KeyFrameAgentOutput.model_validate(raw)

    @staticmethod
    def _prefill_reference_images(
        output: KeyFrameAgentOutput,
        input_data: KeyFrameAgentInput,
    ) -> None:
        """Pre-fill global-anchor entities' image_asset.uri from user uploads.

        Position-based assignment: the i-th user reference goes to the
        i-th entity of the same kind. The materializer's L1 pre-fill
        loop reads ``entity.image_asset.uri`` and, if it points to a
        real file on disk, skips text-to-image and uses those bytes
        verbatim as the L1 anchor. So this pass writes the user
        reference's path into that field AFTER the LLM has produced the
        skeleton. InputResolver has already matched the upload to
        ``[character_reference]`` / ``[location_reference]`` based on
        the artifact caption, so reaching this point means the user's
        intent to use this image as an anchor is already validated
        semantically.
        """
        char_refs = input_data.character_references or []
        loc_refs = input_data.location_references or []
        prop_refs = input_data.prop_references or []
        style_refs = input_data.style_references or []

        chars = output.content.global_anchors.characters
        locs = output.content.global_anchors.locations
        props = output.content.global_anchors.props

        for kind, refs, entities in [
            ("character", char_refs, chars),
            ("location", loc_refs, locs),
            ("prop", prop_refs, props),
        ]:
            for i, ref in enumerate(refs):
                if i >= len(entities):
                    break
                path = (ref.path or "").strip()
                if not path:
                    continue
                entities[i].image_asset.uri = path
                logger.info(
                    "[KeyFrameAgent] L1 pre-fill: %s[%d] (%s) ← user reference %s",
                    kind, i, entities[i].entity_id, path,
                )

        if style_refs:
            logger.info(
                "[KeyFrameAgent] %d style references received but not "
                "pre-filled (no global style entity to attach them to)",
                len(style_refs),
            )

    def recompute_metrics(self, output: KeyFrameAgentOutput) -> None:
        """Derive summary metrics from content — pure derived data, zero rewrites.

        All LLM-authored fields (entity_ids, scene/shot ids, order,
        prompt_summary, image_asset placeholders, style_notes / must_avoid,
        …) are left untouched; KeyframeEvaluator enforces their invariants
        via structural checks + rework. The ``metrics`` field is hidden
        from the user-message template, so populating it here is
        derivation, not a silent patch-up of LLM output.
        """
        c = output.content
        scene_count = len(c.scenes)
        shot_count = sum(len(s.shots) for s in c.scenes)
        kf_count = sum(
            len(sh.keyframes) for s in c.scenes for sh in s.shots
        )
        output.metrics.scene_count = scene_count
        output.metrics.shot_count = shot_count
        output.metrics.keyframe_count_total = kf_count
        output.metrics.avg_keyframes_per_shot = (
            kf_count / shot_count if shot_count else 0.0
        )
        output.metrics.global_character_anchor_count = len(
            c.global_anchors.characters
        )
        output.metrics.global_location_anchor_count = len(
            c.global_anchors.locations
        )
        output.metrics.global_prop_anchor_count = len(
            c.global_anchors.props
        )
        output.metrics.stability_character_keyframe_count = sum(
            len(s.stability_keyframes.characters) for s in c.scenes
        )
        output.metrics.stability_location_keyframe_count = sum(
            len(s.stability_keyframes.locations) for s in c.scenes
        )
        output.metrics.stability_prop_keyframe_count = sum(
            len(s.stability_keyframes.props) for s in c.scenes
        )
