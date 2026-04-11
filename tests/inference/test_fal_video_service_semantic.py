"""Unit tests for FalVideoService's semantic-context plumbing.

Covers the two methods that own fal's model-specific vocabulary:
``_compose_prompt`` (prompt templating) and ``_pack_fal_constraints``
(entity-anchor payload shape). These tests are the inference-layer
equivalents of assertions that used to live in the now-quarantined
``tests/agents/test_media_materializers.py`` file — they verify the
*translation* from a language-neutral ``ShotSemanticContext`` to
fal's wire format without touching any materializer code.
"""

from __future__ import annotations

import asyncio

import pytest

from inference.generation.video_generators.service import FalVideoService
from inference.generation.video_generators.types import (
    ShotSemanticContext,
    VideoClipResult,
)


def _make_service(structured_constraints_field: str | None = None) -> FalVideoService:
    return FalVideoService(
        api_key="test",
        model="fal-ai/test-model",
        structured_constraints_field=structured_constraints_field,
    )


# ---------------------------------------------------------------------------
# _compose_prompt
# ---------------------------------------------------------------------------


def test_compose_prompt_motion_hint_prefixes_and_omits_scene_tone() -> None:
    svc = _make_service()
    ctx = ShotSemanticContext(
        shot_id="sh_001",
        shot_type="medium",
        visual_goal="Show the character entering frame.",
        action_focus="Character walks in from left.",
        characters_in_frame=["char_001"],
        camera_angle="eye_level",
        camera_movement="pan",
        framing_notes="Follow the character into center frame.",
        scene_id="sc_001",
        location_id="loc_001",
        time_of_day="NIGHT",
        environment_notes=["Rain-soaked street with reflective neon lights."],
        style_notes=["Moody cinematic contrast with cool highlights."],
        must_avoid=["Flat lighting and washed-out colors."],
        keyframe_prompt_summaries=["Still: wide interior, rain, neon reflections."],
        video_motion_hints=["Slow push-in; hold composition; subtle rain on glass."],
    )

    prompt = svc._compose_prompt(ctx, anchor_image_count=1)

    # Motion hint becomes the leading prefix before the main body.
    assert prompt.startswith("Slow push-in; hold composition; subtle rain on glass.")
    # Ref line reflects the slim-path I2V phrasing.
    assert "Ref: one L3 still" in prompt
    # Core semantic fields survive the render.
    assert "Show the character entering frame." in prompt
    assert "Character walks in from left." in prompt
    assert "Characters in frame: char_001" in prompt
    assert "Scene context: location_id=loc_001, time_of_day=NIGHT" in prompt
    assert "Framing notes: Follow the character into center frame." in prompt
    assert "Anchor images: 1" in prompt
    # Scene-tone blocks and the task-focus trailer are omitted when a
    # motion prefix is active (they would duplicate the prefix for I2V).
    assert "Scene environment notes:" not in prompt
    assert "Scene style notes:" not in prompt
    assert "Scene must avoid:" not in prompt
    assert "Task focus:" not in prompt


def test_compose_prompt_no_motion_hint_keeps_scene_tone_and_task_focus() -> None:
    svc = _make_service()
    ctx = ShotSemanticContext(
        shot_id="sh_001",
        shot_type="wide",
        visual_goal="Establish space.",
        action_focus="Talent idle.",
        camera_angle="high",
        camera_movement="static",
        scene_id="sc_001",
        location_id="loc_001",
        time_of_day="DAY",
        environment_notes=["Bright daylight studio."],
        style_notes=["Clean high-key look."],
        must_avoid=["Heavy grain."],
        keyframe_prompt_summaries=["Still: empty white cyclorama."],
        video_motion_hints=[""],
    )

    prompt = svc._compose_prompt(ctx, anchor_image_count=1)

    # Without a motion prefix the body starts with the shot header and
    # keeps the full scene-tone + task-focus trailer.
    assert prompt.startswith("Shot sh_001")
    assert "Scene environment notes: Bright daylight studio." in prompt
    assert "Scene style notes: Clean high-key look." in prompt
    assert "Scene must avoid: Heavy grain." in prompt
    assert "Task focus: in this scene, complete this shot action: Talent idle." in prompt
    # prompt_summaries are NOT dumped into the text prompt — they feed
    # the structured-constraints payload (see pack tests below).
    assert "Still: empty white cyclorama." not in prompt


# ---------------------------------------------------------------------------
# _pack_fal_constraints
# ---------------------------------------------------------------------------


def test_pack_fal_constraints_carries_literal_fal_field_names() -> None:
    """``consistency_type`` and ``keyframe_role`` literals live here, nowhere else."""
    svc = _make_service()
    ctx = ShotSemanticContext(
        shot_id="sh_042",
        visual_goal="Establish the room.",
        action_focus="Actor stands center.",
        characters_in_frame=["char_001", "char_002"],
        camera_angle="eye_level",
        camera_movement="static",
        framing_notes="centered two-shot",
        scene_id="sc_007",
        location_id="loc_warehouse",
        time_of_day="DUSK",
        environment_notes=["cavernous", "lit by single overhead lamp"],
        style_notes=["muted palette"],
        must_avoid=["harsh shadows across faces"],
        keyframe_notes=["wide establishing shot", "no camera movement"],
        keyframe_prompt_summaries=["Still: warehouse interior, dusk"],
        video_motion_hints=["slow drift forward"],
    )

    packed = svc._pack_fal_constraints(ctx)

    assert packed["shot_id"] == "sh_042"
    assert packed["consistency_type"] == "entity_anchor_constraints"
    assert packed["keyframe_role"] == "shot_still_l3_only"
    assert packed["characters_in_frame"] == ["char_001", "char_002"]
    sc = packed["scene_context"]
    assert sc["scene_id"] == "sc_007"
    assert sc["location_id"] == "loc_warehouse"
    assert sc["time_of_day"] == "DUSK"
    assert sc["environment_notes"] == ["cavernous", "lit by single overhead lamp"]
    assert sc["style_notes"] == ["muted palette"]
    assert sc["must_avoid"] == ["harsh shadows across faces"]
    assert packed["visual_goal"] == "Establish the room."
    assert packed["action_focus"] == "Actor stands center."
    assert packed["camera"] == {
        "angle": "eye_level",
        "movement": "static",
        "framing_notes": "centered two-shot",
    }
    assert packed["storyboard_keyframe_notes"] == ["wide establishing shot", "no camera movement"]
    assert packed["keyframe_prompt_summaries"] == ["Still: warehouse interior, dusk"]
    assert packed["keyframe_video_motion_hints"] == ["slow drift forward"]


# ---------------------------------------------------------------------------
# generate_clip wiring (end-to-end with stubbed _submit / _download)
# ---------------------------------------------------------------------------


class _FalVideoServiceSpy(FalVideoService):
    """Test double that records submitted arguments without hitting fal."""

    def __init__(self, *, structured_constraints_field: str | None = None) -> None:
        super().__init__(
            api_key="test",
            model="fal-ai/test-model",
            structured_constraints_field=structured_constraints_field,
        )
        self.submitted: list[dict] = []

    async def _submit(self, arguments: dict) -> dict:
        self.submitted.append(arguments)
        return {"video_url": "https://example.com/v.mp4"}

    async def _download_binary(self, url: str) -> bytes:
        return f"video:{url}".encode("utf-8")


def test_generate_clip_with_semantic_context_composes_prompt_and_packs_constraints() -> None:
    svc = _FalVideoServiceSpy(structured_constraints_field="consistency_constraints")
    ctx = ShotSemanticContext(
        shot_id="sh_001",
        visual_goal="Show the doorway.",
        action_focus="Subject steps in.",
        characters_in_frame=["char_001"],
        camera_angle="low",
        location_id="loc_001",
        video_motion_hints=["gentle push"],
    )

    result = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"\x89PNG" + b"\x00" * 20],
            semantic_context=ctx,
            duration_sec=5.0,
        )
    )

    assert isinstance(result, VideoClipResult)
    assert result.bytes == b"video:https://example.com/v.mp4"

    # Prompt was composed from the semantic context, not passed in.
    assert result.resolved_prompt.startswith("gentle push | ")
    assert "Show the doorway." in result.resolved_prompt
    assert "Subject steps in." in result.resolved_prompt
    assert result.resolved_prompt == svc.submitted[0]["prompt"]

    # Structured constraints were packed into the fal arguments under the
    # configured field name, with the fal-specific literal field names.
    packed = svc.submitted[0]["consistency_constraints"]
    assert packed["consistency_type"] == "entity_anchor_constraints"
    assert packed["keyframe_role"] == "shot_still_l3_only"
    assert packed["characters_in_frame"] == ["char_001"]

    # The audit view of the payload strips the inline image data URL so
    # persisted records stay small.
    assert "image_url" not in result.resolved_payload
    assert result.resolved_payload["prompt"] == result.resolved_prompt
    assert "consistency_constraints" in result.resolved_payload


def test_generate_clip_without_semantic_context_passes_prompt_as_is() -> None:
    """Legacy path: caller passes a pre-composed prompt, no structured payload."""
    svc = _FalVideoServiceSpy(structured_constraints_field="consistency_constraints")

    result = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"\x89PNG" + b"\x00" * 20],
            prompt="hand-written prompt",
            duration_sec=5.0,
        )
    )

    assert result.bytes == b"video:https://example.com/v.mp4"
    assert result.resolved_prompt == "hand-written prompt"
    # No semantic_context → no constraints packed even when the field
    # is configured (legacy callers opt in via semantic_context only).
    assert "consistency_constraints" not in svc.submitted[0]


def test_generate_clip_skips_constraints_when_field_not_configured() -> None:
    """Even with a semantic context, skip structured payload if the model endpoint doesn't want one."""
    svc = _FalVideoServiceSpy(structured_constraints_field=None)
    ctx = ShotSemanticContext(shot_id="sh_001", visual_goal="hello")

    result = asyncio.run(
        svc.generate_clip(
            shot_id="sh_001",
            keyframe_images=[b"\x89PNG" + b"\x00" * 20],
            semantic_context=ctx,
            duration_sec=5.0,
        )
    )

    assert result.bytes == b"video:https://example.com/v.mp4"
    assert "consistency_constraints" not in svc.submitted[0]
    # Prompt still composed from the semantic context.
    assert "hello" in result.resolved_prompt
