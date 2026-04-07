"""Test AudioAgent skeleton + recompute_metrics + per_artifact_captions using existing workspace assets.

Loads the real screenplay and video JSON from a prior pipeline run and verifies:
1. build_skeleton() produces a structurally valid AudioAgentOutput
2. recompute_metrics() computes correct counts
3. per_artifact_captions is populated with the right sys_id keys
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from agents.audio.agent import AudioAgent
from agents.audio.schema import AudioAgentInput, AudioAgentOutput

WORKSPACE = (
    _repo_root
    / "Runtime"
    / "live_e2e_outputs"
    / "workspace_global_20260405_145954"
)
SCREENPLAY_JSON = WORKSPACE / "artifacts" / "screenplay" / "screenplay_exec_2.json"
VIDEO_JSON = WORKSPACE / "artifacts" / "video" / "video_exec_4.json"


@pytest.fixture
def existing_assets():
    """Load screenplay + video JSON from the prior pipeline run."""
    if not SCREENPLAY_JSON.exists() or not VIDEO_JSON.exists():
        pytest.skip("Existing workspace assets not found — run full pipeline first")
    screenplay = json.loads(SCREENPLAY_JSON.read_text(encoding="utf-8"))
    video = json.loads(VIDEO_JSON.read_text(encoding="utf-8"))
    return screenplay, video


def test_build_skeleton_from_existing_assets(existing_assets):
    screenplay, video = existing_assets
    agent = AudioAgent(llm_client=None)
    inp = AudioAgentInput(screenplay=screenplay, final_video=video)

    skeleton = agent.build_skeleton(inp)

    assert skeleton is not None, "build_skeleton returned None — screenplay or video may be empty"
    assert isinstance(skeleton, AudioAgentOutput)

    # Content checks
    c = skeleton.content
    assert len(c.scenes) > 0, "Expected at least one scene"

    for scene in c.scenes:
        assert scene.scene_id, "scene_id should be non-empty"
        # Music cue present with matching scene_id
        assert scene.music_cue.cue_id
        assert scene.music_cue.scene_id == scene.scene_id
        # Ambience bed present
        assert scene.ambience_bed.ambience_id
        assert scene.ambience_bed.scene_id == scene.scene_id
        # Mix present
        assert scene.mix.mix_id
        assert scene.mix.scene_id == scene.scene_id

    # Final assets
    assert c.final_audio_asset.asset_id == "aud_final"
    assert c.final_delivery_asset.asset_id == "delivery_final"


def test_recompute_metrics_from_existing_assets(existing_assets):
    screenplay, video = existing_assets
    agent = AudioAgent(llm_client=None)
    inp = AudioAgentInput(screenplay=screenplay, final_video=video)
    skeleton = agent.build_skeleton(inp)
    assert skeleton is not None

    agent.recompute_metrics(skeleton)

    m = skeleton.metrics
    assert m.scene_count == len(skeleton.content.scenes)
    assert m.scene_count > 0

    # Narration count should match segments
    expected_narr = sum(len(s.narration_segments) for s in skeleton.content.scenes)
    assert m.narration_segment_count == expected_narr


def test_per_artifact_captions_populated(existing_assets):
    screenplay, video = existing_assets
    agent = AudioAgent(llm_client=None)
    inp = AudioAgentInput(screenplay=screenplay, final_video=video)
    skeleton = agent.build_skeleton(inp)
    assert skeleton is not None

    agent.recompute_metrics(skeleton)

    pac = skeleton.per_artifact_captions
    assert isinstance(pac, dict), "per_artifact_captions should be a dict"
    assert len(pac) > 0, "per_artifact_captions should not be empty"

    # Check keys follow expected naming conventions
    for key, caption in pac.items():
        assert isinstance(caption, dict), f"Caption for {key} should be a dict"
        assert "what" in caption, f"Caption for {key} missing 'what'"
        assert "why" in caption, f"Caption for {key} missing 'why'"
        assert "scope" in caption, f"Caption for {key} missing 'scope'"

    # Keys must match audio_asset.asset_id values from build_skeleton
    c = skeleton.content
    expected_keys = set()
    for scene in c.scenes:
        for seg in scene.narration_segments:
            if seg.audio_asset.asset_id:
                expected_keys.add(seg.audio_asset.asset_id)
        if scene.music_cue.audio_asset.asset_id:
            expected_keys.add(scene.music_cue.audio_asset.asset_id)
        if scene.ambience_bed.audio_asset.asset_id:
            expected_keys.add(scene.ambience_bed.audio_asset.asset_id)
        if scene.mix.audio_asset.asset_id:
            expected_keys.add(scene.mix.audio_asset.asset_id)
    if c.final_audio_asset.asset_id:
        expected_keys.add(c.final_audio_asset.asset_id)

    assert set(pac.keys()) == expected_keys, (
        f"pac keys don't match asset_ids.\n"
        f"  Missing: {expected_keys - set(pac.keys())}\n"
        f"  Extra: {set(pac.keys()) - expected_keys}"
    )

    # Verify scope values
    for key, caption in pac.items():
        scope = caption["scope"]
        if key == c.final_audio_asset.asset_id:
            assert scope == "global"
        else:
            assert scope.startswith("scene:"), f"Non-global caption {key} should have scene:* scope, got {scope}"


def test_per_artifact_captions_excluded_from_model_dump(existing_assets):
    """per_artifact_captions should NOT appear in JSON serialization (exclude=True)."""
    screenplay, video = existing_assets
    agent = AudioAgent(llm_client=None)
    inp = AudioAgentInput(screenplay=screenplay, final_video=video)
    skeleton = agent.build_skeleton(inp)
    assert skeleton is not None
    agent.recompute_metrics(skeleton)

    dumped = skeleton.model_dump()
    assert "per_artifact_captions" not in dumped, (
        "per_artifact_captions should be excluded from model_dump (exclude=True)"
    )
    # But the attribute should still be accessible
    assert len(skeleton.per_artifact_captions) > 0
