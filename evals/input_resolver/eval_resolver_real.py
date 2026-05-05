#!/usr/bin/env python3
"""
InputResolver eval — REAL workspace replay.

Instead of synthesizing captions via build_captions({}) stubs, this variant
loads real global_memory.md files from a prior assistant_pipeline eval run
and replays each agent step's resolution against the actual upstream
memory snapshot that was visible at that moment.

This eliminates harness-stub noise entirely. Any remaining error is a
genuine InputResolver mistake on production-grade caption input.

Usage:
    PYTHONPATH=. python evals/input_resolver/eval_resolver_real.py \\
        --run-dir Runtime/assistant_pipeline/20260420_181029_user_edits \\
        --workers 16
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
_PKG_ROOT = os.path.join(REPO_ROOT, "plan-stack-backend")
for _p in (REPO_ROOT, _PKG_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Reuse scoring tables + FakeGlobalMemory from the stub harness
from evals.input_resolver.eval_resolver import (  # noqa: E402
    LABEL_PRODUCERS,
    ROLE_SPECIFIC_LABELS,
    FakeGlobalMemory,
    _FakeArtifactRef,
    _FakeEntry,
    _NoopFileManager,
    _score_one_resolution,
)


RUNTIME_DIR = os.path.join(REPO_ROOT, "Runtime", "input_resolver")


# ---------------------------------------------------------------------------
# global_memory.md parsing
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def parse_global_memory_md(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = _JSON_BLOCK_RE.search(content)
    if not m:
        raise ValueError(f"No JSON block in {path}")
    return json.loads(m.group(1))


def find_workspace_memory_path(workspace_case_dir: str) -> Optional[str]:
    if not os.path.isdir(workspace_case_dir):
        return None
    for name in os.listdir(workspace_case_dir):
        inner = os.path.join(workspace_case_dir, name)
        memo = os.path.join(inner, "global_memory.md")
        if os.path.isfile(memo):
            return memo
    return None


# ---------------------------------------------------------------------------
# Replay core
# ---------------------------------------------------------------------------

# Agents whose resolution we test. Skip IntakeAgents — their one label only
# reads the raw upload and resolution is trivial by construction.
TESTED_AGENTS = set(LABEL_PRODUCERS.keys()) - {
    "IntakeTextAgent", "IntakeVideoAgent", "IntakeImageAgent",
}


def _memory_from_entries(entries: List[Dict[str, Any]]) -> FakeGlobalMemory:
    mem = FakeGlobalMemory()
    for e in entries:
        # Strip the "raw_pending" suffix when the live workspace has already
        # promoted the upload to global (mimic what InputResolver sees).
        arts = []
        for a in e.get("artifacts", []):
            caption = a.get("caption", "")
            if a.get("scope") == "global":
                caption = re.sub(
                    r"\s*Pending intake processing[^.]*\.?\s*$", "", caption,
                ).strip()
            arts.append(_FakeArtifactRef(
                path=a.get("path", ""),
                caption=caption,
                scope=a.get("scope", "global"),
                mime=a.get("mime", ""),
            ))
        # Parse created_at; fall back to now if missing
        created_str = e.get("created_at", "")
        try:
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            created_at = datetime.now()
        mem._entries.append(_FakeEntry(
            agent_id=e.get("agent_id", "unknown"),
            step_id=e.get("step_id", ""),
            created_at=created_at,
            artifacts=arts,
        ))
    return mem


async def run_one_real_case(
    *,
    case_name: str,
    entries: List[Dict[str, Any]],
    registry: Dict[str, Any],
    resolver_factory,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    step_results: List[Dict[str, Any]] = []
    chain: List[str] = []

    for i, entry in enumerate(entries):
        agent_id = entry.get("agent_id", "")
        if agent_id == "user":
            continue
        chain.append(agent_id)
        if agent_id not in TESTED_AGENTS:
            continue
        # Memory state = all entries BEFORE this one
        prior = entries[:i]
        mem = _memory_from_entries(prior)
        desc = registry.get(agent_id)
        if desc is None:
            step_results.append({"consumer_agent": agent_id, "step_correct": False,
                                 "labels": [], "error": "agent not registered"})
            continue
        resolver = resolver_factory(mem)
        try:
            r = await resolver.aresolve(
                agent_id=agent_id,
                step_id=entry.get("step_id", f"replay_{i}"),
                input_needs_description=desc.input_needs_description,
                model=model,
            )
            resolved = r.get("resolved_artifacts", {})
            step_results.append(_score_one_resolution(mem, agent_id, resolved))
        except Exception as exc:
            step_results.append({"consumer_agent": agent_id, "step_correct": False,
                                 "labels": [], "error": str(exc)})

    scored = [s for s in step_results if "error" not in s]
    lbl_total = sum(len(s["labels"]) for s in scored)
    lbl_correct = sum(sum(1 for l in s["labels"] if l["correct"]) for s in scored)
    step_total = len(scored)
    step_correct = sum(1 for s in scored if s["step_correct"])
    plan_correct = step_total > 0 and step_correct == step_total

    return {
        "name": case_name,
        "chain": chain,
        "step_results": step_results,
        "label_total": lbl_total,
        "label_correct": lbl_correct,
        "step_total": step_total,
        "step_correct": step_correct,
        "plan_correct": plan_correct,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dir",
        default=os.path.join(
            REPO_ROOT, "Runtime", "assistant_pipeline",
            "20260420_181029_user_edits",
        ),
    )
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--name", default="real_replay")
    parser.add_argument("--only-passed", action="store_true", default=True,
                        help="Only replay cases whose real pipeline passed")
    parser.add_argument("--model", default=None,
                        help="Override LLM model for InputResolver (e.g. gemini-2.5-flash)")
    args = parser.parse_args()

    from agents import AGENT_REGISTRY
    from inference.clients import LLMClient
    from src.assistant.workspace.input_resolver import InputResolver

    summary = json.load(open(os.path.join(args.run_dir, "summary.json")))
    if args.only_passed:
        cases_to_run = [r for r in summary["results"] if r.get("failed_at") is None]
    else:
        cases_to_run = summary["results"]

    print(f"Replaying {len(cases_to_run)} cases from {args.run_dir}")
    print(f"Workers: {args.workers}")

    workspaces_root = os.path.join(args.run_dir, "workspaces")

    # Pre-parse memories
    cases_prepared: List[Tuple[str, List[Dict[str, Any]]]] = []
    for r in cases_to_run:
        case_name = r["name"]
        case_dir = os.path.join(workspaces_root, case_name)
        memo = find_workspace_memory_path(case_dir)
        if not memo:
            print(f"  skip {case_name} — no global_memory.md")
            continue
        try:
            entries = parse_global_memory_md(memo)
            cases_prepared.append((case_name, entries))
        except Exception as e:
            print(f"  skip {case_name} — parse error: {e}")

    llm = LLMClient()
    def resolver_factory(mem: FakeGlobalMemory):
        return InputResolver(global_memory=mem, file_manager=_NoopFileManager(), llm_client=llm)

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(RUNTIME_DIR, f"{ts}_{args.name}.json")

    # ── Parallel execution (asyncio + Semaphore — single event loop avoids
    #    cross-loop Future bug with google.genai's cached async client) ────
    t0 = time.time()
    results = []

    async def _run_one(name: str, entries, sem: asyncio.Semaphore):
        async with sem:
            try:
                return await run_one_real_case(
                    case_name=name,
                    entries=entries,
                    registry=AGENT_REGISTRY,
                    resolver_factory=resolver_factory,
                    model=args.model,
                )
            except Exception as exc:
                return {"name": name, "error": str(exc)}

    async def _run_all():
        sem = asyncio.Semaphore(args.workers)
        tasks = [asyncio.create_task(_run_one(n, e, sem)) for n, e in cases_prepared]
        done = 0
        for coro in asyncio.as_completed(tasks):
            r = await coro
            done += 1
            results.append(r)
            if "error" in r:
                print(f"[{done:>2}/{len(cases_prepared)}] ERR {r['name']}: {r['error']}")
            else:
                mark = "✓" if r["plan_correct"] else "✗"
                print(f"[{done:>2}/{len(cases_prepared)}] {mark} "
                      f"step={r['step_correct']}/{r['step_total']} "
                      f"label={r['label_correct']}/{r['label_total']}  {r['name']}")

    asyncio.run(_run_all())

    elapsed = time.time() - t0
    results.sort(key=lambda r: r.get("name", ""))

    lbl_total = sum(r.get("label_total", 0) for r in results)
    lbl_correct = sum(r.get("label_correct", 0) for r in results)
    step_total = sum(r.get("step_total", 0) for r in results)
    step_correct = sum(r.get("step_correct", 0) for r in results)
    plan_perfect = sum(1 for r in results if r.get("plan_correct"))

    summary_out = {
        "run_dir": args.run_dir,
        "cases": len(results),
        "elapsed_seconds": round(elapsed, 1),
        "plan_perfect": plan_perfect,
        "plan_perfect_rate": round(plan_perfect / max(1, len(results)), 4),
        "step_correct": step_correct,
        "step_total": step_total,
        "step_accuracy": round(step_correct / max(1, step_total), 4),
        "label_correct": lbl_correct,
        "label_total": lbl_total,
        "label_accuracy": round(lbl_correct / max(1, lbl_total), 4),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary_out, "results": results}, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 72)
    print(f"Elapsed:        {summary_out['elapsed_seconds']}s")
    print(f"Plan-perfect:   {summary_out['plan_perfect']}/{summary_out['cases']} "
          f"({100 * summary_out['plan_perfect_rate']:.1f}%)")
    print(f"Step accuracy:  {summary_out['step_correct']}/{summary_out['step_total']} "
          f"({100 * summary_out['step_accuracy']:.1f}%)")
    print(f"Label accuracy: {summary_out['label_correct']}/{summary_out['label_total']} "
          f"({100 * summary_out['label_accuracy']:.1f}%)")
    print(f"Output:         {out_path}")


if __name__ == "__main__":
    main()
