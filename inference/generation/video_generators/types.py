"""Shared types for video generation services.

``ShotSemanticContext`` is the language-neutral description of "what this
shot is supposed to be" that a caller (typically an agents/materializer)
passes to a ``VideoService``. It contains **purely semantic** fields —
visual goal, action focus, characters, camera, scene context, keyframe
planning notes — and deliberately contains **zero model-specific field
names**.

Each ``VideoService`` implementation is responsible for turning a
``ShotSemanticContext`` into whatever text prompt and structured payload
its underlying backend wants. This is how we keep model-specific
vocabulary (e.g. fal's ``consistency_type`` / ``keyframe_role`` literals,
or a given model's prompt templating style) out of the agents layer.

``VideoClipResult`` is what ``generate_clip`` returns: the raw bytes
plus an audit pair (the text prompt the service actually composed and
the structured payload it actually sent). The caller writes the audit
pair back into its own schema so a human inspecting the persisted
VideoPackage JSON can see exactly what was sent to the backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ShotSemanticContext:
    """Language-neutral description of one shot's creative intent.

    Populated by the caller from upstream artifacts (screenplay + any
    keyframe planning document). A concrete ``VideoService`` reads
    whichever fields it needs and discards the rest.

    Field name conventions mirror the screenplay's shot object where
    possible (``visual_goal`` / ``action_focus`` / ``characters_in_frame``
    / ``shot_type``) so the mapping from screenplay → context is
    one-to-one and easy to audit.
    """

    shot_id: str = ""

    # Creative intent (from screenplay shot)
    shot_type: str = ""
    visual_goal: str = ""
    action_focus: str = ""
    characters_in_frame: list[str] = field(default_factory=list)

    # Camera / framing (from screenplay shot.camera)
    camera_angle: str = ""
    camera_movement: str = ""
    framing_notes: str = ""

    # Scene-level context (from screenplay scene.scene_consistency_pack)
    scene_id: str = ""
    location_id: str = ""
    time_of_day: str = ""
    environment_notes: list[str] = field(default_factory=list)
    style_notes: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)

    # Keyframe planning (from screenplay shot.keyframe_plan + keyframes_metadata)
    keyframe_notes: list[str] = field(default_factory=list)
    keyframe_prompt_summaries: list[str] = field(default_factory=list)
    video_motion_hints: list[str] = field(default_factory=list)


@dataclass
class VideoClipResult:
    """Return value of ``VideoService.generate_clip``.

    ``bytes`` is the generated clip payload.

    ``resolved_prompt`` and ``resolved_payload`` are the text prompt and
    structured payload the service *actually* sent to its backend, so the
    caller can persist them alongside the clip for audit/inspection. Both
    may be empty when the service has nothing semantically meaningful to
    report (e.g. ``MockVideoService`` in tests).
    """

    bytes: bytes
    resolved_prompt: str = ""
    resolved_payload: dict[str, Any] = field(default_factory=dict)
