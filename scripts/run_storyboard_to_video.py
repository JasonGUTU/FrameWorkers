#!/usr/bin/env python3
"""Unified screenplay JSON to KeyFrameAgent (LLM + fal) to VideoAgent (skeleton + fal) to MP4.

One-shot offline pipeline (no Task Stack, no POST /api/assistant/execute). VideoAgent is
skeleton-only (no LLM): shot list and durations come from the screenplay; clips are rendered
from keyframe PNGs via VideoMaterializer / FalVideoService.

Requires: chat model env (same as pipeline) + FAL_API_KEY for images and video unless
you use --no-keyframe-materialize / --no-video-materialize to skip the corresponding fal steps.

Example::

  python3 scripts/run_storyboard_to_video.py \\
    --screenplay Runtime/live_e2e_outputs/.../screenplayagent_*.json \\
    --output-dir Runtime/live_e2e_outputs/sp_to_video_run_001

Legacy: --storyboard is an alias for --screenplay (same JSON shape).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

_FRAME_ROOT = Path(__file__).resolve().parents[1]
if str(_FRAME_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRAME_ROOT))

from agents.base_agent import MaterializeContext
from agents.contracts import InputBundleV2
from agents import get_agent_registry
from inference.clients import LLMClient

logger = logging.getLogger(__name__)


async def _run_keyframe_agent_local(
    *,
    screenplay: dict[str, Any],
    task_id: str,
    out_dir: Path,
    materialize: bool,
) -> tuple[int, dict[str, Any] | None]:
    """Run KeyFrameAgent; persist PNGs + ``keyframes_package.json`` under ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)

    bundle = InputBundleV2(
        task_id=task_id,
        context={"resolved_inputs": {"screenplay": screenplay}},
    )

    registry = get_agent_registry()
    descriptor = registry.get_descriptor("KeyFrameAgent")
    if descriptor is None:
        raise RuntimeError("Agent not registered: KeyFrameAgent")

    llm = LLMClient()
    agent = descriptor.build_equipped_agent(llm)
    typed_input = descriptor.build_input(task_id, bundle)

    materialize_ctx: MaterializeContext | None = None
    if materialize and getattr(agent, "materializer", None) is not None:

        def _persist(media_asset):
            path = out_dir / f"{media_asset.sys_id}.{media_asset.extension}"
            path.write_bytes(media_asset.data)
            return str(path.resolve())

        materialize_ctx = MaterializeContext(
            task_id=task_id,
            input_bundle_v2=bundle,
            persist_binary=_persist,
        )

    try:
        result = await agent.run(
            typed_input,
            input_bundle_v2=bundle,
            materialize_ctx=materialize_ctx,
        )
    finally:
        mat = getattr(agent, "materializer", None)
        if mat is not None and hasattr(mat, "image_svc"):
            svc = mat.image_svc
            if hasattr(svc, "close"):
                await svc.close()

    summary = {
        "passed": result.passed,
        "attempts": result.attempts,
        "eval_result": result.eval_result,
    }
    (out_dir / "keyframe_execution_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    payload: dict[str, Any] | None
    if result.asset_dict is not None:
        payload = dict(result.asset_dict)
    elif result.output is not None:
        out = result.output
        payload = out.model_dump() if hasattr(out, "model_dump") else dict(out)
    else:
        payload = None

    if payload is not None:
        (out_dir / "keyframes_package.json").write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )

    if not result.passed:
        logger.error(
            "KeyFrameAgent passed=False (attempts=%s): %s",
            result.attempts,
            result.eval_result.get("summary", ""),
        )
        return 1, None

    logger.info("KeyFrameAgent OK (attempts=%s)", result.attempts)
    return 0, payload


async def _run_video_agent_local(
    *,
    screenplay: dict[str, Any],
    keyframes: dict[str, Any],
    task_id: str,
    out_dir: Path,
    materialize: bool,
) -> tuple[int, dict[str, Any] | None]:
    """Run VideoAgent (skeleton + optional fal clips); persist under ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)

    bundle = InputBundleV2(
        task_id=task_id,
        context={
            "resolved_inputs": {
                "screenplay": screenplay,
                "keyframes": keyframes,
            }
        },
    )

    registry = get_agent_registry()
    descriptor = registry.get_descriptor("VideoAgent")
    if descriptor is None:
        raise RuntimeError("Agent not registered: VideoAgent")

    llm = LLMClient()
    agent = descriptor.build_equipped_agent(llm)
    typed_input = descriptor.build_input(task_id, bundle)

    materialize_ctx: MaterializeContext | None = None
    if materialize and getattr(agent, "materializer", None) is not None:

        def _persist(media_asset):
            path = out_dir / f"{media_asset.sys_id}.{media_asset.extension}"
            path.write_bytes(media_asset.data)
            return str(path.resolve())

        materialize_ctx = MaterializeContext(
            task_id=task_id,
            input_bundle_v2=bundle,
            persist_binary=_persist,
        )

    try:
        result = await agent.run(
            typed_input,
            input_bundle_v2=bundle,
            materialize_ctx=materialize_ctx,
        )
    finally:
        mat = getattr(agent, "materializer", None)
        if mat is not None and hasattr(mat, "video_svc"):
            svc = mat.video_svc
            if hasattr(svc, "close"):
                await svc.close()

    summary = {
        "passed": result.passed,
        "attempts": result.attempts,
        "eval_result": result.eval_result,
    }
    (out_dir / "video_execution_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )

    payload: dict[str, Any] | None
    if result.asset_dict is not None:
        payload = dict(result.asset_dict)
    elif result.output is not None:
        out = result.output
        payload = out.model_dump() if hasattr(out, "model_dump") else dict(out)
    else:
        payload = None

    if payload is not None:
        (out_dir / "video_package.json").write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )

    if not result.passed:
        logger.error(
            "VideoAgent passed=False (attempts=%s): %s",
            result.attempts,
            result.eval_result.get("summary", ""),
        )
        return 1, None

    logger.info("VideoAgent OK (attempts=%s)", result.attempts)
    return 0, payload


async def _pipeline_async(
    *,
    screenplay: dict,
    task_id: str,
    out_dir: Path,
    keyframe_materialize: bool,
    video_materialize: bool,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    kf_dir = out_dir / "keyframes"
    vid_dir = out_dir / "video"

    kf_code, kf_payload = await _run_keyframe_agent_local(
        screenplay=screenplay,
        task_id=f"{task_id}_keyframe",
        out_dir=kf_dir,
        materialize=keyframe_materialize,
    )
    if kf_code != 0 or not kf_payload:
        return 1

    if not video_materialize:
        logger.info(
            "--no-video-materialize: skipping VideoAgent entirely; keyframes in %s",
            kf_dir,
        )
        return 0

    v_code, _vp = await _run_video_agent_local(
        screenplay=screenplay,
        keyframes=kf_payload,
        task_id=f"{task_id}_video",
        out_dir=vid_dir,
        materialize=True,
    )
    return 0 if v_code == 0 else 2


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--screenplay",
        help="Path to unified screenplay JSON (e.g. screenplayagent_*.json)",
    )
    p.add_argument(
        "--storyboard",
        help="Alias for --screenplay (legacy)",
    )
    p.add_argument(
        "--output-dir",
        required=True,
        help="Directory; writes keyframes/ and video/ subfolders",
    )
    p.add_argument(
        "--task-id",
        default="local_screenplay_to_video",
        help="Synthetic task id prefix",
    )
    p.add_argument(
        "--no-keyframe-materialize",
        action="store_true",
        help="KeyFrame LLM only (no fal PNGs); cannot run video fal afterward",
    )
    p.add_argument(
        "--no-video-materialize",
        action="store_true",
        help="After keyframes, skip VideoAgent (no clip/final MP4 generation)",
    )
    args = p.parse_args()

    if bool(args.screenplay) == bool(args.storyboard):
        raise SystemExit("Provide exactly one of --screenplay or --storyboard (alias).")

    if args.no_keyframe_materialize and not args.no_video_materialize:
        raise SystemExit(
            "--no-keyframe-materialize leaves no images; add --no-video-materialize "
            "or remove --no-keyframe-materialize."
        )

    path_str = args.screenplay or args.storyboard
    sp_path = Path(path_str).resolve()
    screenplay = json.loads(sp_path.read_text(encoding="utf-8"))
    if not isinstance(screenplay, dict):
        raise SystemExit("Screenplay JSON root must be an object")

    out_dir = Path(args.output_dir).resolve()
    code = asyncio.run(
        _pipeline_async(
            screenplay=screenplay,
            task_id=str(args.task_id),
            out_dir=out_dir,
            keyframe_materialize=not args.no_keyframe_materialize,
            video_materialize=not args.no_video_materialize,
        )
    )
    if code == 0:
        logger.info("Outputs under %s (keyframes/ and optionally video/)", out_dir)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
