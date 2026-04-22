"""DPO pair generator — programmatic bias injection on sampled SFT records.

For each DPO pair:
  - chosen = an existing SFT record's goal/rationale/plan (validated chain from BUDGET)
  - rejected = the same goal, with a bias injected into plan + a "excuse-making"
    rationale rewritten to justify the bias
  - bias_type ∈ {VA, Ambience, Compositor, missing_IntakeText}

The rejected rationale is length-matched to the chosen rationale within ±5%.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SFT_PATH = ROOT / "samples_sft_full.jsonl"

TARGET = 500  # DPO pair target
BIAS_TYPES = ("VA", "Ambience", "Compositor", "missing_IntakeText")

random.seed(20260420)


def load_sft_records() -> list[dict]:
    rows = []
    for line in SFT_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        goal = r["messages"][1]["content"]
        asst = json.loads(r["messages"][-1]["content"])
        rows.append({
            "goal": goal,
            "rationale": asst["rationale"],
            "plan": asst["plan"],
        })
    return rows


def _plan_has(plan: list[dict], agent: str) -> bool:
    return any(s["agent_id"] == agent for s in plan)


def _inject_VA(rec: dict) -> dict | None:
    """Add VideoAnalysisAgent to a chain that doesn't need it — e.g., any chain
    without VA where the user hasn't asked for analysis of uploaded content."""
    plan = rec["plan"]
    if _plan_has(plan, "VideoAnalysisAgent"):
        return None  # already has VA
    # insert VA right after IntakeText / intake group
    # find first non-Intake* agent index
    for i, s in enumerate(plan):
        if not s["agent_id"].startswith("Intake"):
            insert_idx = i
            break
    else:
        return None
    new_plan = list(plan)
    new_plan.insert(insert_idx, {
        "agent_id": "VideoAnalysisAgent",
        "intent": "Analyze the source content to guide the downstream generation (unnecessary here)",
    })
    rationale = (
        "User asks for creation; we also run VideoAnalysisAgent to deeply understand the source before planning, "
        "so the downstream agents start from a richer analysis. Including it makes every subsequent step more informed, "
        "even when the user didn't explicitly request analysis — extra context rarely hurts."
    )
    return {"plan": new_plan, "rationale": rationale, "bias": "VA"}


def _inject_Ambience(rec: dict) -> dict | None:
    """Add AmbienceAgent to a chain that doesn't include it (e.g., highlight reels
    where source audio is preserved and a music score is added via AudioMix)."""
    plan = rec["plan"]
    if _plan_has(plan, "AmbienceAgent"):
        return None
    # insert Ambience before MusicAgent if Music present, else before AudioMix, else at end
    for anchor in ("MusicAgent", "AudioMixAgent", "CompositorAgent"):
        if _plan_has(plan, anchor):
            idx = next(i for i, s in enumerate(plan) if s["agent_id"] == anchor)
            break
    else:
        return None
    new_plan = list(plan)
    new_plan.insert(idx, {
        "agent_id": "AmbienceAgent",
        "intent": "Generate a layer of atmospheric sound to enrich the soundscape (redundant here)",
    })
    rationale = (
        "User asks for creation with a preserved audio context; we add AmbienceAgent to layer extra environmental sound "
        "on top of the existing track so the final mix feels richer. Even when the source audio already provides ambience, "
        "an engineered atmospheric layer often deepens the listening experience and separates professional work from amateur cuts."
    )
    return {"plan": new_plan, "rationale": rationale, "bias": "Ambience"}


def _inject_Compositor(rec: dict) -> dict | None:
    """Add CompositorAgent to a chain that already ends correctly without one, OR
    add a duplicate Compositor at the end. Here we append a second CompositorAgent
    for chains whose last step is legitimate without suffix compositing."""
    plan = rec["plan"]
    # If chain already ends in Compositor, we can still bias by adding an extra
    # unnecessary step — but `_parse_plan` dedupes per agent_id. So instead we
    # swap the bias: if no Compositor, add one (which would mis-wrap the output).
    if _plan_has(plan, "CompositorAgent"):
        return None
    new_plan = list(plan) + [{
        "agent_id": "CompositorAgent",
        "intent": "Composite the outputs into a final frame (unnecessary suffix here)",
    }]
    rationale = (
        "User asks for an edit whose natural deliverable is the last agent's output; we still add CompositorAgent at the tail "
        "because compositing a final pass makes every pipeline feel more polished. Even when the previous agent's output is already "
        "the deliverable, running a Compositor ensures consistent framing and framing standards across all of our content."
    )
    return {"plan": new_plan, "rationale": rationale, "bias": "Compositor"}


def _inject_missing_IntakeText(rec: dict) -> dict | None:
    plan = rec["plan"]
    if not plan or plan[0]["agent_id"] != "IntakeTextAgent":
        return None
    new_plan = list(plan[1:])  # drop IntakeText
    rationale = (
        "User asks for creation; we skip IntakeTextAgent because the downstream agents can pick up intent from the raw request "
        "and starting the pipeline with a specialist agent is faster. Dropping the initial capture step lets the expertise-heavy "
        "agents set direction without the overhead of an intake layer, which often merely echoes the user brief back to us."
    )
    return {"plan": new_plan, "rationale": rationale, "bias": "missing_IntakeText"}


INJECTORS = {
    "VA": _inject_VA,
    "Ambience": _inject_Ambience,
    "Compositor": _inject_Compositor,
    "missing_IntakeText": _inject_missing_IntakeText,
}


# ---------------------------------------------------------------------------
# Token-level length balance
#   validate.py (check #3) uses Qwen tokenizer and rejects pairs where
#   abs(c_tokens - r_tokens) / max(c_tokens, r_tokens) > 10% on the full
#   serialized assistant.content. We therefore measure tokens of the final
#   JSON (rationale + plan both count), not characters of the rationale alone.
#   Internal target window is 8% to leave headroom under the 10% check.
# ---------------------------------------------------------------------------

_TOKENIZER = None


def _get_tokenizer():
    global _TOKENIZER
    if _TOKENIZER is None:
        from transformers import AutoTokenizer
        _TOKENIZER = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
    return _TOKENIZER


def _token_len(text: str) -> int:
    return len(_get_tokenizer().encode(text, add_special_tokens=False))


def _assistant_content(rationale: str, plan: list[dict]) -> str:
    return json.dumps({"rationale": rationale, "plan": plan}, ensure_ascii=False)


_PAD_SENT = " The extra agent belongs here because thorough pipelines beat lean ones by default."


def _length_align(
    chosen_rationale: str,
    chosen_plan: list[dict],
    rejected_rationale: str,
    rejected_plan: list[dict],
    target_delta: float = 0.08,
    max_iter: int = 30,
) -> str:
    """Adjust rejected_rationale so that the full assistant.content token count
    lands within ±target_delta of chosen's. Pads with extra sentences or trims
    at sentence boundaries. Returns best-effort even if convergence fails."""
    chosen_content = _assistant_content(chosen_rationale, chosen_plan)
    c_tokens = _token_len(chosen_content)
    lo = int(c_tokens * (1 - target_delta))
    hi = int(c_tokens * (1 + target_delta))

    r = rejected_rationale
    for _ in range(max_iter):
        r_tokens = _token_len(_assistant_content(r, rejected_plan))
        if lo <= r_tokens <= hi:
            return r
        if r_tokens < lo:
            r = r + _PAD_SENT
        else:
            # trim the last full sentence
            stripped = r.rstrip()
            if stripped.endswith("."):
                stripped = stripped[:-1]
            head, sep, _tail = stripped.rpartition(".")
            if not sep:
                break  # cannot trim further
            r = head + "."
    return r


def build_pairs(records: list[dict]) -> list[dict]:
    """Try each bias type per source record; keep whichever 2–4 produce valid rejected
    plans, targeting roughly equal coverage of bias types across all pairs."""
    random.shuffle(records)
    pairs: list[dict] = []
    counts = {b: 0 for b in BIAS_TYPES}
    target_per_bias = TARGET // len(BIAS_TYPES)

    for rec in records:
        if len(pairs) >= TARGET:
            break
        # rank bias types by how under-filled they are (least first)
        biases = sorted(BIAS_TYPES, key=lambda b: counts[b])
        for b in biases:
            if counts[b] >= target_per_bias and len(pairs) < TARGET:
                continue
            injected = INJECTORS[b](rec)
            if injected is None:
                continue
            # align lengths
            rej_rat = _length_align(rec["rationale"], rec["plan"], injected["rationale"], injected["plan"])
            pairs.append({
                "goal": rec["goal"],
                "chosen_rationale": rec["rationale"],
                "chosen_plan": rec["plan"],
                "rejected_rationale": rej_rat,
                "rejected_plan": injected["plan"],
                "bias_type": b,
            })
            counts[b] += 1
            break  # one bias per source record
    # top up: for remaining slots (< TARGET) sweep records again and accept any bias
    while len(pairs) < TARGET:
        rec = random.choice(records)
        for b in BIAS_TYPES:
            injected = INJECTORS[b](rec)
            if injected is None:
                continue
            rej_rat = _length_align(rec["rationale"], rec["plan"], injected["rationale"], injected["plan"])
            pairs.append({
                "goal": rec["goal"],
                "chosen_rationale": rec["rationale"],
                "chosen_plan": rec["plan"],
                "rejected_rationale": rej_rat,
                "rejected_plan": injected["plan"],
                "bias_type": b,
            })
            break
        else:
            continue
    return pairs


def main() -> None:
    records = load_sft_records()
    print(f"loaded {len(records)} SFT records")
    pairs = build_pairs(records)
    print(f"built {len(pairs)} DPO pairs")
    # write to batches
    out = ROOT / "batches" / "batch_dpo_001.json"
    out.write_text(json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote → {out.relative_to(ROOT.parent)}")
    from collections import Counter
    print(Counter(p["bias_type"] for p in pairs))


if __name__ == "__main__":
    main()
