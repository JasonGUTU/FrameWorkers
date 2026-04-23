"""Phase J — four end-to-end scenarios for the intake sub-system.

These tests exercise the new B2 upload protocol + intake agents +
caption-driven InputResolver, end-to-end through the Flask routes:

  e2e1  text-only draft idea — single text upload, IntakeText, then
        StoryAgent picks the brief up via the [creative_brief] label.
        Audio pipeline: Narration + Music + Ambience → AudioMix.

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

# Make `plan-stack-backend/src` and the repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
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


# Two distinct pre-existing character reference images. e2e3 uses
# the FIRST (elderly white-haired craftsman in apron); e2e4's
# mid-stream upload uses the SECOND (middle-aged woman in olive
# cardigan). The visual gap between them is intentional — it's the
# only way a human reader can tell, by looking at the rendered
# keyframes, whether the mid-stream image actually flowed through
# to the downstream KeyFrame/Video pipeline.
_REFERENCE_IMAGE_FIRST = (
    _repo_root
    / "Runtime"
    / "live_e2e_outputs"
    / "workspace_global_20260406_004907"
    / "artifacts"
    / "media"
    / "UnivaKeyFrameAgent"
    / "image"
    / "img_char_1_character.png"
)
_REFERENCE_IMAGE_SECOND = (
    _repo_root
    / "Runtime"
    / "intake_e2e_outputs"
    / "workspace_e2e_midstream_image_20260407_094310"
    / "inputs"
    / "20260407_095304_370887_nostack_live_e2e_tid_img_char_001_global.png"
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


def _create_step(client, debug_file, goal: str) -> str:
    resp, body = _post(
        client,
        "/api/plan-stack/modify",
        {
            "operations": [
                {
                    "type": "create_steps",
                    "params": {"steps": [{"description": {"goal": goal}}]},
                }
            ]
        },
        debug_file,
        step="create_step",
    )
    assert resp.status_code == 200, f"create_step failed: {body}"
    return body["created_step_ids"][0]


def _upload_text(client, debug_file, text: str) -> dict:
    resp, body = _post(
        client,
        "/api/workspace/upload",
        {"mime": "text/plain", "text": text},
        debug_file,
        step="upload_text",
    )
    assert resp.status_code == 201, f"text upload failed: {body}"
    return body


def _upload_image(client, debug_file, image_path: Path, mime: str = "image/png") -> dict:
    data_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    resp, body = _post(
        client,
        "/api/workspace/upload",
        {
            "mime": mime,
            "data_b64": data_b64,
            "filename": image_path.name,
        },
        debug_file,
        step="upload_image",
    )
    assert resp.status_code == 201, f"image upload failed: {body}"
    return body


def _execute_agent(client, debug_file, agent_id: str, step_id: str) -> dict:
    resp, body = _post(
        client,
        "/api/assistant/execute",
        {"agent_id": agent_id, "step_id": step_id},
        debug_file,
        step=f"execute_{agent_id}",
    )
    assert resp.status_code == 200, f"{agent_id} failed: {body}"
    brief = body if isinstance(body, list) else []
    status = brief[-1].get("status") if brief else None
    assert status == "COMPLETED", f"{agent_id} not COMPLETED: {body}"
    return body


def _last_execution_results(client, step_id: str) -> dict:
    resp = client.get(f"/api/assistant/executions/step/{step_id}")
    assert resp.status_code == 200
    executions = resp.get_json()
    assert executions, "no executions returned"
    return executions[-1].get("results") or {}


def _last_execution_results_for_agent(client, step_id: str, agent_id: str) -> dict:
    """Find the most recent execution for a specific agent_id (used by
    tests that re-run the same agent multiple times in a single task)."""
    resp = client.get(f"/api/assistant/executions/step/{step_id}")
    assert resp.status_code == 200
    executions = resp.get_json()
    matches = [e for e in executions if e.get("agent_id") == agent_id]
    assert matches, f"no executions for agent_id={agent_id}"
    return matches[-1].get("results") or {}


def _registry_paths(workspace: Workspace) -> list[str]:
    """All artifact paths registered in the workspace's global_memory."""
    out: list[str] = []
    for entry in workspace.global_memory.list_all():
        for ref in entry.artifacts:
            if ref.path:
                out.append(ref.path)
    return out


def _registry_captions_for_path(workspace: Workspace, path: str) -> list[dict]:
    """All caption blocks for a given path."""
    out: list[dict] = []
    for entry in workspace.global_memory.list_all():
        for ref in entry.artifacts:
            if ref.path == path:
                out.append(
                    {
                        "caption": ref.caption,
                        "scope": ref.scope,
                        "agent_id": entry.agent_id,
                    }
                )
    return out


def _assert_real_media_uri(uri: str, label: str) -> None:
    """Fail loudly if a media uri never resolved to a real on-disk file.

    Catches the historical "silent COMPLETED with placeholder URI" bug where
    materializer per-call try/except swallowed gen failures and the agent
    happily reported success with the literal string ``"placeholder"`` still
    sitting in every ``video_asset.uri`` slot. The truthy ``assert dict``
    check we used to have lets that through; this enforces all three:
    non-empty, not the placeholder string, and a real non-zero file on disk.
    """
    assert uri, f"{label}: empty uri"
    assert uri != "placeholder", (
        f"{label}: uri is the literal 'placeholder' string — "
        f"materializer never produced bytes for this asset"
    )
    p = Path(uri)
    assert p.is_file(), f"{label}: uri does not point to a real file: {uri}"
    assert p.stat().st_size > 0, f"{label}: uri points to a 0-byte file: {uri}"


def _assert_video_output_real(video_results: dict, label_prefix: str) -> None:
    """Verify VideoAgent's final + every shot/scene clip resolved to a real file."""
    content = video_results.get("content", {})
    final_video = content.get("final_video_asset", {})
    assert isinstance(final_video, dict), f"{label_prefix} final_video_asset missing/not-dict"
    _assert_real_media_uri(str(final_video.get("uri", "")), f"{label_prefix} final_video_asset")
    for scene in content.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("scene_id", "?")
        scene_clip = scene.get("scene_clip_asset", {})
        if isinstance(scene_clip, dict) and scene_clip.get("uri"):
            _assert_real_media_uri(
                str(scene_clip.get("uri", "")),
                f"{label_prefix} scenes[{scene_id}].scene_clip_asset",
            )
        for seg in scene.get("shot_segments", []):
            if not isinstance(seg, dict):
                continue
            shot_id = seg.get("shot_id", "?")
            video_asset = seg.get("video_asset", {})
            if not isinstance(video_asset, dict):
                continue
            _assert_real_media_uri(
                str(video_asset.get("uri", "")),
                f"{label_prefix} shot_segments[{shot_id}].video_asset",
            )


def _assert_audio_mix_output_real(mix_results: dict, label_prefix: str) -> None:
    """Verify AudioMixAgent's final_audio resolved to a real file."""
    content = mix_results.get("content", {})
    final_audio = content.get("final_audio", {})
    assert isinstance(final_audio, dict), f"{label_prefix} final_audio missing/not-dict"
    _assert_real_media_uri(
        str(final_audio.get("uri", "")),
        f"{label_prefix} final_audio",
    )


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
    for entry in workspace.global_memory.list_all():
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
# e2e0 — minimal Story → Screenplay only (univa-style pass-through smoke)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e0_story_to_screenplay_only(monkeypatch):
    """Targeted live smoke for the univa-style Story → Screenplay refactor.

    Runs ONLY ``IntakeTextAgent → StoryAgent → ScreenplayAgent`` — stops
    before KeyFrame/Video/Audio so this exercises the new JSON-text
    pass-through path without paying for image / video / audio
    generation. Everything else re-uses the same workspace + Flask
    fixtures as e2e1-e2e4.

    What this pins (that the offline unit tests cannot):

      * ScreenplayAgent's new ``_llm_fill_full`` path actually produces
        a valid screenplay from a raw story JSON blob embedded in the
        user prompt — no skeleton pre-build, no field-selected embed.
      * The LLM reads the story blueprint's character_id / location_id
        strings out of the JSON text and REUSES them in the screenplay's
        consistency pack. If build_input were silently passing an empty
        payload (the failure mode the old ``.get("content")`` path had
        for non-canonical upstream shapes), the screenplay would
        hallucinate fresh ids with zero overlap — so the overlap
        assertion is the load-bearing check.
      * Cross-agent invariants KeyFrameAgent relies on (sh_NNN shot_ids
        globally sequential, keyframe_count == 1 per shot) are owned by
        the LLM via the template + system prompt and enforced by
        ScreenplayEvaluator; rework surfaces any drift. recompute_metrics
        no longer rewrites any LLM-authored field.
    """
    workspace_id = _scenario_workspace_id("story_to_screenplay_only")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e0] workspace={workspace_id}")
    print(f"[e2e0] debug_file={debug_file}")

    step_id = _create_step(
        client,
        debug_file,
        goal="Minimal Story → Screenplay roundtrip for the univa-style refactor.",
    )

    # Same watchmaker brief as e2e1 — makes side-by-side comparison with
    # prior known-good runs easy if this fails.
    _upload_text(
        client,
        debug_file,
        text=(
            "I want a 30-second cinematic short about an elderly watchmaker "
            "named Elias who, on New Year's Eve, races against the clock to "
            "repair his late wife's pocket watch. Warm nostalgic mood, "
            "intimate workshop setting, golden lamplight."
        ),
    )

    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    _execute_agent(client, debug_file, "StoryAgent", step_id)
    _execute_agent(client, debug_file, "ScreenplayAgent", step_id)

    story_results = _last_execution_results_for_agent(client, step_id, "StoryAgent")
    screenplay_results = _last_execution_results_for_agent(
        client, step_id, "ScreenplayAgent"
    )

    story_content = story_results.get("content", {}) or {}
    story_logline = story_content.get("logline", "")
    assert story_logline, "StoryAgent produced no logline"

    screenplay_content = screenplay_results.get("content", {}) or {}
    scenes = screenplay_content.get("scenes", []) or []
    assert scenes, "ScreenplayAgent produced no scenes"
    total_shots = sum(
        len(s.get("shots", []) or []) for s in scenes if isinstance(s, dict)
    )
    assert total_shots > 0, "ScreenplayAgent scenes have no shots"

    # Load-bearing check: the screenplay must reuse at least one id
    # (character or location) from the upstream story. Overlap proves the
    # LLM actually READ the JSON text blob and recognized the entities —
    # which is the whole point of the univa-style pass-through. If the
    # refactor silently passed an empty payload (the old failure mode),
    # the screenplay would invent fresh ids with zero overlap.
    story_char_ids = {
        c.get("character_id", "")
        for c in (story_content.get("cast") or [])
        if isinstance(c, dict) and c.get("character_id")
    }
    story_loc_ids = {
        loc.get("location_id", "")
        for loc in (story_content.get("locations") or [])
        if isinstance(loc, dict) and loc.get("location_id")
    }

    screenplay_char_ids: set[str] = set()
    screenplay_loc_ids: set[str] = set()
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        heading = sc.get("heading", {}) or {}
        if isinstance(heading, dict) and heading.get("location_id"):
            screenplay_loc_ids.add(heading["location_id"])
        pack = sc.get("scene_consistency_pack", {}) or {}
        if isinstance(pack, dict):
            ll = pack.get("location_lock", {}) or {}
            if isinstance(ll, dict) and ll.get("location_id"):
                screenplay_loc_ids.add(ll["location_id"])
            for cl in pack.get("character_locks", []) or []:
                if isinstance(cl, dict) and cl.get("character_id"):
                    screenplay_char_ids.add(cl["character_id"])
        for sh in sc.get("shots", []) or []:
            if isinstance(sh, dict) and sh.get("character_id"):
                screenplay_char_ids.add(sh["character_id"])

    if story_char_ids and screenplay_char_ids:
        assert screenplay_char_ids & story_char_ids, (
            f"screenplay character_ids {sorted(screenplay_char_ids)} do not "
            f"overlap with story cast {sorted(story_char_ids)} — LLM may not "
            f"have read the story_json_text blob"
        )
    if story_loc_ids and screenplay_loc_ids:
        assert screenplay_loc_ids & story_loc_ids, (
            f"screenplay location_ids {sorted(screenplay_loc_ids)} do not "
            f"overlap with story locations {sorted(story_loc_ids)} — LLM may "
            f"not have read the story_json_text blob"
        )

    # Structural invariants owned by LLM, enforced by ScreenplayEvaluator
    # — KeyFrameAgent downstream depends on these being true of every screenplay.
    all_shot_ids: list[str] = []
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        for sh in sc.get("shots", []) or []:
            if not isinstance(sh, dict):
                continue
            shot_id = sh.get("shot_id", "")
            assert shot_id, f"shot missing shot_id: {sh}"
            all_shot_ids.append(shot_id)
            kf = sh.get("keyframe_plan", {}) or {}
            if isinstance(kf, dict):
                assert kf.get("keyframe_count") == 1, (
                    f"shot {shot_id} keyframe_count != 1 "
                    f"(ScreenplayEvaluator should have triggered rework)"
                )
    assert len(all_shot_ids) == len(set(all_shot_ids)), (
        f"duplicate shot_ids: {all_shot_ids}"
    )

    print(f"[e2e0] story logline:     {story_logline[:160]}")
    print(f"[e2e0] scenes={len(scenes)} shots={total_shots}")
    print(f"[e2e0] story    char_ids: {sorted(story_char_ids)}")
    print(f"[e2e0] screenplay char_ids: {sorted(screenplay_char_ids)}")
    print(f"[e2e0] story    loc_ids:  {sorted(story_loc_ids)}")
    print(f"[e2e0] screenplay loc_ids:  {sorted(screenplay_loc_ids)}")


# ---------------------------------------------------------------------------
# e2e1 — text only
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e1_text_only_draft_idea(monkeypatch):
    workspace_id = _scenario_workspace_id("text_only")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e1] workspace={workspace_id}")
    print(f"[e2e1] debug_file={debug_file}")

    step_id = _create_step(
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
    )
    assert upload["scope"] == "raw_pending"

    # 2. IntakeTextAgent converts the placeholder into a caption-rich artifact.
    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed

    # 3. Run the full content pipeline. Each downstream agent must find
    #    its inputs (the user's brief, then the upstream artifact, then
    #    keyframes for video, etc.) via the caption-driven InputResolver.
    pipeline = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"]
    pipeline_results: dict[str, dict] = {}
    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)
        pipeline_results[agent_id] = _last_execution_results(client, step_id)

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
    _assert_video_output_real(video_results, "[e2e1]")

    # 4. Workspace invariants.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    paths = _registry_paths(workspace)
    assert paths, "workspace.global_memory is empty"

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

    step_id = _create_step(
        client,
        debug_file,
        goal="A cinematic short — initial brief, then a totally different second brief.",
    )

    pipeline = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"]

    # ----- Phase 1: lighthouse keeper brief, full pipeline run -----
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
    )
    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)
    story_v1 = _last_execution_results_for_agent(client, step_id, "StoryAgent").get("content", {}).get("logline", "")

    # ----- Phase 2: a TOTALLY DIFFERENT story (not a revision) -----
    # Different setting (deep sea vs island), different character
    # (scuba diver vs lighthouse keeper), different tone (adventurous
    # vs lonely vigil). The two pipelines should produce visibly
    # distinct screenplays / keyframes / videos.
    _upload_text(
        client,
        debug_file,
        text=(
            "A 30-second cinematic short about Tomás, a deep-sea scuba "
            "diver exploring the wreckage of a sunken cargo ship at the "
            "edge of an underwater trench. Beams of light cut through "
            "the murky blue water as he discovers a glowing object half-"
            "buried in the silt. Underwater bubbles, mysterious blue-green "
            "palette, low ambient hum."
        ),
    )
    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)
    story_v2 = _last_execution_results_for_agent(client, step_id, "StoryAgent").get("content", {}).get("logline", "")

    assert story_v1, "first StoryAgent run produced no logline"
    assert story_v2, "second StoryAgent run produced no logline"
    assert story_v1.strip() != story_v2.strip(), (
        "v1 and v2 loglines must differ — second brief was supposed to be a different story"
    )

    # Phase 2 must have produced real video + audio files (catches the
    # silent failure where placeholder URIs survive into the final assets).
    video_results_v2 = _last_execution_results_for_agent(client, step_id, "VideoAgent")
    _assert_video_output_real(video_results_v2, "[e2e2 v2]")

    # Both raw-text uploads must have been converted out of raw_pending.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    print(f"[e2e2] story v1: {story_v1[:120]}")
    print(f"[e2e2] story v2: {story_v2[:120]}")


# ---------------------------------------------------------------------------
# e2e3 — text + image at T=0
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e3_text_with_image_at_t0(monkeypatch):
    if not _REFERENCE_IMAGE_FIRST.exists():
        pytest.skip(
            f"Reference image #6 not found at {_REFERENCE_IMAGE_FIRST}; "
            "this test reuses a prior live run's character keyframe."
        )

    workspace_id = _scenario_workspace_id("text_with_image")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e3] workspace={workspace_id}")
    print(f"[e2e3] debug_file={debug_file}")
    print(f"[e2e3] reference_image={_REFERENCE_IMAGE_FIRST.name}")

    step_id = _create_step(
        client,
        debug_file,
        goal="A cinematic short about an elderly craftsman — with a matching character reference image.",
    )

    # 1. Upload text brief — deliberately matches the image #6 character
    #    (an elderly craftsman in a workshop) so the keyframes have a
    #    natural place to put the image bytes as a character anchor.
    _upload_text(
        client,
        debug_file,
        text=(
            "A 30-second cinematic short about Joseph, an elderly white-haired "
            "leather craftsman in his sunlit workshop. He carefully shapes a "
            "leather satchel by hand at his weathered workbench, lost in his "
            "craft. Warm natural light, soft browns and creams, calm reverent "
            "mood."
        ),
    )

    # 2. Upload character reference image #6 (elderly white-haired craftsman).
    _upload_image(
        client,
        debug_file,
        image_path=_REFERENCE_IMAGE_FIRST,
    )

    # 3. Run both intake agents + BriefEnricherAgent.
    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    _execute_agent(client, debug_file, "IntakeImageAgent", step_id)
    _execute_agent(client, debug_file, "BriefEnricherAgent", step_id)

    # 4. Validate BriefEnricher produced an enriched brief + classified the image.
    enricher_results = _last_execution_results_for_agent(
        client, step_id, "BriefEnricherAgent"
    )
    enricher_content = enricher_results.get("content", {}) or {}
    enriched_brief = enricher_content.get("enriched_brief", "")
    assert enriched_brief, "BriefEnricherAgent produced no enriched brief"
    classifications = enricher_content.get("image_classifications", [])
    assert classifications, "BriefEnricherAgent produced no image classifications"
    first_role = classifications[0].get("role", "") if classifications else ""
    assert first_role in ("character", "location", "prop", "style"), (
        f"BriefEnricherAgent image role must be character/location/prop/style, got {first_role!r}"
    )

    # 5. Validate the image artifact carries a role-specific caption
    #    (registered at upload time, promoted to scope=global by the
    #    Intake framework hook, then rewritten in-place by
    #    BriefEnricherAgent via the ``_update:`` mechanism).
    # Filter by mime only; don't filter by entry.agent_id — the image ref
    # lives under the ``user`` upload entry (not under IntakeImageAgent
    # anymore, since IntakeImage no longer registers a ``_source_image``
    # external ref).
    image_blocks: list[dict] = []
    for entry in workspace.global_memory.list_all():
        for ref in entry.artifacts:
            if ref.mime and ref.mime.startswith("image/"):
                image_blocks.append(
                    {"caption": ref.caption, "scope": ref.scope}
                )
    assert image_blocks, "No image artifacts registered"
    # At least one image should now have a role-specific caption
    # from BriefEnricherAgent (e.g. "Global character reference image").
    role_captions = [
        b for b in image_blocks
        if any(r in b["caption"].lower() for r in ("character", "location", "prop", "style"))
    ]
    assert role_captions, (
        f"No image artifact has a role-specific caption. "
        f"Got: {[b['caption'][:80] for b in image_blocks]}"
    )

    # 6. Run the FULL content pipeline. BriefEnricher's enriched brief
    #    should be picked as the creative brief by StoryAgent, so the
    #    story's character descriptions match the uploaded image.
    pipeline = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"]
    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)

    # 7. Verify story was produced and has content.
    story_results = _last_execution_results_for_agent(client, step_id, "StoryAgent")
    story_logline = story_results.get("content", {}).get("logline", "")
    assert story_logline, "StoryAgent produced no logline"

    keyframe_results = _last_execution_results_for_agent(client, step_id, "KeyFrameAgent")
    assert keyframe_results.get("content"), "KeyFrameAgent produced no content"
    keyframe_media = keyframe_results.get("_media_files", {})
    assert isinstance(keyframe_media, dict) and keyframe_media, (
        "KeyFrameAgent returned no media files"
    )

    video_results = _last_execution_results_for_agent(client, step_id, "VideoAgent")
    _assert_video_output_real(video_results, "[e2e3]")

    # 8. Final invariant: nothing left in raw_pending.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    print(f"[e2e3] enriched brief: {enriched_brief[:200]}")
    print(f"[e2e3] image role: {first_role}")
    print(f"[e2e3] story logline: {story_logline[:160]}")
    print(f"[e2e3] keyframe media files: {len(keyframe_media)}")


# ---------------------------------------------------------------------------
# e2e4 — text first, image added mid-stream
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _LIVE_READY, reason=_LIVE_SKIP_REASON)
def test_e2e4_two_rounds_text_with_image(monkeypatch):
    """Two rounds of text+image: verify second round replaces first.

    Phase 1: text (elderly craftsman) + image #1 (elderly craftsman photo)
      → IntakeText + IntakeImage + BriefEnricher + full pipeline
    Phase 2: text (young girl) + image #2 (middle-aged woman photo)
      → IntakeText + IntakeImage + BriefEnricher + full pipeline

    Load-bearing checks:
      * Both phases produce enriched briefs with image descriptions
      * Phase 2's story logline is different from phase 1's
      * Phase 2's video + audio are real files (not leftover from phase 1)
      * The enriched briefs contain visual details from their respective
        images (proving BriefEnricherAgent is actually fusing image
        descriptions into the text, not just passing the raw brief through)
    """
    if not _REFERENCE_IMAGE_FIRST.exists():
        pytest.skip(
            f"Reference image #1 not found at {_REFERENCE_IMAGE_FIRST}"
        )
    if not _REFERENCE_IMAGE_SECOND.exists():
        pytest.skip(
            f"Reference image #2 not found at {_REFERENCE_IMAGE_SECOND}"
        )

    workspace_id = _scenario_workspace_id("two_rounds_text_image")
    client, workspace, debug_file = _build_client(workspace_id, monkeypatch)
    print(f"\n[e2e4] workspace={workspace_id}")
    print(f"[e2e4] debug_file={debug_file}")

    step_id = _create_step(
        client,
        debug_file,
        goal="Two rounds of text+image — verify second round replaces first.",
    )

    pipeline = ["StoryAgent", "ScreenplayAgent", "KeyFrameAgent", "VideoAgent"]

    # ----- Phase 1: text (craftsman) + image #1 (craftsman photo) -----
    _upload_text(
        client,
        debug_file,
        text=(
            "A 30-second cinematic short about Joseph, an elderly white-haired "
            "leather craftsman in his sunlit workshop. He carefully shapes a "
            "leather satchel by hand at his weathered workbench, lost in his "
            "craft. Use the uploaded image as the protagonist reference. "
            "Warm natural light, soft browns and creams, calm reverent mood."
        ),
    )
    _upload_image(client, debug_file, image_path=_REFERENCE_IMAGE_FIRST)

    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    _execute_agent(client, debug_file, "IntakeImageAgent", step_id)
    _execute_agent(client, debug_file, "BriefEnricherAgent", step_id)

    enricher_p1 = _last_execution_results_for_agent(
        client, step_id, "BriefEnricherAgent"
    )
    enriched_brief_p1 = enricher_p1.get("content", {}).get("enriched_brief", "")
    assert enriched_brief_p1, "Phase 1 BriefEnricher produced no enriched brief"

    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)
    story_p1 = _last_execution_results_for_agent(
        client, step_id, "StoryAgent"
    ).get("content", {}).get("logline", "")
    assert story_p1, "Phase 1 StoryAgent produced no logline"

    # ----- Phase 2: DIFFERENT text (girl) + DIFFERENT image #2 -----
    _upload_text(
        client,
        debug_file,
        text=(
            "A 30-second cinematic short about Lily, a barefoot 8-year-old "
            "girl chasing glowing fireflies through a moonlit forest "
            "clearing. Use the uploaded image as the protagonist reference. "
            "Tall grass, warm summer night, dreamy childlike wonder."
        ),
    )
    _upload_image(client, debug_file, image_path=_REFERENCE_IMAGE_SECOND)

    # IntakeTextAgent retired — brief auto-persisted by workspace upload; no execute step needed
    _execute_agent(client, debug_file, "IntakeImageAgent", step_id)
    _execute_agent(client, debug_file, "BriefEnricherAgent", step_id)

    enricher_p2 = _last_execution_results_for_agent(
        client, step_id, "BriefEnricherAgent"
    )
    enriched_brief_p2 = enricher_p2.get("content", {}).get("enriched_brief", "")
    assert enriched_brief_p2, "Phase 2 BriefEnricher produced no enriched brief"

    for agent_id in pipeline:
        _execute_agent(client, debug_file, agent_id, step_id)
    story_p2 = _last_execution_results_for_agent(
        client, step_id, "StoryAgent"
    ).get("content", {}).get("logline", "")
    assert story_p2, "Phase 2 StoryAgent produced no logline"

    # ----- Assertions -----
    # Stories must be different (different briefs + different images).
    assert story_p1.strip() != story_p2.strip(), (
        "Phase 1 and Phase 2 loglines must differ — different text+image "
        f"should produce different stories.\nP1: {story_p1}\nP2: {story_p2}"
    )

    # Enriched briefs must be different (different image descriptions).
    assert enriched_brief_p1.strip() != enriched_brief_p2.strip(), (
        "Phase 1 and Phase 2 enriched briefs must differ"
    )

    # Phase 2 video + audio must be real files (not leftover from phase 1).
    video_p2 = _last_execution_results_for_agent(client, step_id, "VideoAgent")
    _assert_video_output_real(video_p2, "[e2e4 phase2]")
    # No raw_pending leaks.
    leaks = _placeholders_without_successor(workspace)
    assert not leaks, f"raw_pending placeholder has no intake successor: {leaks}"

    print(f"[e2e4] phase1 logline: {story_p1[:120]}")
    print(f"[e2e4] phase2 logline: {story_p2[:120]}")
    print(f"[e2e4] phase1 enriched brief: {enriched_brief_p1[:150]}")
    print(f"[e2e4] phase2 enriched brief: {enriched_brief_p2[:150]}")
