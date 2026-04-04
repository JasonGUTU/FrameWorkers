from __future__ import annotations

from copy import deepcopy
import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

# Make `dynamic-task-stack/src` and repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from director_agent.director import _task_stack_description_to_assistant_text

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
    # Set FW_ENABLE_PROP_KEYFRAMES / FW_ENABLE_PROP_PIPELINE in the shell to override.
    monkeypatch.setenv(
        "FW_ENABLE_PROP_KEYFRAMES",
        os.getenv("FW_ENABLE_PROP_KEYFRAMES", "1"),
    )
    monkeypatch.setenv(
        "FW_ENABLE_PROP_PIPELINE",
        os.getenv("FW_ENABLE_PROP_PIPELINE", "1"),
    )

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        setattr(client, "_fw_runtime_base", str(runtime_base))
        yield client


def _extract_duration_seconds(audio_results: dict, video_results: dict) -> float:
    audio_content = (
        audio_results.get("content", {}) if isinstance(audio_results, dict) else {}
    )
    delivery = audio_content.get("final_delivery_asset", {})
    if isinstance(delivery, dict):
        dur = delivery.get("duration_sec")
        if isinstance(dur, (int, float)):
            return float(dur)

    audio_metrics = audio_results.get("metrics", {}) if isinstance(audio_results, dict) else {}
    dur = audio_metrics.get("total_music_duration_sec")
    if isinstance(dur, (int, float)):
        return float(dur)

    video_metrics = video_results.get("metrics", {}) if isinstance(video_results, dict) else {}
    dur = video_metrics.get("total_duration_sec")
    if isinstance(dur, (int, float)):
        return float(dur)

    raise AssertionError("No duration field found in audio/video results.")


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


def _trim_screenplay_for_media_agents(
    screenplay_asset: dict,
    *,
    max_scenes: int,
    max_shots_per_scene: int,
) -> tuple[dict, dict]:
    """Trim unified screenplay before media-heavy agents (optional helper).

    Reduces media workload by shrinking ``content.scenes`` / ``shots[]``.
    """
    trimmed = deepcopy(screenplay_asset) if isinstance(screenplay_asset, dict) else {}

    def _scene_has_characters(scene: dict) -> bool:
        pack = scene.get("scene_consistency_pack", {}) if isinstance(scene, dict) else {}
        char_locks = pack.get("character_locks", []) if isinstance(pack, dict) else []
        if isinstance(char_locks, list) and any(
            isinstance(item, dict) and item.get("character_id", "") for item in char_locks
        ):
            return True
        shots = scene.get("shots", []) if isinstance(scene, dict) else []
        if isinstance(shots, list):
            for shot in shots:
                if not isinstance(shot, dict):
                    continue
                chars = shot.get("characters_in_frame", [])
                if isinstance(chars, list) and any(isinstance(cid, str) and cid for cid in chars):
                    return True
        return False

    def _pick_scenes(scenes: list[dict], limit: int, prefer_characters: bool) -> list[dict]:
        if not prefer_characters:
            return scenes[: max(1, limit)]
        with_char = [scene for scene in scenes if _scene_has_characters(scene)]
        without_char = [scene for scene in scenes if not _scene_has_characters(scene)]
        selected = (with_char + without_char)[: max(1, limit)]
        if not selected and scenes:
            return scenes[:1]
        return selected

    def _pick_shots(shots: list[dict], limit: int, prefer_characters: bool) -> list[dict]:
        if not prefer_characters:
            return shots[: max(1, limit)]
        with_char = []
        without_char = []
        for shot in shots:
            chars = shot.get("characters_in_frame", []) if isinstance(shot, dict) else []
            if isinstance(chars, list) and any(isinstance(cid, str) and cid for cid in chars):
                with_char.append(shot)
            else:
                without_char.append(shot)
        selected = (with_char + without_char)[: max(1, limit)]
        if not selected and shots:
            return shots[:1]
        return selected

    prefer_character_coverage = (
        os.getenv("FW_MEDIA_TRIM_PREFER_CHARACTER_SHOTS", "1").strip().lower()
        in {"1", "true", "yes", "on"}
    )

    sp_content = trimmed.get("content", {}) if isinstance(trimmed.get("content"), dict) else {}
    original_scenes = sp_content.get("scenes", []) if isinstance(sp_content.get("scenes"), list) else []
    scene_limit = int(max_scenes) if isinstance(max_scenes, int) else 0
    shot_limit = int(max_shots_per_scene) if isinstance(max_shots_per_scene, int) else 0
    trim_scenes_enabled = scene_limit > 0
    trim_shots_enabled = shot_limit > 0

    if trim_scenes_enabled:
        kept_scenes = _pick_scenes(
            original_scenes,
            scene_limit,
            prefer_character_coverage,
        )
    else:
        kept_scenes = list(original_scenes)

    kept_shot_ids: list[str] = []
    total_shot_duration = 0.0

    for scene in kept_scenes:
        shots = scene.get("shots", []) if isinstance(scene.get("shots"), list) else []
        if trim_shots_enabled:
            trimmed_shots = _pick_shots(
                shots,
                shot_limit,
                prefer_character_coverage,
            )
        else:
            trimmed_shots = list(shots)
        scene["shots"] = trimmed_shots
        for shot in trimmed_shots:
            try:
                total_shot_duration += float(shot.get("estimated_duration_sec", 0.0) or 0.0)
            except Exception:
                pass
            sid = shot.get("shot_id", "")
            if isinstance(sid, str) and sid and sid not in kept_shot_ids:
                kept_shot_ids.append(sid)

    sp_content["scenes"] = kept_scenes
    trimmed["content"] = sp_content

    sp_metrics = trimmed.get("metrics", {})
    if isinstance(sp_metrics, dict):
        dialogue_count = sum(
            1 for s in kept_scenes for sh in s.get("shots", [])
            if isinstance(sh, dict) and sh.get("block_type") == "dialogue"
        )
        action_count = sum(
            1 for s in kept_scenes for sh in s.get("shots", [])
            if isinstance(sh, dict) and sh.get("block_type") == "action"
        )
        scene_count = len(kept_scenes)
        shot_count = sum(
            len(s.get("shots", [])) if isinstance(s.get("shots"), list) else 0
            for s in kept_scenes
        )
        sp_metrics["scene_count"] = scene_count
        sp_metrics["shot_count_total"] = shot_count
        sp_metrics["avg_shots_per_scene"] = float(shot_count / scene_count) if scene_count else 0.0
        sp_metrics["sum_shot_duration_sec"] = round(total_shot_duration, 2)
        sp_metrics["sum_scene_duration_sec"] = round(total_shot_duration, 2)
        sp_metrics["estimated_total_duration_sec"] = round(total_shot_duration, 2)
        sp_metrics["dialogue_block_count"] = dialogue_count
        sp_metrics["action_block_count"] = action_count
        trimmed["metrics"] = sp_metrics

    kept_scene_ids = {
        scene.get("scene_id", "")
        for scene in kept_scenes
        if isinstance(scene, dict) and isinstance(scene.get("scene_id", ""), str)
    }
    trim_summary = {
        "max_scenes": max_scenes,
        "max_shots_per_scene": max_shots_per_scene,
        "trim_scenes_enabled": trim_scenes_enabled,
        "trim_shots_enabled": trim_shots_enabled,
        "prefer_character_coverage": prefer_character_coverage,
        "kept_scene_ids": sorted(kept_scene_ids),
        "kept_shot_ids": kept_shot_ids,
        "total_shot_duration_sec": round(total_shot_duration, 2),
    }
    return trimmed, trim_summary




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
    target_seconds = int(os.getenv("FW_PIPELINE_TARGET_SECONDS", "10"))
    min_seconds = int(os.getenv("FW_PIPELINE_MIN_SECONDS", "8"))
    max_seconds = int(os.getenv("FW_PIPELINE_MAX_SECONDS", "20"))

    create_task_resp = client.post(
        "/api/tasks/create",
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
            "step": "create_task",
            "status_code": create_task_resp.status_code,
            "body": create_task_resp.get_json(),
        },
    )
    assert create_task_resp.status_code == 201
    task_body = create_task_resp.get_json()
    task_id = task_body["id"]

    common_inputs = {
        "execute_fields": {"text": _task_stack_description_to_assistant_text(task_body["description"])},
    }
    payloads: dict[str, dict] = {}

    pre_media_agents = ["StoryAgent", "ScreenplayAgent"]
    media_agents = ["KeyFrameAgent", "VideoAgent", "AudioAgent"]

    for agent_id in pre_media_agents:
        execute_resp = client.post(
            "/api/assistant/execute",
            json={
                "agent_id": agent_id,
                "task_id": task_id,
                **common_inputs,
            },
        )
        body = execute_resp.get_json()
        _append_debug_record(
            debug_file,
            {
                "step": "execute",
                "agent_id": agent_id,
                "task_id": task_id,
                "status_code": execute_resp.status_code,
                "body": body,
            },
        )
        assert execute_resp.status_code == 200, f"{agent_id} failed: {body}"
        assert body["status"] == "COMPLETED"
        assert "global_memory_brief" in body
        ex_list = client.get(f"/api/assistant/executions/task/{task_id}").get_json()
        assert isinstance(ex_list[-1].get("results"), dict)
        payloads[agent_id] = ex_list[-1]["results"]

    for agent_id in media_agents:
        execute_resp = client.post(
            "/api/assistant/execute",
            json={
                "agent_id": agent_id,
                "task_id": task_id,
                **common_inputs,
            },
        )
        body = execute_resp.get_json()
        _append_debug_record(
            debug_file,
            {
                "step": "execute",
                "agent_id": agent_id,
                "task_id": task_id,
                "status_code": execute_resp.status_code,
                "body": body,
            },
        )
        assert execute_resp.status_code == 200, f"{agent_id} failed: {body}"
        assert body["status"] == "COMPLETED"
        assert "global_memory_brief" in body
        ex_list = client.get(f"/api/assistant/executions/task/{task_id}").get_json()
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

    final_duration_sec = _extract_duration_seconds(audio_results, video_results)
    assert min_seconds <= final_duration_sec <= max_seconds, (
        f"Expected final duration near {target_seconds}s. "
        f"Got {final_duration_sec:.2f}s, expected in [{min_seconds}, {max_seconds}]s."
    )

    executions_resp = client.get(f"/api/assistant/executions/task/{task_id}")
    _append_debug_record(
        debug_file,
        {
            "step": "executions_by_task",
            "task_id": task_id,
            "status_code": executions_resp.status_code,
            "body": executions_resp.get_json(),
        },
    )
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    executed_agents = [item.get("agent_id") for item in executions]
    pipeline_agents = pre_media_agents + media_agents
    assert executed_agents == pipeline_agents
