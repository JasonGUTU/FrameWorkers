"""LLM system prompts and user-message assembly for Upfront planner + merge."""

from __future__ import annotations

import json
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# merge_session_goal — unchanged intent from Markov era
# ---------------------------------------------------------------------------

MERGE_SESSION_GOAL_SYSTEM = (
    "You merge multiple user turns into ONE instruction string (`merged_goal`) for the same "
    "logical session. The **latest user chat line** is authoritative for *how* to update the brief, "
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
    "Still respect **facts already committed** in the stack history when they are assets the "
    "user did not ask to throw away.\n"
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


# ---------------------------------------------------------------------------
# Upfront planner
# ---------------------------------------------------------------------------

PLAN_UPFRONT_SYSTEM = (
    "You are the Director. For ONE user goal, produce the **complete ordered pipeline** of "
    "sub-agent executions needed to satisfy it. You are NOT picking one step — you plan the "
    "whole thing upfront.\n"
    "Respond with JSON only, no markdown: "
    '{"plan":[{"agent_id":"<id>","intent":"<what this step should do, concretely>"},...],'
    '"rationale":"<one short sentence explaining the plan\'s shape>"}\n\n'
    "Rules:\n"
    "- Every agent_id MUST be copied exactly from the allowed list below.\n"
    "- The plan is a flat list executed strictly in order — no branching, no parallel.\n"
    "- Include **exactly** the agents required by the goal; NO extra/speculative steps.\n"
    "  Prefer a shorter plan that matches user intent over a longer template-shaped one.\n"
    "- **Intake first**: if the user provided text / image / video / audio input, the FIRST "
    "  step(s) MUST be the corresponding Intake agent(s) (IntakeTextAgent for the text brief, "
    "  then IntakeImageAgent / IntakeVideoAgent / IntakeAudioAgent per uploaded media). Skip "
    "  intake only when the prior stack memory shows it has already run for the same material.\n"
    "- `intent` for each step should be concrete (what outputs this step should produce, any "
    "  user constraints to honor). Do NOT restate the full user goal — just what THIS step does.\n"
    "\n"
    "**Typical pipeline shapes (SOFT HINTS — deviate whenever user intent differs)**:\n"
    "\n"
    "  1) Creative film production (brief → finished film):\n"
    "     IntakeTextAgent → (BriefEnricherAgent if reference images were uploaded)\n"
    "     → StoryAgent → ScreenplayAgent → KeyFrameAgent → VideoAgent\n"
    "     → subset of {NarrationAgent, MusicAgent, AmbienceAgent} driven by user's\n"
    "       EXPLICIT ask (do NOT auto-add all three; only add a track the user asked for)\n"
    "     → AudioMixAgent (only if any of the three audio tracks ran)\n"
    "     → (SubtitleAgent if subtitles requested) → CompositorAgent → done\n"
    "\n"
    "  2) Existing-video post-edit (single transform on uploaded video):\n"
    "     IntakeTextAgent → IntakeVideoAgent\n"
    "     → one of {StyleTransferAgent | InpaintAgent | VideoExtendAgent | HighlightAgent}\n"
    "     → (TranscriptionAgent + SubtitleAgent if user wants subtitles on the result)\n"
    "     → done\n"
    "\n"
    "  3) Audio workflow (no video creation):\n"
    "     IntakeTextAgent → IntakeAudioAgent → TranscriptionAgent\n"
    "     → (TranslationAgent if user wants a translated transcript / foreign-language subs)\n"
    "     → (SubtitleAgent if user wants an SRT file output)\n"
    "     → done\n"
    "\n"
    "  4) Voice-clone creative (user-supplied voice → full film):\n"
    "     IntakeTextAgent → IntakeAudioAgent (voice sample) → VoiceCloneAgent\n"
    "     → then continue as shape (1), but VoiceCloneAgent REPLACES NarrationAgent —\n"
    "       do NOT also run NarrationAgent in the same pipeline.\n"
    "\n"
    "  5) Transcribe → translate → subtitle on existing video:\n"
    "     IntakeTextAgent → IntakeVideoAgent → TranscriptionAgent\n"
    "     → TranslationAgent → SubtitleAgent → done\n"
    "\n"
    "**These shapes are MAPS, not CONTRACTS.** When the user asks for something outside\n"
    "these shapes (e.g. 'only background music on this existing video', 'just transcribe\n"
    "and translate'), compose the minimum subset of agents that satisfies user intent.\n"
    "**Prefer doing LESS than the template shape when the user's ask is narrower.**\n"
)


# ---------------------------------------------------------------------------
# Replanner — invoked when a step fails mid-plan
# ---------------------------------------------------------------------------

REPLAN_TAIL_SYSTEM = (
    "A step in the current Plan Stack just FAILED. You have three options:\n"
    '  {"action":"retry"}  — retry the failed step with the same agent_id\n'
    '  {"action":"skip"}   — leave the failure in place, continue to the next planned step\n'
    '  {"action":"replan","plan":[{"agent_id":"...","intent":"..."},...],'
    '"rationale":"<why>"}  — replace ALL remaining (PENDING) steps in the stack with a new tail\n'
    "\n"
    "Rules:\n"
    "- Only the PENDING tail can be replanned. COMPLETED steps stay frozen.\n"
    "- If the failure looks transient / infra-level, prefer retry.\n"
    "- If the failed step is optional / the downstream can run without it, prefer skip.\n"
    "- If the failure invalidates the remaining plan's assumptions, replan.\n"
    "- agent_ids in a replan MUST be copied from the allowed list exactly.\n"
    "Respond with JSON only, no markdown."
)


# ---------------------------------------------------------------------------
# User-prompt builders
# ---------------------------------------------------------------------------


def build_merge_user_prompt(
    *,
    prior_user_lines: List[str],
    latest_line: str,
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
        + "\n\nstack_memory (slim rows of recent PlanSteps, chronological):\n"
        + mem_blob
        + "\n\nProduce merged_goal JSON only."
    )


def build_plan_upfront_user_prompt(
    *,
    allowed: List[str],
    catalog: List[Dict[str, Any]],
    user_goal: str,
    mem_blob: str,
    max_plan_steps: int,
) -> str:
    return (
        "Allowed agent ids (you MUST copy one exactly for each plan step):\n"
        + json.dumps(allowed, ensure_ascii=False)
        + "\n\nAgent catalog:\n"
        + json.dumps(catalog, ensure_ascii=False, default=str)
        + "\n\nUser goal (merged single instruction):\n"
        + (user_goal or "").strip()[:12000]
        + "\n\nstack_memory (slim rows from prior PlanSteps on this session; empty if first turn):\n"
        + mem_blob
        + f"\n\nHard upper bound on plan length: {max_plan_steps} steps. "
        "Prefer shorter plans. Respond with JSON only."
    )


def build_replan_user_prompt(
    *,
    allowed: List[str],
    catalog: List[Dict[str, Any]],
    user_goal: str,
    failed_step_blob: str,
    pending_tail_blob: str,
    completed_blob: str,
) -> str:
    return (
        "Allowed agent ids:\n"
        + json.dumps(allowed, ensure_ascii=False)
        + "\n\nAgent catalog (short):\n"
        + json.dumps(catalog, ensure_ascii=False, default=str)
        + "\n\nUser goal:\n"
        + (user_goal or "").strip()[:12000]
        + "\n\nFailed step (the one that just failed):\n"
        + failed_step_blob
        + "\n\nPENDING tail (will be replaced if action=replan):\n"
        + pending_tail_blob
        + "\n\nCOMPLETED history (immutable; for context):\n"
        + completed_blob
        + "\n\nDecide action ∈ {retry, skip, replan}. Respond with JSON only."
    )
