"""Video clip materializer — generates video clips via VideoService.

This materializer is a **pure generator** — it calls VideoService to
produce video bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.

Responsibility boundary
-----------------------
The materializer reads **only the agent's own output** (``asset_dict``)
and ``typed_input.shot_stills``. It does NOT touch the upstream
screenplay or keyframes_metadata — those flow to VideoAgent as opaque
JSON text blobs, are consumed by VideoAgent's LLM, and the relevant
per-shot semantic information is mirrored into each ShotSegment's
``semantic_context`` sub-object by the LLM. This removes the old
string-keyed coupling (``_build_screenplay_shot_index`` and
``_build_shot_keyframe_inputs_index``) and leaves the materializer as
a thin shim around ``VideoService``.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from typing import TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_generators.service import VideoService
from inference.generation.video_generators.types import ShotSemanticContext

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import VideoAgentInput

logger = logging.getLogger(__name__)


class VideoMaterializer(BaseMaterializer):
    """Generate video clips for all shots via VideoService.

    Constructor:
        video_service: ``VideoService`` instance.
    """

    def __init__(self, video_service: VideoService) -> None:
        self.video_svc = video_service

    @staticmethod
    def _normalize_local_path(uri: str) -> str:
        if not uri:
            return ""
        if uri.startswith("file://"):
            return uri[7:]
        return uri

    def _build_shot_still_index(
        self, typed_input: "VideoAgentInput"
    ) -> dict[str, str]:
        """Map shot_id → starting-frame image path, from ``typed_input.shot_stills``.

        Each ``ImageReferenceEntry`` in ``shot_stills`` carries a direct
        ``path`` + a ``scope`` like ``"shot:sh_001"``. We parse the scope
        to pair an image with the right shot. No upstream keyframes_metadata
        JSON unwrap is needed — the Director + InputResolver have already
        matched the images to the shot_stills label by caption.
        """
        index: dict[str, str] = {}
        for img in typed_input.shot_stills:
            scope = img.scope or ""
            if not scope.startswith("shot:"):
                continue
            shot_id = scope[5:]
            if not shot_id or shot_id in index:
                continue
            path = self._normalize_local_path(img.path)
            if path:
                index[shot_id] = path
        return index

    @staticmethod
    def _to_inference_context(
        shot_id: str, seg_semantic: dict, scene_ctx: dict
    ) -> ShotSemanticContext:
        """Convert the agent-layer per-shot semantic dict + parent scene's
        scene_context into the inference-layer dataclass the VideoService
        expects.

        Scene-level fields (scene_id / location_id / time_of_day /
        environment_notes / style_notes / must_avoid) are read from the
        parent ``VideoScene``'s ``scene_context`` and the scene itself.
        Per-shot fields are read from ``seg_semantic``. The inference-layer
        dataclass in ``inference/generation/video_generators/types.py``
        still carries the full flat field set, so this is where the
        scene/shot merge happens.
        """
        return ShotSemanticContext(
            shot_id=shot_id,
            shot_type=seg_semantic.get("shot_type", "") or "",
            visual_goal=seg_semantic.get("visual_goal", "") or "",
            action_focus=seg_semantic.get("action_focus", "") or "",
            characters_in_frame=list(seg_semantic.get("characters_in_frame", []) or []),
            camera_angle=seg_semantic.get("camera_angle", "") or "",
            camera_movement=seg_semantic.get("camera_movement", "") or "",
            framing_notes=seg_semantic.get("framing_notes", "") or "",
            scene_id=scene_ctx.get("scene_id", "") or "",
            location_id=scene_ctx.get("location_id", "") or "",
            time_of_day=scene_ctx.get("time_of_day", "") or "",
            environment_notes=list(scene_ctx.get("environment_notes", []) or []),
            style_notes=list(scene_ctx.get("style_notes", []) or []),
            must_avoid=list(scene_ctx.get("must_avoid", []) or []),
            video_motion_hints=list(
                seg_semantic.get("video_motion_hints", []) or []
            ),
            dialogue_text=seg_semantic.get("dialogue_text", "") or "",
            emotion_hint=seg_semantic.get("emotion_hint", "") or "",
        )

    @staticmethod
    def _load_image_bytes(path: str) -> bytes | None:
        if not path or not os.path.isfile(path):
            return None
        try:
            with open(path, "rb") as fh:
                return fh.read()
        except Exception:
            return None

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        """Generate actual video clips for all shots.

        System-generates sequential asset_ids (IDs already include type prefix):
          Shot clip  -- ``clip_{shot_id}``      e.g. ``clip_sh_001``
          Scene clip -- ``clip_{scene_id}``     e.g. ``clip_sc_001``
          Final      -- ``clip_final``

        Returns:
            List of ``MediaAsset`` objects for Assistant to persist.
        """
        typed_input = ctx.typed_input  # type: VideoAgentInput
        step_id = ctx.step_id
        pending: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        scene_bytes_list: list[bytes] = []

        shot_still_index = self._build_shot_still_index(typed_input)

        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            scene_ctx = dict(scene.get("scene_context", {}) or {})
            scene_ctx["scene_id"] = scene_id
            clip_bytes_list: list[bytes] = []

            for seg in scene.get("shot_segments", []):
                shot_id = seg.get("shot_id", "")
                sys_vid_id = f"clip_{shot_id}"
                # Per-clip URI holder is local — agent output no longer
                # carries a per-shot video_asset block. MediaAsset's
                # uri_holder just needs somewhere to write the persisted
                # URI; Assistant reads it off the returned MediaAsset.
                video_asset: dict[str, Any] = {"asset_id": sys_vid_id, "format": "mp4"}

                # --- Load the starting-frame image for this shot ---
                # Missing keyframe input is a chain-config failure (upstream
                # KeyFrameAgent should have produced one); raise rather
                # than silently skip the shot.
                still_path = shot_still_index.get(shot_id, "")
                image_bytes = self._load_image_bytes(still_path)
                if image_bytes is None:
                    raise RuntimeError(
                        f"Video clip {shot_id}: missing on-disk starting "
                        f"frame (shot_stills scope=shot:{shot_id})"
                    )

                # --- Build the semantic context from the agent's own
                #     typed output — the LLM already mirrored the
                #     upstream screenplay + keyframes fields into
                #     seg.semantic_context + scene.scene_context, so we
                #     only need a mechanical conversion to the inference-
                #     layer dataclass here.
                seg_semantic = seg.get("semantic_context", {}) or {}
                semantic_context = self._to_inference_context(
                    shot_id, seg_semantic, scene_ctx
                )

                # --- Per-shot partial-resume retry budget ---
                last_exc: Exception | None = None
                clip_bytes: bytes | None = None
                for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                    try:
                        result = await self.video_svc.generate_clip(
                            shot_id=shot_id,
                            keyframe_images=[image_bytes],
                            semantic_context=semantic_context,
                        )
                        clip_bytes = result.bytes
                        if clip_bytes:
                            break
                        last_exc = RuntimeError("generate_clip returned empty bytes")
                    except Exception as exc:
                        last_exc = exc
                    logger.warning(
                        "[attempt %d/%d] Video clip generation failed for "
                        "%s: %s",
                        attempt, DEFAULT_ASSET_RETRIES, shot_id, last_exc,
                    )

                if not clip_bytes:
                    raise RuntimeError(
                        f"generate_clip for {shot_id} failed after "
                        f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
                    )

                pending.append(MediaAsset(
                    sys_id=sys_vid_id, data=clip_bytes,
                    extension="mp4", uri_holder=video_asset,
                ))
                clip_bytes_list.append(clip_bytes)

            # --- Per-scene assemble: retry transient failures, raise
            #     otherwise. ``clip_bytes_list`` is non-empty because the
            #     inner loop raises on per-shot failure, so this branch
            #     only handles the assembly call's own retries.
            sys_scene_clip_id = f"clip_{scene_id}"
            scene_clip: dict[str, Any] = {
                "asset_id": sys_scene_clip_id, "format": "mp4",
            }
            if not clip_bytes_list:
                # Defensive: scene with zero shot_segments — chain config
                # issue. L1 evaluator should catch but raise here too.
                raise RuntimeError(
                    f"scene {scene_id} has no shot_segments to assemble"
                )

            last_exc = None
            scene_bytes: bytes | None = None
            for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                try:
                    scene_bytes = await self.video_svc.assemble_scene(
                        scene_id=scene_id,
                        clip_bytes_list=clip_bytes_list,
                        transitions=scene.get("transition_plan", []),
                    )
                    if scene_bytes:
                        break
                    last_exc = RuntimeError("assemble_scene returned empty bytes")
                except Exception as exc:
                    last_exc = exc
                logger.warning(
                    "[attempt %d/%d] Scene assembly failed for %s: %s",
                    attempt, DEFAULT_ASSET_RETRIES, scene_id, last_exc,
                )

            if not scene_bytes:
                raise RuntimeError(
                    f"assemble_scene for {scene_id} failed after "
                    f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
                )

            pending.append(MediaAsset(
                sys_id=sys_scene_clip_id, data=scene_bytes,
                extension="mp4", uri_holder=scene_clip,
            ))
            scene_bytes_list.append(scene_bytes)

        # --- Final assemble: retry transient failures, raise otherwise ---
        if not scene_bytes_list:
            raise RuntimeError(
                "no scene clips were produced — cannot assemble final video"
            )

        final: dict[str, Any] = {"asset_id": "clip_final", "format": "mp4"}
        last_exc = None
        final_bytes: bytes | None = None
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            try:
                final_bytes = await self.video_svc.assemble_final(
                    scene_bytes_list=scene_bytes_list
                )
                if final_bytes:
                    break
                last_exc = RuntimeError("assemble_final returned empty bytes")
            except Exception as exc:
                last_exc = exc
            logger.warning(
                "[attempt %d/%d] Final video assembly failed: %s",
                attempt, DEFAULT_ASSET_RETRIES, last_exc,
            )

        if not final_bytes:
            raise RuntimeError(
                f"assemble_final failed after {DEFAULT_ASSET_RETRIES} "
                f"attempts: {last_exc}"
            )

        pending.append(MediaAsset(
            sys_id="clip_final", data=final_bytes,
            extension="mp4", uri_holder=final,
        ))

        logger.info("All video clips materialized for %s", step_id)
        return pending
