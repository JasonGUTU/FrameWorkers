#!/usr/bin/env python3
"""End-to-end runner with a hand-injected GT plan chain (skips director planning).

Use case
========
Run the full sub-agent pipeline against a known-good plan without
burning the planner LLM budget or risking planner drift between runs.
Also supports a ``--stop-after-agent`` pause point so a human can
review intermediate artifacts (e.g. KeyFrame stills) before resuming.

This script mirrors ``director_agent/director.py::_execute_planned_steps``
one-for-one (update_step_status IN_PROGRESS → /api/assistant/execute →
update_step_status COMPLETED → advance_execution_pointer) but replaces
the upfront planner LLM call with a hardcoded ``_DEFAULT_CHAIN``. No
replan-on-failure; halts on the first FAILED step.

Examples
--------

  # First half: Story → Screenplay → KeyFrame, then stop
  python -u scripts/run_e2e_gt_chain.py \\
      --user-goal "$(cat /tmp/fox_demon_prompt.txt)" \\
      --stop-after-agent KeyFrameAgent

  # Resume from where it stopped (Video → … → Compositor)
  python -u scripts/run_e2e_gt_chain.py --resume

Backend prerequisite
--------------------
``plan-stack-backend`` must already be running with the desired
``FW_USE_REAL_MEDIA_GEN`` / ``FW_WORKSPACE_ROOT`` / ``FW_TRACE_DIR`` /
``FW_VIDEO_SHOT_SPILL_DIR`` env vars baked into the process (they're
read by the materializer / trace writer at request time, not by this
script).
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from director_agent.api_client import BackendAPIClient  # noqa: E402
from director_agent.director import _persist_plan  # noqa: E402
from director_agent.router import PlanStepSpec  # noqa: E402


# 12-step GT chain — adds IntakeImage + BriefEnricher head when an image
# is uploaded via ``--upload-image``. When run without an image upload,
# the head two steps still appear but Intake will skip (no raw_pending
# artifact to consume) and BriefEnricher degrades to text-only enrichment.
# (agent_id, intent) — intent goes into PlanStep.description.intent so the
# resulting plan stack reads like a director-planned one.
_DEFAULT_CHAIN: list[tuple[str, str]] = [
    ("IntakeImageAgent",
     "Ingest the uploaded raw image into a caption-rich workspace artifact."),
    ("BriefEnricherAgent",
     "Merge the raw user brief with the uploaded image descriptors into an "
     "enriched creative brief."),
    ("StoryAgent",
     "Generate a high-level story blueprint from the enriched brief."),
    ("ScreenplayAgent",
     "Develop the screenplay (scenes/shots, dialogue, camera) from the story."),
    ("KeyFrameAgent",
     "Generate L1 global + L2 scene + L3 per-shot keyframe stills, picking up "
     "the uploaded image as a character/style reference where applicable."),
    ("VideoAgent",
     "Produce per-shot video clips via i2v and assemble into a film."),
    ("TranscriptionAgent",
     "Transcribe the assembled video's baked-in dialogue audio."),
    ("TranslationAgent",
     "Translate the transcript into the second subtitle language."),
    ("MusicAgent",
     "Generate a film-wide classical-Chinese BGM track."),
    ("AmbienceAgent",
     "Generate film-wide ambient sounds (nine-heaven thunder)."),
    ("AudioMixAgent",
     "Mix video baked audio + music + ambience into a final track."),
    ("CompositorAgent",
     "Mux final audio + video and burn bilingual subtitle tracks."),
]


def _upload_image(client: "BackendAPIClient", image_path: Path) -> dict[str, Any]:
    """POST /api/workspace/upload with a base64-encoded image.

    The endpoint creates a raw_pending workspace artifact that
    IntakeImageAgent (which declares [raw_image_upload] (single)) picks
    up via caption pattern match.
    """
    image_bytes = image_path.read_bytes()
    mime, _ = mimetypes.guess_type(str(image_path))
    if not mime or not mime.startswith("image/"):
        mime = "image/png"
    payload = {
        "mime": mime,
        "data_b64": base64.b64encode(image_bytes).decode("ascii"),
        "filename": image_path.name,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{client.base_url}/api/workspace/upload",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30.0) as r:
        resp = json.loads(r.read().decode("utf-8"))
    return resp


def _wait_backend(base_url: str, *, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"{base_url}/api/plan-stack", timeout=2.0,
            ) as r:
                if r.status == 200:
                    return
        except Exception as exc:
            last_err = exc
        time.sleep(0.5)
    raise RuntimeError(f"backend at {base_url} not ready: {last_err}")


def _print_step_done(
    idx: int, total: int, agent_id: str, step_id: str,
    dur_s: float, status: str, eval_summary: str = "",
) -> None:
    print(
        f"[{idx}/{total}] {agent_id:24s} step={step_id} "
        f"status={status} elapsed={dur_s:.1f}s"
    )
    if eval_summary:
        print(f"          eval: {eval_summary[:150]}")
    sys.stdout.flush()


def run(args: argparse.Namespace) -> int:
    _wait_backend(args.backend)
    client = BackendAPIClient(base_url=args.backend)

    chain = _DEFAULT_CHAIN
    total = len(chain)
    chain_agent_order = [c[0] for c in chain]

    if not args.resume:
        if args.upload_image:
            img_path = Path(args.upload_image).expanduser().resolve()
            if not img_path.is_file():
                print(f"[gt-chain] FATAL: --upload-image path not a file: {img_path}")
                return 2
            print(f"[gt-chain] uploading image {img_path.name} "
                  f"({img_path.stat().st_size} bytes) → /api/workspace/upload…")
            upload_resp = _upload_image(client, img_path)
            print(f"[gt-chain] uploaded: {upload_resp}")

        print(f"[gt-chain] seeding creative_brief via /api/messages/create…")
        msg = client.create_message(content=args.user_goal, sender_type="user")
        print(f"[gt-chain] seeded message id={msg.get('id')}")

        plan = [
            PlanStepSpec(agent_id=aid, intent=intent)
            for aid, intent in chain
        ]
        print(f"[gt-chain] persisting {len(plan)} GT plan steps to plan stack…")
        step_ids = _persist_plan(
            client, plan=plan,
            rationale="GT chain injected — planner bypassed",
        )
        if not step_ids:
            print("[gt-chain] FATAL: _persist_plan returned no step ids")
            return 2
        print(f"[gt-chain] plan persisted: {len(step_ids)} steps")
    else:
        print("[gt-chain] --resume: skipping seed + persist, "
              "continuing from current execution pointer")

    stop_after = (args.stop_after_agent or "").strip()

    while True:
        try:
            next_step = client.get_next_step()
        except Exception as exc:
            print(f"[gt-chain] get_next_step error: {exc}")
            return 3
        if not next_step:
            print("[gt-chain] No more pending steps — pipeline complete ✅")
            return 0

        step_id = next_step.get("step_id")
        step_payload = next_step.get("step") or {}
        description = (
            step_payload.get("description")
            if isinstance(step_payload, dict) else {}
        )
        agent_id = (
            description.get("agent_id")
            if isinstance(description, dict) else None
        )
        if not agent_id:
            print(f"[gt-chain] step {step_id} has no agent_id; advancing")
            client.advance_execution_pointer()
            continue

        try:
            current_idx = chain_agent_order.index(agent_id) + 1
        except ValueError:
            current_idx = -1

        print(f"\n>>> [{current_idx}/{total}] starting {agent_id} "
              f"(step_id={step_id})")
        sys.stdout.flush()
        t_start = time.time()

        try:
            client.update_step_status(step_id, "IN_PROGRESS")
        except Exception as exc:
            print(f"[gt-chain] update_step_status IN_PROGRESS warning: {exc}")

        try:
            result = client.execute_agent(agent_id=agent_id, step_id=step_id)
        except Exception as exc:
            print(f"[gt-chain] execute_agent {agent_id} FAILED: {exc}")
            try:
                client.update_step_status(step_id, "FAILED")
            except Exception:
                pass
            return 4

        elapsed = time.time() - t_start
        status = str((result or {}).get("status") or "").upper()
        error_msg = (result or {}).get("error") or ""

        try:
            if status == "FAILED":
                client.update_step_status(step_id, "FAILED")
            else:
                client.update_step_status(step_id, "COMPLETED")
        except Exception as exc:
            print(f"[gt-chain] update_step_status final warning: {exc}")

        eval_summary = ""
        results: Any = (result or {}).get("results") or {}
        if isinstance(results, dict):
            debug = results.get("_execution_debug") or {}
            eval_summary = debug.get("eval_summary") or ""

        _print_step_done(
            current_idx, total, agent_id, step_id,
            elapsed, status, eval_summary,
        )

        if status == "FAILED":
            print(f"[gt-chain] step FAILED with error: {error_msg}")
            print("[gt-chain] halting (GT chain has no replan path)")
            return 5

        # Advance pointer BEFORE checking stop, so on --resume we pick up
        # the next step cleanly without re-running the stopped one.
        try:
            client.advance_execution_pointer()
        except Exception as exc:
            print(f"[gt-chain] advance_execution_pointer warning: {exc}")

        if stop_after and agent_id == stop_after:
            next_agent = (
                chain_agent_order[current_idx]
                if 0 <= current_idx < total else "(none — chain done)"
            )
            print(f"\n=== STOPPED after {agent_id} ===")
            print(f"Steps 1..{current_idx} are COMPLETED.")
            print(f"Pointer now on next step: {next_agent}")
            print("To resume: "
                  f"python -u {Path(__file__).relative_to(_REPO_ROOT)} --resume")
            return 0


def main() -> None:
    p = argparse.ArgumentParser(
        description="GT-chain e2e runner (bypasses director planner)."
    )
    p.add_argument(
        "--user-goal", default=None,
        help="Creative brief text. Required unless --resume.",
    )
    p.add_argument(
        "--upload-image", default=None,
        help="Path to an image file to upload as raw_pending workspace "
             "artifact before the chain starts. IntakeImageAgent will "
             "ingest it; KeyFrameAgent picks it up via "
             "INPUT_LABEL_*_REFERENCE caption match.",
    )
    p.add_argument(
        "--stop-after-agent", default=None,
        help="Agent name to stop after (executes that step, advances "
             "pointer, exits). E.g. 'KeyFrameAgent'.",
    )
    p.add_argument(
        "--resume", action="store_true",
        help="Continue from current execution pointer; skip seed + "
             "plan persist (chain already in plan stack).",
    )
    p.add_argument(
        "--backend",
        default=os.getenv("BACKEND_BASE_URL", "http://localhost:5002"),
    )
    args = p.parse_args()

    if not args.resume and not args.user_goal:
        p.error("--user-goal is required unless --resume is set")

    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
