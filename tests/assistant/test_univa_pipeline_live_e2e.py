"""Live end-to-end test for the UniVA pipeline sub-agents.

Runs UnivaStoryboardAgent → UnivaKeyFrameAgent → UnivaVideoAgent
via the assistant HTTP API with real LLM + FAL API calls.

Enable with:
    FW_ENABLE_FULL_PIPELINE_E2E=1 FW_ENABLE_LIVE_LLM_TESTS=1 \
        python -m pytest tests/assistant/test_univa_pipeline_live_e2e.py -s
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
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from inference.clients import LLMClient


# ---------------------------------------------------------------------------
# Readiness check
# ---------------------------------------------------------------------------

def _is_live_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_FULL_PIPELINE_E2E") != "1":
        return False, "Set FW_ENABLE_FULL_PIPELINE_E2E=1 to run."
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return False, "Set FW_ENABLE_LIVE_LLM_TESTS=1 to run."
    try:
        client = LLMClient()
        resolved_model = client.model or client.default_model
        provider = client.resolve_provider_for_model(resolved_model)
        routing = client.get_runtime_routing()
        provider_key_env = (
            routing.get("provider_key_env", {}).get(provider)
            if isinstance(routing, dict)
            else None
        ) or f"{provider.upper()}_API_KEY"
        key_value = os.getenv(provider_key_env, "").strip()
    except Exception as exc:
        return False, f"Live precheck failed: {exc}"
    if not key_value:
        return False, f"Missing provider key: {provider_key_env}"
    return True, ""


_LIVE_READY, _LIVE_SKIP_REASON = _is_live_ready()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def assistant_http_client_real_agents(tmp_path, monkeypatch):
    runtime_base = Path(
        os.getenv(
            "FW_LIVE_E2E_RUNTIME_DIR",
            str(_repo_root / "Runtime" / "live_e2e_outputs"),
        )
    )
    runtime_base.mkdir(parents=True, exist_ok=True)

    storage = AssistantStateStore(runtime_base_path=runtime_base)
    monkeypatch.setattr(routes_module, "assistant_state_store", storage)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        setattr(client, "_fw_runtime_base", str(runtime_base))
        yield client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _append_debug_record(debug_file: Path, payload: dict) -> None:
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with debug_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def _contains_raw_bytes(node: object) -> bool:
    if isinstance(node, (bytes, bytearray)):
        return True
    if isinstance(node, dict):
        return any(_contains_raw_bytes(v) for v in node.values())
    if isinstance(node, list):
        return any(_contains_raw_bytes(v) for v in node)
    return False


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_univa_pipeline_live_e2e(assistant_http_client_real_agents):
    """Run UnivaStoryboardAgent → UnivaKeyFrameAgent → UnivaVideoAgent end-to-end."""

    client = assistant_http_client_real_agents
    runtime_base = Path(getattr(client, "_fw_runtime_base", ""))
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_file = runtime_base / "debug" / f"univa_pipeline_trace_{run_id}.jsonl"

    print(f"\n[univa-e2e] runtime_base={runtime_base}")
    print(f"[univa-e2e] api_trace={debug_file}")

    # -- Create task (same prompt as the original FrameWorkers e2e test) ----
    create_step_resp = client.post(
        "/api/steps/create",
        json={
            "description": {
                "goal": (
                    "Create a simple cinematic short video: "
                    "A retired watchmaker races against the final moments before "
                    "midnight to repair his late wife's cherished pocket watch, seeking "
                    "a moment of peace and connection as the new year begins."
                )
            }
        },
    )
    _append_debug_record(debug_file, {
        "step": "create_step",
        "status_code": create_step_resp.status_code,
        "body": create_step_resp.get_json(),
    })
    assert create_step_resp.status_code == 201
    task_body = create_step_resp.get_json()
    step_id = task_body["id"]
    print(f"[univa-e2e] step_id={step_id}")

    common_inputs: dict = {}

    # -- Define the UniVA pipeline agents in order --------------------------
    univa_agents = [
        "UnivaStoryboardAgent",
        "UnivaKeyFrameAgent",
        "UnivaVideoAgent",
    ]
    payloads: dict[str, dict] = {}

    for agent_id in univa_agents:
        print(f"[univa-e2e] Executing {agent_id} ...")
        execute_resp = client.post(
            "/api/assistant/execute",
            json={
                "agent_id": agent_id,
                "step_id": step_id,
                **common_inputs,
            },
        )
        body = execute_resp.get_json()
        _append_debug_record(debug_file, {
            "step": "execute",
            "agent_id": agent_id,
            "step_id": step_id,
            "status_code": execute_resp.status_code,
            "body": body,
        })
        assert execute_resp.status_code == 200, f"{agent_id} failed: {body}"
        brief = body if isinstance(body, list) else []
        assert isinstance(brief, list) and len(brief) >= 1
        assert brief[-1]["status"] == "COMPLETED", f"{agent_id} not COMPLETED: {brief[-1]}"
        print(f"[univa-e2e] {agent_id} COMPLETED")

        ex_list = client.get(f"/api/assistant/executions/step/{step_id}").get_json()
        assert isinstance(ex_list[-1].get("results"), dict)
        payloads[agent_id] = ex_list[-1]["results"]

    # -- Verify UnivaStoryboardAgent output --------------------------------
    sb_content = payloads["UnivaStoryboardAgent"].get("content", {})
    assert sb_content.get("characters"), "Storyboard should have characters"
    assert sb_content.get("shots"), "Storyboard should have shots"
    assert sb_content.get("style"), "Storyboard should have a style"

    shot_count = len(sb_content["shots"])
    char_count = len(sb_content["characters"])
    print(f"[univa-e2e] Storyboard: {char_count} characters, {shot_count} shots")

    # -- Verify UnivaKeyFrameAgent output ----------------------------------
    kf_results = payloads["UnivaKeyFrameAgent"]
    kf_content = kf_results.get("content", {})
    assert kf_content.get("character_images"), "Should have character images"
    assert kf_content.get("shot_keyframes"), "Should have shot keyframes"

    media_files = kf_results.get("_media_files", {})
    assert isinstance(media_files, dict)
    assert not _contains_raw_bytes(media_files), "JSON response should not contain raw bytes"
    print(f"[univa-e2e] KeyFrames: {len(kf_content['character_images'])} chars, "
          f"{len(kf_content['shot_keyframes'])} shots, "
          f"{len(media_files)} media files")

    # -- Verify UnivaVideoAgent output -------------------------------------
    video_results = payloads["UnivaVideoAgent"]
    video_content = video_results.get("content", {})
    assert video_content.get("shot_videos"), "Should have shot videos"
    assert video_content.get("final_video_asset"), "Should have final video asset"

    video_media = video_results.get("_media_files", {})
    assert isinstance(video_media, dict)
    print(f"[univa-e2e] Video: {len(video_content['shot_videos'])} shot clips, "
          f"{len(video_media)} media files")

    # -- Verify execution order --------------------------------------------
    executions_resp = client.get(f"/api/assistant/executions/step/{step_id}")
    _append_debug_record(debug_file, {
        "step": "executions_by_task",
        "step_id": step_id,
        "status_code": executions_resp.status_code,
        "body": executions_resp.get_json(),
    })
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    executed_agents = [item.get("agent_id") for item in executions]
    assert executed_agents == univa_agents

    print(f"\n[univa-e2e] ALL PASSED - pipeline: {' -> '.join(univa_agents)}")
    print(f"[univa-e2e] Debug trace: {debug_file}")
