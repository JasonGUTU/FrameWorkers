"""Programmatic reward function for GRPO routing distillation.

Standard binary + additive design (DeepSeek-R1 / DeepSeekMath template):

    R = R_format + R_accuracy           ∈ {0.0, 1.0, 2.0}
    R_format   = 1 if completion parses to a valid plan with all-known
                 agent_ids and no duplicates, else 0
    R_accuracy = 1 if parsed chain perfectly matches expected_chain
                 (set-aware slots), else 0

GRPO trainer reads only ``RewardBreakdown.score``; the other fields exist
purely for training-dynamics logging (format-failure rates by category,
truncation rate, perfect-chain rate).

Pure Python, no torch dependency. Self-tested at module bottom.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass


_JSON_SPAN_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class RewardBreakdown:
    score: float                 # what GRPO loss reads
    did_parse: bool              # JSON object recoverable from completion
    all_agents_known: bool       # every agent_id in allowed whitelist
    no_duplicate: bool           # each agent_id appears at most once
    chain_perfect: bool          # set-aware exact full-chain match
    got_truncated: bool          # rollout hit max_new_tokens (no EOS / no JSON close)
    n_correct: int               # diagnostic: correctly-placed slots (when format_ok)
    n_expected: int
    n_actual: int


def _extract_json_object(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = _JSON_SPAN_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def parse_plan(completion: str) -> list[str] | None:
    obj = _extract_json_object(completion)
    if not isinstance(obj, dict):
        return None
    plan = obj.get("plan")
    if not isinstance(plan, list) or not plan:
        return None
    chain: list[str] = []
    for step in plan:
        if not isinstance(step, dict):
            return None
        aid = step.get("agent_id")
        if not isinstance(aid, str):
            return None
        chain.append(aid)
    return chain


def _slot_matches(agent: str, slot) -> bool:
    if isinstance(slot, list):
        return agent in slot
    return agent == slot


def compute_reward(
    completion_text: str,
    expected_chain: list,
    allowed_agents: set,
    eos_hit: bool = True,
) -> RewardBreakdown:
    """Format gate + chain-accuracy partial credit + perfect bonus.

    R = 0.5 * pos_correct + 0.5 * float(chain_perfect)  ∈ [0, 1]

    Format gate: parse fail OR unknown agent_id OR duplicate agent → R = 0
    (SFT base never produces format errors empirically — gate just prevents
    GRPO from drifting into nonsense output during exploration).

    Partial credit avoids σ=0 collapse when 4 rollouts all hit the same
    binary {0,1} bucket. Perfect bonus prevents satisficing (model learning
    "stable 4/5" instead of "risk-it 5/5") — perfect rewards 2.5× more than
    near-miss 4/5 (1.0 vs 0.4).
    """
    actual = parse_plan(completion_text)
    n_exp = len(expected_chain)

    if actual is None:
        return RewardBreakdown(
            score=0.0, did_parse=False,
            all_agents_known=False, no_duplicate=False, chain_perfect=False,
            got_truncated=not eos_hit,
            n_correct=0, n_expected=n_exp, n_actual=0,
        )

    all_known = all(a in allowed_agents for a in actual)
    no_dup = len(set(actual)) == len(actual)

    # Format gate — agent_id wrong / duplicate → 0
    if not (all_known and no_dup):
        return RewardBreakdown(
            score=0.0, did_parse=True,
            all_agents_known=all_known, no_duplicate=no_dup,
            chain_perfect=False, got_truncated=False,
            n_correct=0, n_expected=n_exp, n_actual=len(actual),
        )

    # Format pass — score on chain accuracy
    n_correct = sum(
        1 for i, a in enumerate(actual)
        if i < n_exp and _slot_matches(a, expected_chain[i])
    )
    chain_perfect = (len(actual) == n_exp and n_correct == n_exp)

    pos_correct = n_correct / max(len(actual), n_exp) if n_exp > 0 else 0.0
    score = 0.5 * pos_correct + 0.5 * (1.0 if chain_perfect else 0.0)

    return RewardBreakdown(
        score=score,
        did_parse=True,
        all_agents_known=all_known,
        no_duplicate=no_dup,
        chain_perfect=chain_perfect,
        got_truncated=False,
        n_correct=n_correct,
        n_expected=n_exp,
        n_actual=len(actual),
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ALLOWED = {"StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent",
               "MusicAgent", "AmbienceAgent", "AudioMixAgent", "CompositorAgent"}
    EXPECTED = ["StoryAgent", "ScreenplayAgent", "VideoAgent"]

    cases = [
        ("perfect", EXPECTED,
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "ScreenplayAgent", "intent": "x"},
             {"agent_id": "VideoAgent", "intent": "x"},
         ]}), 2.0),
        ("format ok content wrong", EXPECTED,
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "MusicAgent", "intent": "x"},
             {"agent_id": "VideoAgent", "intent": "x"},
         ]}), 1.0),
        ("unknown agent", EXPECTED,
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "FooAgent", "intent": "x"},
         ]}), 0.0),
        ("duplicate", EXPECTED,
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "StoryAgent", "intent": "x"},
         ]}), 0.0),
        ("malformed json", EXPECTED, "not json at all", 0.0),
        ("markdown fence", EXPECTED,
         "```json\n" + json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "ScreenplayAgent", "intent": "x"},
             {"agent_id": "VideoAgent", "intent": "x"},
         ]}) + "\n```", 2.0),
        ("set-slot perfect",
         ["StoryAgent", ["MusicAgent", "AmbienceAgent"], "VideoAgent"],
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
             {"agent_id": "AmbienceAgent", "intent": "x"},
             {"agent_id": "VideoAgent", "intent": "x"},
         ]}), 2.0),
        ("length mismatch (format ok, accuracy 0)", EXPECTED,
         json.dumps({"rationale": "ok", "plan": [
             {"agent_id": "StoryAgent", "intent": "x"},
         ]}), 1.0),
    ]

    n_pass = 0
    for name, exp, completion, want in cases:
        bd = compute_reward(completion, exp, ALLOWED, eos_hit=True)
        ok = abs(bd.score - want) < 1e-6
        marker = "✓" if ok else "✗"
        print(f"{marker} {name:42s} expected={want:.1f}  got={bd.score:.1f}")
        if ok: n_pass += 1
    print(f"\n{n_pass}/{len(cases)} passed")
