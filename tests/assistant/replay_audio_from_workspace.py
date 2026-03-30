#!/usr/bin/env python3
"""Offline (and optional live) replay of AudioAgent against saved workspace JSON.

Use this to verify that screenplay + storyboard + video snapshots still form a
valid skeleton and to inspect the creative-fill prompt size (the step that calls
``chat_json`` in skeleton mode).

Example (no API calls)::

    cd /path/to/FrameWorkers
    PYTHONPATH=. python tests/assistant/replay_audio_from_workspace.py \\
        --workspace Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887

Optional: one real ``chat_json`` call to reproduce parse failures::

    PYTHONPATH=. FW_ENABLE_LIVE_LLM_TESTS=1 python tests/assistant/replay_audio_from_workspace.py \\
        --workspace ... --live
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_audio_inputs(workspace: Path) -> dict:
    """Load the three assets AudioAgent expects (same shape as hydrated registry JSON)."""
    base = workspace / "artifacts"
    paths = {
        "screenplay": base / "screenplay" / "screenplay_exec_2.json",
        "storyboard": base / "storyboard" / "storyboard_exec_3.json",
        "video": base / "video" / "video_exec_5.json",
    }
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing expected artifact files:\n  " + "\n  ".join(missing)
        )
    return {
        "screenplay": json.loads(paths["screenplay"].read_text(encoding="utf-8")),
        "storyboard": json.loads(paths["storyboard"].read_text(encoding="utf-8")),
        "video": json.loads(paths["video"].read_text(encoding="utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay AudioAgent skeleton + creative prompt from a Runtime workspace folder."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=_repo_root()
        / "Runtime/live_e2e_outputs/workspace_global_20260330_112100_851887",
        help="Path to workspace_global_* directory",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Perform one real chat_json call (needs FW_ENABLE_LIVE_LLM_TESTS=1 and API keys).",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of live chat_json attempts (stop on first failure).",
    )
    args = parser.parse_args()
    ws: Path = args.workspace.resolve()

    # Import after argparse so ``python tests/assistant/replay_audio_from_workspace.py -h`` works
    # without PYTHONPATH in some environments.
    repo = _repo_root()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    from agents.audio.agent import AudioAgent
    from agents.audio.schema import AudioAgentInput
    from inference.clients import LLMClient

    assets = load_audio_inputs(ws)
    inp = AudioAgentInput(
        screenplay=assets["screenplay"],
        storyboard=assets["storyboard"],
        video=assets["video"],
    )

    agent = AudioAgent(llm_client=LLMClient())
    sk = agent.build_skeleton(inp)
    if sk is None:
        print(
            "build_skeleton returned None — check screenplay/storyboard/video "
            "non-empty and video content.scenes present.",
            file=sys.stderr,
        )
        return 1

    n_scenes = len(sk.content.scenes)
    user_prompt = agent.build_creative_prompt(inp, sk)
    vid_scenes = (
        assets["video"].get("content", {}).get("scenes", [])
        if isinstance(assets["video"].get("content"), dict)
        else []
    )

    print(f"workspace: {ws}")
    print(f"video scenes (asset): {len(vid_scenes)}")
    print(f"audio skeleton scenes: {n_scenes}")
    print(f"creative user prompt chars: {len(user_prompt)}")
    print(
        "template tail (OUTPUT FORMAT excerpt, first 800 chars of rules+template block):"
    )
    tail_start = user_prompt.find("=== OUTPUT FORMAT ===")
    if tail_start >= 0:
        print(user_prompt[tail_start : tail_start + 800])
    else:
        print(user_prompt[:800])

    if not args.live:
        print(
            "\nOffline check done. Failure mode 'chat_json: ... not valid JSON' happens "
            "when the model returns non-JSON text; it is not caused by missing assets "
            "if skeleton built successfully above.\n"
            "Re-run with --live to call the API once."
        )
        return 0

    import os

    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        print(
            "Refusing --live: set FW_ENABLE_LIVE_LLM_TESTS=1 (same gate as live e2e tests).",
            file=sys.stderr,
        )
        return 2

    async def _once() -> None:
        system = agent.system_prompt()
        await agent.llm.chat_json(system, user_prompt)

    n = int(args.repeat or 1)
    if n < 1:
        n = 1

    print(f"\nCalling chat_json (repeat={n}) …")
    for i in range(1, n + 1):
        try:
            asyncio.run(_once())
        except Exception as exc:
            print(f"\nchat_json FAILED on attempt {i}/{n}: {exc!r}", file=sys.stderr)
            dump_on = os.getenv("FW_JSON_DIAG_DUMP", "").strip().lower() in {"1", "true", "yes", "on"}
            dump_dir = os.getenv("FW_JSON_DIAG_DUMP_DIR", "").strip() or "Runtime/debug/json_parse_failures"
            if dump_on:
                print(f"Invalid JSON dump directory: {dump_dir}", file=sys.stderr)
            else:
                print(
                    "Tip: set FW_JSON_DIAG_DUMP=1 to write the raw invalid model output to disk.",
                    file=sys.stderr,
                )
            return 1
        else:
            print(f"attempt {i}/{n}: chat_json OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
