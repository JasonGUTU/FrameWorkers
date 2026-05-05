#!/usr/bin/env python3
"""End-to-end driver that stops at KeyFrameAgent.

Used to test L1/L2/L3 keyframe pipeline patches (P1/P2/P3/P5) without
burning fal video / audio credits. Reuses cr_009 (assistant_test_cases)
as the input goal so the keyframe outputs are visually comparable to the
17:10 baseline run (workspace_global_20260504_171033).

Manually persists a 3-step plan (StoryAgent → ScreenplayAgent →
KeyFrameAgent) instead of going through Director's LLM planner — keeps
the test deterministic and avoids depending on the planner picking the
right chain.

Assumes plan-stack-backend is already running at BACKEND_BASE_URL
(default http://localhost:5002) with FW_USE_REAL_MEDIA_GEN=1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from director_agent.api_client import BackendAPIClient, BackendAPIError  # noqa: E402


_AGENT_CHAIN = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent"]


def _load_case(name: str) -> dict[str, Any]:
    cases_path = _REPO_ROOT / "assistant_test" / "assistant_test_cases.json"
    cases = json.loads(cases_path.read_text())
    for c in cases:
        if c["name"] == name:
            return c
    raise KeyError(f"case {name!r} not found in {cases_path}")


def _wait_backend(base_url: str, *, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/plan-stack", timeout=2.0) as r:
                if r.status == 200:
                    return
        except Exception as exc:
            last_err = exc
        time.sleep(0.5)
    raise RuntimeError(f"backend at {base_url} did not become ready: {last_err}")


def _http_get_json(base_url: str, path: str) -> Any:
    req = urllib.request.Request(f"{base_url}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=15.0) as r:
        return json.loads(r.read().decode("utf-8"))


def _persist_plan(client: BackendAPIClient, plan: list[str]) -> list[str]:
    layers = client.get_plan_stack()
    new_layer_index = len(layers)
    descriptions = [
        {
            "description": {
                "agent_id": agent_id,
                "intent": f"keyframe-only test: {agent_id}",
                "plan_rationale": "scripts/run_keyframe_only.py manual chain",
            }
        }
        for agent_id in plan
    ]
    ops = [
        {"type": "create_steps", "params": {"steps": descriptions}},
        {"type": "create_layers", "params": {"layers": [{"layer_index": new_layer_index}]}},
    ]
    resp = client.modify_plan_stack(ops)
    if not resp.get("success"):
        raise RuntimeError(f"modify_plan_stack failed: {resp.get('errors')}")
    created_step_ids = resp.get("created_step_ids") or []
    if len(created_step_ids) != len(plan):
        raise RuntimeError(
            f"create_steps returned {len(created_step_ids)} ids, expected {len(plan)}"
        )

    add_ops = [
        {
            "type": "add_steps_to_layers",
            "params": {
                "additions": [
                    {"layer_index": new_layer_index, "step_id": sid}
                    for sid in created_step_ids
                ]
            },
        }
    ]
    resp = client.modify_plan_stack(add_ops)
    if not resp.get("success"):
        raise RuntimeError(f"add_steps_to_layers failed: {resp.get('errors')}")

    try:
        pointer = client.get_execution_pointer()
    except Exception:
        pointer = None
    if pointer is None:
        try:
            client.set_execution_pointer(
                layer_index=new_layer_index,
                step_index=0,
            )
        except Exception as exc:
            print(f"  [warn] set_execution_pointer failed: {exc}")

    return created_step_ids


def _execute_step(client: BackendAPIClient, agent_id: str, step_id: str) -> dict[str, Any]:
    t0 = time.time()
    try:
        client.update_step_status(step_id, "IN_PROGRESS")
    except Exception as exc:
        print(f"  [warn] update_step_status(IN_PROGRESS) failed: {exc}")
    try:
        result = client.execute_agent(agent_id, step_id)
    except BackendAPIError as exc:
        print(f"  [error] execute_agent failed: {exc}")
        try:
            client.update_step_status(step_id, "FAILED")
        except Exception:
            pass
        return {"status": "FAILED", "error": str(exc), "elapsed_s": time.time() - t0}
    elapsed = time.time() - t0
    status = str((result or {}).get("status") or "").upper() or "COMPLETED"
    try:
        client.update_step_status(step_id, status)
    except Exception:
        pass
    try:
        client.advance_execution_pointer()
    except Exception:
        pass
    return {"status": status, "elapsed_s": elapsed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="cr_009")
    ap.add_argument("--backend", default=os.getenv("BACKEND_BASE_URL", "http://localhost:5002"))
    args = ap.parse_args()

    case = _load_case(args.case)
    user_goal = case["user_goal"]
    print(f"[kf-only] case          = {case['name']}  category={case['category']}")
    print(f"[kf-only] chain         = {' → '.join(_AGENT_CHAIN)}")
    print(f"[kf-only] user_goal     = {user_goal[:120]}...")
    print(f"[kf-only] backend       = {args.backend}")
    print(f"[kf-only] FW_USE_REAL_MEDIA_GEN = {os.getenv('FW_USE_REAL_MEDIA_GEN', '<unset>')}")
    print()

    _wait_backend(args.backend)
    client = BackendAPIClient(base_url=args.backend)

    msg = client.create_message(content=user_goal, sender_type="user")
    print(f"[kf-only] seeded chat message id={msg.get('id')} (auto-persists creative_brief)")

    step_ids = _persist_plan(client, _AGENT_CHAIN)
    print(f"[kf-only] persisted plan: {list(zip(_AGENT_CHAIN, step_ids))}")
    print()

    timing: list[tuple[str, str, float]] = []
    for agent_id, step_id in zip(_AGENT_CHAIN, step_ids):
        print(f"[kf-only] executing {agent_id} (step={step_id}) ...")
        info = _execute_step(client, agent_id, step_id)
        print(f"  → status={info['status']}  elapsed={info['elapsed_s']:.1f}s")
        timing.append((agent_id, info["status"], info["elapsed_s"]))
        if info["status"] == "FAILED":
            print(f"  [abort] {agent_id} failed; stopping chain")
            break

    print("\n[kf-only] timing:")
    total = 0.0
    for agent_id, status, sec in timing:
        print(f"  {agent_id:18s} {status:12s} {sec:7.1f}s")
        total += sec
    print(f"  {'TOTAL':18s} {'':12s} {total:7.1f}s")

    print()
    print("[kf-only] keyframe artifacts:")
    kf_step_id = next(
        (sid for ag, sid in zip(_AGENT_CHAIN, step_ids) if ag == "KeyFrameAgent"),
        None,
    )
    if kf_step_id is None:
        return 0
    try:
        execs = _http_get_json(args.backend, f"/api/assistant/executions/step/{kf_step_id}")
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code}")
        return 0
    if not isinstance(execs, list):
        return 0
    for ex in execs:
        results = ex.get("results") or {}
        media = (results.get("_media_files") or {}) if isinstance(results, dict) else {}
        for k, v in sorted(media.items()):
            filename = v.get("filename", "?") if isinstance(v, dict) else "?"
            size = (v.get("file_content") or {}).get("size_bytes", "?") if isinstance(v, dict) else "?"
            print(f"  {k:32s}  {filename:40s}  {size} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
