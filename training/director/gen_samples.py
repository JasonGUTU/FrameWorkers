"""Canonical training-data prompt helpers.

Exports three helpers shared by every training-data generator in this
directory:

  - ``build_agent_catalog``   : full descriptor catalog without topology
                                (basic info; byte-identical to
                                ``router._agents_catalog_for_prompt`` with
                                FW_TOPOLOGY=0)
  - ``build_system_prompt``   : canonical system prompt for LoRA training
                                and LoRA inference — calls
                                ``director_agent.prompts.build_plan_system_prompt``
                                so the exact same assembly logic feeds
                                production Gemini eval (via
                                ``LlmSubAgentPlanner.plan_pipeline_upfront``).
                                This keeps train prompt ≡ inference prompt
                                byte-for-byte.
  - ``_assistant_response``   : serialize the ``{rationale, plan}`` JSON
                                response.

Scaffold config (by default): ``policies=False``, ``fewshots=False``,
``topology=False``. Uses the minimal ``PLAN_UPFRONT_CORE`` (rules + basic
descriptor catalog only, no routing-policy scaffolding) — matches the new
Gemini baseline which also drops the policies block.
"""

from __future__ import annotations

import json

from agents import get_agent_registry
from director_agent import prompts as director_prompts
from director_agent.config import MAX_PIPELINE_STEPS


def build_agent_catalog() -> list[dict]:
    """Full descriptor catalog without topology — basic info only.

    Matches ``router._agents_catalog_for_prompt(..., FW_TOPOLOGY=0)`` in
    shape: ``[{id, description: <AgentSpec.render_catalog_entry()>}]``.
    Each description is ~1500 chars (Inputs list + Output + Purpose /
    routing). The ``capabilities`` / ``agent_type`` fields were dropped
    2026-04 — they were always the same value for every agent and carried
    zero routing signal.
    """
    out: list[dict] = []
    for info in get_agent_registry().get_all_agents_info():
        aid = (info.get("id") or info.get("name") or "").strip()
        if not aid:
            continue
        out.append({
            "id": aid,
            "description": info.get("description") or "",
        })
    return out


def build_system_prompt() -> str:
    """Canonical system prompt for training + LoRA eval.

    Composed via ``director_agent.prompts.build_plan_system_prompt`` with:
      - core = ``PLAN_UPFRONT_CORE`` (no policies scaffolding, no fewshots —
        matches the new Gemini baseline)
      - catalog = full descriptor, no topology (``build_agent_catalog``)
      - max_plan_steps = ``MAX_PIPELINE_STEPS``

    Gemini eval through ``eval_routing.py --no-policies --no-fewshots`` on
    the same flags produces the byte-identical system prompt, so LoRA vs
    Gemini comparison is apples-to-apples.
    """
    catalog = build_agent_catalog()
    allowed = [c["id"] for c in catalog]
    return director_prompts.build_plan_system_prompt(
        core=director_prompts.PLAN_UPFRONT_CORE,
        allowed=allowed,
        catalog=catalog,
        max_plan_steps=MAX_PIPELINE_STEPS,
    )


def _assistant_response(rationale: str, plan_steps: list[dict]) -> str:
    """Serialize assistant response in the exact schema the planner demands."""
    return json.dumps(
        {"rationale": rationale, "plan": plan_steps},
        ensure_ascii=False,
    )


def build_system_prompt_no_rationale() -> str:
    """CoT-ablation variant of :func:`build_system_prompt`.

    Same composition (``build_plan_system_prompt`` + full descriptor catalog
    + no topology + MAX_PIPELINE_STEPS), but the core block is
    ``PLAN_UPFRONT_CORE_NO_RATIONALE`` — assistant schema drops the
    top-level ``rationale`` field and the per-step ``intent`` field.

    Used to generate the ``samples_sft_full.no_rationale.jsonl`` training
    data + drive ``eval_lora.py --schema-variant no_rationale`` inference.
    Train prompt ≡ inference prompt byte-for-byte for the no-rationale
    branch.
    """
    catalog = build_agent_catalog()
    allowed = [c["id"] for c in catalog]
    return director_prompts.build_plan_system_prompt(
        core=director_prompts.PLAN_UPFRONT_CORE_NO_RATIONALE,
        allowed=allowed,
        catalog=catalog,
        max_plan_steps=MAX_PIPELINE_STEPS,
    )


def _assistant_response_no_rationale(plan_steps: list[dict]) -> str:
    """Serialize assistant response in the no-rationale schema.

    Strips top-level ``rationale`` and per-step ``intent`` — the assistant
    output is just the ordered ``agent_id`` sequence wrapped as
    ``{"plan":[{"agent_id":"..."}, ...]}``.
    """
    stripped = [{"agent_id": s["agent_id"]} for s in plan_steps]
    return json.dumps({"plan": stripped}, ensure_ascii=False)
