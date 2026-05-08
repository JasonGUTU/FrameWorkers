"""IllustrationAgent — LLM-driven extractor of per-segment image prompts.

Generation model: ONE LLM call via ``_llm_fill_full``. Reads the upstream
NarrationAgent output as a raw JSON text blob (Postel's Law — zero
key-name assumptions on upstream shape) and emits its own structured
output containing the cross-segment art-style anchor + per-segment
image_prompt list. The actual image generation — first-frame-as-anchor
strategy, parallel edit_image for segments 2..N — lives in
``IllustrationMaterializer``; this layer only owns the worklist.

Why an LLM instead of ``json.loads()``: the previous version hard-coded
``content.segments[].image_prompt`` access into the producer's schema,
violating the project-wide "对外宽进" (Postel's Law) rule. A single
upstream rename or restructure would silently produce an empty
illustration list. Routing the parse through this agent's own LLM lets
the system tolerate upstream drift the same way ScreenplayAgent
tolerates StoryAgent drift.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    IllustrationAgentInput,
    IllustrationAgentOutput,
)


# Output template the LLM follows. Shows only the fields the LLM should
# fill — per-entry ``image`` is left out because IllustrationMaterializer
# populates it post-generation.
ILLUSTRATION_OUTPUT_TEMPLATE = """{
  "content": {
    "overall_style": "<cross-segment art-style anchor: medium, palette, lighting, mood>",
    "character_anchors": [
      {
        "character_id": "char_001",
        "appearance_prompt": "<1-2 sentence visual identity verbatim from upstream cast entry>"
      }
    ],
    "illustrations": [
      {
        "segment_id": "seg_001",
        "image_prompt": "<concrete visual prompt for this segment's illustration>",
        "characters_in_segment": ["char_001"]
      },
      {
        "segment_id": "seg_002",
        "image_prompt": "...",
        "characters_in_segment": []
      }
    ]
  },
  "metrics": {
    "illustration_count": 2
  }
}"""


class IllustrationAgent(BaseAgent[IllustrationAgentInput, IllustrationAgentOutput]):

    async def generate(
        self,
        input_data: IllustrationAgentInput,
        *,
        rework_notes: str = "",
    ) -> IllustrationAgentOutput:
        """Single full-output LLM call from the narration script JSON text blob."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are IllustrationAgent: extract a per-segment illustration "
            "worklist from an upstream narration script. The downstream "
            "materializer takes your output and renders one illustration "
            "per segment via an image-generation API.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch ONLY if the "
            "narration script is structurally unusable. Concretely, reject "
            "when ANY of these is true after reading narration_script_json_text "
            "carefully:\n"
            "  * narration_script_json_text is empty, whitespace-only, or "
            "an empty JSON object — there is literally nothing to extract.\n"
            "  * No segment-like structure anywhere: no segments / scenes / "
            "parts / chapters / pages array with at least one entry that "
            "could plausibly correspond to one illustration.\n"
            "  * No visual prompt material whatsoever: not a single field "
            "across the whole document hints at what to draw (no image_prompt "
            "/ visual / scene_description / setting / illustration_brief or "
            "anything similar).\n"
            "When you reject, populate the rejection fields:\n"
            "  * reason: the single most specific defect.\n"
            "  * missing_labels: ['narration_script'].\n"
            "  * offending_fields: the field paths you looked at, e.g. "
            "['content.segments', 'content.illustrations'].\n"
            "If the script is merely sparse (e.g. one segment with a thin "
            "prompt) — DO NOT reject; proceed and produce one illustration "
            "entry with whatever visual material you can find.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream NarrationAgent output as a RAW "
            "JSON TEXT BLOB inside the user message. Do NOT assume specific "
            "field names in advance. READ the JSON, understand whatever shape "
            "it happens to have, and extract three things:\n"
            "  1. The cross-segment art-style anchor (typical names: "
            "overall_style / art_style / visual_style / style — but READ "
            "the document, do not key-lookup blindly). This single string "
            "describes medium + palette + lighting + mood that should "
            "carry across every illustration.\n"
            "  2. The recurring-character cast (typical names: cast / "
            "characters / dramatis_personae). For each character with a "
            "visual identity description (typical fields: appearance_prompt "
            "/ description / portrait), capture its character_id and the "
            "appearance prompt verbatim. These identities drive cross-"
            "segment character consistency downstream — without them the "
            "image model re-invents each character's face per segment.\n"
            "  3. Per-segment data (typical container names: segments / "
            "scenes / parts / pages). For each segment, capture:\n"
            "     - segment_id (or invent seg_001, seg_002, ... if upstream "
            "has no ids)\n"
            "     - image_prompt — verbatim if present, otherwise synthesize "
            "from the segment's narrative text\n"
            "     - characters_in_segment — the cast character_ids the "
            "segment exposes (typical names: characters_in_segment / "
            "characters / cast_in_scene). Empty list when the segment has "
            "no recurring characters visible.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. Use empty string or empty list for unknowns, never "
            "null.\n\n"
            "=== ID CONVENTIONS ===\n"
            "segment_id: seg_001, seg_002, ... in the order segments appear, "
            "with 3-digit zero-padding. If upstream provides matching ids "
            "(seg_NNN style), REUSE them verbatim — keeping ids consistent "
            "across the pipeline lets the slideshow compositor align "
            "illustrations with narrator timing.\n"
            "If upstream uses different id style (e.g. scene_001, page_1), "
            "renumber to seg_NNN in declaration order and rely on positional "
            "alignment downstream.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "content.overall_style: a non-empty, concrete style description "
            "(NOT a placeholder like 'TBD'). If upstream truly omits it, "
            "synthesize one from any tone / mood / genre fields you can find.\n"
            "content.character_anchors: one entry per recurring named "
            "character upstream defines (mirrored verbatim — character_id + "
            "appearance_prompt). Empty list is allowed when the upstream "
            "has no recurring cast.\n"
            "content.illustrations: one entry per segment in the upstream "
            "narration. illustration_count must equal len(illustrations). "
            "Each entry's characters_in_segment lists the character_ids the "
            "segment exposes — these MUST be a subset of the character_ids "
            "you put in character_anchors. Empty list is allowed.\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: IllustrationAgentInput) -> str:
        return (
            "Read the upstream narration script below and produce an "
            "illustration worklist (one entry per segment).\n\n"
            "=== NARRATION SCRIPT (raw JSON — read the shape before writing) ===\n"
            f"{input_data.narration_script_json_text}\n"
            "=== END NARRATION SCRIPT ===\n\n"
            "Extract from the script:\n"
            "  - the cross-segment art-style anchor (overall_style)\n"
            "  - per-segment {segment_id, image_prompt}\n\n"
            "Produce the full illustration worklist JSON in EXACTLY this shape:\n\n"
            f"{ILLUSTRATION_OUTPUT_TEMPLATE}\n\n"
            "Per-entry requirements:\n"
            "  * segment_id: seg_001, seg_002, ... in declaration order, "
            "3-digit zero-padded. Reuse upstream seg_NNN ids verbatim if present.\n"
            "  * image_prompt: a concrete visual prompt that an image-gen model "
            "can render directly. If upstream provides image_prompt / visual / "
            "illustration_brief / scene_description, copy it. Otherwise synthesize "
            "one from the segment's narrative text.\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> IllustrationAgentOutput:
        return IllustrationAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: IllustrationAgentOutput) -> None:
        """Pure derived count; LLM is not asked to compute it independently."""
        output.metrics.illustration_count = len(output.content.illustrations)
