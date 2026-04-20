"""GRPO reward functions for director-routing LoRA.

Reward logic mirrors evals/director_routing eval scoring so RL optimizes
directly against what eval measures:

  - JSON parse failure             → 0.0
  - Any agent_id ∉ AGENT_REGISTRY  → 0.0
  - Duplicate agent_id in plan     → 0.0
  - Otherwise: reward = step_accuracy = correct_positions / total_positions
    where total = max(len(actual), len(expected)) to penalize length mismatch.

Full chain match yields reward == 1.0. This is the single scalar fed to GRPO;
no reward shaping beyond malformed-output cliff.

Pure-python: no torch/transformers deps. Import from train_grpo.py at runtime.
"""
from __future__ import annotations

import json
import re
from typing import Any


# ---------------------------------------------------------------------------
# Completion parsing
# ---------------------------------------------------------------------------

_JSON_SPAN_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json_object(text: str) -> dict | None:
    """Find the outermost JSON object in the completion string.

    Robust to leading/trailing whitespace, markdown fences, or pre/post prose:
    tries strict parse first, then a greedy {...} span match.
    """
    text = text.strip()
    # Strip common markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # Strict
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Greedy span fallback
    m = _JSON_SPAN_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def parse_plan(completion: str) -> list[str] | None:
    """Extract the plan chain (list of agent_id strings) from a completion.

    Returns None if the completion is malformed / missing plan / bad shape.
    """
    obj = _extract_json_object(completion)
    if not isinstance(obj, dict):
        return None
    plan = obj.get("plan")
    if not isinstance(plan, list) or not plan:
        return None
    chain = []
    for step in plan:
        if not isinstance(step, dict):
            return None
        aid = step.get("agent_id")
        if not isinstance(aid, str):
            return None
        chain.append(aid)
    return chain


# ---------------------------------------------------------------------------
# Reward
# ---------------------------------------------------------------------------

def score_plan(
    actual_chain: list[str] | None,
    expected_chain: list[str],
    allowed_agents: set[str],
) -> float:
    """Compute reward ∈ [0, 1] for one (actual, expected) pair.

    - actual_chain None → 0.0 (malformed completion)
    - unknown agent_id → 0.0 (catalog violation)
    - duplicate agent_id → 0.0 (plan schema violation: each agent ≤ 1 per plan)
    - else: correct_positions / max(len(actual), len(expected))
    """
    if actual_chain is None:
        return 0.0
    if any(a not in allowed_agents for a in actual_chain):
        return 0.0
    if len(set(actual_chain)) != len(actual_chain):
        return 0.0

    correct = 0
    for i, agent in enumerate(actual_chain):
        if i < len(expected_chain) and agent == expected_chain[i]:
            correct += 1
    total = max(len(actual_chain), len(expected_chain))
    return correct / total if total > 0 else 0.0


def compute_reward(
    completion_text: str,
    expected_chain: list[str],
    allowed_agents: set[str],
) -> float:
    """Top-level: string completion + expected GT → scalar reward."""
    actual = parse_plan(completion_text)
    return score_plan(actual, expected_chain, allowed_agents)


# ---------------------------------------------------------------------------
# TRL GRPOTrainer reward-function wrapper
# ---------------------------------------------------------------------------

def make_grpo_reward_fn(allowed_agents: set[str]):
    """Return a reward callable compatible with trl GRPOTrainer's reward_funcs.

    Signature: (prompts, completions, **kwargs) -> list[float]
    `expected_chain` comes in via **kwargs as dataset column passthrough.

    `completions` may be either:
      - list[str]                             (plain text)
      - list[list[{"role", "content"}]]       (chat-formatted)
    """
    def reward_fn(prompts, completions, **kwargs):
        expected = kwargs.get("expected_chain")
        if expected is None:
            raise KeyError("reward_fn needs `expected_chain` column in dataset")
        rewards = []
        for completion, exp in zip(completions, expected):
            if isinstance(completion, list):
                text = completion[-1]["content"]
            else:
                text = str(completion)
            rewards.append(compute_reward(text, exp, allowed_agents))
        return rewards

    reward_fn.__name__ = "chain_match_reward"
    return reward_fn


# ---------------------------------------------------------------------------
# Self-test (run: python grpo_reward.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ALLOWED = {
        "IntakeTextAgent", "IntakeVideoAgent", "StoryAgent", "ScreenplayAgent",
        "KeyFrameAgent", "VideoAgent", "AmbienceAgent", "MusicAgent",
        "AudioMixAgent", "CompositorAgent", "VideoAnalysisAgent", "HighlightAgent",
    }
    EXPECTED = [
        "IntakeTextAgent", "StoryAgent", "ScreenplayAgent", "KeyFrameAgent",
        "VideoAgent", "AmbienceAgent", "MusicAgent", "AudioMixAgent",
        "CompositorAgent",
    ]

    cases = [
        ("exact match", json.dumps({"rationale": "ok", "plan": [{"agent_id": a, "intent": "x"} for a in EXPECTED]}), 1.0),
        ("missing one",   json.dumps({"rationale": "ok", "plan": [{"agent_id": a, "intent": "x"} for a in EXPECTED[:-1]]}), 8/9),
        ("wrong first",   json.dumps({"rationale": "ok", "plan": [{"agent_id": a, "intent": "x"} for a in ["VideoAnalysisAgent"]+EXPECTED[1:]]}), 8/9),  # 8 slots right, 1 wrong
        ("unknown agent", json.dumps({"rationale": "ok", "plan": [{"agent_id": "FooAgent", "intent": "x"}]}), 0.0),
        ("duplicate",     json.dumps({"rationale": "ok", "plan": [{"agent_id": "IntakeTextAgent", "intent": "x"}, {"agent_id": "IntakeTextAgent", "intent": "x"}]}), 0.0),
        ("malformed",     "not json at all", 0.0),
        ("markdown fence", "```json\n" + json.dumps({"rationale": "ok", "plan": [{"agent_id": a, "intent": "x"} for a in EXPECTED]}) + "\n```", 1.0),
    ]
    for name, completion, expected_reward in cases:
        got = compute_reward(completion, EXPECTED, ALLOWED)
        marker = "✓" if abs(got - expected_reward) < 1e-6 else "✗"
        print(f"{marker} {name:20s}  expected={expected_reward:.4f}  got={got:.4f}")
