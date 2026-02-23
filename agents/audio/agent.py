"""AudioAgent — generates narration, music, and ambience aligned with video.

Input:  AudioAgentInput (project_id, draft_id, screenplay, storyboard, video,
        constraints)
Output: AudioAgentOutput (AudioPackage with narration segments, music cues,
        ambience beds, per-scene mixes, metrics)

Audio alignment rules (three-layer):
  1. Semantic source: block (from Screenplay) — determines WHAT to say
  2. Timing alignment: shot (from Storyboard) — determines WHEN to say
  3. Hard boundary: scene (from Video) — determines MAX duration

Uses **skeleton-first mode**: most of the output is deterministic —
narration text/speaker come from screenplay, timing from storyboard/video,
IDs and asset placeholders are system-generated.  The LLM is only asked
to fill ``music_cue.mood`` and ``ambience_bed.description`` per scene.

Coupling: receives Screenplay + Storyboard + Video from upstream; output is
the final audio layer that gets combined with video.
"""

from __future__ import annotations

import json
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
    MusicCue,
    NarrationSegment,
)


class AudioAgent(BaseAgent[AudioAgentInput, AudioAgentOutput]):

    # ------------------------------------------------------------------
    # Skeleton-first mode
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: AudioAgentInput
    ) -> AudioAgentOutput | None:
        """Pre-build the audio package from screenplay + storyboard + video.

        Narration text and speaker are copied from screenplay dialogue/
        narration blocks.  Timing is estimated from storyboard shot
        durations.  Scene boundaries come from the video package.
        Only ``music_cue.mood`` and ``ambience_bed.description`` are left
        empty for the LLM.
        """
        sp = input_data.screenplay
        sb = input_data.storyboard
        vid = input_data.video

        if not sp or not sb or not vid:
            return None

        sp_content = sp.get("content", {})
        sb_content = sb.get("content", {})
        vid_content = vid.get("content", {})
        vid_scenes = vid_content.get("scenes", [])

        if not vid_scenes:
            return None

        # --- Build block → shot mapping from storyboard ---
        block_to_shot: dict[str, str] = {}
        for sb_scene in sb_content.get("scenes", []):
            for shot in sb_scene.get("shots", []):
                shot_id = shot.get("shot_id", "")
                for bid in shot.get("linked_blocks", []):
                    block_to_shot[bid] = shot_id

        # --- Build scene lookups ---
        vid_scene_map = {
            vs.get("scene_id", ""): vs for vs in vid_scenes
        }
        sp_scene_map = {
            s.get("scene_id", ""): s
            for s in sp_content.get("scenes", [])
        }

        narr_counter = 1
        scenes: list[AudioScene] = []

        for scene_order, vs in enumerate(vid_scenes, 1):
            scene_id = vs.get("scene_id", "")
            # Scene duration from video
            clip = vs.get("scene_clip_asset", {})
            scene_dur = clip.get("scene_duration_sec", 0.0)
            if scene_dur <= 0:
                scene_dur = sum(
                    seg.get("actual_duration_sec", 0.0)
                    for seg in vs.get("shot_segments", [])
                )

            sp_scene = sp_scene_map.get(scene_id, {})

            # --- Build narration segments from screenplay dialogue/narration ---
            # Two-pass: first estimate raw durations, then proportionally
            # compress if total exceeds scene_dur so every block gets narration.
            raw_entries: list[tuple[str, str, str, str, float]] = []
            total_raw = 0.0
            for block in sp_scene.get("blocks", []):
                block_id = block.get("block_id", "")
                block_type = block.get("block_type", "")
                if block_type not in ("dialogue", "narration", "monologue"):
                    continue
                text = block.get("text", "")
                speaker = block.get("character_name", "")
                if not speaker and block_type == "narration":
                    speaker = "Narrator"
                shot_id = block_to_shot.get(block_id, "")
                word_count = len(text.split()) if text else 0
                est_dur = max(word_count / 2.5, 1.0)
                raw_entries.append((block_id, shot_id, speaker, text, est_dur))
                total_raw += est_dur

            scale = 1.0
            if scene_dur > 0 and total_raw > scene_dur and raw_entries:
                scale = scene_dur / total_raw

            segments: list[NarrationSegment] = []
            current_sec = 0.0
            for block_id, shot_id, speaker, text, est_dur in raw_entries:
                scaled_dur = round(est_dur * scale, 2)
                scaled_dur = max(scaled_dur, 0.1)
                start = round(current_sec, 2)
                end = round(current_sec + scaled_dur, 2)
                if scene_dur > 0:
                    end = min(end, round(scene_dur, 2))

                segments.append(
                    NarrationSegment(
                        segment_id=f"narr_{narr_counter:03d}",
                        linked_block_id=block_id,
                        linked_shot_id=shot_id,
                        speaker=speaker,
                        text=text,
                        start_sec=start,
                        end_sec=end,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_narr_{scene_id}_{narr_counter:02d}",
                            uri="placeholder",
                            format="wav",
                            duration_sec=round(end - start, 2),
                            sample_rate=44100,
                        ),
                    )
                )
                narr_counter += 1
                current_sec = end

            scenes.append(
                AudioScene(
                    scene_id=scene_id,
                    order=scene_order,
                    scene_duration_sec=scene_dur,
                    narration_segments=segments,
                    music_cue=MusicCue(
                        cue_id=f"music_{scene_id}",
                        scene_id=scene_id,
                        mood="",  # CREATIVE — LLM fills
                        start_sec=0.0,
                        end_sec=scene_dur,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_music_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            duration_sec=scene_dur,
                            sample_rate=44100,
                        ),
                    ),
                    ambience_bed=AmbienceBed(
                        ambience_id=f"amb_{scene_id}",
                        scene_id=scene_id,
                        description="",  # CREATIVE — LLM fills
                        start_sec=0.0,
                        end_sec=scene_dur,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_amb_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            duration_sec=scene_dur,
                            sample_rate=44100,
                        ),
                    ),
                    mix=AudioMix(
                        mix_id=f"mix_{scene_id}",
                        scene_id=scene_id,
                        duration_sec=scene_dur,
                        audio_asset=AudioAsset(
                            asset_id=f"aud_mix_{scene_id}",
                            uri="placeholder",
                            format="wav",
                            duration_sec=scene_dur,
                            sample_rate=44100,
                        ),
                    ),
                )
            )

        total_dur = sum(s.scene_duration_sec for s in scenes)

        output = AudioAgentOutput()
        output.content = AudioContent(
            scenes=scenes,
            final_audio_asset=AudioAsset(
                asset_id="aud_final",
                uri="placeholder",
                format="wav",
                duration_sec=total_dur,
                sample_rate=44100,
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
            '{\n  "scenes": [\n'
            + ",\n".join(scene_entries)
            + "\n  ]\n}"
        )

        return (
            "The system has pre-built all structural fields (IDs, timing, "
            "narration text/speaker, audio asset placeholders).  Your ONLY "
            "job is to write the music mood and ambience description for "
            "each scene.\n\n"
            "=== SCREENPLAY CONTEXT ===\n"
            f"{context}\n\n"
            "=== RULES ===\n"
            "- music_mood: 3-6 keywords describing the musical mood / style "
            "(e.g. 'melancholic, ambient, solo piano').\n"
            "- ambience_description: Short description of ambient sounds "
            "(e.g. 'Ocean waves crashing, distant seagulls, wind').\n\n"
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
        narr_dur = sum(
            seg.end_sec - seg.start_sec
            for s in c.scenes
            for seg in s.narration_segments
        )
        music_dur = sum(
            s.music_cue.end_sec - s.music_cue.start_sec
            for s in c.scenes
            if s.music_cue.cue_id
        )
        output.metrics.scene_count = len(c.scenes)
        output.metrics.narration_segment_count = narr_count
        output.metrics.total_narration_duration_sec = round(narr_dur, 2)
        output.metrics.total_music_duration_sec = round(music_dur, 2)

    # Quality evaluation has been moved to AudioEvaluator
    # (see evaluator.py in this package).
