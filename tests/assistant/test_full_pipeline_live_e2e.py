from __future__ import annotations

import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

# Make `plan-stack-backend/src` and repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# `src/__init__.py` imports app.py -> flask_cors.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from inference.clients import LLMClient


def _is_full_pipeline_live_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_FULL_PIPELINE_E2E") != "1":
        return (
            False,
            (
                "Full pipeline live e2e disabled. "
                "Set FW_ENABLE_FULL_PIPELINE_E2E=1 to run."
            ),
        )
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return (
            False,
            (
                "Live LLM test disabled. "
                "Set FW_ENABLE_LIVE_LLM_TESTS=1 to run."
            ),
        )

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
        return False, f"Live full-pipeline precheck failed: {exc}"

    if not key_value:
        return (
            False,
            (
                "Live full-pipeline test missing provider key. "
                f"Set {provider_key_env} or configure routing/api_keys."
            ),
        )

    return True, ""


_LIVE_READY, _LIVE_SKIP_REASON = _is_full_pipeline_live_ready()


@pytest.fixture
def assistant_http_client_real_agents(tmp_path, monkeypatch):
    _ = tmp_path  # keep fixture signature stable
    runtime_base = Path(
        os.getenv(
            "FW_LIVE_E2E_RUNTIME_DIR",
            str(_repo_root / "Runtime" / "live_e2e_outputs"),
        )
    )
    runtime_base.mkdir(parents=True, exist_ok=True)

    storage = AssistantStateStore(runtime_base_path=runtime_base)
    monkeypatch.setattr(routes_module, "assistant_state_store", storage)

    # Default on for this suite: prop L1/L2 keyframes + video prop constraints.
    # Set FW_ENABLE_PROP_PIPELINE in the shell to override.
    monkeypatch.setenv(
        "FW_ENABLE_PROP_PIPELINE",
        os.getenv("FW_ENABLE_PROP_PIPELINE", "1"),
    )

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        setattr(client, "_fw_runtime_base", str(runtime_base))
        yield client


def _append_debug_record(debug_file: Path, payload: dict) -> None:
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with debug_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _contains_raw_bytes(node: object) -> bool:
    if isinstance(node, (bytes, bytearray)):
        return True
    if isinstance(node, dict):
        return any(_contains_raw_bytes(v) for v in node.values())
    if isinstance(node, list):
        return any(_contains_raw_bytes(v) for v in node)
    return False


@pytest.mark.skipif(
    not _LIVE_READY,
    reason=_LIVE_SKIP_REASON,
)
def test_full_pipeline_live_http_flow_generates_about_one_minute_video(
    assistant_http_client_real_agents,
):
    client = assistant_http_client_real_agents
    runtime_base = Path(getattr(client, "_fw_runtime_base", ""))
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_file = runtime_base / "debug" / f"full_pipeline_api_trace_{run_id}.jsonl"
    print(f"[full-pipeline-live-e2e] runtime_base={runtime_base}")
    print(f"[full-pipeline-live-e2e] api_trace={debug_file}")

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
    _append_debug_record(
        debug_file,
        {
            "step": "create_step",
            "status_code": create_step_resp.status_code,
            "body": create_step_resp.get_json(),
        },
    )
    assert create_step_resp.status_code == 201
    task_body = create_step_resp.get_json()
    step_id = task_body["id"]

    common_inputs: dict = {}
    payloads: dict[str, dict] = {}

    pre_media_agents = ["StoryAgent", "ScreenplayAgent"]
    media_agents = ["KeyFrameAgent", "VideoAgent", "AudioAgent"]

    for agent_id in pre_media_agents:
        execute_resp = client.post(
            "/api/assistant/execute",
            json={
                "agent_id": agent_id,
                "step_id": step_id,
                **common_inputs,
            },
        )
        body = execute_resp.get_json()
        _append_debug_record(
            debug_file,
            {
                "step": "execute",
                "agent_id": agent_id,
                "step_id": step_id,
                "status_code": execute_resp.status_code,
                "body": body,
            },
        )
        assert execute_resp.status_code == 200, f"{agent_id} failed: {body}"
        brief = body if isinstance(body, list) else []
        assert isinstance(brief, list) and len(brief) >= 1
        assert brief[-1]["status"] == "COMPLETED", f"{agent_id} not COMPLETED: {brief[-1]}"
        ex_list = client.get(f"/api/assistant/executions/step/{step_id}").get_json()
        assert isinstance(ex_list[-1].get("results"), dict)
        payloads[agent_id] = ex_list[-1]["results"]

    for agent_id in media_agents:
        execute_resp = client.post(
            "/api/assistant/execute",
            json={
                "agent_id": agent_id,
                "step_id": step_id,
                **common_inputs,
            },
        )
        body = execute_resp.get_json()
        _append_debug_record(
            debug_file,
            {
                "step": "execute",
                "agent_id": agent_id,
                "step_id": step_id,
                "status_code": execute_resp.status_code,
                "body": body,
            },
        )
        assert execute_resp.status_code == 200, f"{agent_id} failed: {body}"
        brief = body if isinstance(body, list) else []
        assert isinstance(brief, list) and len(brief) >= 1
        assert brief[-1]["status"] == "COMPLETED", f"{agent_id} not COMPLETED: {brief[-1]}"
        ex_list = client.get(f"/api/assistant/executions/step/{step_id}").get_json()
        assert isinstance(ex_list[-1].get("results"), dict)
        payloads[agent_id] = ex_list[-1]["results"]

    story_content = payloads["StoryAgent"].get("content", {})
    assert story_content.get("logline")

    screenplay_scenes = payloads["ScreenplayAgent"].get("content", {}).get(
        "scenes", []
    )
    assert screenplay_scenes
    assert any(
        scene.get("shots")
        for scene in screenplay_scenes
        if isinstance(scene, dict)
    )

    keyframe_results = payloads["KeyFrameAgent"]
    assert keyframe_results.get("content")
    media_files = keyframe_results.get("_media_files", {})
    assert isinstance(media_files, dict)
    assert media_files, "Expected KeyFrameAgent to return media files metadata"
    assert not _contains_raw_bytes(media_files), "JSON response still contains raw bytes"

    video_results = payloads["VideoAgent"]
    assert video_results.get("content", {}).get("final_video_asset")

    audio_results = payloads["AudioAgent"]
    assert audio_results.get("content", {}).get("final_delivery_asset")

    executions_resp = client.get(f"/api/assistant/executions/step/{step_id}")
    _append_debug_record(
        debug_file,
        {
            "step": "executions_by_task",
            "step_id": step_id,
            "status_code": executions_resp.status_code,
            "body": executions_resp.get_json(),
        },
    )
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    executed_agents = [item.get("agent_id") for item in executions]
    pipeline_agents = pre_media_agents + media_agents
    assert executed_agents == pipeline_agents
