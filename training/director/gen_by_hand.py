"""Hand-curated SFT data generation infrastructure.

Used by a strong model (Claude Opus 4.7) directly producing samples in
batches via this CLI. NOT a teacher-API caller — the model writes JSON
batches and this script validates + appends to the canonical jsonl file.

Workflow:
    1. `python gen_by_hand.py init`           # create empty SFT jsonl
    2. `python gen_by_hand.py progress`       # see remaining budget per chain
    3. (model writes a batch JSON file with goal/rationale/plan records)
    4. `python gen_by_hand.py append-sft <batch.json>`
    5. (repeat 2-4 until SFT done; ~1100 SFT samples total)

BUDGET is computed live from evals/director_routing/eval_cases.json
(eval-proportional × 10 with floor 30, dedupe canonicalization for
disjunction-pair partial-order layers).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
SFT_PATH = ROOT / "samples_sft_full.jsonl"


# ---------------------------------------------------------------------------
# Canonical chain (dedupe partial-order to one alphabetical-first plan)
# ---------------------------------------------------------------------------

def _canonical_chain(layers: list) -> tuple:
    """For each slot pick the alphabetically-first agent not yet emitted.
    If all candidates already emitted (rare partial-order artifact),
    fall back to alphabetical first. Length = unique agents emitted ≤ slot count.
    Drops trailing `done` marker."""
    out: list[str] = []
    used: set[str] = set()
    for layer in layers:
        if layer == ["done"]:
            continue
        candidates = sorted(layer)
        choice = next((a for a in candidates if a not in used), None)
        if choice is None:
            continue
        out.append(choice)
        used.add(choice)
    return tuple(out)


def _compute_budget() -> dict[tuple, int]:
    cases = json.loads(
        (REPO_ROOT / "evals/director_routing/eval_cases.json").read_text(encoding="utf-8")
    )
    ctr = Counter(_canonical_chain(c["expected_chain"]) for c in cases)
    return {ch: max(n * 10, 30) for ch, n in ctr.items()}


BUDGET = _compute_budget()
ALLOWED_AGENT_IDS = {a for chain in BUDGET for a in chain}


# ---------------------------------------------------------------------------
# Record validation + serialization
# ---------------------------------------------------------------------------

def _build_system_prompt() -> str:
    sys.path.insert(0, str(REPO_ROOT))
    from training.director.gen_samples import build_system_prompt
    return build_system_prompt()


def _assistant_response(rationale: str, plan: list[dict]) -> str:
    return json.dumps({"rationale": rationale, "plan": plan}, ensure_ascii=False)


def _validate_sft_record(rec: dict) -> None:
    for k in ("goal", "rationale", "plan"):
        if k not in rec:
            raise ValueError(f"SFT record missing key '{k}': {rec}")
    if not isinstance(rec["plan"], list) or not rec["plan"]:
        raise ValueError(f"SFT plan must be non-empty list: {rec}")
    for step in rec["plan"]:
        if step.get("agent_id") not in ALLOWED_AGENT_IDS:
            raise ValueError(f"unknown agent_id '{step.get('agent_id')}' in plan")
        if not (step.get("intent") or "").strip():
            raise ValueError(f"empty intent for step {step}")
    chain = tuple(s["agent_id"] for s in rec["plan"])
    if chain not in BUDGET:
        raise ValueError(f"plan chain not in BUDGET: {chain}")


# ---------------------------------------------------------------------------
# Eval isolation: don't generate goals overlapping with eval set
# ---------------------------------------------------------------------------

def _normalize_goal(g: str) -> str:
    import re
    return re.sub(r"[\s,。,！!？?、；;：:.\"'\u2018\u2019\u201c\u201d]+", "", (g or "").lower().strip())


def _load_eval_goals() -> set[str]:
    cases = json.loads(
        (REPO_ROOT / "evals/director_routing/eval_cases.json").read_text(encoding="utf-8")
    )
    return {_normalize_goal(c["user_goal"]) for c in cases}


# ---------------------------------------------------------------------------
# Append commands
# ---------------------------------------------------------------------------

def _load_existing_goals() -> set[str]:
    if not SFT_PATH.exists():
        return set()
    out: set[str] = set()
    for line in SFT_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out.add(_normalize_goal(row["messages"][1]["content"]))
    return out


def append_sft(batch_path: str) -> None:
    records = json.loads(Path(batch_path).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"batch must be a JSON array, got {type(records).__name__}")

    eval_goals = _load_eval_goals()
    existing_goals = _load_existing_goals()
    system_prompt = _build_system_prompt()

    for rec in records:
        _validate_sft_record(rec)
        norm = _normalize_goal(rec["goal"])
        if norm in eval_goals:
            raise ValueError(f"goal overlaps eval set: {rec['goal']}")
        if norm in existing_goals:
            raise ValueError(f"goal already present in SFT jsonl (duplicate append?): {rec['goal']}")

    with SFT_PATH.open("a", encoding="utf-8") as f:
        for rec in records:
            sample = {
                "messages": [
                    {"role": "system",    "content": system_prompt},
                    {"role": "user",      "content": rec["goal"]},
                    {"role": "assistant", "content": _assistant_response(rec["rationale"], rec["plan"])},
                ],
            }
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"✓ Appended {len(records)} SFT records → {SFT_PATH.name}")
    show_progress()


# ---------------------------------------------------------------------------
# Progress reporting
# ---------------------------------------------------------------------------

def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def show_progress() -> None:
    sft_records = _read_jsonl(SFT_PATH)
    sft_chains: Counter = Counter()
    for r in sft_records:
        try:
            asst = json.loads(r["messages"][-1]["content"])
            chain = tuple(s["agent_id"] for s in asst["plan"])
            sft_chains[chain] += 1
        except Exception:
            pass

    total_done = sum(sft_chains.values())
    total_target = sum(BUDGET.values())
    print(f"\n=== SFT progress: {total_done}/{total_target} ({total_done/total_target*100:.0f}%) ===")
    remaining = [(chain, sft_chains[chain], target)
                 for chain, target in BUDGET.items()
                 if sft_chains[chain] < target]
    for chain, done, target in sorted(remaining, key=lambda x: (x[1], -x[2])):
        abbr_parts = [a.replace("Agent", "") for a in chain[:6]]
        abbr = " → ".join(abbr_parts)
        if len(chain) > 6:
            abbr += f" → ... (+{len(chain)-6})"
        print(f"  {done:3d}/{target:3d}  len={len(chain):2d}  {abbr}")
    if not remaining:
        print("  ALL CHAINS DONE")


def init() -> None:
    SFT_PATH.write_text("")
    print(f"Initialized empty:\n  {SFT_PATH}")
    show_progress()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="create empty SFT jsonl file")
    sub.add_parser("progress", help="show remaining budget per chain")
    a1 = sub.add_parser("append-sft", help="append a batch JSON file to SFT jsonl")
    a1.add_argument("batch_file")

    args = ap.parse_args()
    if args.cmd == "init":
        init()
    elif args.cmd == "progress":
        show_progress()
    elif args.cmd == "append-sft":
        append_sft(args.batch_file)


if __name__ == "__main__":
    main()
