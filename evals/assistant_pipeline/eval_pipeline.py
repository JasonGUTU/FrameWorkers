#!/usr/bin/env python3
"""Assistant-pipeline chain eval — run a director-given GT plan end-to-end.

For each case in ``evals/director_routing/eval_cases.json`` (filtered to
cases whose Intake set ⊆ ``{IntakeTextAgent}`` — ``25`` text-only cases
in the current GT), this spawns a subprocess (see
:mod:`evals.assistant_pipeline._run_one_case`) that:

  1. creates a fresh :class:`AssistantStateStore` + Workspace,
  2. seeds ``user_goal`` as a ``text/plain`` raw upload,
  3. executes the linearized ``expected_chain`` through
     :meth:`AssistantService.execute_agent_for_step`, and
  4. emits per-step status / error / ``resolved_input_paths`` /
     result bookkeeping to a per-case JSON.

Why chain eval (vs per-agent smoke): this layer is meant to catch the
stuff director_routing's eval cannot — cross-agent data-flow coherence
(producer output → consumer input), Workspace side-effects (artifact
persistence, caption index, GC), and InputResolver's ability to pick
the right artifact out of the caption index as the chain progresses.

Media backends are stubbed (``FW_USE_REAL_MEDIA_GEN`` is unset in the
subprocess env) — image / video / audio / compositor / transcription /
video_edit route to their ``Mock*`` counterparts. Text LLMs run for
real; that is the point.

Subprocess isolation: the assistant's :class:`AssistantStateStore` is
process-local, so per-case subprocesses are the clean way to prevent
caption-index pollution across cases. ``--workers N`` runs N cases in
parallel. Each agent within a case still runs serially because the
chain is producer → consumer by construction.

Usage (from repo root)::

    PYTHONPATH=. python evals/assistant_pipeline/eval_pipeline.py
    PYTHONPATH=. python evals/assistant_pipeline/eval_pipeline.py \\
        --names cr_01,cr_05 --workers 1
    PYTHONPATH=. python evals/assistant_pipeline/eval_pipeline.py \\
        --limit 3 --name baseline
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CASES_PATH = REPO_ROOT / "evals" / "director_routing" / "eval_cases.json"
RUN_ONE_CASE_ENTRY = SCRIPT_DIR / "_run_one_case.py"
RUNTIME_DIR = REPO_ROOT / "Runtime" / "assistant_pipeline"
INTAKE_FILTER_DEFAULT = frozenset({"IntakeTextAgent"})


# ---------------------------------------------------------------------------
# Case selection
# ---------------------------------------------------------------------------


def _strip_trailing_done(chain: List[Any]) -> List[Any]:
    out = list(chain)
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


def _case_intake_agents(case: Dict[str, Any]) -> Set[str]:
    seen: Set[str] = set()
    for slot in _strip_trailing_done(case["expected_chain"]):
        agents = slot if isinstance(slot, list) else [slot]
        for a in agents:
            if isinstance(a, str) and a.startswith("Intake"):
                seen.add(a)
    return seen


def load_cases(
    path: Path,
    *,
    intake_filter: Optional[Set[str]] = None,
    names: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Load, filter, and optionally trim the case list.

    ``intake_filter``: only keep cases whose Intake set is a subset of
    this set. Defaults to ``{"IntakeTextAgent"}`` — i.e. text-only
    cases, because the other 75/100 cases need image / video / audio
    seed fixtures that don't exist in ``eval_cases.json``.
    """
    if intake_filter is None:
        intake_filter = set(INTAKE_FILTER_DEFAULT)

    with open(path, "r", encoding="utf-8") as f:
        all_cases = json.load(f)

    kept: List[Dict[str, Any]] = []
    for case in all_cases:
        intakes = _case_intake_agents(case)
        if intakes and not intakes.issubset(intake_filter):
            continue
        if names is not None and case["name"] not in names:
            continue
        kept.append(case)

    if limit is not None:
        kept = kept[:limit]
    return kept


# ---------------------------------------------------------------------------
# Per-case subprocess driver
# ---------------------------------------------------------------------------


def _invoke_subprocess(
    case: Dict[str, Any],
    *,
    run_dir: Path,
    timeout_s: int,
) -> Dict[str, Any]:
    """Spawn ``_run_one_case.py`` for one case and return the result dict.

    The subprocess writes its result JSON to ``<run_dir>/cases/<name>.json``
    so even if this function raises, the partial per-case output survives
    for debugging.
    """
    case_name = case["name"]
    cases_dir = run_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    out_path = cases_dir / f"{case_name}.json"

    per_case_workspace_base = run_dir / "workspaces" / case_name
    per_case_workspace_base.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(RUN_ONE_CASE_ENTRY),
        "--case-json",
        json.dumps(case, ensure_ascii=False),
        "--runtime-base",
        str(per_case_workspace_base),
        "--out-path",
        str(out_path),
    ]

    env = os.environ.copy()
    # Belt-and-suspenders: media mocks on. _run_one_case.py also pops
    # this env var at startup, but we do it here too so the subprocess
    # ``cmd`` context is reproducible without reading that module.
    env.pop("FW_USE_REAL_MEDIA_GEN", None)
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    t0 = time.time()
    stderr_tail = ""
    try:
        proc = subprocess.run(
            cmd,
            env=env,
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            capture_output=True,
            text=True,
        )
        returncode = proc.returncode
        stderr_tail = (proc.stderr or "")[-2000:]
    except subprocess.TimeoutExpired as exc:
        elapsed = round(time.time() - t0, 2)
        stderr_tail = (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else "")[-2000:]
        return {
            "name": case_name,
            "user_goal": case.get("user_goal", ""),
            "chain_correct": False,
            "error": f"subprocess timeout after {timeout_s}s",
            "elapsed_s": elapsed,
            "steps": [],
            "completed_steps": 0,
            "_stderr_tail": stderr_tail,
            "_returncode": None,
        }

    # Load the per-case result JSON if the subprocess wrote one —
    # _run_one_case.py writes it even on internal failure, so this is
    # the canonical outcome. If the file is missing the subprocess
    # crashed before it could emit one; synthesize a failure record.
    if out_path.is_file():
        with open(out_path, "r", encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = {
            "name": case_name,
            "user_goal": case.get("user_goal", ""),
            "chain_correct": False,
            "error": "subprocess produced no result JSON",
            "elapsed_s": round(time.time() - t0, 2),
            "steps": [],
            "completed_steps": 0,
        }

    if returncode != 0 and not result.get("error"):
        result["error"] = f"subprocess exited {returncode}"
    result.setdefault("elapsed_s", round(time.time() - t0, 2))
    result["_returncode"] = returncode
    if stderr_tail.strip():
        result["_stderr_tail"] = stderr_tail
    return result


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_eval(
    *,
    cases_path: Path = DEFAULT_CASES_PATH,
    names: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    workers: int = 4,
    run_name: Optional[str] = None,
    timeout_s: int = 1200,
) -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{run_name}" if run_name else ""
    run_dir = RUNTIME_DIR / f"{ts}{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / "summary.json"

    cases = load_cases(cases_path, names=names, limit=limit)
    if not cases:
        print("[eval_pipeline] no cases matched — aborting")
        return output_path

    print(f"Cases source:   {cases_path}")
    print(f"Selected:       {len(cases)} text-only case(s)")
    print(f"Workers:        {workers}")
    print(f"Timeout/case:   {timeout_s}s")
    print(f"Run dir:        {run_dir}")
    print("=" * 80)

    t_start = time.time()
    results_by_name: Dict[str, Dict[str, Any]] = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(
                _invoke_subprocess, case, run_dir=run_dir, timeout_s=timeout_s
            ): case["name"]
            for case in cases
        }
        for fut in as_completed(futures):
            case_name = futures[fut]
            try:
                result = fut.result()
            except Exception as exc:
                result = {
                    "name": case_name,
                    "chain_correct": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "steps": [],
                    "completed_steps": 0,
                    "elapsed_s": 0.0,
                }
            results_by_name[case_name] = result
            completed += 1
            tag = "PASS" if result.get("chain_correct") else "FAIL"
            n_steps = len(result.get("steps") or [])
            n_done = result.get("completed_steps", 0)
            plan_len = len(result.get("plan") or [])
            total = plan_len or n_steps
            failed_at = result.get("failed_at")
            extra = f" failed_at={failed_at}" if failed_at else ""
            err = result.get("error")
            err_tag = f" | ERR: {err}" if err else ""
            print(
                f"[{completed:02d}/{len(cases):02d}] {tag} | "
                f"steps {n_done}/{total} | "
                f"{result.get('elapsed_s', 0.0):6.1f}s | {case_name}{extra}{err_tag}",
                flush=True,
            )

    elapsed_total = time.time() - t_start
    # Preserve original case order for the summary.
    results = [results_by_name[c["name"]] for c in cases]

    # ── Aggregates ────────────────────────────────────────────────────
    pass_count = sum(1 for r in results if r.get("chain_correct"))
    fail_count = len(results) - pass_count
    step_totals = [(r.get("completed_steps", 0), len(r.get("plan") or r.get("steps") or [])) for r in results]
    total_done = sum(a for a, _ in step_totals)
    total_steps = sum(b for _, b in step_totals)
    elapsed_list = [r.get("elapsed_s", 0.0) for r in results]

    # Which agent is the most common failure point? — useful signal when
    # tuning the pipeline; if KeyFrame always fails first the fix is
    # likely upstream of KeyFrame.
    fail_by_agent: Dict[str, int] = {}
    for r in results:
        if r.get("chain_correct"):
            continue
        # Find the first non-COMPLETED step, if any.
        for s in r.get("steps") or []:
            if s.get("status") != "COMPLETED":
                aid = s.get("agent_id", "?")
                fail_by_agent[aid] = fail_by_agent.get(aid, 0) + 1
                break
        else:
            # No step records — subprocess failed before anything ran.
            fail_by_agent["<pre_step>"] = fail_by_agent.get("<pre_step>", 0) + 1

    print("\n" + "=" * 80)
    print(f"Elapsed total:    {elapsed_total:.0f}s")
    print(
        f"Pass / fail:      {pass_count} / {fail_count}  "
        f"({100 * pass_count / len(results):.1f}% pass)"
    )
    print(
        f"Step completion:  {total_done} / {total_steps}  "
        f"({100 * total_done / total_steps:.1f}%)" if total_steps else "Step completion:  n/a"
    )
    if elapsed_list:
        print(
            f"Per-case elapsed: mean={statistics.mean(elapsed_list):.1f}s  "
            f"median={statistics.median(elapsed_list):.1f}s  "
            f"max={max(elapsed_list):.1f}s"
        )
    if fail_by_agent:
        print("\nFirst-failure distribution by agent:")
        for aid, n in sorted(fail_by_agent.items(), key=lambda x: -x[1]):
            print(f"  {aid:<25s}: {n}")

    summary = {
        "meta": {
            "timestamp": ts,
            "run_name": run_name or "",
            "cases_source": str(cases_path),
            "selected_cases": len(cases),
            "workers": workers,
            "timeout_per_case_s": timeout_s,
            "elapsed_total_s": round(elapsed_total, 1),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_pct": round(100 * pass_count / len(results), 2) if results else 0.0,
            "total_steps_completed": total_done,
            "total_steps_planned": total_steps,
            "step_completion_pct": (
                round(100 * total_done / total_steps, 2) if total_steps else 0.0
            ),
            "first_failure_by_agent": fail_by_agent,
        },
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nResults → {output_path}")
    print(f"Per-case JSONs under {run_dir / 'cases'}")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_names(s: Optional[str]) -> Optional[Set[str]]:
    if not s:
        return None
    return {x.strip() for x in s.split(",") if x.strip()}


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--cases",
        type=str,
        default=str(DEFAULT_CASES_PATH),
        help=f"Path to eval_cases.json (default: {DEFAULT_CASES_PATH}).",
    )
    parser.add_argument(
        "--names",
        type=str,
        default=None,
        help="Comma-separated case names to run (e.g. cr_01,cr_05).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N matching cases.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel case subprocesses (default: 4).",
    )
    parser.add_argument(
        "--name",
        dest="run_name",
        type=str,
        default=None,
        help="Optional run name — appears in the Runtime output path.",
    )
    parser.add_argument(
        "--timeout",
        dest="timeout_s",
        type=int,
        default=1200,
        help="Per-case subprocess timeout in seconds (default: 1200 = 20min).",
    )
    args = parser.parse_args(argv)

    run_eval(
        cases_path=Path(args.cases),
        names=_parse_names(args.names),
        limit=args.limit,
        workers=args.workers,
        run_name=args.run_name,
        timeout_s=args.timeout_s,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
