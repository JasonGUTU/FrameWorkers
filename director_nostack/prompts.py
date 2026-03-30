"""LLM system prompts and user-message assembly for merge + pipeline routing (no Task Stack)."""

from __future__ import annotations

import json
from typing import Any, Dict, List

MERGE_SESSION_GOAL_SYSTEM = (
    "You merge multiple user turns into ONE instruction string (`merged_goal`) for the same "
    "logical task. The **latest user chat line** is authoritative for *how* to update the brief, "
    "but you must infer **intent shape** before writing.\n\n"
    "**Infer the relationship** (do not output labels — only the merged text in JSON):\n"
    "1) **Supplement / additive** — new line adds tone, length, medium, characters, scenes, "
    "constraints, or details. **merged_goal** = full integrated brief: keep everything from "
    "earlier user lines + memory that the new line does **not** contradict, then weave in the "
    "new requirements explicitly.\n"
    "2) **Correction / override** — new line fixes or replaces one part (e.g. \"改成喜剧\", "
    "\"主角换成女性\"). **merged_goal** = previous brief with that part updated; leave the rest "
    "stable unless the new line clearly invalidates it.\n"
    "3) **Replacement / fresh brief** — user discards prior work or starts an unrelated ask "
    "(e.g. 忽略前面 / 重新来 / 换一个题材 / clearly disjoint topic). **merged_goal** = follow the "
    "**latest line** as the new primary spec; drop superseded prior **user** requirements. "
    "Still respect **facts already committed** in global_memory / last execution when they are "
    "assets the user did not ask to throw away.\n"
    "4) **Restate / clarify** — same intent, clearer wording. **merged_goal** = one clean, "
    "non-redundant version.\n\n"
    "**Heuristics:** short follow-ups (\"再短一点\", \"加一段对白\") usually **supplement**. "
    "Strong reset language or a totally new premise usually **replacement**. If ambiguous, "
    "prefer **supplement**: keep prior user requirements and layer the latest line on top, "
    "unless the latest line clearly negates them.\n\n"
    "**Output rules:** `merged_goal` must stand alone — imperative, concrete, no markdown, no "
    "meta (\"the user previously…\"), no reuse/skip lists. Sub-agents only see this string plus "
    "their normal context.\n"
    "**Message order (recency):** The block \"Prior user chat lines\" is chronological "
    "**oldest → newest** (line 1 = earliest; the **last** numbered line = the user turn "
    "immediately before the current one). \"Latest user chat line\" is always the **newest** "
    "turn overall and weighs most for supplement vs replace vs correct.\n"
    "Respond with JSON only, no markdown: "
    '{"merged_goal":"<full current instruction for sub-agents>"}'
)

MERGE_PRIOR_LINES_HEADER = (
    "Prior user chat lines (chronological: **1 = oldest**, higher numbers = **more recent**; "
    "the **last** number is the turn just before current). Current turn is ONLY below under "
    "\"Latest user chat line\":\n"
)

MERGE_LATEST_USER_HEADER = (
    "Latest user chat line (**newest** — this turn; use it to decide supplement vs replace vs correct):\n"
)

ROUTING_PIPELINE_STEP_SYSTEM = (
    "You are the Director for a multi-step creative pipeline (film / media production). "
    "The user gave ONE overall goal. Steps run one agent at a time; each run updates "
    "workspace memory and execution history. "
    "Decide EITHER the single next agent to run OR that the goal is already fully met.\n"
    "Respond with JSON only, no markdown, exactly one of:\n"
    '{"action":"run","agent_id":"<id>","rationale":"<short reason>"}\n'
    '{"action":"done","rationale":"<why no more agents are needed>"}\n'
    "Rules:\n"
    "- For action run, agent_id MUST be copied exactly from the allowed list.\n"
    "- Use action done ONLY when you judge from user goal + global_memory + latest execution "
    "that the creative request is fully met or additional agents would be redundant; there is "
    "no other stop signal in code.\n"
    "- Do NOT assume a fixed pipeline order. Choose the next agent based on the user goal and the "
    "current global_memory / latest execution summary.\n"
    "- If the user goal clearly asks for a **watchable video / clip / rendered footage** and the "
    "latest execution + memory show only upstream planning assets (e.g. story, screenplay, boards, "
    "keyframes) with **no** completed video-style deliverable yet, prefer **action run** toward "
    "the next missing production step (often progressing toward VideoAgent) rather than **done**. "
    "Return **done** only after the user-visible deliverable matches the request or the user asked "
    "for a partial deliverable only.\n"
)

ROUTING_TRIGGER_AFTER_USER_MESSAGE = (
    "Trigger: **A user message was just received from the frontend** (one chat line "
    "consumed to start this pipeline run). \"User goal\" below is the **single** "
    "instruction for this run (Director may have merged it with prior workspace "
    "context when the same task already had memory or executions). Your job is only to "
    "choose the next agent_id or done — not to explain reuse. Another user message later "
    "starts a **new** run."
)

ROUTING_TRIGGER_PIPELINE_CONTINUE = (
    "Trigger: **No new message from the frontend** since the last agent; this routing "
    "call is an automatic pipeline continuation. \"User goal\" below is unchanged for "
    "this run."
)


def build_merge_user_prompt(
    *,
    prior_user_lines: List[str],
    latest_line: str,
    summary_blob: str,
    mem_blob: str,
) -> str:
    prior_blob = ""
    if prior_user_lines:
        numbered = "\n".join(
            f"{i + 1}. {t[:4000]}" for i, t in enumerate(prior_user_lines[:50])
        )
        prior_blob = MERGE_PRIOR_LINES_HEADER + numbered + "\n\n"
    return (
        prior_blob
        + MERGE_LATEST_USER_HEADER
        + latest_line[:12000]
        + "\n\nLatest execution summary (may be null):\n"
        + summary_blob
        + "\n\nglobal_memory (newest first; slim rows: task_id, agent_id, created_at, execution_result only):\n"
        + mem_blob
        + "\n\nProduce merged_goal JSON only."
    )


def build_routing_user_prompt(
    *,
    allowed: List[str],
    catalog: List[Dict[str, Any]],
    original_user_goal: str,
    trigger_block: str,
    continuation_note: str,
    summary_blob: str,
    mem_blob: str,
) -> str:
    return (
        "Allowed agent ids (you MUST copy one exactly when action is run):\n"
        + json.dumps(allowed, ensure_ascii=False)
        + "\n\nAgent catalog:\n"
        + json.dumps(catalog, ensure_ascii=False, default=str)
        + "\n\n"
        + trigger_block
        + "\n\nUser goal (this pipeline run):\n"
        + (original_user_goal or "").strip()[:12000]
        + "\n\n"
        + continuation_note
        + "\n\nLatest execution summary (may be null):\n"
        + summary_blob
        + "\n\nglobal_memory (newest first; slim rows: task_id, agent_id, created_at, execution_result only):\n"
        + mem_blob
    )
