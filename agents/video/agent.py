"""VideoAgent — renders keyframes into video clips.

Input:  VideoAgentInput (screenplay, keyframes, constraints)
Output: VideoAgentOutput (VideoPackage with shot_segments, transition_plan,
        scene_clip_assets, metrics)

Coupling: receives Screenplay + Keyframes from shared assets; output feeds AudioAgent.

Uses **LLM-free skeleton mode**: the entire output is deterministic — scene IDs,
shot segments, transitions, and asset placeholders are all derived from the
screenplay (unified shots).  No LLM call is made.  The VideoAgent schema has zero
creative fields.

Note: Actual video generation requires a backend (Wan2.6, Runway, etc.).
This agent plans the generation and manages the video assembly pipeline.
Wan2.6 supports audio-visual sync.
"""

from __future__ import annotations

from ..base_agent import BaseAgent
from .schema import (
    SceneClipAsset,
    ShotSegment,
    TransitionPlan,
    VideoAgentInput,
    VideoAgentOutput,
    VideoAsset,
    VideoContent,
    VideoScene,
)


class VideoAgent(BaseAgent[VideoAgentInput, VideoAgentOutput]):

    async def generate(
        self,
        input_data: VideoAgentInput,
        *,
        rework_notes: str = "",
    ) -> VideoAgentOutput:
        """LLM-free: deterministic skeleton from screenplay is the final output.

        VideoAgent's output has zero creative fields — every value is
        derived from the screenplay structure. ``rework_notes`` are
        ignored because there is no LLM to give them to.
        """
        output = self.build_skeleton(input_data)
        self.recompute_metrics(output)
        return output

    # ------------------------------------------------------------------
    # Skeleton-first mode (LLM-free — all fields are structural)
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: VideoAgentInput
    ) -> VideoAgentOutput:
        """Build the complete video package deterministically from screenplay.

        VideoAgent's output has zero creative fields — everything (scene IDs,
        shot segments, transitions, asset placeholders) is derived from the
        screenplay.  No LLM call is needed.
        """
        sp = input_data.screenplay
        sp_content = sp.get("content", {})
        sp_scenes = sp_content.get("scenes", [])

        if not sp_scenes:
            # VideoAgent has no legacy/full-LLM fallback path — without
            # a non-empty screenplay there is nothing to assemble.
            # Returning None here would make BaseAgent fall through to
            # ``_run_legacy_mode`` → ``build_user_prompt`` which is not
            # implemented for this agent and would crash with a confusing
            # NotImplementedError. Raise a clear error so the caller (and
            # the director) sees exactly what went wrong.
            raise ValueError(
                "VideoAgent.build_skeleton: upstream screenplay has "
                "zero scenes. Check that ScreenplayAgent's last execution "
                "actually produced content (status COMPLETED, non-empty "
                "content.scenes) and that InputResolver matched the "
                "[screenplay] label to it."
            )

        # The legacy ``VideoAgentInput.constraints`` slot was deleted in
        # the Phase A schema slim-down. Defaults below match the prior
        # constants (24 fps, 1024x576, "auto" transitions).
        fps = 24
        width = 1024
        height = 576
        transition_policy = "auto"

        scenes: list[VideoScene] = []

        for scene_order, sp_scene in enumerate(sp_scenes, 1):
            scene_id = sp_scene.get("scene_id", f"sc_{scene_order:03d}")
            sp_shots = sp_scene.get("shots", [])

            # --- Shot segments ---
            segments: list[ShotSegment] = []
            for shot_order, sp_shot in enumerate(sp_shots, 1):
                shot_id = sp_shot.get("shot_id", "")
                segments.append(
                    ShotSegment(
                        shot_id=shot_id,
                        order=shot_order,
                        video_asset=VideoAsset(
                            asset_id=f"vid_{shot_id}",
                            uri="placeholder",
                            width=width,
                            height=height,
                            format="mp4",
                            fps=fps,
                        ),
                    )
                )

            # --- Transition plan (between consecutive shots) ---
            transitions: list[TransitionPlan] = []
            for i in range(len(segments) - 1):
                from_id = segments[i].shot_id
                to_id = segments[i + 1].shot_id
                if transition_policy == "soft":
                    transitions.append(
                        TransitionPlan(
                            from_shot_id=from_id,
                            to_shot_id=to_id,
                            transition_type="dissolve",
                        )
                    )
                else:
                    transitions.append(
                        TransitionPlan(
                            from_shot_id=from_id,
                            to_shot_id=to_id,
                            transition_type="cut",
                        )
                    )

            scenes.append(
                VideoScene(
                    scene_id=scene_id,
                    order=scene_order,
                    shot_segments=segments,
                    transition_plan=transitions,
                    scene_clip_asset=SceneClipAsset(
                        asset_id=f"clip_{scene_id}",
                        uri="placeholder",
                        format="mp4",
                    ),
                )
            )

        output = VideoAgentOutput()
        output.content = VideoContent(
            scenes=scenes,
            final_video_asset=VideoAsset(
                asset_id="final_video",
                uri="placeholder",
                width=width,
                height=height,
                format="mp4",
                fps=fps,
            ),
        )
        return output

    # ------------------------------------------------------------------
    # Metrics & validation
    # ------------------------------------------------------------------

    def recompute_metrics(self, output: VideoAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        for scene in c.scenes:
            self._normalize_order(scene.shot_segments)
        scene_count = len(c.scenes)
        shot_count = sum(len(s.shot_segments) for s in c.scenes)
        output.metrics.scene_count = scene_count
        output.metrics.shot_segment_count = shot_count

    # Quality evaluation has been moved to VideoEvaluator
    # (see evaluator.py in this package).
