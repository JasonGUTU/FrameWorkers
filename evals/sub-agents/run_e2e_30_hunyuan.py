#!/usr/bin/env python3
"""Bypass-director e2e driver for the e2e_30 selection over HunyuanVideo backend."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Optional

import httpx

REPO = Path("/home/zhendong_li/FrameWorkers")
sys.path.insert(0, str(REPO))

from director_agent.api_client import BackendAPIClient, BackendAPIError  # noqa: E402
from director_agent.director import _persist_plan  # noqa: E402
from director_agent.router import PlanStepSpec  # noqa: E402

SELECTION = REPO / "evals/sub-agents/e2e_30/selection.json"
UPLOADS = REPO / "evals/sub-agents/e2e_30/uploads"
# Output to /scratch since cephfs home is at write threshold; copy back at end if quota frees.
RESULTS = Path("/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results")
BACKEND_PORT_BASE = 5002
BACKEND_DIR = REPO / "plan-stack-backend"

logger = logging.getLogger("e2e_30")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def category_dir(category): return "creative" if category == "cr" else "intakeimage"


def flatten_chain(expected_chain):
    flat = []
    for layer in expected_chain:
        for ag in layer:
            if ag != "done":
                flat.append(ag)
    return flat


def detect_existing_workspace_id(case_workspace: Path) -> Optional[str]:
    """Return the most-recent ``workspace_global_<TS>`` dir name under
    ``case_workspace`` if one exists with persisted artifacts, else None.

    Used by resume mode so a restarted backend re-attaches to the same
    Workspace and reads the existing global_memory.md (no Story / KF redo).
    """
    if not case_workspace.is_dir():
        return None
    candidates = sorted(case_workspace.glob("workspace_global_*"), reverse=True)
    for cand in candidates:
        if cand.is_dir() and (cand / "global_memory.md").is_file():
            return cand.name
    return None


def has_agent_artifacts(workspace_global_path: Path, agent_id: str) -> bool:
    """True if ``artifacts/<agent_id>/`` has at least one persisted file —
    used to skip re-executing already-done agents in resume mode."""
    agent_dir = workspace_global_path / "artifacts" / agent_id
    if not agent_dir.is_dir():
        return False
    return any(agent_dir.iterdir())


def spawn_backend(port, workspace_root, hunyuan_endpoint, infer_steps, workspace_id=None):
    workspace_root.mkdir(parents=True, exist_ok=True)
    log_path = workspace_root / "_backend.log"
    env = os.environ.copy()
    spill_dir = workspace_root / "video_shots_spill"
    env.update({
        "FW_USE_REAL_MEDIA_GEN": "1",
        "FW_VIDEO_BACKEND": "hunyuan",
        "HUNYUAN_VIDEO_ENDPOINT_URL": hunyuan_endpoint,
        "HUNYUAN_VIDEO_INFER_STEPS": str(infer_steps),
        "FW_WORKSPACE_ROOT": str(workspace_root),
        # Per-shot eager spill: each Hunyuan i2v output lands here immediately,
        # so partial work survives even if a later shot times out / fails.
        "FW_VIDEO_SHOT_SPILL_DIR": str(spill_dir),
        "PYTHONUNBUFFERED": "1",
    })
    if workspace_id:
        # Resume mode: backend re-attaches to existing workspace_global_<TS>
        # so global_memory.md + artifacts from prior run are reused.
        env["FW_WORKSPACE_ID"] = workspace_id
    runner_src = (
        "import sys\nsys.path.insert(0, \"/home/zhendong_li/FrameWorkers/plan-stack-backend\")\n"
        "from src.app import create_app\n"
        "app = create_app()\n"
        f"app.run(host='0.0.0.0', port={port}, debug=False, use_reloader=False)\n"
    )
    runner_path = workspace_root / "_run_inline.py"
    runner_path.write_text(runner_src)
    log_f = open(log_path, "w")
    return subprocess.Popen(
        [sys.executable, str(runner_path)],
        cwd=str(BACKEND_DIR), env=env, stdout=log_f, stderr=subprocess.STDOUT,
    )


async def wait_url_ready(url, timeout=600.0):
    deadline = time.time() + timeout
    async with httpx.AsyncClient() as c:
        while time.time() < deadline:
            try:
                r = await c.get(url, timeout=3)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(3)
    return False


async def wait_hunyuan_ready(endpoint, timeout=1200.0):
    deadline = time.time() + timeout
    async with httpx.AsyncClient() as c:
        while time.time() < deadline:
            try:
                r = await c.get(f"{endpoint}/health", timeout=3)
                if r.status_code == 200 and r.json().get("ok"):
                    return True
            except Exception:
                pass
            await asyncio.sleep(5)
    return False


def _reset_plan_stack(client):
    try:
        layers = client.get_plan_stack()
    except Exception:
        return
    if not layers:
        return
    layer_indices = [l.get("layer_index") for l in layers if l.get("layer_index") is not None]
    if not layer_indices:
        return
    try:
        client.modify_plan_stack([{"type": "delete_layers", "params": {"layer_indices": layer_indices}}])
    except Exception as exc:
        logger.warning("delete_layers failed: %s", exc)


async def run_case(case, backend_url, hunyuan_endpoint, infer_steps, workspace_root):
    name = case["name"]
    category = case["category"]
    user_goal = case["user_goal"]
    expected_chain = case["expected_chain"]
    chain = flatten_chain(expected_chain)
    out_dir = RESULTS / category_dir(category) / name
    out_dir.mkdir(parents=True, exist_ok=True)
    final_marker = out_dir / "00_done.json"
    if final_marker.is_file():
        return {"name": name, "status": "SKIPPED_PRIOR_DONE"}
    log_path = out_dir / "00_run.log"
    log_f = open(log_path, "w")

    def lp(msg):
        ts = time.strftime("%H:%M:%S")
        log_f.write(f"[{ts}] {msg}\n"); log_f.flush()
        logger.info("[%s] %s", name, msg)

    config = {
        "case_name": name, "category": category, "user_goal": user_goal,
        "expected_chain": expected_chain, "flat_chain": chain,
        "backend_url": backend_url, "hunyuan_endpoint": hunyuan_endpoint,
        "infer_steps": infer_steps, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (out_dir / "00_run_config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    case_t0 = time.time()
    lp(f"START case={name} cat={category} chain={chain}")
    lp(f"  backend={backend_url}  hunyuan={hunyuan_endpoint}  steps={infer_steps}")

    # Resume detection: re-using prior workspace?
    existing_ws_id = detect_existing_workspace_id(workspace_root)
    workspace_global_path = (workspace_root / existing_ws_id) if existing_ws_id else None
    is_resume = bool(workspace_global_path and (workspace_global_path / "artifacts").is_dir())
    if is_resume:
        lp(f"  [resume] re-attaching to {existing_ws_id}; will skip steps with existing artifacts")

    try:
        client = BackendAPIClient(base_url=backend_url, timeout=43200.0)
        _reset_plan_stack(client)

        if category == "intake_img" and not is_resume:
            img_path = UPLOADS / f"{name}.png"
            if not img_path.is_file():
                lp(f"FATAL: image not found at {img_path}")
                return {"name": name, "status": "FAIL_NO_IMAGE"}
            img_bytes = img_path.read_bytes()
            async with httpx.AsyncClient(timeout=60) as ac:
                up = await ac.post(
                    f"{backend_url}/api/workspace/upload",
                    json={"mime": "image/png",
                          "data_b64": base64.b64encode(img_bytes).decode("ascii"),
                          "filename": f"{name}.png"},
                )
                up.raise_for_status()
                upload_resp = up.json()
            (out_dir / "01_upload_response.json").write_text(json.dumps(upload_resp, indent=2, ensure_ascii=False), encoding="utf-8")
            lp(f"  uploaded {img_path.name} ({len(img_bytes)//1024}KB)")

        if not is_resume:
            try:
                msg = client.create_message(content=user_goal, sender_type="user")
                lp(f"  chat msg id={msg.get('id', '?')}")
            except Exception as exc:
                lp(f"FATAL: create_message failed: {exc}")
                return {"name": name, "status": "FAIL_CHAT", "error": str(exc)}

        plan = [PlanStepSpec(agent_id=ag, intent=f"e2e_30 step {i+1}/{len(chain)}: {ag}")
                for i, ag in enumerate(chain)]
        step_ids = _persist_plan(client, plan=plan, rationale=f"e2e_30 bypass-director: {name}")
        if not step_ids or len(step_ids) != len(plan):
            lp(f"FATAL: persist_plan returned {len(step_ids) if step_ids else 0} ids, expected {len(plan)}")
            return {"name": name, "status": "FAIL_PERSIST_PLAN"}
        lp(f"  plan persisted: {len(step_ids)} steps")

        step_results = []
        for idx, (step_id, agent_id) in enumerate(zip(step_ids, chain)):
            step_t0 = time.time()
            # Resume skip: agent already produced artifacts on a prior run.
            # Mark the new plan-step COMPLETED + advance pointer; InputResolver
            # picks up the prior artifacts via global_memory.md captions.
            if is_resume and has_agent_artifacts(workspace_global_path, agent_id):
                lp(f"  step {idx+1}/{len(chain)}: {agent_id} -> SKIP (artifact present, resume)")
                try: client.update_step_status(step_id=step_id, status="COMPLETED")
                except Exception: pass
                try: client.advance_execution_pointer()
                except Exception: pass
                step_results.append({"agent_id": agent_id, "step_id": step_id, "ok": True,
                                     "error": None, "elapsed_sec": 0.0, "skipped_resume": True})
                continue
            lp(f"  step {idx+1}/{len(chain)}: {agent_id} ...")
            ok = False; err = None
            try:
                client.execute_agent(agent_id=agent_id, step_id=step_id)
                ok = True
            except Exception as exc:
                err = f"{type(exc).__name__}: {exc}"
            elapsed = time.time() - step_t0
            if ok:
                lp(f"    OK {agent_id} done in {elapsed:.1f}s")
                try: client.update_step_status(step_id=step_id, status="COMPLETED")
                except Exception: pass
            else:
                lp(f"    FAIL {agent_id} in {elapsed:.1f}s: {err}")
                try: client.update_step_status(step_id=step_id, status="FAILED")
                except Exception: pass
            try: client.advance_execution_pointer()
            except Exception: pass
            step_results.append({"agent_id": agent_id, "step_id": step_id, "ok": ok, "error": err, "elapsed_sec": elapsed})

        case_elapsed = time.time() - case_t0
        all_ok = all(s["ok"] for s in step_results)
        (out_dir / "02_step_results.json").write_text(json.dumps(step_results, indent=2, ensure_ascii=False), encoding="utf-8")

        # Copy artifacts from workspace -> per-case artifacts/ dir. Mirror the
        # entire workspace_global_<TS>/artifacts/ subtree so resume-skipped
        # agents (whose step_ids don't match this run's _persist_plan output)
        # are also captured. Backend's per-case workspace is already isolated
        # to this case, so a tree copy is correct (no cross-case pollution).
        case_artifacts_dir = out_dir / "artifacts"
        case_artifacts_dir.mkdir(exist_ok=True)
        copied_count = 0
        ws_globals = sorted(workspace_root.glob("workspace_global_*"))
        for ws_global in ws_globals:
            ws_artifacts = ws_global / "artifacts"
            if not ws_artifacts.is_dir():
                continue
            target_root = case_artifacts_dir / ws_global.name / "artifacts"
            for f in ws_artifacts.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    rel = f.relative_to(ws_artifacts)
                    dest = target_root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    copied_count += 1
                except Exception:
                    pass
            # also copy the global_memory.md captions index for traceability
            gm = ws_global / "global_memory.md"
            if gm.is_file():
                try:
                    shutil.copy2(gm, case_artifacts_dir / ws_global.name / "global_memory.md")
                except Exception:
                    pass
        lp(f"  copied {copied_count} artifacts to {case_artifacts_dir}")

        try:
            mp4s = sorted(workspace_root.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            if mp4s:
                shutil.copy2(mp4s[0], out_dir / "final.mp4")
                lp(f"  copied {mp4s[0].name} -> final.mp4")
        except Exception as exc:
            lp(f"  (warn) mp4 copy failed: {exc}")

        lp(f"END case={name} elapsed={case_elapsed:.1f}s all_ok={all_ok}")
        final_marker.write_text(json.dumps({
            "case_name": name, "all_ok": all_ok, "elapsed_sec": case_elapsed,
            "n_steps": len(chain), "n_succeeded": sum(1 for s in step_results if s["ok"]),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=2), encoding="utf-8")
        return {"name": name, "status": "DONE" if all_ok else "PARTIAL", "elapsed_sec": case_elapsed}

    except Exception as exc:
        lp(f"FATAL CASE EXCEPTION: {type(exc).__name__}: {exc}")
        log_f.write(traceback.format_exc() + "\n"); log_f.flush()
        return {"name": name, "status": "FAIL_EXCEPTION", "error": str(exc)}
    finally:
        log_f.close()


async def worker(worker_id, bucket, backend_port, hunyuan_endpoint, infer_steps):
    """Spawn per-case backend so each case has isolated workspace inside its own dir."""
    logger.info("[w%d] starting bucket=%s on hunyuan=%s port=%d",
                worker_id, [c["name"] for c in bucket], hunyuan_endpoint, backend_port)
    results = []
    backend_url = f"http://localhost:{backend_port}"
    for case in bucket:
        case_dir = RESULTS / category_dir(case["category"]) / case["name"]
        case_dir.mkdir(parents=True, exist_ok=True)
        # Race-safety: skip if marker already written (another worker / sub-driver finished it).
        final_marker = case_dir / "00_done.json"
        if final_marker.is_file():
            logger.info("[w%d] case %s -> SKIPPED_PRIOR_DONE (marker present, before workspace prep)", worker_id, case["name"])
            results.append({"name": case["name"], "status": "SKIPPED_PRIOR_DONE"})
            continue
        # Race-safety: skip if another live worker holds the case lock.
        lock_file = case_dir / ".running_lock"
        if lock_file.is_file():
            try:
                holder_pid = lock_file.read_text().strip()
            except Exception:
                holder_pid = ""
            if holder_pid.isdigit() and Path(f"/proc/{holder_pid}").exists():
                logger.warning("[w%d] case %s -> SKIPPED_LOCKED by PID %s", worker_id, case["name"], holder_pid)
                results.append({"name": case["name"], "status": "SKIPPED_LOCKED", "holder_pid": holder_pid})
                continue
        lock_file.write_text(str(os.getpid()))
        case_workspace = case_dir / "_workspace"
        # Resume detection: if existing workspace_global_<TS> dir has
        # global_memory.md, re-attach via FW_WORKSPACE_ID and skip wipe so
        # prior Story / Screenplay / KeyFrame artifacts survive.
        existing_ws_id = detect_existing_workspace_id(case_workspace)
        if existing_ws_id:
            logger.info("[w%d] case %s -> RESUME (workspace_id=%s)",
                        worker_id, case["name"], existing_ws_id)
        else:
            if case_workspace.exists():
                shutil.rmtree(case_workspace)
            case_workspace.mkdir(parents=True)
        # Spawn fresh backend for this case
        proc = spawn_backend(port=backend_port, workspace_root=case_workspace,
                             hunyuan_endpoint=hunyuan_endpoint, infer_steps=infer_steps,
                             workspace_id=existing_ws_id)
        # Wait backend ready
        ready = await wait_url_ready(f"{backend_url}/api/plan-stack", timeout=60)
        if not ready:
            logger.error("[w%d] backend %d failed to start for %s", worker_id, backend_port, case["name"])
            try: proc.send_signal(signal.SIGTERM)
            except Exception: pass
            results.append({"name": case["name"], "status": "FAIL_BACKEND_START"})
            continue
        try:
            result = await asyncio.to_thread(_run_case_sync_wrapper, case, backend_url, hunyuan_endpoint, infer_steps, case_workspace)
        finally:
            try: proc.send_signal(signal.SIGTERM)
            except Exception: pass
            try: proc.wait(timeout=10)
            except Exception:
                try: proc.kill()
                except Exception: pass
            try: lock_file.unlink(missing_ok=True)
            except Exception: pass
        results.append(result)
        logger.info("[w%d] case %s -> %s", worker_id, case["name"], result.get("status"))
    return results


def _run_case_sync_wrapper(case, backend_url, hunyuan_endpoint, infer_steps, workspace_root):
    return asyncio.run(run_case(case, backend_url, hunyuan_endpoint, infer_steps, workspace_root))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hunyuan-endpoints", required=True)
    ap.add_argument("--infer-steps", type=int, default=50)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--case", default=None)
    ap.add_argument("--case-names", default=None,
                    help="Explicit comma-separated list of case names to run")
    ap.add_argument("--backend-port-base", type=int, default=BACKEND_PORT_BASE,
                    help="Per-worker backend ports = base + worker_idx. Sub-drivers MUST pass a unique base to avoid port collision with the main driver (5002-5005).")
    return ap.parse_args()


async def main():
    args = parse_args()
    global RESULTS
    if args.smoke:
        RESULTS = Path("/home/zhendong_li/FrameWorkers/evals/sub-agents/30_results_smoke")
        logger.info("[smoke] redirecting output to %s", RESULTS)

    endpoints = [e.strip().rstrip("/") for e in args.hunyuan_endpoints.split(",") if e.strip()]
    num_gpus = len(endpoints)
    if num_gpus < 1:
        logger.error("No hunyuan endpoints provided"); return 2
    logger.info("Using %d hunyuan endpoint(s)", num_gpus)

    all_cases = json.loads(SELECTION.read_text(encoding="utf-8"))
    target = [c for c in all_cases if c["category"] in ("cr", "intake_img")]
    if args.case:
        target = [c for c in target if args.case in c["name"]]
    if args.case_names:
        wanted = set(n.strip() for n in args.case_names.split(",") if n.strip())
        target = [c for c in target if c["name"] in wanted]
        logger.info("[--case-names filter] kept %d cases: %s", len(target), [c["name"] for c in target])
    if args.smoke:
        cr_first = next((c for c in target if c["category"] == "cr"), None)
        ii_first = next((c for c in target if c["category"] == "intake_img"), None)
        target = [c for c in (cr_first, ii_first) if c is not None]
    logger.info("Target cases (%d):", len(target))
    for c in target:
        logger.info("  - %s [%s]", c["name"], c["category"])

    buckets = [[] for _ in range(num_gpus)]
    for i, c in enumerate(target):
        buckets[i % num_gpus].append(c)
    for i, b in enumerate(buckets):
        logger.info("  bucket %d (n=%d): %s", i, len(b), [c["name"] for c in b])

    # Workers spawn their own per-case backend; just wait for hunyuan endpoints to be ready.
    logger.info("Waiting for %d hunyuan endpoints ready ...", num_gpus)
    ready = await asyncio.gather(
        *[wait_hunyuan_ready(ep) for ep in endpoints],
        return_exceptions=True,
    )
    if not all(r is True for r in ready):
        logger.error("Not all hunyuan ready: %s", ready)
    logger.info("Hunyuan readiness: %s", ready)

    all_results = await asyncio.gather(
        *[worker(i, buckets[i], args.backend_port_base + i, endpoints[i], args.infer_steps)
          for i in range(num_gpus)],
        return_exceptions=True,
    )

    summary_path = RESULTS / f"00_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hunyuan_endpoints": endpoints, "infer_steps": args.infer_steps,
        "results_per_worker": [r if not isinstance(r, Exception) else {"error": str(r)} for r in all_results],
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Summary -> %s", summary_path)

    flat_results = [r for ws in all_results if not isinstance(ws, Exception) for r in ws]
    n_done = sum(1 for r in flat_results if r.get("status") == "DONE")
    n_partial = sum(1 for r in flat_results if r.get("status") == "PARTIAL")
    n_fail = sum(1 for r in flat_results if r.get("status", "").startswith("FAIL"))
    logger.info("Final: DONE=%d PARTIAL=%d FAIL=%d / %d", n_done, n_partial, n_fail, len(flat_results))
    return 0 if (n_done + n_partial == len(flat_results)) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
