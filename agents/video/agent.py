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

    @property
    def skeleton_is_complete(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Skeleton-first mode (LLM-free — all fields are structural)
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: VideoAgentInput
    ) -> VideoAgentOutput | None:
        """Build the complete video package deterministically from screenplay.

        VideoAgent's output has zero creative fields — everything (scene IDs,
        shot segments, transitions, asset placeholders) is derived from the
        screenplay.  No LLM call is needed.
        """
        sp = input_data.screenplay
        sp_content = sp.get("content", {})
        sp_scenes = sp_content.get("scenes", [])

        if not sp_scenes:
            return None  # fall back to legacy mode

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
        # Build top-level artifact_caption (for the JSON snapshot)
        from ..common_schema import ArtifactCaption
        output.artifact_caption = ArtifactCaption(
            what=(
                f"A manifest of the assembled video for the whole story: "
                f"{scene_count} scene(s), {shot_count} shot clip(s). It "
                f"catalogs the per-shot clips, the per-scene cuts, and the "
                f"single complete final video file. It is the document "
                f"describing the finished video; downstream audio mixing "
                f"reads it to mux audio against the final video file."
            ),
            why="Deterministic assembly from screenplay shot structure; no creative LLM decisions.",
            scope="global",
        )
        # Build per_artifact_captions for individual video clip files (sys_id → caption dict).
        # ArtifactWriter uses this to register each clip with its own ArtifactRef.
        pac: dict = {}
        for scene in c.scenes:
            scene_id = scene.scene_id or ""
            for seg in scene.shot_segments:
                shot_id = seg.shot_id or ""
                if not shot_id:
                    continue
                pac[f"clip_{shot_id}"] = {
                    "what": (
                        f"A moving video clip rendered for shot {shot_id} of "
                        f"the screenplay timeline. It is the animated form of "
                        f"that shot's planned starting frame, covering only "
                        f"this single shot of the story."
                    ),
                    "why": (
                        f"One such clip exists per shot in the screenplay. "
                        f"Used downstream when assembling the per-scene cuts "
                        f"and the final continuous video."
                    ),
                    "scope": f"shot:{shot_id}",
                }
            if scene_id:
                pac[f"clip_{scene_id}"] = {
                    "what": (
                        f"A video clip assembled by concatenating all the "
                        f"per-shot clips of scene {scene_id} in screenplay "
                        f"order. It represents the visual flow of that whole "
                        f"scene, but is not the final deliverable."
                    ),
                    "why": (
                        f"Intermediate per-scene assembly used as input when "
                        f"building the complete final video; not the per-shot "
                        f"clips and not the final delivery."
                    ),
                    "scope": f"scene:{scene_id}",
                }
        pac["clip_final"] = {
            "what": (
                f"The single complete video file ({shot_count} shots) "
                f"produced by concatenating every scene clip in screenplay "
                f"order. This is the finished, watchable video for the whole "
                f"story — there is exactly one of these."
            ),
            "why": (
                f"The final visual deliverable. Downstream the audio mixing "
                f"step uses this as the video track when muxing the final "
                f"audio + video product."
            ),
            "scope": "global",
        }
        output.per_artifact_captions = pac

    # Quality evaluation has been moved to VideoEvaluator
    # (see evaluator.py in this package).
