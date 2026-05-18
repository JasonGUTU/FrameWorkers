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

import asyncio
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
            language=seg_semantic.get("language", "") or "",
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

        # ── Stage 1: collect per-shot specs across ALL scenes ─────────
        # Cross-scene gather lets us issue every Kling I2V call in
        # parallel up to the Semaphore cap; per-scene assembly stays
        # sequential afterwards (it's local ffmpeg, fast).
        # Per memory:feedback_video_gen_must_parallel.
        shot_specs: list[dict[str, Any]] = []
        for sc_idx, scene in enumerate(content.get("scenes", [])):
            scene_id = scene.get("scene_id", "")
            scene_ctx = dict(scene.get("scene_context", {}) or {})
            scene_ctx["scene_id"] = scene_id
            for sh_idx, seg in enumerate(scene.get("shot_segments", [])):
                shot_id = seg.get("shot_id", "")
                still_path = shot_still_index.get(shot_id, "")
                image_bytes = self._load_image_bytes(still_path)
                if image_bytes is None:
                    raise RuntimeError(
                        f"Video clip {shot_id}: missing on-disk starting "
                        f"frame (shot_stills scope=shot:{shot_id})"
                    )
                seg_semantic = seg.get("semantic_context", {}) or {}
                semantic_context = self._to_inference_context(
                    shot_id, seg_semantic, scene_ctx
                )
                duration_sec = float(seg.get("duration_sec", 5.0) or 5.0)
                shot_specs.append({
                    "sc_idx": sc_idx,
                    "sh_idx": sh_idx,
                    "scene_id": scene_id,
                    "shot_id": shot_id,
                    "image_bytes": image_bytes,
                    "semantic_context": semantic_context,
                    "duration_sec": duration_sec,
                })

        # ── Stage 2: parallel render with partial-resume retry ────────
        # Mirror IllustrationMaterializer.materialize: gather all
        # remaining specs each attempt, collect successes, retry only
        # failures next attempt. Semaphore caps fal concurrency.
        sem = asyncio.Semaphore(8)

        # Optional eager spill: persist each successful shot mp4 to disk as
        # soon as generate_clip returns, so partial results survive a later
        # raise. Opt-in via FW_VIDEO_SHOT_SPILL_DIR env var.
        spill_dir = os.getenv("FW_VIDEO_SHOT_SPILL_DIR", "").strip()

        async def _gen_one(spec: dict) -> bytes | Exception:
            async with sem:
                try:
                    result = await self.video_svc.generate_clip(
                        shot_id=spec["shot_id"],
                        keyframe_images=[spec["image_bytes"]],
                        semantic_context=spec["semantic_context"],
                        duration_sec=spec["duration_sec"],
                    )
                    if result.bytes:
                        if spill_dir:
                            try:
                                os.makedirs(spill_dir, exist_ok=True)
                                sp = os.path.join(spill_dir, f"clip_{spec['shot_id']}.mp4")
                                with open(sp, "wb") as fh:
                                    fh.write(result.bytes)
                                logger.info("[shot-spill] wrote %s (%.1f KB)", sp, len(result.bytes) / 1024)
                            except Exception as spill_exc:
                                logger.warning("[shot-spill] write failed for %s: %s", spec["shot_id"], spill_exc)
                        return result.bytes
                    return RuntimeError("generate_clip returned empty bytes")
                except Exception as exc:
                    return exc

        results_by_idx: dict[int, bytes] = {}
        last_excs: dict[int, Exception] = {}
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            pending_idxs = [i for i in range(len(shot_specs)) if i not in results_by_idx]
            if not pending_idxs:
                break
            pending_specs = [shot_specs[i] for i in pending_idxs]
            partial = await asyncio.gather(
                *(_gen_one(s) for s in pending_specs),
                return_exceptions=True,
            )
            for idx, outcome in zip(pending_idxs, partial):
                if isinstance(outcome, bytes) and outcome:
                    results_by_idx[idx] = outcome
                elif isinstance(outcome, Exception):
                    last_excs[idx] = outcome
                else:
                    last_excs[idx] = RuntimeError(
                        f"unexpected outcome: {outcome!r}"
                    )
            logger.info(
                "[attempt %d/%d] VideoMaterializer: %d/%d shots successful",
                attempt, DEFAULT_ASSET_RETRIES,
                len(results_by_idx), len(shot_specs),
            )

        if len(results_by_idx) < len(shot_specs):
            failed_idxs = [
                i for i in range(len(shot_specs)) if i not in results_by_idx
            ]
            failed_shot_ids = [shot_specs[i]["shot_id"] for i in failed_idxs]
            first_exc = last_excs.get(failed_idxs[0])
            raise RuntimeError(
                f"VideoMaterializer: generate_clip failed for "
                f"{len(failed_idxs)}/{len(shot_specs)} shots after "
                f"{DEFAULT_ASSET_RETRIES} attempts: {failed_shot_ids}; "
                f"first error: {first_exc}"
            )

        # ── Stage 3: emit per-shot MediaAsset + group by scene ───────
        clips_by_scene_id: dict[str, list[bytes]] = {}
        for spec_idx, spec in enumerate(shot_specs):
            shot_id = spec["shot_id"]
            scene_id = spec["scene_id"]
            sys_vid_id = f"clip_{shot_id}"
            video_asset: dict[str, Any] = {"asset_id": sys_vid_id, "format": "mp4"}
            clip_bytes = results_by_idx[spec_idx]
            pending.append(MediaAsset(
                sys_id=sys_vid_id, data=clip_bytes,
                extension="mp4", uri_holder=video_asset,
            ))
            clips_by_scene_id.setdefault(scene_id, []).append(clip_bytes)

        # ── Stage 4: per-scene assembly (sequential local ffmpeg) ────
        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            clip_bytes_list = clips_by_scene_id.get(scene_id, [])

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
