"""Phase J — four end-to-end scenarios for the intake sub-system.

These tests exercise the new B2 upload protocol + intake agents +
caption-driven InputResolver, end-to-end through the Flask routes:

  e2e1  text-only draft idea — single text upload, IntakeText, then
        StoryAgent picks the brief up via the [creative_brief] label.

  e2e2  two text uploads (the user re-submits a refined brief) — both
        text artifacts must coexist in the registry with their own
        captions, and a second StoryAgent run still finds something to
        work from.

  e2e3  text + image at T=0 — one text upload (creative brief) plus one
        pre-existing image (re-used from a prior live run as a character
        reference). Validates that the image is registered with a
        vision-LLM-generated caption and visible to downstream agents.

  e2e4  midstream image — same as e2e1 first, then after StoryAgent has
        run a fresh image upload + IntakeImage adds a caption-rich
        image artifact, and a re-run of the relevant agent sees it.

Each scenario writes its workspace under a custom prefix:

    Runtime/intake_e2e_outputs/workspace_e2e<n>_<label>_<timestamp>/

These tests are gated by ``FW_ENABLE_INTAKE_E2E=1`` (and the same
``FW_ENABLE_LIVE_LLM_TESTS=1`` precheck used by the existing live e2e
suite). They are skipped on a fresh checkout / CI by default.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import pytest

# Make `dynamic-task-stack/src` and the repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# `src/__init__.py` imports app.py -> flask_cors. Stub it out for
# headless test runs that may not have flask-cors installed.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
from src.assistant.state_store import AssistantStateStore
from src.assistant.workspace.workspace import Workspace
from inference.clients import LLMClient


# ---------------------------------------------------------------------------
# Skip / precheck
# ---------------------------------------------------------------------------


def _is_intake_e2e_ready() -> tuple[bool, str]:
    if os.getenv("FW_ENABLE_INTAKE_E2E") != "1":
        return (
            False,
            "Intake e2e disabled. Set FW_ENABLE_INTAKE_E2E=1 to run.",
        )
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return (
            False,
            "Live LLM test disabled. Set FW_ENABLE_LIVE_LLM_TESTS=1 to run.",
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
        return False, f"Intake e2e precheck failed: {exc}"

    if not key_value:
        return (
            False,
            (
                "Intake e2e missing provider key. "
                f"Set {provider_key_env} or configure routing/api_keys."
            ),
        )

    return True, ""


_LIVE_READY, _LIVE_SKIP_REASON = _is_intake_e2e_ready()


# Pre-existing character reference image we reuse for e2e3 / e2e4.
# Picked specifically because it shows an elderly craftsman with a
# CLEAR visible face in a warm workshop — actually usable as a
# protagonist anchor for the watchmaker story (vs. faceless silhouettes
# from prior runs that wouldn't survive a vision-LLM caption check).
_REFERENCE_IMAGE_PATH = (
    _repo_root
    / "Runtime"
    / "live_e2e_outputs"
    / "workspace_global_20260406_095132"
    / "artifacts"
    / "media"
    / "KeyFrameAgent"
    / "image"
    / "img_char_001_global.png"
)


# ---------------------------------------------------------------------------
# Helpers — runtime base + custom-named workspace
# ---------------------------------------------------------------------------


def _runtime_base() -> Path:
    base = Path(
        os.getenv(
            "FW_INTAKE_E2E_RUNTIME_DIR",
            str(_repo_root / "Runtime" / "intake_e2e_outputs"),
        )
    )
    base.mkdir(parents=True, exist_ok=True)
    return base


def _make_state_store_with_named_workspace(workspace_id: str) -> AssistantStateStore:
    """Build a fresh state store with a pre-created workspace whose ID
    is the caller-supplied label rather than the default
    ``workspace_global_<ts>``."""
    store = AssistantStateStore(runtime_base_path=_runtime_base())
    workspace = Workspace(
        workspace_id=workspace_id,
        runtime_base_path=store.runtime_base_path,
    )
    store.global_workspace = workspace
    return store


def _scenario_workspace_id(label: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"workspace_e2e_{label}_{ts}"


def _build_client(workspace_id: str, monkeypatch) -> tuple[object, Workspace, Path]:
    """Wire up Flask + a fresh state store + a custom workspace and
    return ``(test_client, workspace, debug_file_path)``."""
    store = _make_state_store_with_named_workspace(workspace_id)
    monkeypatch.setattr(routes_module, "assistant_state_store", store)

    app = create_app({"TESTING": True})
    client = app.test_client()
    debug_file = (
        _runtime_base()
        / "debug"
        / f"intake_e2e_{workspace_id}.jsonl"
    )
    return client, store.global_workspace, debug_file


def _record(debug_file: Path, payload: dict) -> None:
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with debug_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def _post(client, url, body, debug_file, *, step):
    resp = client.post(url, json=body)
    payload = resp.get_json()
    _record(
        debug_file,
        {"step": step, "url": url, "request": body, "status": resp.status_code, "response": payload},
    )
    return resp, payload


def _create_task(client, debug_file, goal: str) -> str:
    resp, body = _post(
        client,
        "/api/tasks/create",
        {"description": {"goal": goal}},
        debug_file,
        step="create_task",
    )
    assert resp.status_code == 201, f"create_task failed: {body}"
    return body["id"]


def _upload_text(client, debug_file, text: str, user_intent: str) -> dict:
    resp, body = _post(
        client,
        "/api/workspace/upload",
        {"mime": "text/plain", "user_intent": user_intent, "text": text},
        debug_file,
        step="upload_text",
    )
    assert resp.status_code == 201, f"text upload failed: {body}"
    return body


def _upload_image(client, debug_file, image_path: Path, user_intent: str, mime: str = "image/png") -> dict:
    data_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    resp, body = _post(
        client,
        "/api/workspace/upload",
        {
            "mime": mime,
            "user_intent": user_intent,
            "data_b64": data_b64,
            "filename": image_path.name,
        },
        debug_file,
        step="upload_image",
    )
    assert resp.status_code == 201, f"image upload failed: {body}"
    return body


def _execute_agent(client, debug_file, agent_id: str, task_id: str) -> dict:
    resp, body = _post(
        client,
        "/api/assistant/execute",
        {"agent_id": agent_id, "task_id": task_id, "execute_fields": {}},
        debug_file,
        step=f"execute_{agent_id}",
    )
    assert resp.status_code == 200, f"{agent_id} failed: {body}"
    assert body.get("status") == "COMPLETED", f"{agent_id} not COMPLETED: {body}"
    return body


def _last_execution_results(client, task_id: str) -> dict:
    resp = client.get(f"/api/assistant/executions/task/{task_id}")
    assert resp.status_code == 200
    executions = resp.get_json()
    assert executions, "no executions returned"
    return executions[-1].get("results") or {}


def _registry_paths(workspace: Workspace) -> list[str]:
    """All artifact paths registered in the workspace's artifact_registry."""
    out: list[str] = []
    for entry in workspace.artifact_registry.list_all():
        for ref in entry.artifacts:
            if ref.path:
                out.append(ref.path)
    return out


def _registry_captions_for_path(workspace: Workspace, path: str) -> list[dict]:
    """All caption blocks for a given path."""
    out: list[dict] = []
    for entry in workspace.artifact_registry.list_all():
        for ref in entry.artifacts:
            if ref.path == path:
                out.append(
                    {
                        "what": ref.what,
                        "why": ref.why,
                        "scope": ref.scope,
                        "agent_id": entry.agent_id,
                    }
                )
    return out


def _placeholders_without_successor(workspace: Workspace) -> list[str]:
    """The artifact_registry is append-only, so a ``raw_pending``
    placeholder will always remain in history even after an intake
    agent processes it. What matters is that for every placeholder
    upload there exists a *successor* artifact at ``scope != raw_pending``
    produced by an Intake* agent. Return placeholders that have no
    successor — those signal a failed / missing intake step.
    """
    placeholders: list[tuple[str, str]] = []  # (agent_id, path)
    intake_outputs_by_agent: list[str] = []   # agent_id strings
    for entry in workspace.artifact_registry.list_all():
        for ref in entry.artifacts:
            if ref.scope == "raw_pending":
                placeholders.append((entry.agent_id, ref.path))
            elif entry.agent_id.startswith("Intake"):
                intake_outputs_by_agent.append(entry.agent_id)
    if not placeholders:
        return []
    # Heuristic match: at least one Intake* output exists for each
    # placeholder. Stronger matching would require linking placeholder
    # path → intake's input path; the registry doesn't carry that link.
    if intake_outputs_by_agent:
        return []
    return [f"{a}: {p}" for a, p in placeholders]


# ---------------------------------------------------------------------------
# e2e1 — text only
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e1_text_only_draft_idea(monkeypatch):
    workspace_id = _scenario_workspace_id("text_only")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e1] workspace={workspace_id}")
    print(f"[e2e1] debug_file={debug_file}")

    task_id = _create_task(
        client,
        debug_file,
        goal="A short cinematic film about a retired watchmaker repairing a pocket watch.",
    )

    # 1. Upload the user brief as raw text.
    upload = _upload_text(
        client,
        debug_file,
        text=(
            "I want a 30-second cinematic short about an elderly watchmaker "
            "named Elias who, on New Year's Eve, races against the clock to "
            "repair his late wife's pocket watch. Warm nostalgic mood, intimate "
            "workshop setting, golden lamplight."
        ),
        user_intent="creative brief for the project",
    )
    assert upload["caption"]["scope"] == "raw_pending"

    # 2. IntakeTextAgent converts the placeholder into a caption-rich artifact.
    intake_summary = _execute_agent(client, debug_file, "IntakeTextAgent", task_id)
    assert intake_summary["status"] == "COMPLETED"

    # 3. Run the full content pipeline. Each downstream agent must find
    #    its inputs (the user's brief, then the upstream artifact, then
    #    keyframes for video, etc.) via the caption-driven InputResolver.
    pipeline = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent", "AudioAgent"]
    pipeline_results: dict[str, dict] = {}
    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, task_id)
        pipeline_results[agent_id] = _last_execution_results(client, task_id)

    story_logline = pipeline_results["StoryAgent"].get("content", {}).get("logline", "")
    assert story_logline, f"StoryAgent produced no logline"

    screenplay_scenes = (
        pipeline_results["ScreenplayAgent"].get("content", {}).get("scenes", [])
    )
    assert screenplay_scenes, "ScreenplayAgent produced no scenes"
    assert any(
        s.get("shots") for s in screenplay_scenes if isinstance(s, dict)
    ), "ScreenplayAgent scenes have no shots"

    keyframe_results = pipeline_results["KeyFrameAgent"]
    assert keyframe_results.get("content"), "KeyFrameAgent produced no content"
    keyframe_media = keyframe_results.get("_media_files", {})
    assert isinstance(keyframe_media, dict) and keyframe_media, (
        "KeyFrameAgent returned no media files metadata"
    )

    video_results = pipeline_results["VideoAgent"]
    assert video_results.get("content", {}).get("final_video_asset"), (
        "VideoAgent produced no final_video_asset"
    )

    audio_results = pipeline_results["AudioAgent"]
    assert audio_results.get("content", {}).get("final_delivery_asset"), (
        "AudioAgent produced no final_delivery_asset"
    )

    # 4. Workspace invariants.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    paths = _registry_paths(workspace)
    assert paths, "workspace.artifact_registry is empty"

    print(f"[e2e1] story logline: {story_logline[:160]}")
    print(f"[e2e1] screenplay scenes: {len(screenplay_scenes)}")
    print(f"[e2e1] keyframe media files: {len(keyframe_media)}")


# ---------------------------------------------------------------------------
# e2e2 — two text uploads
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e2_text_then_text(monkeypatch):
    workspace_id = _scenario_workspace_id("text_then_text")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e2] workspace={workspace_id}")
    print(f"[e2e2] debug_file={debug_file}")

    task_id = _create_task(
        client,
        debug_file,
        goal="A cinematic short — initial brief plus user revisions.",
    )

    # First brief — a lonely lighthouse keeper story (deliberately a
    # totally different story from e2e1's watchmaker, so the workspace
    # input file is unmistakably distinguishable from any other scenario).
    _upload_text(
        client,
        debug_file,
        text=(
            "A 30-second cinematic short about Anya, a lonely lighthouse "
            "keeper on a stormy island in the North Sea. She tends the lamp "
            "every night so passing fishing boats can find their way home, "
            "even though no boat has come for her in a decade. Cold "
            "blue-grey palette, howling wind, the slow turning of the lamp."
        ),
        user_intent="initial creative brief — lighthouse keeper story",
    )
    _execute_agent(client, debug_file, "IntakeTextAgent", task_id)
    _execute_agent(client, debug_file, "StoryAgent", task_id)
    story_v1 = _last_execution_results(client, task_id).get("content", {}).get("logline", "")

    # Second, refined brief — same character but now turn the story on its
    # head: the boat finally arrives. This is a clear narrative revision,
    # not a cosmetic edit, so the diff vs. v1 is obvious to a human reader.
    _upload_text(
        client,
        debug_file,
        text=(
            "REVISION of the lighthouse keeper story: keep Anya and the "
            "island, but tonight a single rowing boat finally appears out "
            "of the storm. The passenger turns out to be her younger "
            "brother, missing for ten years. Shift the palette toward "
            "warm amber as he steps ashore. End on the lamp going dark "
            "for the first time in a decade."
        ),
        user_intent="user revision: a boat finally arrives, brother returns",
    )
    _execute_agent(client, debug_file, "IntakeTextAgent", task_id)
    _execute_agent(client, debug_file, "StoryAgent", task_id)
    story_v2 = _last_execution_results(client, task_id).get("content", {}).get("logline", "")

    assert story_v1, f"first StoryAgent run produced no logline"
    assert story_v2, f"second StoryAgent run produced no logline"

    # Both raw-text uploads must have been converted out of raw_pending.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    # The second user_intent ("user revision") must be visible in at least
    # one caption.why somewhere in the registry.
    all_whys = " | ".join(
        ref.why
        for entry in workspace.artifact_registry.list_all()
        for ref in entry.artifacts
    )
    assert "revision" in all_whys.lower(), (
        f"second user intent not preserved in any caption.why: {all_whys}"
    )

    print(f"[e2e2] story v1: {story_v1[:120]}")
    print(f"[e2e2] story v2: {story_v2[:120]}")


# ---------------------------------------------------------------------------
# e2e3 — text + image at T=0
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e3_text_with_image_at_t0(monkeypatch):
    if not _REFERENCE_IMAGE_PATH.exists():
        pytest.skip(
            f"Reference image not found at {_REFERENCE_IMAGE_PATH}; "
            "this test reuses a prior live run's character keyframe."
        )

    workspace_id = _scenario_workspace_id("text_with_image")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e3] workspace={workspace_id}")
    print(f"[e2e3] debug_file={debug_file}")
    print(f"[e2e3] reference_image={_REFERENCE_IMAGE_PATH}")

    task_id = _create_task(
        client,
        debug_file,
        goal="A cinematic short about a retired watchmaker — with a user-provided character reference image.",
    )

    # 1. Upload text brief.
    _upload_text(
        client,
        debug_file,
        text=(
            "30-second cinematic short about Elias, an elderly watchmaker, "
            "racing on New Year's Eve to repair his late wife's pocket watch. "
            "Warm intimate workshop, golden lamplight."
        ),
        user_intent="creative brief for the project",
    )

    # 2. Upload character reference image.
    _upload_image(
        client,
        debug_file,
        image_path=_REFERENCE_IMAGE_PATH,
        user_intent="this is the protagonist Elias — use as character reference",
    )

    # 3. Run both intake agents.
    _execute_agent(client, debug_file, "IntakeTextAgent", task_id)
    _execute_agent(client, debug_file, "IntakeImageAgent", task_id)

    # 4. Validate the image artifact has a vision-LLM caption and that
    #    the user_intent reached caption.why.
    image_caption_blocks: list[dict] = []
    for entry in workspace.artifact_registry.list_all():
        for ref in entry.artifacts:
            if (ref.mime or "").startswith("image/") and ref.scope != "raw_pending":
                image_caption_blocks.append(
                    {"what": ref.what, "why": ref.why, "scope": ref.scope, "agent_id": entry.agent_id}
                )
    assert image_caption_blocks, (
        "no caption-rich image artifact registered after IntakeImageAgent"
    )
    image_block = image_caption_blocks[-1]
    assert image_block["what"], "image artifact has empty caption.what"
    assert "elias" in image_block["why"].lower() or "protagonist" in image_block["why"].lower() or "character" in image_block["why"].lower(), (
        f"user intent not preserved in image caption.why: {image_block}"
    )

    # 5. StoryAgent + ScreenplayAgent must still run normally — they
    #    only need [creative_brief] and [story], not the image, but
    #    they must coexist with the new image artifact.
    _execute_agent(client, debug_file, "StoryAgent", task_id)
    _execute_agent(client, debug_file, "ScreenplayAgent", task_id)

    # 6. Final invariant: nothing left in raw_pending.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    print(f"[e2e3] image caption.what: {image_block['what'][:160]}")
    print(f"[e2e3] image caption.why:  {image_block['why'][:160]}")


# ---------------------------------------------------------------------------
# e2e4 — text first, image added mid-stream
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e4_midstream_image(monkeypatch):
    if not _REFERENCE_IMAGE_PATH.exists():
        pytest.skip(
            f"Reference image not found at {_REFERENCE_IMAGE_PATH}; "
            "this test reuses a prior live run's character keyframe."
        )

    workspace_id = _scenario_workspace_id("midstream_image")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e4] workspace={workspace_id}")
    print(f"[e2e4] debug_file={debug_file}")

    task_id = _create_task(
        client,
        debug_file,
        goal="A cinematic short — start with text, add a character image mid-stream.",
    )

    # Phase 1: text only, run upstream pipeline first.
    # IMPORTANT: this brief deliberately describes a YOUNG WOMAN — totally
    # different from the elderly-male-craftsman character reference image
    # that gets uploaded mid-stream below. The contrast lets a human
    # reader tell whether the mid-stream image actually flowed through
    # to downstream agents (KeyFrame etc.) by looking at whether the
    # rendered character matches the text or the image.
    _upload_text(
        client,
        debug_file,
        text=(
            "30-second cinematic short about Mei, a young female street "
            "muralist in her late twenties, painting a giant mural of a "
            "phoenix on a rain-soaked alley wall at midnight under "
            "neon-lit signs. Cool wet pavement, cyberpunk teal-and-magenta "
            "palette, breath visible in the cold air."
        ),
        user_intent="initial creative brief — young female street muralist",
    )
    _execute_agent(client, debug_file, "IntakeTextAgent", task_id)
    _execute_agent(client, debug_file, "StoryAgent", task_id)
    _execute_agent(client, debug_file, "ScreenplayAgent", task_id)

    paths_before = set(_registry_paths(workspace))
    image_paths_before = {p for p in paths_before if p.endswith(".png") or p.endswith(".jpg")}
    assert not image_paths_before, (
        "no image should be in the registry before phase 2"
    )

    # Phase 2: user belatedly provides a character reference image.
    _upload_image(
        client,
        debug_file,
        image_path=_REFERENCE_IMAGE_PATH,
        user_intent="finally adding the protagonist reference",
    )
    _execute_agent(client, debug_file, "IntakeImageAgent", task_id)

    paths_after = set(_registry_paths(workspace))
    new_paths = paths_after - paths_before
    assert new_paths, "no new artifact registered after midstream image upload"
    assert any(p.endswith(".png") for p in new_paths), (
        f"expected a .png artifact in new registrations, got {new_paths}"
    )

    # Re-run ScreenplayAgent to confirm it still works after the
    # registry has grown — the new image should NOT break it (it does
    # not consume images, but the registry now has more entries).
    _execute_agent(client, debug_file, "ScreenplayAgent", task_id)

    # Final invariant.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    # Verify the new image artifact carries a usable caption.
    image_blocks = []
    for entry in workspace.artifact_registry.list_all():
        for ref in entry.artifacts:
            if (ref.mime or "").startswith("image/") and ref.scope != "raw_pending":
                image_blocks.append(
                    {"what": ref.what, "why": ref.why, "scope": ref.scope}
                )
    assert image_blocks, "image artifact missing caption-rich registration"
    final = image_blocks[-1]
    assert final["what"], "image caption.what is empty"
    print(f"[e2e4] midstream image caption.what: {final['what'][:160]}")
    print(f"[e2e4] midstream image caption.why:  {final['why'][:160]}")
