#!/usr/bin/env python3
"""Bypass director planner — drive plan-stack-backend with locked GT chain.

Pretend the director already produced a perfect chain. Build that chain
directly into plan stack via /api/plan-stack/modify, then walk it step-by-step
through /api/assistant/execute. No replan / retry / skip at the director level
(sub-agent-internal evaluator+rework still runs).

Per case lifecycle:
  1. kill stale backend, clear _workspaces/
  2. start fresh backend (background, FW_USE_REAL_MEDIA_GEN=1)
  3. wait /health
  4. upload user_goal as text/plain → [creative_brief]
  5. upload portrait png if chain has IntakeImageAgent
  6. POST /api/plan-stack/modify (create_steps + create_layers + add_steps_to_layers)
  7. PUT /api/execution-pointer/set {0,0}
  8. for each step: POST /api/assistant/execute → advance pointer
  9. snapshot _workspaces/ → 30_results/storytelling/<case>/_workspace/
 10. kill backend
"""
from __future__ import annotations
import base64
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load .env
env_path = REPO_ROOT / ".env"
for line in env_path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    os.environ.setdefault(k.strip(), v.strip())

import httpx  # noqa: E402

BACKEND_PORT = 5050  # avoid collision with hunyuan driver on 5002-5005
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
BACKEND_DIR = REPO_ROOT / "plan-stack-backend"
WORKSPACES_DIR = REPO_ROOT / "_workspaces"
RESULTS_DIR = REPO_ROOT / "evals" / "sub-agents" / "30_results" / "storytelling"
SELECTION = json.loads((Path(__file__).parent / "selection.json").read_text())
UPLOADS_DIR = Path(__file__).parent / "uploads"

CASES_TO_RUN = ["storytelling_047"]
PER_AGENT_TIMEOUT_SEC = 900  # 15 min per sub-agent execution


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def kill_backend(proc: subprocess.Popen | None = None) -> None:
    """Reliably tear down the backend.

    1. SIGTERM/SIGKILL the Popen we spawned (if known) — this is the
       authoritative way to stop our subprocess.
    2. Belt-and-braces: also kill anything holding port 5002 via fuser, in
       case a stale backend from an earlier session is squatting.
    3. Wait until lsof confirms port 5002 is free, up to 15s.
    """
    if proc is not None and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    # Belt-and-braces: nuke anything still listening on the port (stale
    # backend from earlier session that we didn't spawn).
    for _ in range(15):
        r = subprocess.run(["lsof", "-i", f":{BACKEND_PORT}", "-sTCP:LISTEN", "-t"],
                           capture_output=True, text=True)
        pids = [p for p in r.stdout.strip().split("\n") if p]
        if not pids:
            return
        for pid in pids:
            try:
                subprocess.run(["kill", "-9", pid], check=False, capture_output=True)
            except Exception:
                pass
        time.sleep(1)


def clear_workspaces() -> None:
    if WORKSPACES_DIR.exists():
        for child in WORKSPACES_DIR.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


def start_backend(log_path: Path) -> subprocess.Popen:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(log_path, "w")
    env = {
        **os.environ,
        "FW_USE_REAL_MEDIA_GEN": "1",
        "FW_BACKEND_PORT": str(BACKEND_PORT),
    }
    return subprocess.Popen(
        ["python", "run.py"],
        cwd=str(BACKEND_DIR),
        stdout=log_f, stderr=subprocess.STDOUT,
        env=env,
    )


def wait_health(timeout: int = 60) -> bool:
    t0 = time.time()
    with httpx.Client(timeout=5) as client:
        while time.time() - t0 < timeout:
            try:
                r = client.get(f"{BACKEND_URL}/health")
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)
    return False


def upload_text(client: httpx.Client, text: str) -> dict:
    r = client.post(f"{BACKEND_URL}/api/workspace/upload",
                    json={"mime": "text/plain", "text": text})
    r.raise_for_status()
    return r.json()


def upload_image(client: httpx.Client, image_path: Path) -> dict:
    data = base64.b64encode(image_path.read_bytes()).decode()
    r = client.post(f"{BACKEND_URL}/api/workspace/upload",
                    json={"mime": "image/png", "data_b64": data,
                          "filename": image_path.name})
    r.raise_for_status()
    return r.json()


def build_plan(client: httpx.Client, chain: list[list[str]]) -> list[str]:
    n = len(chain) - 1  # exclude trailing ["done"]
    steps = [
        {"description": {"agent_id": chain[i][0],
                         "intent": f"Run {chain[i][0]} (locked GT chain step {i+1}/{n})"}}
        for i in range(n)
    ]
    layers = [{"layer_index": i} for i in range(n)]
    r = client.post(f"{BACKEND_URL}/api/plan-stack/modify", json={
        "operations": [
            {"type": "create_steps", "params": {"steps": steps}},
            {"type": "create_layers", "params": {"layers": layers}},
        ]
    })
    r.raise_for_status()
    step_ids = r.json()["created_step_ids"]
    additions = [{"layer_index": i, "step_id": step_ids[i]} for i in range(n)]
    r = client.post(f"{BACKEND_URL}/api/plan-stack/modify", json={
        "operations": [
            {"type": "add_steps_to_layers", "params": {"additions": additions}},
        ]
    })
    r.raise_for_status()
    return step_ids


def execute_chain(client: httpx.Client, chain: list[list[str]],
                  step_ids: list[str], case_name: str) -> list[dict]:
    n = len(chain) - 1
    client.put(f"{BACKEND_URL}/api/execution-pointer/set",
               json={"layer_index": 0, "step_index": 0}).raise_for_status()

    log_entries: list[dict] = []
    for i in range(n):
        agent_id = chain[i][0]
        step_id = step_ids[i]
        log(f"  [{case_name}] step {i+1}/{n} {agent_id}…")
        t0 = time.time()
        try:
            r = client.post(f"{BACKEND_URL}/api/assistant/execute",
                            json={"agent_id": agent_id, "step_id": step_id},
                            timeout=PER_AGENT_TIMEOUT_SEC)
            elapsed = time.time() - t0
            if r.status_code != 200:
                log_entries.append({
                    "agent_id": agent_id, "step_id": step_id,
                    "http_status": r.status_code, "body": r.text[:500],
                    "elapsed_sec": elapsed, "status": "HTTP_ERROR",
                })
                log(f"    ✗ HTTP {r.status_code} in {elapsed:.1f}s")
                break
            res = r.json()
            status = res.get("status", "UNKNOWN")
            log_entries.append({
                "agent_id": agent_id, "step_id": step_id, "status": status,
                "elapsed_sec": elapsed, "error": res.get("error"),
            })
            log(f"    → {status} in {elapsed:.1f}s")
            if status != "COMPLETED":
                log(f"    ✗ {status}: {res.get('error', '(no error msg)')[:200]}")
                break
            # Don't advance after the last step — pointer is already at end
            if i < n - 1:
                client.post(f"{BACKEND_URL}/api/execution-pointer/advance").raise_for_status()
        except Exception as e:
            log_entries.append({"agent_id": agent_id, "step_id": step_id,
                                "status": "DRIVER_EXCEPTION", "error": str(e)})
            log(f"    ✗ driver exception: {e}")
            break
    return log_entries


def snapshot_workspace(case_dir: Path) -> None:
    if WORKSPACES_DIR.exists() and any(WORKSPACES_DIR.iterdir()):
        dst = case_dir / "_workspace"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(WORKSPACES_DIR, dst)


def run_one(case: dict) -> None:
    case_name = case["name"]
    case_dir = RESULTS_DIR / case_name
    case_dir.mkdir(parents=True, exist_ok=True)
    log(f"=== {case_name} ===")

    kill_backend()
    clear_workspaces()
    backend_log = case_dir / "backend.log"
    proc = start_backend(backend_log)
    log(f"  backend pid={proc.pid}, log={backend_log}")

    if not wait_health(60):
        log(f"  ✗ backend health failed; aborting {case_name}")
        kill_backend(proc)
        return

    try:
        with httpx.Client(timeout=120) as client:
            log(f"  upload user_goal text")
            upload_text(client, case["user_goal"])

            chain = case["expected_chain"]
            if any("IntakeImageAgent" in layer for layer in chain):
                img = UPLOADS_DIR / f"{case_name}.png"
                log(f"  upload portrait {img.name}")
                upload_image(client, img)

            log(f"  build plan stack — {len(chain)-1} steps")
            step_ids = build_plan(client, chain)
            (case_dir / "plan_stack.json").write_text(
                json.dumps({"chain": chain, "step_ids": step_ids},
                           ensure_ascii=False, indent=2))

            entries = execute_chain(client, chain, step_ids, case_name)
            (case_dir / "execution_log.json").write_text(
                json.dumps(entries, ensure_ascii=False, indent=2))

            ok = sum(1 for e in entries if e.get("status") == "COMPLETED")
            log(f"  done: {ok}/{len(chain)-1} steps COMPLETED")

    except Exception as e:
        log(f"  ✗ case-level error: {e}")
        (case_dir / "case_error.txt").write_text(repr(e))

    finally:
        log(f"  snapshot workspace")
        snapshot_workspace(case_dir)
        kill_backend(proc)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cases = {c["name"]: c for c in SELECTION}
    overall_t0 = time.time()
    for name in CASES_TO_RUN:
        run_one(cases[name])
    log(f"\n=== ALL DONE in {time.time()-overall_t0:.0f}s ===")


if __name__ == "__main__":
    main()
