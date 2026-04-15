"""TranslationAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import TranslationAgent
from .labels import INPUT_LABEL_SOURCE_TEXT
from .schema import TranslationAgentInput
from .evaluator import TranslationEvaluator


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    Pass-through: dump the entire upstream payload as raw JSON text.
    The target_language is expected to be in the task parameters
    (surfaced via the creative_brief or task metadata); if absent
    the LLM defaults to English.
    """
    entry = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_TEXT)
    )

    # Extract target language from payload if present, default to "en"
    target_lang = "en"
    if entry.payload and isinstance(entry.payload.get("target_language"), str):
        target_lang = entry.payload["target_language"]

    return TranslationAgentInput(
        source_json_text=json.dumps(
            entry.payload or {}, ensure_ascii=False, indent=2
        ),
        target_language=target_lang,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    src = content.get("source_language", "?")
    tgt = content.get("target_language", "?")
    return {
        agent_id: {
            "caption": (
                f"Translation ({src} → {tgt}). Full structured text translated "
                f"with original structure preserved."
            ),
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "TranslationAgent\n"
    "  - Input: any structured text artifact (screenplay, transcript, subtitle SRT, ingested "
    "user text, etc.). Whatever shape it has on input is preserved on output.\n"
    "  - Output: translation (translated text preserving the input structure: keys, ids, "
    "timing, ordering).\n"
    "  - Purpose: Translate structured text between languages. The choice of WHEN to "
    "translate depends on the deliverable shape:\n"
    "      * 'transcribe + translate': translate the transcript directly (no subtitle step needed).\n"
    "      * 'subtitled video in foreign language only': translate the text source FIRST, "
    "then run subtitle generation on the translated text.\n"
    "      * 'bilingual subtitles' (e.g. Chinese + English): generate the source-language "
    "subtitle FIRST, then translate the SRT to the second language."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="TranslationAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: TranslationAgent(llm_client=llm),
    evaluator_factory=TranslationEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I translate structured text (screenplays, transcripts, story "
        "blueprints) from one language to another while preserving the "
        "original document structure.\n\n"
        f"[{INPUT_LABEL_SOURCE_TEXT}] (single)\n"
        "The upstream artifact to translate — typically a screenplay, "
        "transcript, or story blueprint. Its payload is forwarded as raw "
        "JSON text; I read whatever structure it has and translate all "
        "human-readable fields."
    ),
)
