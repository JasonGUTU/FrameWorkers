"""Replay a saved simplified workspace through KeyFrame/Video/Audio agents.

This script does three things:
1) Save (copy) a timestamped live-e2e workspace into a stable snapshot folder.
2) Simplify storyboard/screenplay to N shots (default 3) using linked_blocks.
3) Load storyboard/screenplay/story assets from that snapshot.
3) Execute KeyFrameAgent -> VideoAgent -> AudioAgent via assistant HTTP APIs
   (Flask test client) and persist a replay summary.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import types
from datetime import datetime
from pathlib import Path
from typing import Any


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root containing agents/__init__.py")


PROJECT_ROOT = _resolve_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PKG_ROOT = PROJECT_ROOT / "dynamic-task-stack"
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

# create_app imports flask_cors in this repo setup; keep script runnable standalone.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_asset_file(snapshot_dir: Path, prefix: str) -> Path:
    matches = sorted(snapshot_dir.glob(f"{prefix}*.json"))
    if not matches:
        raise FileNotFoundError(f"No file matching {prefix}*.json in {snapshot_dir}")
    return matches[0]


def _copy_workspace(src_dir: Path, save_dir: Path) -> Path:
    if not src_dir.exists():
        raise FileNotFoundError(f"Source workspace not found: {src_dir}")
    save_dir.parent.mkdir(parents=True, exist_ok=True)
    if save_dir.exists():
        shutil.rmtree(save_dir)
    shutil.copytree(src_dir, save_dir)
    return save_dir


def _simplify_workspace_to_shots(snapshot_dir: Path, shot_limit: int) -> dict[str, Any]:
    """Trim storyboard and screenplay JSONs to the first `shot_limit` shots."""
    storyboard_path = _find_asset_file(snapshot_dir, "storyboardagent_storyboard_")
    screenplay_path = _find_asset_file(snapshot_dir, "screenplayagent_screenplay_")
    storyboard = _load_json(storyboard_path)
    screenplay = _load_json(screenplay_path)

    scenes = storyboard.get("content", {}).get("scenes", [])
    if not scenes:
        raise RuntimeError("Storyboard has no scenes to simplify")
    first_scene = scenes[0]
    shots = first_scene.get("shots", [])
    trimmed_shots = shots[:shot_limit]
    first_scene["shots"] = trimmed_shots

    linked_block_ids: list[str] = []
    for shot in trimmed_shots:
        for bid in shot.get("linked_blocks", []):
            if bid and bid not in linked_block_ids:
                linked_block_ids.append(bid)

    sp_scenes = screenplay.get("content", {}).get("scenes", [])
    if sp_scenes:
        sp_scene = sp_scenes[0]
        blocks = sp_scene.get("blocks", [])
        sp_scene["blocks"] = [
            b for b in blocks
            if b.get("block_id", "") in linked_block_ids
        ]
        sp_scene["estimated_duration"] = {
            "seconds": round(sum(float(s.get("estimated_duration_sec", 0.0)) for s in trimmed_shots), 2),
            "confidence": 0.7,
        }

    total_duration = round(sum(float(s.get("estimated_duration_sec", 0.0)) for s in trimmed_shots), 2)
    first_scene["estimated_duration"] = {"seconds": total_duration, "confidence": 0.7}
    sb_metrics = storyboard.setdefault("metrics", {})
    sb_metrics["scene_count"] = 1
    sb_metrics["shot_count_total"] = len(trimmed_shots)
    sb_metrics["avg_shots_per_scene"] = float(len(trimmed_shots))
    sb_metrics["sum_shot_duration_sec"] = total_duration

    sp_metrics = screenplay.setdefault("metrics", {})
    sp_metrics["scene_count"] = 1
    sp_metrics["estimated_total_duration_sec"] = total_duration
    sp_metrics["sum_scene_duration_sec"] = total_duration
    blocks_after = screenplay.get("content", {}).get("scenes", [{}])[0].get("blocks", [])
    sp_metrics["dialogue_block_count"] = sum(1 for b in blocks_after if b.get("block_type") == "dialogue")
    sp_metrics["action_block_count"] = sum(1 for b in blocks_after if b.get("block_type") == "action")

    storyboard_path.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")
    screenplay_path.write_text(json.dumps(screenplay, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "shot_limit": shot_limit,
        "shots_kept": [s.get("shot_id", "") for s in trimmed_shots],
        "linked_blocks_kept": linked_block_ids,
        "total_duration_sec": total_duration,
        "storyboard_file": str(storyboard_path),
        "screenplay_file": str(screenplay_path),
    }


def _execute_pipeline(snapshot_dir: Path, runtime_base: Path) -> dict[str, Any]:
    storyboard = _load_json(_find_asset_file(snapshot_dir, "storyboardagent_storyboard_"))
    screenplay = _load_json(_find_asset_file(snapshot_dir, "screenplayagent_screenplay_"))
    story = _load_json(_find_asset_file(snapshot_dir, "storyagent_story_blueprint_"))

    draft_text = (
        story.get("content", {}).get("logline")
        or story.get("content", {}).get("title")
        or "Replay simplified workspace"
    )

    storage = AssistantStateStore(runtime_base_path=runtime_base)
    routes_module.assistant_state_store = storage
    app = create_app({"TESTING": True})

    with app.test_client() as client:
        create_task_resp = client.post(
            "/api/tasks/create",
            json={"description": {"goal": "Replay simplified saved workspace through media agents."}},
        )
        if create_task_resp.status_code != 201:
            raise RuntimeError(f"create task failed: {create_task_resp.status_code} {create_task_resp.get_json()}")
        task_id = create_task_resp.get_json()["id"]

        base_assets = {
            "draft_idea": draft_text,
            "source_text": draft_text,
            "screenplay": screenplay,
            "storyboard": storyboard,
        }
        common_inputs = {
            "assets": base_assets,
            "config": {"target_total_duration_sec": 10, "language": "en"},
        }

        agents = ["KeyFrameAgent", "VideoAgent", "AudioAgent"]
        outputs: dict[str, Any] = {}
        for agent_id in agents:
            resp = client.post(
                "/api/assistant/execute",
                json={
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "additional_inputs": common_inputs,
                },
            )
            body = resp.get_json()
            if resp.status_code != 200 or body.get("status") != "COMPLETED":
                raise RuntimeError(
                    f"{agent_id} failed: status={resp.status_code}, body={body}"
                )
            outputs[agent_id] = body

    return {
        "task_id": task_id,
        "agents": agents,
        "outputs": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay simplified workspace through media agents.")
    parser.add_argument("--shot-limit", type=int, default=3, help="Keep first N storyboard shots")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Only snapshot+simplify workspace, do not execute agents.",
    )
    args = parser.parse_args()

    src_workspace = PROJECT_ROOT / "Runtime" / "live_e2e_outputs" / "workspace_global_20260320_105714_349207"
    saved_workspace = PROJECT_ROOT / "Runtime" / "saved_workspaces" / "workspace_simplified_20260320_105714"
    runtime_base = PROJECT_ROOT / "Runtime" / "saved_workspace_replay_outputs"

    snapshot_dir = _copy_workspace(src_workspace, saved_workspace)
    simplify_summary = _simplify_workspace_to_shots(snapshot_dir, shot_limit=max(1, args.shot_limit))

    if args.prepare_only:
        summary = {
            "status": "prepared",
            "saved_workspace": str(snapshot_dir),
            "simplified": simplify_summary,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    replay = _execute_pipeline(snapshot_dir=snapshot_dir, runtime_base=runtime_base)

    out_dir = runtime_base / "debug"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"replay_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    summary = {
        "status": "ok",
        "saved_workspace": str(snapshot_dir),
        "simplified": simplify_summary,
        "runtime_base": str(runtime_base),
        "task_id": replay["task_id"],
        "agents": replay["agents"],
        "agent_statuses": {
            aid: replay["outputs"][aid]["status"] for aid in replay["agents"]
        },
        "result_keys": {
            aid: sorted(list((replay["outputs"][aid].get("results") or {}).keys()))
            for aid in replay["agents"]
        },
    }
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

