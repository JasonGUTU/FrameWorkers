#!/usr/bin/env python3
"""End-to-end driver with a user-uploaded character reference image.

Mimics the real chat-flow:
  1. POST /api/workspace/upload — register PNG bytes as a raw_pending upload
  2. POST chat message — auto-persists user_goal as a [creative_brief] artifact
  3. Director run_plan_pipeline — picks up the IntakeImageAgent step itself
     and continues into the downstream cinematic chain
  4. dump plan stack + per-step executions + media paths into a timestamped
     output dir under evals/sub-agents/

Assumes plan-stack-backend is already running on BACKEND_BASE_URL
(default http://localhost:5002). Set ``FW_USE_REAL_MEDIA_GEN=1`` for
real media generation; without it the backend mocks every fal call.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


_REPO = Path("/home/zhendong_li/FrameWorkers")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO / ".env")

from director_agent.api_client import BackendAPIClient, BackendAPIError  # noqa: E402
from director_agent.director import run_plan_pipeline  # noqa: E402
from director_agent.router import LlmSubAgentPlanner  # noqa: E402


_DEFAULT_REF_IMAGE = (
    _REPO / "evals" / "sub-agents" / "samurai_reference.png"
)
_OUTPUT_DIR_BASE = _REPO / "evals" / "sub-agents"

_DEFAULT_USER_GOAL = (
    "I've attached a reference image of a lone samurai. Make a 3-shot "
    "feudal-Japan revenge drama using him as the protagonist — a former "
    "retainer hunting the warlord who burned his village. Add muted "
    "feudal-Japan ambience and burn English subtitles."
)


def _wait_backend(base_url: str, *, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/plan-stack", timeout=2.0) as r:
                if r.status == 200:
                    return
        except Exception as exc:
            last_err = exc
        time.sleep(0.5)
    raise RuntimeError(f"backend at {base_url} did not become ready: {last_err}")


def _http_post_json(base_url: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120.0) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_get_json(base_url: str, path: str) -> Any:
    req = urllib.request.Request(f"{base_url}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=30.0) as r:
        return json.loads(r.read().decode("utf-8"))


def _normalize_uri(uri: Any) -> str | None:
    if not uri:
        return None
    s = str(uri)
    if s.startswith("file://"):
        s = s[len("file://"):]
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--backend",
        default=os.getenv("BACKEND_BASE_URL", "http://localhost:5002"),
    )
    ap.add_argument("--ref-image", default=str(_DEFAULT_REF_IMAGE))
    ap.add_argument("--user-goal", default=_DEFAULT_USER_GOAL)
    ap.add_argument(
        "--with-scaffolds",
        action="store_true",
        help=(
            "Opt-in: enable production scaffold (fewshots=True, "
            "policies=True, FW_TOPOLOGY=1) on the Director planner. "
            "Default is core prompt only (matches Qwen3-8B templated "
            "LoRA training distribution and the cloud baselines in "
            "Runtime/eval_routing/*_core*.json). Use when validating "
            "sub-agent / framework end-to-end and router accuracy "
            "matters for the chain to be runnable."
        ),
    )
    ap.add_argument(
        "--no-ref-image",
        action="store_true",
        help=(
            "Skip the reference-image upload step. Use for text-only "
            "briefs (e.g. cr_* cases) where the Director plan starts "
            "from the chat message alone, no IntakeImage step. "
            "--ref-image is ignored when this flag is set."
        ),
    )
    ap.add_argument(
        "--run-name",
        default=None,
        help=(
            "Subdir name under evals/sub-agents/ for this run's output. "
            "Default = e2e_run_<UTC timestamp>. Pass an explicit name "
            "when the backend was started with FW_WORKSPACE_ROOT pointing "
            "at the same path so wrapper-meta JSONs land alongside the "
            "backend workspace_global_*/ tree."
        ),
    )
    args = ap.parse_args()

    if args.run_name:
        run_name = args.run_name
    else:
        run_name = "e2e_run_" + time.strftime("%Y%m%d_%H%M%S")
    out_dir = _OUTPUT_DIR_BASE / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    # Backend reads FW_WORKSPACE_ROOT from env (see state_store.py) — when
    # set, the workspace is created under out_dir directly instead of
    # the default <repo>/_workspaces/. This keeps every e2e artifact in a
    # single self-contained directory under evals/sub-agents/. The env
    # var must be set BEFORE the backend process starts; if you started
    # the backend without it, the workspace will land in _workspaces/
    # and you'll need to move it manually afterwards.
    if not os.environ.get("FW_WORKSPACE_ROOT"):
        print(
            "[e2e] WARNING: FW_WORKSPACE_ROOT not set — backend will write "
            "the workspace under _workspaces/. Set it BEFORE starting the "
            f"backend (e.g. `FW_WORKSPACE_ROOT={out_dir}`) to keep the "
            "workspace inside out_dir."
        )

    # --no-ref-image: text-only brief case (e.g. cr_*); skip upload step,
    # let Director plan from the chat message alone (no IntakeImage step
    # in the resulting plan).
    skip_upload = bool(getattr(args, "no_ref_image", False))
    ref_image = Path(args.ref_image) if not skip_upload else None
    if not skip_upload and not ref_image.is_file():
        print(f"[e2e] FATAL: reference image not found: {ref_image}")
        return 2

    print(f"[e2e] output dir            : {out_dir}")
    print(f"[e2e] backend               : {args.backend}")
    print(f"[e2e] reference image       : {ref_image if ref_image else '<skipped: --no-ref-image>'}")
    print(f"[e2e] FW_USE_REAL_MEDIA_GEN : {os.getenv('FW_USE_REAL_MEDIA_GEN', '<unset>')}")
    print(f"[e2e] FAL_VIDEO_MODEL       : {os.getenv('FAL_VIDEO_MODEL', '<unset>')}")
    print(f"[e2e] FAL_IMAGE_MODEL       : {os.getenv('FAL_IMAGE_MODEL', '<unset>')}")
    print(f"[e2e] user_goal             : {args.user_goal}")
    print()

    # Persist run config so the dir is self-contained for later inspection.
    (out_dir / "00_run_config.json").write_text(
        json.dumps({
            "run_name": run_name,
            "backend": args.backend,
            "ref_image": str(ref_image) if ref_image else None,
            "skip_upload": skip_upload,
            "user_goal": args.user_goal,
            "with_scaffolds": args.with_scaffolds,
            "FW_USE_REAL_MEDIA_GEN": os.getenv("FW_USE_REAL_MEDIA_GEN"),
            "FW_WORKSPACE_ROOT": os.getenv("FW_WORKSPACE_ROOT"),
            "FW_TOPOLOGY": os.getenv("FW_TOPOLOGY"),
            "FAL_VIDEO_MODEL": os.getenv("FAL_VIDEO_MODEL"),
            "FAL_IMAGE_MODEL": os.getenv("FAL_IMAGE_MODEL"),
        }, indent=2),
        encoding="utf-8",
    )

    _wait_backend(args.backend)
    client = BackendAPIClient(base_url=args.backend)

    # ── 1. Upload reference image ──────────────────────────────────
    if skip_upload:
        print("[e2e] STEP 1: SKIPPED (--no-ref-image, text-only brief)")
        upload_resp = {"skipped": True, "reason": "no-ref-image flag set"}
    else:
        print(f"[e2e] STEP 1: uploading reference image...")
        img_bytes = ref_image.read_bytes()
        upload_resp = _http_post_json(args.backend, "/api/workspace/upload", {
            "mime": "image/png",
            "data_b64": base64.b64encode(img_bytes).decode("ascii"),
            "filename": ref_image.name,
        })
    (out_dir / "01_upload_response.json").write_text(
        json.dumps(upload_resp, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[e2e] STEP 1 done → upload sys_id={upload_resp.get('sys_id', '?')}")

    # ── 2. Catalog ─────────────────────────────────────────────────
    try:
        agents = client.get_all_agents()
    except BackendAPIError as exc:
        print(f"[e2e] FATAL: get_all_agents: {exc}")
        return 2
    print(f"[e2e] sub-agent catalog size = {len(agents)}")

    # ── 3. Post chat message → auto-persist creative_brief ─────────
    msg = client.create_message(content=args.user_goal, sender_type="user")
    print(f"[e2e] STEP 2 done → chat message id={msg.get('id')} (auto-persisted creative_brief)")

    # ── 4. Director plan pipeline ──────────────────────────────────
    # Default = core prompt only (matches Qwen3-8B templated LoRA's
    # training distribution + cloud baselines in Runtime/eval_routing/
    # *_core*.json). --with-scaffolds opts in to production scaffolds
    # (fewshots + policies + topology) when accurate routing matters
    # for the chain to be runnable end-to-end (sub-agent functional
    # validation, not routing benchmark).
    if args.with_scaffolds:
        os.environ["FW_TOPOLOGY"] = "1"
        planner = LlmSubAgentPlanner(fewshots=True, policies=True)
        print(f"[e2e] STEP 3: launching director run_plan_pipeline...")
        print(f"[e2e] planner config: PRODUCTION SCAFFOLDS "
              f"(fewshots=True, policies=True, FW_TOPOLOGY=1) "
              f"— opt-in via --with-scaffolds")
    else:
        os.environ["FW_TOPOLOGY"] = "0"
        planner = LlmSubAgentPlanner(fewshots=False, policies=False)
        print(f"[e2e] STEP 3: launching director run_plan_pipeline...")
        print(f"[e2e] planner config: core prompt only "
              f"(fewshots=False, policies=False, FW_TOPOLOGY=0) "
              f"— default per memory rule; pass --with-scaffolds to opt in")
    t0 = time.time()
    run_plan_pipeline(client, planner, agents=agents, user_goal=args.user_goal)
    elapsed = time.time() - t0
    print(f"[e2e] STEP 3 done → run_plan_pipeline returned in {elapsed:.1f}s")

    # ── 5. Collect plan stack + per-step executions ────────────────
    layers = client.get_plan_stack()
    (out_dir / "02_plan_stack.json").write_text(
        json.dumps(layers, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    plan_summary: list[dict[str, Any]] = []
    for li, layer in enumerate(layers):
        for step in layer.get("steps", []):
            desc = step.get("description") or {}
            plan_summary.append({
                "layer": li,
                "step_id": step.get("step_id"),
                "agent_id": desc.get("agent_id") if isinstance(desc, dict) else None,
                "status": step.get("status"),
                "intent": (
                    desc.get("intent") if isinstance(desc, dict) else None
                ),
            })
    (out_dir / "03_plan_summary.json").write_text(
        json.dumps(plan_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n[e2e] plan stack: {len(layers)} layer(s)")
    for entry in plan_summary:
        print(
            f"  L{entry['layer']} | "
            f"{entry['agent_id'] or '<no-agent>':24s} | "
            f"step={entry['step_id']} | {entry['status']}"
        )

    # ── 6. Collect each step's executions + media paths ────────────
    all_exec_data: dict[str, Any] = {}
    media_paths: dict[str, str] = {}
    for entry in plan_summary:
        sid = entry["step_id"]
        try:
            execs = _http_get_json(args.backend, f"/api/assistant/executions/step/{sid}")
        except urllib.error.HTTPError as exc:
            print(f"[e2e] step {sid}: HTTP {exc.code} fetching executions")
            continue
        except Exception as exc:
            print(f"[e2e] step {sid}: failed to fetch executions: {exc}")
            continue
        all_exec_data[sid] = execs
        if not isinstance(execs, list):
            continue
        for ex in execs:
            results = ex.get("results") if isinstance(ex, dict) else None
            mf = (results or {}).get("_media_files", {}) if isinstance(results, dict) else {}
            for k, v in (mf or {}).items():
                uri = (
                    v.get("uri") or v.get("path") or v
                ) if isinstance(v, dict) else v
                norm = _normalize_uri(uri)
                if norm:
                    media_paths[k] = norm

    (out_dir / "04_executions.json").write_text(
        json.dumps(all_exec_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (out_dir / "05_media_paths.json").write_text(
        json.dumps(media_paths, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n[e2e] media artifacts ({len(media_paths)}):")
    for k, v in media_paths.items():
        print(f"  {k}: {v}")

    print(f"\n[e2e] DONE.")
    print(f"[e2e]   wrapper meta JSONs : {out_dir}/0[0-5]_*.json")
    print(f"[e2e]   workspace artifacts: see {os.environ.get('FW_WORKSPACE_ROOT', '<_workspaces/...>')}")
    print(f"[e2e]   (backend wrote workspace_global_*/ inside the FW_WORKSPACE_ROOT path; "
          f"all media + JSON artifacts + global_memory.md live there)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
