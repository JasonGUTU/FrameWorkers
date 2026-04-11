"""AudioAgent — generates narration, music, and ambience aligned with video.

Input:  AudioAgentInput (screenplay, video, constraints)
Output: AudioAgentOutput (AudioPackage with narration segments, music cues,
        ambience beds, per-scene mixes, final muxed delivery, metrics)

Audio sourcing rules:
  1. Semantic source: screenplay shots (dialogue/narration/monologue text)
  2. Each scene gets one music cue and one ambience bed.

Uses **skeleton-first mode**: most of the output is deterministic —
narration text/speaker come from screenplay, IDs and asset placeholders
are system-generated.  The LLM is only asked to fill ``music_cue.mood``
and ``ambience_bed.description`` per scene.

Coupling: receives unified Screenplay + Video from shared assets; output is
the final audio layer that gets combined with video.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    AmbienceBed,
    AudioAgentInput,
    AudioAgentOutput,
    AudioAsset,
    AudioContent,
    AudioMix,
    AudioScene,
    DeliveryVideoAsset,
    MusicCue,
    NarrationSegment,
)


class AudioAgent(BaseAgent[AudioAgentInput, AudioAgentOutput]):

    # ------------------------------------------------------------------
    # Skeleton-first mode
    # ------------------------------------------------------------------

    async def generate(
        self,
        input_data: AudioAgentInput,
        *,
        rework_notes: str = "",
    ) -> AudioAgentOutput:
        """Build the deterministic skeleton from screenplay + final video,
        then ask the LLM to fill the music_mood / ambience_description
        creative fields per scene.
        """
        skeleton = self.build_skeleton(input_data)
        output = await self._llm_fill_creative(input_data, skeleton, rework_notes)
        self.recompute_metrics(output)
        return output

    def build_skeleton(
        self, input_data: AudioAgentInput
    ) -> AudioAgentOutput:
        """Pre-build the audio package from screenplay + video.

        Narration text and speaker are copied from screenplay shots whose
        block_type is dialogue/narration/monologue.  Only ``music_cue.mood``
        and ``ambience_bed.description`` are left empty for the LLM.
        """
        sp = input_data.screenplay
        vid = input_data.final_video

        if not sp or not vid:
            # AudioAgent has no legacy/full-LLM fallback path — without
            # the upstream screenplay AND video packages there is nothing
            # to build. Raise a clear error rather than returning None,
            # because returning None makes BaseAgent fall through to
            # ``_run_legacy_mode`` → ``build_user_prompt`` which is not
            # implemented for this agent and would crash with a
            # confusing NotImplementedError.
            missing = []
            if not sp:
                missing.append("screenplay")
            if not vid:
                missing.append("final_video")
            raise ValueError(
                "AudioAgent.build_skeleton: required upstream artifacts "
                f"missing from input: {missing}. Check that InputResolver "
                f"matched the [screenplay] / [final_video] labels for this "
                f"task and that those artifacts exist in the workspace."
            )

        sp_content = sp.get("content", {})
        vid_content = vid.get("content", {})
        vid_scenes = vid_content.get("scenes", [])

        if not vid_scenes:
            # Same reasoning as the missing-screenplay-or-video raise
            # above: AudioAgent has no legacy fallback. The earlier
            # commit af341e8 raised on the missing-upstream check but
            # missed this empty-vid_scenes path. Make it loud too so
            # the director sees a real error instead of a confusing
            # NotImplementedError on the fall-through to
            # ``build_user_prompt``.
            raise ValueError(
                "AudioAgent.build_skeleton: upstream final_video has "
                "zero scenes. Check that VideoAgent's last execution "
                "actually produced content (status COMPLETED, non-empty "
                "content.scenes) and that InputResolver matched the "
                "[final_video] label to it."
            )

        sp_scene_map = {
            s.get("scene_id", ""): s
            for s in sp_content.get("scenes", [])
        }

        narr_counter = 1
        scenes: list[AudioScene] = []

        for scene_order, vs in enumerate(vid_scenes, 1):
            scene_id = vs.get("scene_id", "")
            sp_scene = sp_scene_map.get(scene_id, {})

            segments: list[NarrationSegment] = []
            for shot in sp_scene.get("shots", []):
                block_type = shot.get("block_type", "")
                if block_type not in ("dialogue", "narration", "monologue"):
                    continue
                text = shot.get("text", "")
                speaker = shot.get("character_name", "")
                if not speaker and block_type == "narration":
                    speaker = "Narrator"
                shot_id = str(shot.get("shot_id", "") or "")

                segments.append(
                    NarrationSegment(
                        segment_id=f"narr_{narr_counter:03d}",
                        linked_shot_id=shot_id,
                        speaker=speaker,
                        text=text,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_narr_{scene_id}_{narr_counter:02d}",
                            uri="placeholder",
                            format="wav",
                            sample_rate=44100,
                        ),
                    )
                )
                narr_counter += 1

            scenes.append(
                AudioScene(
                    scene_id=scene_id,
                    order=scene_order,
                    narration_segments=segments,
                    music_cue=MusicCue(
                        cue_id=f"music_{scene_id}",
                        scene_id=scene_id,
                        mood="",  # CREATIVE — LLM fills
                        audio_asset=AudioAsset(
                            asset_id=f"aud_music_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            sample_rate=44100,
                        ),
                    ),
                    ambience_bed=AmbienceBed(
                        ambience_id=f"amb_{scene_id}",
                        scene_id=scene_id,
                        description="",  # CREATIVE — LLM fills
                        audio_asset=AudioAsset(
                            asset_id=f"aud_amb_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            sample_rate=44100,
                        ),
                    ),
                    mix=AudioMix(
                        mix_id=f"mix_{scene_id}",
                        scene_id=scene_id,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_mix_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            sample_rate=44100,
                        ),
                    ),
                )
            )

        output = AudioAgentOutput()
        output.content = AudioContent(
            scenes=scenes,
            final_audio_asset=AudioAsset(
                asset_id="aud_final",
                uri="placeholder",
                format="wav",
                sample_rate=44100,
            ),
            final_delivery_asset=DeliveryVideoAsset(
                asset_id="delivery_final",
                uri="placeholder",
                format="mp4",
            ),
        )
        return output

    def build_creative_prompt(
        self, input_data: AudioAgentInput, skeleton: AudioAgentOutput
    ) -> str:
        """Build a compact prompt — LLM only fills mood and ambience description."""
        sp = input_data.screenplay
        sp_content = sp.get("content", {})

        # Provide screenplay context for mood / atmosphere
        context_parts: list[str] = []
        for sp_scene in sp_content.get("scenes", []):
            scene_id = sp_scene.get("scene_id", "")
            summary = sp_scene.get("summary", "")
            heading = sp_scene.get("heading", {})
            scene_end = sp_scene.get("scene_end", {})
            context_parts.append(
                f"--- {scene_id} ---\n"
                f"heading: {heading.get('location_name', '')} "
                f"({heading.get('interior_exterior', '')} / "
                f"{heading.get('time_of_day', '')})\n"
                f"summary: {summary}\n"
                f"scene_end: turn={scene_end.get('turn', '')}, "
                f"emotional_shift={scene_end.get('emotional_shift', '')}"
            )
        context = "\n\n".join(context_parts)

        # Build template — one entry per scene
        scene_entries = [
            f'    {{"scene_id": "{scene.scene_id}", '
            f'"music_mood": "<FILL>", '
            f'"ambience_description": "<FILL>"}}'
            for scene in skeleton.content.scenes
        ]
        template = (
            '{\n'
            '  "scenes": [\n'
            + ",\n".join(scene_entries)
            + "\n  ]\n}"
        )

        return (
            "The system has pre-built all structural fields (IDs, timing, "
            "narration text/speaker, audio asset placeholders).  Your job is:\n"
            "Write music mood and ambience description for each scene.\n"
            "Do NOT include an artifact_caption block — the system generates it.\n\n"
            "=== SCREENPLAY CONTEXT ===\n"
            f"{context}\n\n"
            "=== RULES ===\n"
            "- music_mood: 3-6 keywords describing the musical mood / style "
            "(e.g. 'melancholic, ambient, solo piano').\n"
            "- ambience_description: Short description of ambient sounds "
            "(e.g. 'Ocean waves crashing, distant seagulls, wind').\n"
            "- Output must be STRICT JSON that parses with json.loads.\n"
            "- Return exactly ONE JSON object and NOTHING else.\n"
            "- Do NOT add any extra keys or lines (no comments, no markdown, no code fences).\n"
            "- Do NOT include type annotations or schema hints such as `TypeOf: string`.\n"
            "- Every scene object MUST contain ONLY: scene_id, music_mood, ambience_description.\n\n"
            "=== OUTPUT FORMAT ===\n"
            f"{template}\n\n"
            "Return JSON only."
        )

    def fill_creative(
        self, skeleton: AudioAgentOutput, creative: dict
    ) -> AudioAgentOutput:
        """Merge LLM output (mood + ambience_description) into skeleton."""
        scene_map = {
            s.get("scene_id", ""): s
            for s in creative.get("scenes", [])
        }

        for scene in skeleton.content.scenes:
            sc_data = scene_map.get(scene.scene_id, {})
            scene.music_cue.mood = sc_data.get("music_mood", "")
            scene.ambience_bed.description = sc_data.get(
                "ambience_description", ""
            )

        return skeleton

    def system_prompt(self) -> str:
        return (
            "You are AudioAgent — an audio design specialist for film.\n"
            "Follow the instructions in the user message exactly."
        )

    def recompute_metrics(self, output: AudioAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        narr_count = sum(len(s.narration_segments) for s in c.scenes)
        output.metrics.scene_count = len(c.scenes)
        output.metrics.narration_segment_count = narr_count

    # Quality evaluation has been moved to AudioEvaluator
    # (see evaluator.py in this package).
