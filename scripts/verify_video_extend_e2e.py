"""Ad-hoc real-run verifier for VideoExtendAgent.

Seeds a mock video artifact + a user creative_brief JSON artifact
(matches the shape workspace.persist_raw_upload's text/plain branch
registers at scope=global; IntakeTextAgent was retired 2026-04-23),
calls POST /api/assistant/execute, then prints every non-trivial piece
of the execution so we can eyeball the full chain end-to-end:

  * resolved continuation_description fed into the LLM
  * raw LLM-planned extension_spec (continuation_prompt, motion, duration)

Usage:
    source .env
    # LLM-only: Mock video service, no fal credits
    FW_ENABLE_LIVE_LLM_TESTS=1 python scripts/verify_video_extend_e2e.py
    # Full pipeline: real Kling video generation (costs fal credits, ~1-3 min)
    FW_ENABLE_LIVE_LLM_TESTS=1 FW_USE_REAL_MEDIA_GEN=1 python scripts/verify_video_extend_e2e.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import types
from datetime import datetime
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
_pkg_root = _repo_root / "plan-stack-backend"
for p in [str(_repo_root), str(_pkg_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from inference.config.config_loader import ConfigLoader
for fname in (".env", ".env.example"):
    p = _repo_root / fname
    if p.is_file():
        ConfigLoader.load_env_file(str(p), override=False)

if "flask_cors" not in sys.modules:
    fc = types.ModuleType("flask_cors")
    fc.CORS = lambda *a, **kw: None
    sys.modules["flask_cors"] = fc

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from src.assistant.workspace.workspace import Workspace
from src.assistant.workspace.models import ArtifactRef


_MOCK_MP4 = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"


def _use_real_media_gen() -> bool:
    return os.getenv("FW_USE_REAL_MEDIA_GEN", "").strip().lower() in ("1", "true", "yes")


def _real_tiny_mp4() -> bytes:
    """Synthesize a 3s 512x512 @ 24fps testsrc mp4 via ffmpeg.

    Needs to be (a) well-formed enough for fal.ai upload, (b) long enough
    and high-enough-fps that ``-sseof -0.1`` can seek to a real last frame,
    and (c) large enough that Kling's I2V pipeline accepts the extracted
    keyframe resolution. A 1s 16x16 black clip fails all three — in
    particular, ffmpeg's ``-sseof -0.1`` on a 1s / 1fps clip yields
    nothing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        path = tmp.name
    try:
        subprocess.run(
            ["ffmpeg", "-y",
             "-f", "lavfi", "-i", "testsrc=size=512x512:rate=24:duration=3",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
            check=True, capture_output=True,
        )
        with open(path, "rb") as f:
            return f.read()
    finally:
        if os.path.isfile(path):
            os.unlink(path)


def _seed_video_bytes() -> bytes:
    return _real_tiny_mp4() if _use_real_media_gen() else _MOCK_MP4


def _runtime_base() -> Path:
    b = _repo_root / "Runtime" / "verify_video_extend"
    b.mkdir(parents=True, exist_ok=True)
    return b


def _make_env():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ws_id = f"VideoExtendVerify_{ts}"
    store = AssistantStateStore(runtime_base_path=_runtime_base())
    workspace = Workspace(workspace_id=ws_id, runtime_base_path=store.runtime_base_path)
    store.global_workspace = workspace
    routes_module.assistant_state_store = store
    app = create_app({"TESTING": True})
    return app.test_client(), workspace


def _ws_path(ws: Workspace) -> Path:
    return ws.runtime_base_path / ws.id


def _seed_file(ws: Workspace, agent_id: str, filename: str, data: bytes,
               caption: str, mime: str, scope: str = "global"):
    art_dir = _ws_path(ws) / "artifacts" / agent_id
    art_dir.mkdir(parents=True, exist_ok=True)
    fpath = art_dir / filename
    fpath.write_bytes(data)
    ws.global_memory.register(
        agent_id=agent_id,
        execution_id=f"seed_{agent_id.lower()}",
        step_id="seed",
        artifacts=[ArtifactRef(caption=caption, scope=scope, path=str(fpath), mime=mime)],
    )
    return str(fpath)


def _seed_json(ws: Workspace, agent_id: str, payload: dict, caption: str):
    art_dir = _ws_path(ws) / "artifacts" / agent_id
    art_dir.mkdir(parents=True, exist_ok=True)
    fpath = art_dir / f"seed_{agent_id.lower()}.json"
    fpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    ws.global_memory.register(
        agent_id=agent_id,
        execution_id=f"seed_{agent_id.lower()}",
        step_id="seed",
        artifacts=[ArtifactRef(
            caption=caption, scope="global", path=str(fpath), mime="application/json",
        )],
    )


def main() -> int:
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        print("Set FW_ENABLE_LIVE_LLM_TESTS=1 (and source .env) before running.")
        return 2

    real = _use_real_media_gen()
    print(f"[config] FW_USE_REAL_MEDIA_GEN={'1' if real else '0'} → "
          f"{'real Kling video generation' if real else 'MockVideoService (no fal credits)'}")

    simulate_intake = os.getenv("FW_SIMULATE_INTAKE_OUTPUT", "").strip().lower() in ("1", "true", "yes")
    print(f"[config] FW_SIMULATE_INTAKE_OUTPUT={'1' if simulate_intake else '0'} → "
          f"{'will add IntakeVideoAgent JSON snapshot alongside raw mp4 (mimics real production post-Intake registry state)' if simulate_intake else 'only raw mp4 seeded (no Intake snapshot competition)'}")

    client, ws = _make_env()

    # Condition 1: raw mp4 as user-uploaded it. Use the real workspace.py caption
    # format (scope=raw_pending, mime=video/mp4) when simulating Intake, because
    # that's what `persist_raw_upload` actually writes.
    if simulate_intake:
        mp4_path = _seed_file(
            ws, "user", "final.mp4", _seed_video_bytes(),
            "Raw user upload (mime=video/mp4). Pending intake processing — only visible to Intake* agents.",
            "video/mp4", scope="raw_pending",
        )
        # Condition 2: IntakeVideoAgent JSON snapshot — exact shape ArtifactWriter
        # would produce, exact caption build_captions returns.
        _seed_json(
            ws, "IntakeVideoAgent",
            {
                "meta": {"asset_type": "", "schema_version": "0.3",
                         "created_by_agent": "IntakeVideoAgent", "language": "en"},
                "content": {
                    "visual_summary": "Astronaut in white suit reaching toward a glowing blue crystal in a cave.",
                    "video_asset": {"asset_id": "", "uri": mp4_path, "format": "mp4"},
                },
            },
            "User-uploaded video reference. Available for downstream agents.",
        )
    else:
        _seed_file(
            ws, "VideoAgent", "final.mp4", _seed_video_bytes(),
            "Video clip ending with astronaut reaching toward glowing crystal",
            "video/mp4",
        )

    user_instruction = (
        "Extend the clip by 5 seconds: the astronaut picks up the crystal "
        "and holds it to the light."
    )
    _seed_json(
        ws, "user",
        {"content": {"text": user_instruction}, "metrics": {"char_count": len(user_instruction)}},
        "Structured metadata document (JSON) for a user-submitted text brief. "
        "Payload carries the raw text verbatim. Pipeline entry point — "
        "consumed by story / screenplay / narration agents.",
    )

    resp = client.post(
        "/api/plan-stack/modify",
        json={
            "operations": [
                {
                    "type": "create_steps",
                    "params": {
                        "steps": [{"description": {"goal": "Extend video clip"}}]
                    },
                }
            ]
        },
    )
    assert resp.status_code == 200, resp.status_code
    step_id = resp.get_json()["created_step_ids"][0]

    resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "VideoExtendAgent", "step_id": step_id},
    )
    body = resp.get_json() or {}

    print("\n" + "=" * 80)
    print("[seed] user_instruction:")
    print(f"    {user_instruction!r}")
    print("\n[response] top-level keys:", sorted(body.keys()))
    print("\n[response] status:", body.get("status"))

    print("\n[response] full JSON:")
    print(json.dumps(body, ensure_ascii=False, indent=2))

    if body.get("status") != "COMPLETED":
        return 1

    # Verify the materialized video on disk
    uri = (((body.get("results") or {}).get("content") or {})
           .get("output_video") or {}).get("uri", "")
    if uri and Path(uri).is_file():
        size = Path(uri).stat().st_size
        print(f"\n[media] materialized video: {uri}")
        print(f"[media] size: {size} bytes ({size / 1024:.1f} KB)")
        if real:
            min_real = 50_000
            if size < min_real:
                print(f"[media] WARNING: size < {min_real} — not a real Kling clip?")
                return 1
            print(f"[media] OK — well above MockVideoService's 28-byte placeholder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
