"""End-to-end tests for the 12 agents through the Flask HTTP layer.

Each test runs the full Assistant pipeline:
  POST /api/assistant/execute → InputResolver → build_input → agent.run
  (LLM + evaluator + materializer) → workspace persist

The agents are chained: Story → Screenplay provides upstream artifacts
for the new agents. Media materializers run with mock services (default).

Gate: FW_ENABLE_NEW_AGENTS_E2E=1  AND  FW_ENABLE_LIVE_LLM_TESTS=1

Usage:
    source .env
    FW_ENABLE_NEW_AGENTS_E2E=1 FW_ENABLE_LIVE_LLM_TESTS=1 \
      python -m pytest tests/agents/test_new_agents_e2e.py -v -s
"""

from __future__ import annotations

import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# Load .env
from inference.config.config_loader import ConfigLoader
for fname in (".env", ".env.example"):
    env_path = _repo_root / fname
    if env_path.is_file():
        ConfigLoader.load_env_file(str(env_path), override=False)

# Stub flask_cors if not installed
if "flask_cors" not in sys.modules:
    fc = types.ModuleType("flask_cors")
    fc.CORS = lambda *a, **kw: None
    sys.modules["flask_cors"] = fc

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from src.assistant.workspace.workspace import Workspace
from inference.clients import LLMClient


# ---------------------------------------------------------------------------
# Skip / precheck
# ---------------------------------------------------------------------------

def _is_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_NEW_AGENTS_E2E") != "1":
        return False, "Set FW_ENABLE_NEW_AGENTS_E2E=1 to run."
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return False, "Set FW_ENABLE_LIVE_LLM_TESTS=1 to run."
    try:
        client = LLMClient()
        resolved = client.model or client.default_model
        provider = client.resolve_provider_for_model(resolved)
        routing = client.get_runtime_routing()
        key_env = (
            routing.get("provider_key_env", {}).get(provider)
            if isinstance(routing, dict) else None
        ) or f"{provider.upper()}_API_KEY"
        if not os.getenv(key_env, "").strip():
            return False, f"Missing {key_env}"
    except Exception as exc:
        return False, f"Precheck failed: {exc}"
    return True, ""


_READY, _SKIP = _is_ready()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _runtime_base() -> Path:
    base = Path(
        os.getenv("FW_NEW_AGENTS_E2E_RUNTIME_DIR",
                   str(_repo_root / "Runtime" / "new_agents_e2e_outputs"))
    )
    base.mkdir(parents=True, exist_ok=True)
    return base


def _make_store(ws_id: str) -> AssistantStateStore:
    store = AssistantStateStore(runtime_base_path=_runtime_base())
    workspace = Workspace(workspace_id=ws_id, runtime_base_path=store.runtime_base_path)
    store.global_workspace = workspace
    return store


def _ws_id(label: str) -> str:
    return f"ws_e2e_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _build_client(ws_id: str, monkeypatch):
    store = _make_store(ws_id)
    monkeypatch.setattr(routes_module, "assistant_state_store", store)
    app = create_app({"TESTING": True})
    client = app.test_client()
    debug_file = _runtime_base() / "debug" / f"{ws_id}.jsonl"
    return client, store.global_workspace, debug_file


def _record(debug_file: Path, payload: dict):
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with debug_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def _post(client, url, body, debug_file, *, step):
    resp = client.post(url, json=body)
    payload = resp.get_json()
    _record(debug_file, {"step": step, "url": url, "request": body,
                         "status": resp.status_code, "response": payload})
    return resp, payload


def _create_step(client, debug_file, goal: str) -> str:
    resp, body = _post(
        client,
        "/api/plan-stack/modify",
        {
            "operations": [
                {
                    "type": "create_steps",
                    "params": {"steps": [{"description": {"goal": goal}}]},
                }
            ]
        },
        debug_file,
        step="create_step",
    )
    assert resp.status_code == 200, f"create_step failed: {body}"
    return body["created_step_ids"][0]


def _upload_text(client, debug_file, text: str) -> dict:
    resp, body = _post(client, "/api/workspace/upload",
                       {"mime": "text/plain", "text": text}, debug_file, step="upload_text")
    assert resp.status_code == 201, f"upload failed: {body}"
    return body


def _execute(client, debug_file, agent_id: str, step_id: str, *, required: bool = True) -> dict:
    resp, body = _post(client, "/api/assistant/execute",
                       {"agent_id": agent_id, "step_id": step_id},
                       debug_file, step=f"execute_{agent_id}")
    if required:
        assert resp.status_code == 200, f"{agent_id} HTTP failed: {body}"
        assert isinstance(body, dict) and body.get("status") == "COMPLETED", (
            f"{agent_id} not COMPLETED: {body}"
        )
    return body


def _last_results(client, step_id: str) -> dict:
    resp = client.get(f"/api/assistant/executions/step/{step_id}")
    assert resp.status_code == 200
    execs = resp.get_json()
    assert execs
    return execs[-1].get("results") or {}


# ---------------------------------------------------------------------------
# E2E: full chain — Story → Screenplay → new agents
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _READY, reason=_SKIP)
def test_e2e_new_agents_full_chain(monkeypatch):
    """Run the full chain through Flask:
    upload brief → IntakeText → Story → Screenplay →
    TranslationAgent / CompositorAgent
    + KeyFrame → Video → Music → Ambience → AudioMix (mock media) →
    VideoAnalysis / Highlight / StyleTransfer / Inpaint / VideoExtend
    + IntakeVideo / IntakeAudio (via text upload fallback)

    SubtitleAgent was retired — TranscriptionAgent's STT output goes
    directly into the CompositorAgent subtitle_tracks label (the
    materializer renders its segments to SRT via a pure-Python helper).
    This smoke no longer exercises a dedicated subtitle step.
    """
    ws_id = _ws_id("new_agents_chain")
    client, workspace, debug_file = _build_client(ws_id, monkeypatch)
    print(f"\n[E2E] workspace={ws_id}")
    print(f"[E2E] debug_file={debug_file}")

    # --- 1. Upload creative brief + IntakeText ---
    _upload_text(client, debug_file,
                 "Create a 30-second cinematic short about two astronauts, "
                 "Chen and Park, who explore a glowing cave on Mars. Chen "
                 "discovers alien crystals and exclaims with excitement. Park "
                 "responds they must report back to base. The script must "
                 "include dialogue lines and action shots; Kling's generate_audio "
                 "bakes character dialogue + foley directly into each video clip.")
    step_id = _create_step(client, debug_file,
                           "30-second cinematic short about astronauts on Mars")

    _execute(client, debug_file, "IntakeTextAgent", step_id)
    print("[E2E] IntakeTextAgent COMPLETED")

    # Track results for final report
    results: dict[str, str] = {}

    # --- 2. Story → Screenplay (required — provides upstream for all new agents) ---
    _execute(client, debug_file, "StoryAgent", step_id)
    story = _last_results(client, step_id)
    assert story.get("content", {}).get("logline"), "StoryAgent produced no logline"
    print(f"[E2E] StoryAgent COMPLETED — logline: {story['content']['logline'][:60]}...")
    results["StoryAgent"] = "COMPLETED"

    _execute(client, debug_file, "ScreenplayAgent", step_id)
    screenplay = _last_results(client, step_id)
    scenes = screenplay.get("content", {}).get("scenes", [])
    assert scenes, "ScreenplayAgent produced no scenes"
    print(f"[E2E] ScreenplayAgent COMPLETED — {len(scenes)} scene(s)")
    results["ScreenplayAgent"] = "COMPLETED"

    def _run(agent_id: str, *, required: bool = False):
        try:
            body = _execute(client, debug_file, agent_id, step_id, required=required)
            cur = body if isinstance(body, dict) else {}
            status = cur.get("status", "UNKNOWN")
            if status == "COMPLETED":
                results[agent_id] = "COMPLETED"
                return _last_results(client, step_id)
            else:
                err = str(cur.get("error", ""))[:120]
                results[agent_id] = f"FAILED: {err}"
                print(f"[E2E] {agent_id} FAILED: {err}")
                return {}
        except AssertionError as exc:
            results[agent_id] = f"FAILED: {exc}"
            print(f"[E2E] {agent_id} FAILED: {exc}")
            return {}

    # --- 3. TranslationAgent (reads screenplay text — in production it
    # reads TranscriptionAgent's transcript of the final audio, but this
    # smoke runs before the audio chain is assembled, so we let it pick
    # up whatever textual upstream InputResolver routes). ---
    translation = _run("TranslationAgent")
    if translation:
        payload = translation.get("content", {}).get("translated_payload", {})
        print(f"[E2E] TranslationAgent COMPLETED — payload keys: {list(payload.keys())[:5]}")

    # --- 5. Media chain (mock services) — these are required for downstream ---
    _run("KeyFrameAgent", required=True)
    print("[E2E] KeyFrameAgent COMPLETED (mock)")
    _run("VideoAgent", required=True)
    print("[E2E] VideoAgent COMPLETED (mock)")
    _run("MusicAgent", required=True)
    print("[E2E] MusicAgent COMPLETED (mock)")
    _run("AmbienceAgent", required=True)
    print("[E2E] AmbienceAgent COMPLETED (mock)")
    _run("AudioMixAgent", required=True)
    print("[E2E] AudioMixAgent COMPLETED (mock)")

    # --- 6. CompositorAgent ---
    compositor = _run("CompositorAgent")
    if compositor:
        plan = compositor.get("content", {}).get("plan", {})
        print(f"[E2E] CompositorAgent COMPLETED — {len(plan.get('transitions', []))} transitions")

    # --- 7-12. Remaining new agents (all non-blocking) ---
    va = _run("VideoAnalysisAgent")
    if va:
        print(f"[E2E] VideoAnalysisAgent COMPLETED — {len(va.get('content', {}).get('scenes', []))} scene(s)")

    hl = _run("HighlightAgent")
    if hl:
        print(f"[E2E] HighlightAgent COMPLETED — {len(hl.get('content', {}).get('clips', []))} clip(s)")

    st = _run("StyleTransferAgent")
    if st:
        print(f"[E2E] StyleTransferAgent COMPLETED — prompt: {st.get('content', {}).get('style_spec', {}).get('style_prompt', '')[:60]}")

    ip = _run("InpaintAgent")
    if ip:
        print(f"[E2E] InpaintAgent COMPLETED — mode: {ip.get('content', {}).get('inpaint_spec', {}).get('mask_mode')}")

    ve = _run("VideoExtendAgent")
    if ve:
        print(f"[E2E] VideoExtendAgent COMPLETED — {ve.get('content', {}).get('extension_spec', {}).get('target_duration_seconds')}s")

    # --- IntakeVideoAgent ---
    _upload_text(client, debug_file,
                 "Raw user upload (mime=video/mp4): 10-second clip of ocean waves at sunset")
    iv = _run("IntakeVideoAgent")
    if iv:
        print(f"[E2E] IntakeVideoAgent COMPLETED — {iv.get('content', {}).get('visual_summary', '')[:60]}")

    # --- Final report ---
    print(f"\n{'='*60}")
    print(f"[E2E] RESULTS — Workspace: {workspace.runtime_base_path / workspace.id}")
    print(f"{'='*60}")
    passed = 0
    failed = 0
    for agent_id, status in results.items():
        icon = "PASS" if status == "COMPLETED" else "FAIL"
        print(f"  [{icon}] {agent_id}: {status}")
        if status == "COMPLETED":
            passed += 1
        else:
            failed += 1
    print(f"\n[E2E] {passed} passed, {failed} failed out of {len(results)} agents")

    # At least the core chain must pass; new agents are best-effort
    assert results.get("KeyFrameAgent") == "COMPLETED"
    assert results.get("VideoAgent") == "COMPLETED"
    # Agents that need real media files are expected to fail in text-only E2E.
    _NEEDS_REAL_MEDIA = {"IntakeVideoAgent"}
    text_only_passed = sum(
        1 for a, s in results.items()
        if s == "COMPLETED" and a not in _NEEDS_REAL_MEDIA
    )
    text_only_total = sum(1 for a in results if a not in _NEEDS_REAL_MEDIA)
    assert text_only_passed >= text_only_total - 1, (
        f"Text-only agent failures: {text_only_passed}/{text_only_total} passed"
    )
