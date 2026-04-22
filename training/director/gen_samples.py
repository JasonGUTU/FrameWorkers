"""System prompt + compact catalog + assistant-content serializer.

Three helpers shared by every training-data generator in this directory
(gen_training_full.py, gen_by_hand.py, gen_dpo.py). The full catalog (with
topology blocks) is ~35K chars; the compact one is ~2K, which lets seq_len
4096 fit a full sample including rationale + plan.
"""

from __future__ import annotations

import json

from agents import get_agent_registry
from director_agent import prompts as director_prompts


def build_compact_catalog() -> list[dict]:
    registry = get_agent_registry()
    infos = registry.get_all_agents_info()
    compact = []
    for info in infos:
        agent_id = info.get("id") or info.get("name")
        # Take just the first sentence of description as the one-line purpose.
        desc = (info.get("description") or "").strip()
        one_line = desc.split("\n")[0][:200]
        compact.append({"agent_id": agent_id, "purpose": one_line})
    return compact


def build_system_prompt() -> str:
    """System prompt = PLAN_UPFRONT_SYSTEM_BARE (fewshots stripped) + compact catalog.

    Training + eval both use the bare variant: apples-to-apples deployment
    compares to the bare Gemini baseline (FW_TOPOLOGY=0 + no fewshots). The
    fewshots-on variant was tried and underperformed (LoRA overfit the creative-flow
    chain shape onto VideoExtend/Highlight terminals).
    """
    catalog = build_compact_catalog()
    allowed = [c["agent_id"] for c in catalog]
    return (
        director_prompts.PLAN_UPFRONT_SYSTEM_BARE
        + "\n\nAllowed agent ids:\n"
        + json.dumps(allowed, ensure_ascii=False)
        + "\n\nAgent catalog (compact, one-line purposes):\n"
        + json.dumps(catalog, ensure_ascii=False)
    )


def _assistant_response(rationale: str, plan_steps: list[dict]) -> str:
    """Serialize assistant response in the exact schema PLAN_UPFRONT_SYSTEM demands."""
    return json.dumps(
        {"rationale": rationale, "plan": plan_steps},
        ensure_ascii=False,
    )
