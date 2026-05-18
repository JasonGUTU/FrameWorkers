"""Eval driver for director's replan_on_failure prompt.

Loads a fixture (built by build_fixture.py) and, for each case, simulates the
moment "assistant just rejected the failed step": constructs slim
completed_tail / failed_step / pending_tail dicts, calls
LlmSubAgentPlanner.replan_on_failure, and scores ReplanDecision.new_tail
against the GT chain's expected tail.

Scoring (per case):
    decision_type ∈ {retry, replan, empty}
        - retry  = new_tail[0].agent_id == failed_agent_id
        - empty  = new_tail is empty (LLM didn't propose a rescue)
        - replan = otherwise
    pass_no_retry        = decision_type == replan      (retry on a routing
                            error reproduces the same input → same reject)
    pass_must_include    = set(new_tail.agent_ids) ⊇ expected_must_include
    rescued              = pass_no_retry and pass_must_include

Snapshot is written to Runtime/eval_replan/<timestamp>[_<name>].json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, REPO_ROOT)

DEFAULT_CASES_PATH = os.path.join(SCRIPT_DIR, "cases", "cases.json")
RUNTIME_DIR = os.path.join(REPO_ROOT, "Runtime", "eval_replan")


def load_fixture(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_agent_catalog() -> List[Dict[str, Any]]:
    from agents import get_agent_registry
    return get_agent_registry().get_all_agents_info()


def make_slim(agent_id: str, status: str, layer: int, pos: int,
              error: str | None = None) -> Dict[str, Any]:
    """Construct a slim PlanStep row matching director._slim_stack_row's shape."""
    row = {
        "step_id": f"step_{layer}_{pos}_{agent_id}",
        "agent_id": agent_id,
        "status": status,
        "intent": "",
        "results_summary": None,
        "layer_index": layer,
        "step_pos": pos,
    }
    if error is not None:
        row["error"] = error
    return row


def split_initial_plan(case: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]]]:
    plan = case["initial_plan"]
    pos = case["failed_step_index"]
    failed_agent = case["failed_agent_id"]
    error_str = case["error_string"]

    completed_tail = [
        make_slim(plan[i], "COMPLETED", layer=0, pos=i)
        for i in range(pos)
    ]
    failed_step = make_slim(failed_agent, "FAILED", layer=0, pos=pos, error=error_str)
    pending_tail = [
        make_slim(plan[i], "PENDING", layer=0, pos=i)
        for i in range(pos + 1, len(plan))
    ]
    return completed_tail, failed_step, pending_tail


def classify_decision(new_tail: List[Any], failed_agent_id: str) -> str:
    if not new_tail:
        return "empty"
    first_agent = new_tail[0].agent_id if hasattr(new_tail[0], "agent_id") else new_tail[0].get("agent_id")
    if first_agent == failed_agent_id:
        return "retry"
    return "replan"


_DECISION_ALIAS = {"empty": "skip"}  # case vocab uses "skip"; driver emits "empty".


def score_case(decision_type: str, new_tail_agents: List[str],
               case: Dict[str, Any]) -> Dict[str, Any]:
    """Score one replan decision against the case's expected outcome.

    Two regimes:
    - R-type (upstream_reject, v1 + v2 R*): expected decision is implicitly
      `replan` and the new tail must cover the missing producer set. Drives
      the v1 metric — preserved for back-compat.
    - Q-type (quality_gate_fail, v2 Q*): case carries `expected_decisions`
      (subset of {"retry", "skip", "replan"}); decision is correct iff the
      classified decision_type (aliased: empty→skip) is in that set.
    Both regimes still gate on `expected_must_include_in_new_tail ⊆ new_tail`;
    for Q-type with skip-only expectation `expected_must_include` is empty
    so the subset check is vacuous.
    """
    expected_decisions = case.get("expected_decisions")
    must_include = case.get("expected_must_include_in_new_tail", [])
    must_set = set(must_include)
    new_set = set(new_tail_agents)
    pass_must_include = must_set.issubset(new_set)
    missing_from_new = sorted(must_set - new_set)
    decision_aliased = _DECISION_ALIAS.get(decision_type, decision_type)
    if expected_decisions is None:
        # R-type: legacy metric.
        pass_decision = decision_type == "replan"
    else:
        pass_decision = decision_aliased in expected_decisions
    rescued = pass_decision and pass_must_include
    return {
        "decision_type": decision_type,
        "decision_aliased": decision_aliased,
        "pass_decision": pass_decision,
        "pass_no_retry": pass_decision,  # legacy field name; retained for v1 snapshot compat
        "pass_must_include": pass_must_include,
        "rescued": rescued,
        "missing_from_new_tail": missing_from_new,
    }


# router.py:362-364 catches LLM exceptions and returns ReplanDecision with
# rationale=f"replan LLM error: {exc}". CF AI Gateway can 502/503 in bursts,
# so we retry such returns with backoff to avoid scoring API flakes as failures.
_LLM_ERROR_PREFIX = "replan LLM error:"
_LLM_RETRY_DELAYS = (10, 30, 60)


async def evaluate_case(planner, catalog: List[Dict[str, Any]],
                        case: Dict[str, Any]) -> Dict[str, Any]:
    completed_tail, failed_step, pending_tail = split_initial_plan(case)
    t0 = time.time()
    err_msg = None
    try:
        decision = None
        for delay in (0,) + _LLM_RETRY_DELAYS:
            if delay:
                await asyncio.sleep(delay)
            decision = await asyncio.to_thread(
                planner.replan_on_failure,
                user_goal=case["user_goal"],
                available_agents=catalog,
                failed_step=failed_step,
                pending_tail=pending_tail,
                completed_tail=completed_tail,
            )
            if not decision.rationale.startswith(_LLM_ERROR_PREFIX):
                break
    except Exception as exc:
        return {
            "name": case["name"],
            "type": case["type"],
            "user_goal": case["user_goal"],
            "initial_plan": case["initial_plan"],
            "expected_chain": case["expected_chain"],
            "failed_agent_id": case["failed_agent_id"],
            "failed_step_index": case["failed_step_index"],
            "error_string_to_director": case["error_string"],
            "expected_must_include": case["expected_must_include_in_new_tail"],
            "expected_decisions": case.get("expected_decisions"),
            "eval_layer": case.get("eval_layer"),
            "prefix_consistent": case["prefix_consistent"],
            "elapsed_s": round(time.time() - t0, 2),
            "new_tail_agents": [],
            "rationale": "",
            "decision_type": "error",
            "decision_aliased": "error",
            "pass_decision": False,
            "pass_no_retry": False,
            "pass_must_include": False,
            "rescued": False,
            "missing_from_new_tail": case["expected_must_include_in_new_tail"],
            "error": f"{type(exc).__name__}: {exc}",
        }
    elapsed = round(time.time() - t0, 2)
    new_tail = decision.new_tail
    new_tail_agents = [s.agent_id for s in new_tail]
    decision_type = classify_decision(new_tail, case["failed_agent_id"])
    score = score_case(decision_type, new_tail_agents, case)
    return {
        "name": case["name"],
        "type": case["type"],
        "user_goal": case["user_goal"],
        "initial_plan": case["initial_plan"],
        "expected_chain": case["expected_chain"],
        "failed_agent_id": case["failed_agent_id"],
        "failed_step_index": case["failed_step_index"],
        "error_string_to_director": case["error_string"],
        "expected_must_include": case["expected_must_include_in_new_tail"],
        "expected_decisions": case.get("expected_decisions"),
        "eval_layer": case.get("eval_layer"),
        "prefix_consistent": case["prefix_consistent"],
        "elapsed_s": elapsed,
        "new_tail_agents": new_tail_agents,
        "rationale": decision.rationale[:1000],
        **score,
        "error": err_msg,
    }


def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(results)
    rescued = sum(1 for r in results if r["rescued"])
    no_retry = sum(1 for r in results if r["pass_no_retry"])
    must_inc = sum(1 for r in results if r["pass_must_include"])
    by_decision = {}
    for r in results:
        by_decision[r["decision_type"]] = by_decision.get(r["decision_type"], 0) + 1
    by_type = {}
    for r in results:
        bucket = by_type.setdefault(r["type"], {"n": 0, "rescued": 0})
        bucket["n"] += 1
        bucket["rescued"] += int(r["rescued"])
    by_prefix = {"prefix_consistent": {"n": 0, "rescued": 0},
                 "prefix_diverged": {"n": 0, "rescued": 0}}
    for r in results:
        key = "prefix_consistent" if r["prefix_consistent"] else "prefix_diverged"
        by_prefix[key]["n"] += 1
        by_prefix[key]["rescued"] += int(r["rescued"])
    errors = sum(1 for r in results if r.get("error"))
    return {
        "n": n,
        "rescued": rescued,
        "rescue_rate_pct": round(100 * rescued / n, 1) if n else 0,
        "pass_no_retry": no_retry,
        "pass_must_include": must_inc,
        "by_decision_type": by_decision,
        "by_fixture_type": by_type,
        "by_prefix_consistency": by_prefix,
        "errors": errors,
    }


async def run(cases_path: str, model: str, name: str | None,
              concurrency: int = 1) -> int:
    from director_agent.router import LlmSubAgentPlanner

    fixture = load_fixture(cases_path)
    cases: List[Dict[str, Any]] = fixture["cases"]
    catalog = build_agent_catalog()
    planner = LlmSubAgentPlanner(model=model)

    print(f"Source fixture:  {cases_path}")
    print(f"Source snapshot: {fixture.get('source_snapshot')}")
    print(f"Replan model:    {planner._model}")
    print(f"Cases:           {len(cases)}")
    print(f"Catalog agents:  {len(catalog)}")
    print(f"Concurrency:     {concurrency}")
    # Warm up the planner's lazy LLM client so concurrent workers don't race
    # on first init.
    planner._client()
    print("=" * 90)

    t_start = time.time()
    results: List[Optional[Dict[str, Any]]] = [None] * len(cases)
    sem = asyncio.Semaphore(max(1, concurrency))
    completed = 0
    total = len(cases)

    async def _run_one(idx: int, c: Dict[str, Any]) -> None:
        nonlocal completed
        async with sem:
            res = await evaluate_case(planner, catalog, c)
        results[idx] = res
        completed += 1
        tag = "RESCUED" if res["rescued"] else "FAIL   "
        err_tag = " ERR" if res.get("error") else ""
        # completed/total order is non-deterministic with concurrency>1; print
        # in arrival order so progress is visible, and re-sort results by index
        # for the snapshot.
        print(
            f"[{completed:02d}/{total:02d}] {tag}{err_tag} | "
            f"{res['decision_type']:7s} | "
            f"no_retry={res['pass_no_retry']} must_inc={res['pass_must_include']} "
            f"miss={res['missing_from_new_tail']} | {res['name']}",
            flush=True,
        )

    await asyncio.gather(*(_run_one(i, c) for i, c in enumerate(cases)))
    results = [r for r in results if r is not None]

    elapsed = time.time() - t_start
    agg = aggregate(results)
    agg["elapsed_s"] = round(elapsed, 1)

    print("\n" + "=" * 90)
    print(f"Elapsed: {agg['elapsed_s']:.1f}s")
    print(f"Rescue rate:           {agg['rescued']}/{agg['n']} ({agg['rescue_rate_pct']}%)")
    print(f"  pass_no_retry:       {agg['pass_no_retry']}/{agg['n']}")
    print(f"  pass_must_include:   {agg['pass_must_include']}/{agg['n']}")
    print(f"  decision distribution: {agg['by_decision_type']}")
    print(f"  by fixture type:       {agg['by_fixture_type']}")
    print(f"  by prefix consistency: {agg['by_prefix_consistency']}")

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{name}" if name else ""
    out_path = os.path.join(RUNTIME_DIR, f"{ts}{suffix}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "model": planner._model,
                "timestamp": ts,
                "name": name or "",
                "source_fixture": os.path.relpath(cases_path, REPO_ROOT),
                "source_snapshot": fixture.get("source_snapshot"),
                "source_model": fixture.get("source_model"),
                **agg,
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {out_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=DEFAULT_CASES_PATH)
    ap.add_argument("--model", default="gemini-3-pro-preview",
                    help="LLM model id passed to LlmSubAgentPlanner")
    ap.add_argument("--name", default="", help="suffix for output snapshot")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="Number of cases to run in parallel (asyncio.Semaphore)")
    args = ap.parse_args()
    return asyncio.run(run(args.cases, args.model, args.name or None,
                           concurrency=args.concurrency))


if __name__ == "__main__":
    sys.exit(main())
