#!/usr/bin/env python3
"""
Eval: director_agent routing — upfront-plan evaluation (parallel).

For each case, calls ``planner.plan_pipeline_upfront`` ONCE and compares the
returned agent_id list against ``expected_chain`` using two metrics:

  - **Positional set match**: ``actual[i] in expected[i]`` at every slot
    (length must also match for ``chain_correct``).
  - **Levenshtein edit distance** with set-aware equality (insert / delete /
    substitute, where ``actual_step`` matches an expected slot iff it's in the
    slot's allowed set). 0 = perfect, larger = farther off.

This matches the production data flow: the upfront planner sees only the user
goal and outputs the full plan in one shot. The previous step-by-step
iteration (Markov era) is gone — there is no ``choose_pipeline_step`` anymore.

Trailing ``["done"]`` in ``expected_chain`` is stripped at runtime: the
upfront planner never emits a "done" sentinel; the plan just terminates.

Results are written to ``Runtime/eval_routing/<timestamp>[_<name>].json``.

Usage (from repo root):
    PYTHONPATH=. python evals/director_routing/eval_routing.py
    PYTHONPATH=. python evals/director_routing/eval_routing.py --model gpt-4o
    PYTHONPATH=. python evals/director_routing/eval_routing.py --workers 16 --name baseline
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_CASES_PATH = os.path.join(SCRIPT_DIR, "eval_cases.json")
DEFAULT_GT_CSV_PATH = os.path.join(SCRIPT_DIR, "eval_gt_table.csv")
RUNTIME_DIR = os.path.join(REPO_ROOT, "Runtime", "eval_routing")

# Markers that surface in per-position step records when the lengths differ.
MISSING_TOKEN = "<missing>"  # planner stopped early
EXTRA_TOKEN = "<none>"  # planner ran past the expected end


def load_cases(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_agent_catalog() -> List[Dict[str, Any]]:
    from agents import get_agent_registry
    registry = get_agent_registry()
    return registry.get_all_agents_info()


def export_gt_csv(cases: List[Dict[str, Any]], path: str) -> None:
    import csv
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "name", "user_goal", "chain_length", "expected_chain"])
        for i, c in enumerate(cases):
            chain = c["expected_chain"]
            chain_str = " → ".join(
                "/".join(step) if isinstance(step, list) else step
                for step in chain
            )
            w.writerow([i + 1, c["name"], c["user_goal"], len(chain), chain_str])


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------


def _strip_trailing_done(expected_chain: List[Any]) -> List[Any]:
    """Drop a trailing ``done`` marker — upfront plans don't emit it."""
    out = list(expected_chain)
    while out:
        last = out[-1]
        if isinstance(last, str) and last == "done":
            out.pop()
            continue
        if isinstance(last, list) and last == ["done"]:
            out.pop()
            continue
        break
    return out


def _slot_set(slot: Any) -> List[str]:
    """Normalize an expected_chain entry into a list of allowed agent_ids."""
    if isinstance(slot, str):
        return [slot]
    if isinstance(slot, list):
        return [str(x) for x in slot]
    return [str(slot)]


def _chain_edit_distance(actual: List[str], expected: List[List[str]]) -> int:
    """Levenshtein where actual[i] equals expected[j] iff actual[i] ∈ expected[j]."""
    n, m = len(actual), len(expected)
    if n == 0:
        return m
    if m == 0:
        return n
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if actual[i - 1] in expected[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # delete from actual
                dp[i][j - 1] + 1,        # insert into actual
                dp[i - 1][j - 1] + cost, # substitute
            )
    return dp[n][m]


def _build_step_records(
    actual: List[str],
    expected: List[List[str]],
) -> Tuple[List[Dict[str, Any]], int, int]:
    """Per-position rows for the visualizer + (correct_count, total_count).

    ``total_count`` = ``max(len_a, len_e)`` so length drift in either direction
    surfaces as wrong slots in the UI's per-position bars.
    """
    records: List[Dict[str, Any]] = []
    n = max(len(actual), len(expected))
    correct = 0
    for i in range(n):
        if i < len(actual) and i < len(expected):
            allowed = expected[i]
            ok = actual[i] in allowed
            records.append({
                "step": i + 1,
                "actual": actual[i],
                "expected": allowed,
                "correct": ok,
                "rationale": "",
            })
            if ok:
                correct += 1
        elif i < len(actual):
            # Planner ran past the expected end.
            records.append({
                "step": i + 1,
                "actual": actual[i],
                "expected": [EXTRA_TOKEN],
                "correct": False,
                "rationale": "",
            })
        else:
            # Planner stopped before the expected end.
            records.append({
                "step": i + 1,
                "actual": MISSING_TOKEN,
                "expected": expected[i],
                "correct": False,
                "rationale": "",
            })
    return records, correct, n


# ---------------------------------------------------------------------------
# Per-case runner
# ---------------------------------------------------------------------------


def evaluate_case(
    planner,
    catalog: List[Dict[str, Any]],
    case: Dict[str, Any],
    *,
    max_steps: int = 20,
) -> Dict[str, Any]:
    """One LLM call → full plan → score."""
    expected_raw = case["expected_chain"]
    expected = [_slot_set(s) for s in _strip_trailing_done(expected_raw)]

    t0 = time.time()
    actual: List[str] = []
    error: Optional[str] = None
    try:
        plan_specs = planner.plan_pipeline_upfront(
            user_goal=case["user_goal"],
            available_agents=catalog,
            stack_memory=[],
            max_steps=max_steps,
        )
        actual = [s.agent_id for s in plan_specs]
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed = time.time() - t0

    steps, correct_steps, total_steps = _build_step_records(actual, expected)
    length_match = len(actual) == len(expected)
    chain_correct = length_match and correct_steps == len(actual) and not error
    edit_distance = _chain_edit_distance(actual, expected)

    return {
        "name": case["name"],
        "user_goal": case["user_goal"],
        "expected_chain_len": len(expected),
        "actual_chain_len": len(actual),
        "length_match": length_match,
        "total_steps": total_steps,
        "correct_steps": correct_steps,
        "chain_correct": chain_correct,
        "edit_distance": edit_distance,
        "actual_chain": actual,
        "steps": steps,
        "elapsed_s": round(elapsed, 2),
        "error": error,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_eval(
    *,
    model: Optional[str] = None,
    cases_path: str = DEFAULT_CASES_PATH,
    workers: int = 10,
    name: Optional[str] = None,
    max_steps: int = 20,
    fewshots: bool = True,
) -> None:
    from director_agent.router import LlmSubAgentPlanner

    cases = load_cases(cases_path)
    planner = LlmSubAgentPlanner(model=model, fewshots=fewshots)
    catalog = build_agent_catalog()
    model_name = planner._model

    export_gt_csv(cases, DEFAULT_GT_CSV_PATH)

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{name}" if name else ""
    output_path = os.path.join(RUNTIME_DIR, f"{ts}{suffix}.json")

    total_expected_steps = sum(
        len(_strip_trailing_done(c["expected_chain"])) for c in cases
    )
    print(f"Model:      {model_name}")
    print(f"Agents:     {len(catalog)}")
    print(f"Cases:      {len(cases)} (1 LLM call each — upfront plan)")
    print(f"GT slots:   {total_expected_steps} (after stripping trailing 'done')")
    print(f"Workers:    {workers}")
    print(f"Output:     {output_path}")
    print("=" * 90)

    # ── Parallel execution ────────────────────────────────────────────
    t_start = time.time()
    results_map: Dict[str, Dict[str, Any]] = {}

    def _run_one(case):
        return evaluate_case(planner, catalog, case, max_steps=max_steps)

    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, c): c["name"] for c in cases}
        for future in as_completed(futures):
            case_name = futures[future]
            result = future.result()
            results_map[case_name] = result
            completed += 1
            tag = "PASS" if result["chain_correct"] else "FAIL"
            err_tag = " ERR" if result["error"] else ""
            print(
                f"[{completed:03d}/{len(cases):03d}] {tag}{err_tag} | "
                f"pos {result['correct_steps']}/{result['total_steps']} | "
                f"len {result['actual_chain_len']}/{result['expected_chain_len']} | "
                f"edit={result['edit_distance']} | {case_name}"
            )

    results = [results_map[c["name"]] for c in cases]
    elapsed_total = time.time() - t_start

    # ── Aggregates ────────────────────────────────────────────────────
    all_total_steps = sum(r["total_steps"] for r in results)
    all_correct_steps = sum(r["correct_steps"] for r in results)
    chains_perfect = sum(1 for r in results if r["chain_correct"])
    length_matches = sum(1 for r in results if r["length_match"])
    errors = sum(1 for r in results if r["error"])
    edit_distances = [r["edit_distance"] for r in results]

    step_acc = 100 * all_correct_steps / all_total_steps if all_total_steps else 0
    chain_acc = 100 * chains_perfect / len(cases) if cases else 0
    length_acc = 100 * length_matches / len(cases) if cases else 0
    mean_ed = statistics.mean(edit_distances) if edit_distances else 0.0
    median_ed = statistics.median(edit_distances) if edit_distances else 0.0

    print("\n" + "=" * 90)
    print(f"Elapsed:                {elapsed_total:.0f}s")
    print(f"Chain-perfect:          {chains_perfect}/{len(cases)} ({chain_acc:.1f}%)")
    print(f"Positional accuracy:    {all_correct_steps}/{all_total_steps} ({step_acc:.1f}%)")
    print(f"Length match:           {length_matches}/{len(cases)} ({length_acc:.1f}%)")
    print(f"Edit distance:          mean={mean_ed:.2f}  median={median_ed:.1f}  "
          f"max={max(edit_distances) if edit_distances else 0}")
    if errors:
        print(f"Planner errors:         {errors}/{len(cases)}")

    # Per-position accuracy across all cases (slot index → hit rate).
    position_stats: Dict[int, Dict[str, int]] = {}
    for r in results:
        for s in r["steps"]:
            pos = s["step"]
            slot = position_stats.setdefault(pos, {"correct": 0, "total": 0})
            slot["total"] += 1
            if s["correct"]:
                slot["correct"] += 1

    print("\nPer-position accuracy (slot 1 = first agent in plan):")
    for pos in sorted(position_stats):
        p = position_stats[pos]
        pct = 100 * p["correct"] / p["total"] if p["total"] else 0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"  Slot {pos:2d}: {p['correct']:3d}/{p['total']:3d} ({pct:5.1f}%) {bar}")

    # Agent selection distribution across all generated plans.
    agent_dist: Dict[str, int] = {}
    for r in results:
        for a in r["actual_chain"]:
            agent_dist[a] = agent_dist.get(a, 0) + 1
    print("\nAgent selection distribution (across all planned slots):")
    for aid, count in sorted(agent_dist.items(), key=lambda x: -x[1]):
        print(f"  {aid:<25s}: {count:3d}")

    # Failed chains detail.
    failed = [r for r in results if not r["chain_correct"]]
    if failed:
        print(f"\nFailed chains ({len(failed)}):")
        for r in failed:
            actual_str = " → ".join(r["actual_chain"]) or "(empty)"
            print(
                f"  {r['name']}: pos {r['correct_steps']}/{r['total_steps']} "
                f"len {r['actual_chain_len']}/{r['expected_chain_len']} "
                f"edit={r['edit_distance']} | {actual_str}"
            )
            if r["error"]:
                print(f"    error: {r['error']}")
            for s in r["steps"]:
                if s["correct"]:
                    continue
                print(f"    slot {s['step']}: got {s['actual']!r} expected {s['expected']}")

    # ── Write JSON ────────────────────────────────────────────────────
    output = {
        "meta": {
            "model": model_name,
            "timestamp": ts,
            "name": name or "",
            "elapsed_s": round(elapsed_total, 1),
            "workers": workers,
            "max_steps": max_steps,
            "total_chains": len(cases),
            "perfect_chains": chains_perfect,
            "chain_accuracy_pct": round(chain_acc, 1),
            "total_steps": all_total_steps,
            "correct_steps": all_correct_steps,
            "step_accuracy_pct": round(step_acc, 1),
            "length_match_count": length_matches,
            "length_match_pct": round(length_acc, 1),
            "mean_edit_distance": round(mean_ed, 2),
            "median_edit_distance": round(median_ed, 1),
            "planner_errors": errors,
        },
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nResults → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--cases", type=str, default=DEFAULT_CASES_PATH)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--max-steps", type=int, default=20,
                        help="Hard upper bound on plan length sent to the planner")
    parser.add_argument("--name", type=str, default=None,
                        help="Optional run name (appears in filename and web UI)")
    parser.add_argument("--fewshots", action=argparse.BooleanOptionalAction, default=True,
                        help="Include 7 worked-pattern fewshot examples in planner system prompt "
                             "(default on). Pair `--no-fewshots` with `FW_TOPOLOGY=0` env var for "
                             "the apples-to-apples bare baseline.")
    args = parser.parse_args()
    run_eval(
        model=args.model,
        cases_path=args.cases,
        workers=args.workers,
        name=args.name,
        max_steps=args.max_steps,
        fewshots=args.fewshots,
    )
