"""VideoAgent — renders keyframes into video clips.

Input:  VideoAgentInput (project_id, draft_id, storyboard, keyframes, constraints)
Output: VideoAgentOutput (VideoPackage with shot_segments, transition_plan,
        scene_clip_assets, metrics)

Coupling: receives Storyboard + Keyframes from upstream; output feeds AudioAgent.

Uses **LLM-free skeleton mode**: the entire output is deterministic — scene IDs,
shot segments, durations, transitions, and asset placeholders are all derived
from the storyboard.  No LLM call is made.  The VideoAgent schema has zero
creative fields.

Note: Actual video generation requires a backend (Wan2.6, Runway, etc.).
This agent plans the generation and manages the video assembly pipeline.
Wan2.6 supports audio-visual sync.
"""

from __future__ import annotations

from typing import Any

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

    @property
    def skeleton_is_complete(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Skeleton-first mode (LLM-free — all fields are structural)
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: VideoAgentInput
    ) -> VideoAgentOutput | None:
        """Build the complete video package deterministically from storyboard.

        VideoAgent's output has zero creative fields — everything (scene IDs,
        shot segments, durations, transitions, asset placeholders) is derived
        from the storyboard.  No LLM call is needed.
        """
        sb = input_data.storyboard
        sb_content = sb.get("content", {})
        sb_scenes = sb_content.get("scenes", [])

        if not sb_scenes:
            return None  # fall back to legacy mode

        fps = input_data.constraints.fps
        parts = input_data.constraints.output_resolution.split("x")
        width = int(parts[0]) if len(parts) == 2 else 1024
        height = int(parts[1]) if len(parts) == 2 else 576
        transition_policy = input_data.constraints.transition_policy

        scenes: list[VideoScene] = []
        total_duration = 0.0

        for scene_order, sb_scene in enumerate(sb_scenes, 1):
            scene_id = sb_scene.get("scene_id", f"sc_{scene_order:03d}")
            sb_shots = sb_scene.get("shots", [])

            # --- Shot segments ---
            segments: list[ShotSegment] = []
            for shot_order, sb_shot in enumerate(sb_shots, 1):
                shot_id = sb_shot.get("shot_id", "")
                duration = sb_shot.get("estimated_duration_sec", 3.0)
                segments.append(
                    ShotSegment(
                        shot_id=shot_id,
                        order=shot_order,
                        estimated_duration_sec=duration,
                        actual_duration_sec=duration,
                        video_asset=VideoAsset(
                            asset_id=f"vid_{shot_id}",
                            uri="placeholder",
                            width=width,
                            height=height,
                            format="mp4",
                            duration_sec=duration,
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
                            duration_sec=0.5,
                        )
                    )
                else:
                    transitions.append(
                        TransitionPlan(
                            from_shot_id=from_id,
                            to_shot_id=to_id,
                            transition_type="cut",
                            duration_sec=0.0,
                        )
                    )

            scene_dur = sum(seg.actual_duration_sec for seg in segments)
            scenes.append(
                VideoScene(
                    scene_id=scene_id,
                    order=scene_order,
                    shot_segments=segments,
                    transition_plan=transitions,
                    scene_clip_asset=SceneClipAsset(
                        asset_id=f"clip_{scene_id}",
                        uri="placeholder",
                        scene_duration_sec=scene_dur,
                        format="mp4",
                    ),
                )
            )
            total_duration += scene_dur

        output = VideoAgentOutput()
        output.content = VideoContent(
            scenes=scenes,
            final_video_asset=VideoAsset(
                asset_id="final_video",
                uri="placeholder",
                width=width,
                height=height,
                format="mp4",
                duration_sec=total_duration,
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
        total_dur = sum(
            seg.actual_duration_sec
            for s in c.scenes
            for seg in s.shot_segments
        )
        output.metrics.scene_count = scene_count
        output.metrics.shot_segment_count = shot_count
        output.metrics.total_duration_sec = total_dur
        output.metrics.avg_shot_duration_sec = (
            total_dur / shot_count if shot_count else 0.0
        )

    # Quality evaluation has been moved to VideoEvaluator
    # (see evaluator.py in this package).
