"""BriefEnricherAgent — merges image visual descriptions into the creative brief.

Input:  BriefEnricherInput (raw_brief_json_text + image_payloads_json_text
        + image_paths)
Output: BriefEnricherOutput (enriched_brief with visual descriptions
        injected + image_classifications from text context)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives
the raw brief JSON and the image description JSON array, determines each
image's role from the TEXT context (not from the image itself), and
produces an enriched brief that weaves the visual descriptions into the
narrative so the downstream story step creates characters / locations /
props that MATCH the uploaded reference images.

Post-LLM pass: ``image_paths`` (runtime file paths the LLM cannot know)
are copied from input_data into the output so ``build_captions`` can
register role-specific caption entries pointing at the original files.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import BriefEnricherInput, BriefEnricherOutput


ENRICHER_OUTPUT_TEMPLATE = """{
  "content": {
    "enriched_brief": "<the original user brief rewritten to weave in visual descriptions from the uploaded images>",
    "image_classifications": [
      {
        "image_index": 0,
        "role": "character"
      }
    ]
  }
}"""


class BriefEnricherAgent(BaseAgent[BriefEnricherInput, BriefEnricherOutput]):

    async def generate(
        self,
        input_data: BriefEnricherInput,
        *,
        rework_notes: str = "",
    ) -> BriefEnricherOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        # Copy runtime image paths into the output so build_captions
        # can register role-specific caption entries for each image.
        output.content.image_paths = list(input_data.image_paths)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are BriefEnricherAgent: merge visual descriptions from "
            "uploaded reference images into the user's creative brief.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make merging "
            "impossible. Concretely, reject when ANY of these is true "
            "after you have read both JSON blobs carefully:\n"
            "  * raw_brief_json_text is empty, whitespace-only, or an "
            "empty JSON object — there is no brief to enrich.\n"
            "  * The brief has no human-readable text at all (no text / "
            "summary / content / brief / prompt fields with non-empty "
            "values). Without text intent, there is nothing to weave "
            "visual details into.\n"
            "  * image_payloads_json_text is empty or contains zero "
            "image entries. This agent only exists to merge image "
            "descriptions into a brief — with no images, there is "
            "literally nothing for me to do (the brief should bypass me "
            "entirely and go straight to the story step).\n"
            "  * Every image payload lacks a visual_description (or any "
            "equivalent description field) — without descriptions, "
            "there is nothing concrete to weave in.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'no image "
            "descriptions present in image_payloads_json_text — there is "
            "nothing visual to merge').\n"
            "  * missing_labels: whichever of ['raw_brief', "
            "'image_descriptions'] is unusable.\n"
            "  * offending_fields: e.g. ['content.text', "
            "'[].content.visual_description'].\n"
            "If the brief is merely short or the image descriptions are "
            "thin — DO NOT reject; weave whatever is present.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive TWO JSON text blobs:\n"
            "1. The raw creative brief (from the text-intake step) — "
            "contains the user's story/video concept.\n"
            "2. An array of image description payloads (from the image-"
            "intake step) — each has a ``content.visual_description`` "
            "describing what the uploaded image shows.\n\n"
            "=== YOUR JOB ===\n"
            "1. Read the user's TEXT to understand their intent. The text "
            "tells you what each image is FOR — e.g. 'with this person as "
            "the protagonist' means image #0 is a CHARACTER reference; "
            "'in this setting' means it is a LOCATION reference; 'the old "
            "pocket watch' means it is a PROP reference; 'in this visual "
            "style' means it is a STYLE reference.\n\n"
            "2. For each image, classify its role as one of: character, "
            "location, prop, style. Write this into "
            "``image_classifications[i].role``.\n\n"
            "3. Rewrite the brief to WEAVE IN the visual descriptions. "
            "The enriched brief should read naturally — not 'image #0 "
            "shows a red-haired woman' but 'the protagonist is a young "
            "woman with fiery red hair and a freckled face'. Include "
            "enough visual detail from the image descriptions that "
            "the downstream story step will create characters / locations "
            "/ props whose descriptions MATCH the uploaded reference "
            "images. You MAY restructure sentences and rephrase the "
            "user's prose freely — but every plot element, character, "
            "and stated creative intent in the original brief MUST "
            "survive into the enriched version. Do not invent new plot "
            "elements either; the rewrite adds visual specificity, not "
            "story content.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the template exactly.\n"
            "``enriched_brief``: one continuous text string (the rewritten "
            "brief with visual details woven in).\n"
            "``image_classifications``: one entry per image, in the same "
            "order as the input array. ``image_index`` is 0-based.\n"
            "``role``: character | location | prop | style.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: BriefEnricherInput) -> str:
        return (
            "=== RAW CREATIVE BRIEF (JSON) ===\n"
            f"{input_data.raw_brief_json_text}\n"
            "=== END BRIEF ===\n\n"
            "=== UPLOADED IMAGE DESCRIPTIONS (JSON array) ===\n"
            f"{input_data.image_payloads_json_text}\n"
            "=== END IMAGE DESCRIPTIONS ===\n\n"
            "Read the user's text to determine each image's role "
            "(character / location / prop / style). Then rewrite the "
            "brief to weave in the visual descriptions so the story "
            "will match the reference images.\n\n"
            "Output JSON in this shape:\n\n"
            f"{ENRICHER_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> BriefEnricherOutput:
        return BriefEnricherOutput.model_validate(raw)

    def recompute_metrics(self, output: BriefEnricherOutput) -> None:
        c = output.content
        output.metrics.image_count = len(c.image_paths)
        output.metrics.classified_count = len(c.image_classifications)
