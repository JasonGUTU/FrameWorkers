#!/usr/bin/env python3
"""End-to-end driver: pick a case from ``assistant_test/assistant_test_cases.json``,
drive Director ``run_plan_pipeline`` against a live backend, then dump the plan
stack + every step's compositor output.

Assumes ``plan-stack-backend`` is already running on ``BACKEND_BASE_URL``
(default ``http://localhost:5002``). For real media generation set
``FW_USE_REAL_MEDIA_GEN=1`` before invoking.
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
from director_agent.director import run_plan_pipeline  # noqa: E402
from director_agent.router import LlmSubAgentPlanner  # noqa: E402


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
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15.0) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None,
                    help="Case name from assistant_test/assistant_test_cases.json. "
                         "Mutually exclusive with --user-goal; default 'cr_009' "
                         "if neither is given.")
    ap.add_argument("--user-goal", default=None,
                    help="Inline user_goal string. Skips the case lookup, "
                         "useful for ad-hoc demos. expected_chain is then "
                         "unknown so the comparison line is omitted.")
    ap.add_argument("--backend", default=os.getenv("BACKEND_BASE_URL", "http://localhost:5002"))
    args = ap.parse_args()

    if args.user_goal:
        user_goal = args.user_goal
        case_name = "<inline>"
        category = "<inline>"
        expected = "(unknown — inline user_goal)"
    else:
        case = _load_case(args.case or "cr_009")
        user_goal = case["user_goal"]
        case_name = case["name"]
        category = case["category"]
        expected = " → ".join("/".join(s) for s in case["expected_chain"])
    print(f"[e2e] case            = {case_name}  category={category}")
    print(f"[e2e] user_goal       = {user_goal}")
    print(f"[e2e] expected chain  = {expected}")
    print(f"[e2e] backend         = {args.backend}")
    print(f"[e2e] FW_USE_REAL_MEDIA_GEN = {os.getenv('FW_USE_REAL_MEDIA_GEN', '<unset>')}")
    print(f"[e2e] FAL_VIDEO_MODEL = {os.getenv('FAL_VIDEO_MODEL', '<unset>')}")
    print()

    _wait_backend(args.backend)
    client = BackendAPIClient(base_url=args.backend)
    planner = LlmSubAgentPlanner()  # default scaffold

    try:
        agents = client.get_all_agents()
    except BackendAPIError as exc:
        print(f"[e2e] FATAL: get_all_agents: {exc}")
        return 2
    print(f"[e2e] sub-agent catalog size = {len(agents)}")

    # Mimic the real chat flow: posting a user message auto-persists the
    # text as a [creative_brief] workspace artifact (see
    # plan-stack-backend/src/plan_stack/routes.py POST /api/messages/create
    # ``persist_raw_upload`` block). Without this, StoryAgent /
    # BriefEnricherAgent reject upstream input as empty.
    msg = client.create_message(content=user_goal, sender_type="user")
    print(f"[e2e] seeded chat message id={msg.get('id')} (auto-persists creative_brief)")

    t0 = time.time()
    run_plan_pipeline(client, planner, agents=agents, user_goal=user_goal)
    elapsed = time.time() - t0
    print(f"\n[e2e] run_plan_pipeline returned in {elapsed:.1f}s\n")

    layers = client.get_plan_stack()
    print(f"[e2e] plan stack: {len(layers)} layer(s)")
    final_step_ids: list[str] = []
    for li, layer in enumerate(layers):
        steps = layer.get("steps", [])
        print(f"  layer[{li}] ({len(steps)} step(s)):")
        for step in steps:
            desc = step.get("description") or {}
            agent_id = desc.get("agent_id") if isinstance(desc, dict) else None
            sid = step.get("step_id")
            status = step.get("status")
            print(f"    {agent_id or '<no-agent>':24s} | step={sid} | status={status}")
            final_step_ids.append(sid)

    print()
    for sid in final_step_ids:
        try:
            execs = _http_get_json(args.backend, f"/api/assistant/executions/step/{sid}")
        except urllib.error.HTTPError as exc:
            print(f"[e2e] step {sid}: executions HTTP {exc.code}")
            continue
        if not isinstance(execs, list):
            continue
        for ex in execs:
            agent_id = ex.get("agent_id") or "<unknown>"
            status = ex.get("status")
            results = ex.get("results") or {}
            content_keys = list((results.get("content") or {}).keys()) if isinstance(results, dict) else []
            mf = (results.get("_media_files") or {}) if isinstance(results, dict) else {}
            print(f"  exec {ex.get('id')} agent={agent_id} status={status} content_keys={content_keys}")
            for k, v in mf.items():
                if isinstance(v, dict):
                    uri = v.get("uri") or v.get("path") or v
                else:
                    uri = v
                print(f"    media[{k}] = {uri}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
