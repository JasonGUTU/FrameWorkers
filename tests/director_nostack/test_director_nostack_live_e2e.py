"""
**Live** director_nostack path: real ``LlmSubAgentPlanner`` (merge when prior context exists, route with LLM),
real Flask ``test_client`` I/O, stub ``NostackE2eAgent`` so Assistant does not call production media APIs.

Opt-in only (may cost API tokens; may be flaky if the model returns ``done`` or invalid JSON on step 1):

- ``FW_ENABLE_NOSTACK_LIVE_E2E=1``
- ``FW_ENABLE_LIVE_LLM_TESTS=1`` (same gate as ``test_full_pipeline_live_e2e``)
- Provider API key per ``inference`` runtime (e.g. ``OPENAI_API_KEY`` / routing yaml)

**Two modes**

- **Stub catalog** (default): dummy ``NostackE2eAgent`` only; fast, no media APIs.
- **Real sub-agents**: ``FW_ENABLE_NOSTACK_REAL_AGENTS=1`` — uses real ``agents/`` registry. Optional filter:

  - ``FW_NOSTACK_REAL_AGENT_IDS=StoryAgent`` — only those ids visible to the router (comma-separated).
  - ``FW_NOSTACK_REAL_AGENT_IDS`` empty, or ``*`` / ``ALL`` / ``all`` — **no filter** (full catalog; may run Story→…→Video and cost a lot / take a long time).

- Optional: ``FW_NOSTACK_EXPECT_VIDEO=1`` — assert at least one execution used ``VideoAgent`` (full-catalog runs).

Run::

    export FW_ENABLE_NOSTACK_LIVE_E2E=1
    export FW_ENABLE_LIVE_LLM_TESTS=1
    PYTHONPATH=. python -m pytest tests/director_nostack/test_director_nostack_live_e2e.py -v -s
"""

from __future__ import annotations

import os
import sys
import types
import json
from pathlib import Path
from datetime import datetime

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
for p in (_repo_root, _pkg_root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

_ns_dir = Path(__file__).resolve().parent
if str(_ns_dir) not in sys.path:
    sys.path.insert(0, str(_ns_dir))
from flask_nostack_test_client import FlaskTestNoStackClient, post_user_chat_line

from director_nostack import director as director_mod
from director_nostack.director import DirectorNoStack
from director_nostack.router import LlmSubAgentPlanner


def _nostack_live_e2e_opted_in() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_NOSTACK_LIVE_E2E") != "1":
        return (
            False,
            "Set FW_ENABLE_NOSTACK_LIVE_E2E=1 to run director_nostack live routing test.",
        )
    return True, ""


_NOSTACK_LIVE_READY, _NOSTACK_LIVE_SKIP_REASON = _nostack_live_e2e_opted_in()


@pytest.mark.skipif(not _NOSTACK_LIVE_READY, reason=_NOSTACK_LIVE_SKIP_REASON)
def test_nostack_live_real_llm_router_runs_stub_agent(
    director_nostack_http_app,
    monkeypatch,
):
    """
    One user chat line → real routing planner code path.

    If live LLM is configured (DIRECTOR_ROUTING_MODEL + provider key), this should execute the stub
    agent and finish. If not configured, this test still runs and asserts we get a clear routing
    failure director message (no executions).

    Default mode catalogs only the stub agent so the model cannot pick an undefined id.
    Opt-in real-agent mode uses the real registry; optional ``FW_NOSTACK_REAL_AGENT_IDS`` restricts
    the visible catalog (omit or ``*`` for full catalog).
    """
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        pytest.skip("Live LLM test disabled. Set FW_ENABLE_LIVE_LLM_TESTS=1 to run.")

    # Mirror `tests/assistant/test_full_pipeline_live_e2e.py` precheck: instantiate LLMClient so it loads
    # `.env` and `inference_runtime.yaml`, then verify the provider key env is present.
    from inference.clients import LLMClient

    client = LLMClient()
    resolved_model = os.getenv("DIRECTOR_ROUTING_MODEL") or client.model or client.default_model
    provider = client.resolve_provider_for_model(resolved_model)
    routing = client.get_runtime_routing()
    provider_key_env = (
        routing.get("provider_key_env", {}).get(provider) if isinstance(routing, dict) else None
    ) or f"{provider.upper()}_API_KEY"
    key_value = os.getenv(provider_key_env, "").strip()
    if not key_value:
        pytest.skip(
            "Live director_nostack test missing provider key. "
            f"Set {provider_key_env} or configure routing/api_keys."
        )

    task_id = "nostack_live_e2e_tid"
    monkeypatch.setattr(director_mod, "STANDALONE_TASK_ID", task_id)

    fc = director_nostack_http_app
    user_brief = (
        "Generate about a 10-second cinematic clip: rain on cobblestones, a cyclist rolls "
        "under one warm streetlight; no dialogue, slow mood."
    )
    post_user_chat_line(fc, user_brief)

    http = FlaskTestNoStackClient(fc)
    planner = LlmSubAgentPlanner()
    d = DirectorNoStack(client=http, planner=planner)

    # Real-agent mode: optional catalog filter (comma list). Empty / * / ALL / all = full catalog.
    allowed_ids: set[str] | None = None
    if os.getenv("FW_ENABLE_NOSTACK_REAL_AGENTS") == "1":
        raw = (os.getenv("FW_NOSTACK_REAL_AGENT_IDS") or "StoryAgent").strip()
        if raw not in ("", "*", "ALL", "all"):
            allowed_ids = {x.strip() for x in raw.split(",") if x.strip()}
            orig_get_all_agents = http.get_all_agents

            def _filtered_agents():
                agents = orig_get_all_agents()
                return [
                    a
                    for a in agents
                    if isinstance(a, dict) and str(a.get("id") or "") in allowed_ids
                ]

            http.get_all_agents = _filtered_agents  # type: ignore[method-assign]
    d._cycle()

    ex = fc.get(f"/api/assistant/executions/task/{task_id}")
    assert ex.status_code == 200, ex.get_data(as_text=True)
    executions = ex.get_json()
    assert isinstance(executions, list)
    listed = fc.get("/api/messages/list").get_json()
    bodies = [str(m.get("content", "")) for m in listed if m.get("sender_type") == "director"]

    # Persist a small, human-readable trace under Runtime when live mode is enabled.
    runtime_base = Path(getattr(fc, "_fw_runtime_base", ""))
    if runtime_base:
        debug_dir = runtime_base / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = debug_dir / f"nostack_live_e2e_trace_{run_id}.jsonl"
        with trace_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"step": "user_brief", "task_id": task_id, "text": user_brief}, ensure_ascii=False) + "\n")
            f.write(json.dumps({"step": "director_messages", "count": len(bodies), "messages": bodies[:50]}, ensure_ascii=False) + "\n")
            f.write(json.dumps({"step": "executions", "count": len(executions), "executions": executions}, ensure_ascii=False, default=str) + "\n")

    assert executions, (
        "Expected at least one Assistant execution in live mode. "
        "If routing returned done immediately or failed JSON parse, inspect director messages."
    )
    last = executions[-1]
    if os.getenv("FW_ENABLE_NOSTACK_REAL_AGENTS") == "1":
        if allowed_ids is not None:
            assert str(last.get("agent_id") or "") in allowed_ids
    else:
        assert last.get("agent_id") == "NostackE2eAgent"
    assert last.get("status") == "COMPLETED"
    if os.getenv("FW_ENABLE_NOSTACK_REAL_AGENTS") != "1":
        assert any("NostackE2eAgent" in b for b in bodies)
    if os.getenv("FW_NOSTACK_EXPECT_VIDEO") == "1":
        agent_ids = [str(e.get("agent_id") or "") for e in executions if isinstance(e, dict)]
        assert "VideoAgent" in agent_ids, (
            "Expected VideoAgent in execution chain (set FW_NOSTACK_EXPECT_VIDEO=0 to skip). "
            f"Got: {agent_ids}"
        )
    assert any("Pipeline complete" in b for b in bodies)
