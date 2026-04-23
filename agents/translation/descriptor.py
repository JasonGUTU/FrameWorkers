"""TranslationAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import TranslationAgent
from .evaluator import TranslationEvaluator
from .labels import INPUT_LABEL_SOURCE_TEXT
from .schema import TranslationAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Pass upstream payload through as raw JSON text.

    target_language lives in the payload (surfaced via creative_brief or
    task metadata) — defaults to English if absent.
    """
    entry = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_TEXT)
    )

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
                f"Translation ({src} → {tgt}). Full structured text "
                f"translated with original structure preserved "
                f"(keys / ids / timing / ordering). Output shape mirrors "
                f"input shape — a translated SRT remains an SRT, a "
                f"translated screenplay remains a screenplay."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="TranslationAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_TEXT,
            cardinality="single",
            description=(
                "The upstream artifact to translate. Accepts ANY "
                "structured text: a timestamped transcript (the most "
                "common source for bilingual / foreign-subtitle flows — "
                "produced by the preceding transcription step), a "
                "screenplay document, a story blueprint, or ingested "
                "user text. Payload is forwarded as raw JSON text; the "
                "LLM reads whatever structure it has and translates all "
                "human-readable fields while preserving keys, ids, "
                "timing, ordering."
            ),
        ),
    ],
    output_description=(
        "translation (translated text preserving the input structure: keys, "
        "ids, timing, ordering — e.g. a translated transcript keeps every "
        "segment timestamp intact)."
    ),
    purpose_and_routing=(
        """Translate structured text (timestamped transcript, screenplay, etc.) preserving keys / ids / timing / ordering. On subtitle flows MUST follow the transcription step so segment boundaries are already defined; the compositor then renders both the original and translated segments to burn-in SRT. Trigger: bilingual subtitle output or foreign-language subtitle on any video flow."""
    ),
    input_preamble=(
        "I translate structured text (screenplays, transcripts, subtitle "
        "SRTs, story blueprints, ingested user text) from one language to "
        "another while preserving the original document structure."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: TranslationAgent(llm_client=llm),
    evaluator_factory=TranslationEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
