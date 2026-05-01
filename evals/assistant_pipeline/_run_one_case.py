#!/usr/bin/env python3
"""Run ONE assistant_pipeline eval case in this process.

Spawned by :mod:`evals.assistant_pipeline.eval_pipeline` as a subprocess
so each case gets a fresh :class:`AssistantStateStore` / :class:`Workspace`
/ global_memory — the state store is process-local by design, so
subprocess isolation is the clean way to prevent cross-case caption
pollution on the InputResolver side.

Per case this entry:

  1. Creates a fresh store rooted at ``--runtime-base`` (isolated
     ``_workspaces`` dir, one per case run).
  2. Seeds ``user_goal`` as a ``text/plain`` raw upload (always — lands
     as a global ``[creative_brief]`` artifact via the same path as
     ``POST /api/workspace/upload``). If the chain begins with
     ``IntakeImageAgent`` / ``IntakeVideoAgent`` / ``IntakeAudioAgent``,
     additionally seeds the matching ``--{image,video,audio}-fixture``
     file so the intake agent has a ``raw_pending`` artifact to caption.
  3. Linearizes ``expected_chain`` (strip trailing ``["done"]``, pick the
     first agent from each set-valued slot) and mints step_ids like
     ``<case_name>_s01``.
  4. For each (agent_id, step_id) calls
     ``AssistantService.execute_agent_for_step(agent_id, step_id)`` and
     collects status / error / resolved_input_paths / result keys.
  5. Writes the per-case result JSON to ``--out-path``.

The chain stops early on the FIRST failed step (no point running
downstream agents when their upstream artifact is missing).

Media backends are stubbed by default: we explicitly unset
``FW_USE_REAL_MEDIA_GEN`` in this subprocess so image / video / audio /
compositor / transcription / video_edit all route to their ``Mock*``
counterparts. Text LLMs run for real — that's the point of the eval.
IntakeImage / IntakeVideo agents also run real LLMs (captioning), so
they consume API credits even though the downstream generators are
mocked.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# sys.path + env bootstrap
# ---------------------------------------------------------------------------

_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[2]
_PKG_ROOT = _REPO_ROOT / "plan-stack-backend"
for _p in (str(_REPO_ROOT), str(_PKG_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load .env for API keys (OpenRouter / Google AI Studio / etc.) — we run
# real text LLMs by design.
from inference.config.config_loader import ConfigLoader  # noqa: E402

for _fname in (".env", ".env.example"):
    _p = _REPO_ROOT / _fname
    if _p.is_file():
        ConfigLoader.load_env_file(str(_p), override=False)

# Media mocks: belt-and-suspenders — even if the parent shell had
# FW_USE_REAL_MEDIA_GEN set, the eval subprocess must not spend fal credits.
os.environ.pop("FW_USE_REAL_MEDIA_GEN", None)

# ---------------------------------------------------------------------------
# Assistant imports (after sys.path setup)
# ---------------------------------------------------------------------------

from src.assistant.service import AssistantService  # noqa: E402
from src.assistant.state_store import AssistantStateStore  # noqa: E402
from src.assistant.models import ExecutionStatus  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
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


def _linearize(expected_chain: List[Any]) -> List[str]:
    """Pick the first agent from each set-valued slot; ``["done"]`` stripped."""
    chain = _strip_trailing_done(expected_chain)
    agents: List[str] = []
    for slot in chain:
        if isinstance(slot, list):
            if not slot:
                continue
            agents.append(str(slot[0]))
        else:
            agents.append(str(slot))
    return agents


def _serialize_result_compact(results: Any) -> Dict[str, Any]:
    """Pull the few fields we care about out of execution.results.

    We drop big LLM payloads (``content`` dicts can be tens of KB each)
    and keep only bookkeeping keys the reviewer actually needs:
      * ``_asset_index`` — artifact_writer's list of persisted files
        (path + caption + scope) — this is what tells us *what the
        workspace looks like* after the step.
      * ``_execution_debug`` — attempts / overall_pass / eval_summary /
        input_rejection — surfaces retries and quality-gate outcomes.
      * ``_media_files`` keys only — which binary outputs the materializer
        produced (we don't ship the bytes).
      * top-level keys — so the reviewer can see what structural output
        the agent produced without dumping the full blob.
    """
    if not isinstance(results, dict):
        return {}
    compact: Dict[str, Any] = {
        "top_level_keys": sorted(k for k in results.keys() if not k.startswith("_")),
    }
    if "_asset_index" in results:
        compact["_asset_index"] = results["_asset_index"]
    if "_execution_debug" in results:
        compact["_execution_debug"] = results["_execution_debug"]
    if "_media_files" in results and isinstance(results["_media_files"], dict):
        compact["_media_file_keys"] = sorted(results["_media_files"].keys())
    return compact


# ---------------------------------------------------------------------------
# Main per-case runner
# ---------------------------------------------------------------------------


_INTAKE_TO_FIXTURE_MIME: Dict[str, str] = {
    "IntakeImageAgent": "image/png",
    "IntakeVideoAgent": "video/mp4",
    "IntakeAudioAgent": "audio/wav",
}


def run_case(
    case: Dict[str, Any],
    *,
    runtime_base: Path,
    image_fixture: Path | None = None,
    video_fixture: Path | None = None,
    audio_fixture: Path | None = None,
) -> Dict[str, Any]:
    """Execute one case and return a result dict.

    The caller (parent process) writes this dict to disk. We don't
    ``raise`` on agent failures — every per-step outcome goes into the
    ``steps`` list, even FAILED ones, so the reviewer can see where the
    chain broke.
    """
    case_name = case["name"]
    user_goal = case["user_goal"]

    agents = _linearize(case["expected_chain"])
    plan: List[Dict[str, str]] = [
        {"agent_id": aid, "step_id": f"{case_name}_s{i + 1:02d}"}
        for i, aid in enumerate(agents)
    ]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    runtime_base.mkdir(parents=True, exist_ok=True)

    # Per-case isolated state store — fresh executions dict, fresh
    # global workspace. The state store writes workspace files under
    # ``runtime_base/<workspace_id>/``, so a unique runtime_base per
    # case keeps cases fully isolated even if two subprocesses somehow
    # ended up in the same Python interpreter.
    store = AssistantStateStore(runtime_base_path=runtime_base)
    service = AssistantService(store)
    workspace = service.workspace

    # --- seed 1: user_goal text → [creative_brief] global artifact ---
    seed = workspace.persist_raw_upload(
        file_content=user_goal.encode("utf-8"),
        mime="text/plain",
        original_filename="user_goal.txt",
    )

    # --- seed 2 (only if chain starts with Intake{Image,Video,Audio}Agent):
    # the fixture file → raw_pending artifact, picked up by the intake step.
    media_seed: Dict[str, Any] | None = None
    first_agent = agents[0] if agents else ""
    fixture_by_agent: Dict[str, Path | None] = {
        "IntakeImageAgent": image_fixture,
        "IntakeVideoAgent": video_fixture,
        "IntakeAudioAgent": audio_fixture,
    }
    if first_agent in _INTAKE_TO_FIXTURE_MIME:
        fixture_path = fixture_by_agent[first_agent]
        if fixture_path is None or not Path(fixture_path).is_file():
            return {
                "name": case_name,
                "user_goal": user_goal,
                "workspace_id": workspace.id,
                "workspace_path": str(workspace.runtime_base_path / workspace.id),
                "plan": plan,
                "seed": {"path": seed["path"], "caption": seed["caption"]},
                "timestamp": ts,
                "steps": [],
                "chain_correct": False,
                "completed_steps": 0,
                "failed_at": None,
                "error": (
                    f"chain starts with {first_agent} but matching fixture "
                    f"is missing: fixture_path={fixture_path}"
                ),
                "elapsed_s": 0.0,
            }
        with open(fixture_path, "rb") as fp:
            fixture_bytes = fp.read()
        media_seed = workspace.persist_raw_upload(
            file_content=fixture_bytes,
            mime=_INTAKE_TO_FIXTURE_MIME[first_agent],
            original_filename=Path(fixture_path).name,
        )

    result: Dict[str, Any] = {
        "name": case_name,
        "user_goal": user_goal,
        "workspace_id": workspace.id,
        "workspace_path": str(workspace.runtime_base_path / workspace.id),
        "plan": plan,
        "seed": {"path": seed["path"], "caption": seed["caption"]},
        "media_seed": (
            {"path": media_seed["path"], "mime": media_seed["mime"]}
            if media_seed
            else None
        ),
        "timestamp": ts,
        "steps": [],
        "chain_correct": False,
        "completed_steps": 0,
        "failed_at": None,
        "error": None,
        "elapsed_s": 0.0,
    }

    t0 = time.time()
    failed_at: str | None = None

    for idx, entry in enumerate(plan, start=1):
        agent_id = entry["agent_id"]
        step_id = entry["step_id"]
        step_record: Dict[str, Any] = {
            "index": idx,
            "agent_id": agent_id,
            "step_id": step_id,
            "status": None,
            "error": None,
            "resolved_input_paths": [],
            "results": {},
            "elapsed_s": 0.0,
        }

        print(
            f"[{case_name}] step {idx}/{len(plan)} {agent_id} ({step_id}) ...",
            flush=True,
        )

        t_step = time.time()
        try:
            execution = service.execute_agent_for_step(
                agent_id=agent_id,
                step_id=step_id,
            )
        except Exception as exc:
            step_record["status"] = "EXCEPTION"
            step_record["error"] = f"{type(exc).__name__}: {exc}"
            step_record["traceback"] = traceback.format_exc()
            step_record["elapsed_s"] = round(time.time() - t_step, 2)
            result["steps"].append(step_record)
            failed_at = step_id
            print(
                f"[{case_name}] step {idx}/{len(plan)} {agent_id} "
                f"RAISED {step_record['error']} — stopping chain",
                flush=True,
            )
            break

        step_record["status"] = (
            execution.status.value
            if isinstance(execution.status, ExecutionStatus)
            else str(execution.status)
        )
        step_record["error"] = execution.error
        step_record["resolved_input_paths"] = list(execution.resolved_input_paths or [])
        step_record["results"] = _serialize_result_compact(execution.results)
        step_record["elapsed_s"] = round(time.time() - t_step, 2)

        result["steps"].append(step_record)

        if step_record["status"] != ExecutionStatus.COMPLETED.value:
            failed_at = step_id
            print(
                f"[{case_name}] step {idx}/{len(plan)} {agent_id} "
                f"{step_record['status']} — stopping chain; error={execution.error}",
                flush=True,
            )
            break

        print(
            f"[{case_name}] step {idx}/{len(plan)} {agent_id} "
            f"COMPLETED ({step_record['elapsed_s']}s)",
            flush=True,
        )

    result["elapsed_s"] = round(time.time() - t0, 2)
    result["completed_steps"] = sum(
        1 for s in result["steps"] if s.get("status") == ExecutionStatus.COMPLETED.value
    )
    result["chain_correct"] = (
        failed_at is None and result["completed_steps"] == len(plan)
    )
    result["failed_at"] = failed_at
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--case-json",
        type=str,
        required=True,
        help="JSON string with {name, user_goal, expected_chain}.",
    )
    parser.add_argument(
        "--runtime-base",
        type=str,
        required=True,
        help="Directory for this case's Workspace runtime files.",
    )
    parser.add_argument(
        "--out-path",
        type=str,
        required=True,
        help="Where to write the per-case result JSON.",
    )
    parser.add_argument(
        "--image-fixture",
        type=str,
        default=None,
        help="Path to an image file used to seed cases that start with IntakeImageAgent.",
    )
    parser.add_argument(
        "--video-fixture",
        type=str,
        default=None,
        help="Path to a video file used to seed cases that start with IntakeVideoAgent.",
    )
    parser.add_argument(
        "--audio-fixture",
        type=str,
        default=None,
        help="Path to an audio file used to seed cases that start with IntakeAudioAgent.",
    )
    args = parser.parse_args(argv)

    case = json.loads(args.case_json)
    runtime_base = Path(args.runtime_base).resolve()
    out_path = Path(args.out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    image_fixture = Path(args.image_fixture).resolve() if args.image_fixture else None
    video_fixture = Path(args.video_fixture).resolve() if args.video_fixture else None
    audio_fixture = Path(args.audio_fixture).resolve() if args.audio_fixture else None

    # Global-exception guard: if anything above ``run_case``'s own try
    # blows up (import, env, fresh-store creation), still emit a result
    # JSON so the orchestrator can aggregate rather than hang on a
    # missing file.
    try:
        result = run_case(
            case,
            runtime_base=runtime_base,
            image_fixture=image_fixture,
            video_fixture=video_fixture,
            audio_fixture=audio_fixture,
        )
    except Exception as exc:
        result = {
            "name": case.get("name", "<unknown>"),
            "user_goal": case.get("user_goal", ""),
            "chain_correct": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "steps": [],
            "completed_steps": 0,
            "elapsed_s": 0.0,
        }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    return 0 if result.get("chain_correct") else 1


if __name__ == "__main__":
    raise SystemExit(_main())
