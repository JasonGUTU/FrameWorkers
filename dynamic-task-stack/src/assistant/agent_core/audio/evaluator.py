"""Evaluator for AudioAgent output (Audio Package).

All three layers:

Layer 1 -- structural checks:
  - Upstream cross-check (scene_ids match video)
  - Timing: narration must not exceed scene duration
  - Narration segments must have text + speaker
  - Upstream cross-check (linked_block_id exists in screenplay)
  - Metrics consistency (scene_count, narration_segment_count)
  - Timing accuracy (no narration overlap, music/ambience span scene)
  - Required content (non-empty scenes, music mood, ambience description)

Layer 2 -- creative assessment:
  - narration_alignment: narration faithfully reproduces screenplay
  - music_mood_fit: music cue moods match emotional arc

Layer 3 -- post-materialization asset checks:
  - tts_generation_success: narration segment success rate
  - music_generation_success: music cue success rate
  - mix_completeness: scene mixes + final audio assembly
  - audio_quality: (TODO) waveform analysis (SNR, clipping)
  - timing_accuracy: (TODO) actual vs planned duration comparison
"""

from __future__ import annotations

import json
from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import AudioAgentOutput


class AudioEvaluator(BaseEvaluator[AudioAgentOutput]):

    creative_dimensions = [
        ("narration_alignment", "Does the narration faithfully reproduce the screenplay dialogue/narration? Are speakers correctly matched to characters?"),
        ("music_mood_fit", "Do the music cue moods match the emotional arc of each scene? Does the ambience description fit the location and atmosphere?"),
    ]

    def _build_creative_context(self, output, upstream):
        sp_data = (upstream or {}).get("screenplay", {})
        if sp_data:
            return f"Screenplay:\n{json.dumps(sp_data, ensure_ascii=False, indent=2)}"
        return ""

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: AudioAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural validation for Audio Package."""
        errors: list[str] = []
        c = output.content

        # --- Upstream cross-check: scene_ids must match video ---
        if upstream and "video" in upstream:
            vid_content = upstream["video"].get("content", {})
            vid_scene_ids = {
                s.get("scene_id", "") for s in vid_content.get("scenes", [])
            }
            aud_scene_ids = {s.scene_id for s in c.scenes}
            self._check_id_coverage(
                errors, "audio vs video scenes",
                vid_scene_ids, aud_scene_ids,
            )

        # --- Timing: narration must not exceed scene duration ---
        for scene in c.scenes:
            for seg in scene.narration_segments:
                if seg.end_sec > scene.scene_duration_sec + 0.1:
                    errors.append(
                        f"scene {scene.scene_id} narration segment "
                        f"{seg.segment_id} end_sec ({seg.end_sec}) exceeds "
                        f"scene_duration_sec ({scene.scene_duration_sec})"
                    )
                if seg.start_sec >= seg.end_sec:
                    errors.append(
                        f"narration segment {seg.segment_id}: "
                        f"start_sec ({seg.start_sec}) >= end_sec ({seg.end_sec})"
                    )

            # Music cue must not exceed scene duration
            mc = scene.music_cue
            if mc.end_sec > scene.scene_duration_sec + 0.1:
                errors.append(
                    f"scene {scene.scene_id} music_cue end_sec ({mc.end_sec}) "
                    f"exceeds scene_duration_sec ({scene.scene_duration_sec})"
                )

            # Ambience bed must not exceed scene duration
            ab = scene.ambience_bed
            if ab.end_sec > scene.scene_duration_sec + 0.1:
                errors.append(
                    f"scene {scene.scene_id} ambience_bed end_sec "
                    f"({ab.end_sec}) exceeds scene_duration_sec "
                    f"({scene.scene_duration_sec})"
                )

        # --- Narration: dialogue/narration blocks must have text + speaker ---
        for scene in c.scenes:
            for seg in scene.narration_segments:
                if not seg.text:
                    errors.append(
                        f"narration segment {seg.segment_id} has empty text"
                    )
                if not seg.speaker:
                    errors.append(
                        f"narration segment {seg.segment_id} has empty speaker"
                    )

        # --- Upstream cross-check: linked_block_id must exist in screenplay ---
        if upstream and "screenplay" in upstream:
            sp_content = upstream["screenplay"].get("content", {})
            all_block_ids: set[str] = set()
            for sp_scene in sp_content.get("scenes", []):
                for block in sp_scene.get("blocks", []):
                    all_block_ids.add(block.get("block_id", ""))
            if all_block_ids:
                for scene in c.scenes:
                    for seg in scene.narration_segments:
                        if (
                            seg.linked_block_id
                            and seg.linked_block_id not in all_block_ids
                        ):
                            errors.append(
                                f"narration segment {seg.segment_id} references "
                                f"unknown block {seg.linked_block_id}"
                            )

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(
            errors, "narration_segment_count", output.metrics.narration_segment_count,
            sum(len(s.narration_segments) for s in c.scenes),
        )

        # --- Timing accuracy ---
        for scene in c.scenes:
            # Narration segments should not overlap
            sorted_segs = sorted(
                scene.narration_segments, key=lambda s: s.start_sec
            )
            for i in range(len(sorted_segs) - 1):
                if sorted_segs[i].end_sec > sorted_segs[i + 1].start_sec + 0.05:
                    errors.append(
                        f"scene {scene.scene_id}: narration segments "
                        f"{sorted_segs[i].segment_id} and "
                        f"{sorted_segs[i + 1].segment_id} overlap "
                        f"({sorted_segs[i].end_sec} > "
                        f"{sorted_segs[i + 1].start_sec})"
                    )

            # Music cue should span the scene
            mc = scene.music_cue
            if mc.cue_id and mc.start_sec > 0.1:
                errors.append(
                    f"scene {scene.scene_id} music_cue starts at "
                    f"{mc.start_sec}, expected near 0"
                )

            # Ambience bed should span the scene
            ab = scene.ambience_bed
            if ab.ambience_id and ab.start_sec > 0.1:
                errors.append(
                    f"scene {scene.scene_id} ambience_bed starts at "
                    f"{ab.start_sec}, expected near 0"
                )

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.music_cue.mood:
                errors.append(
                    f"scene {scene.scene_id} music_cue has empty mood"
                )
            if not scene.ambience_bed.description:
                errors.append(
                    f"scene {scene.scene_id} ambience_bed has empty description"
                )

        return errors

    # ------------------------------------------------------------------
    # Layer 3 -- Post-materialization asset evaluation
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
        upstream: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Check TTS narration, music, ambience, scene mixes, and final audio."""
        content = asset_data.get("content", {})
        scenes = content.get("scenes", [])

        # --- TTS narration segments ---
        narr_planned = 0
        narr_success = 0
        narr_error = 0
        for scene in scenes:
            for seg in scene.get("narration_segments", []):
                uri = seg.get("audio_asset", {}).get("uri", "")
                narr_planned += 1
                status = check_uri(uri)
                if status == "success":
                    narr_success += 1
                elif status == "error":
                    narr_error += 1

        # --- Music cues ---
        music_planned = 0
        music_success = 0
        for scene in scenes:
            mc = scene.get("music_cue", {})
            if mc.get("cue_id"):
                music_planned += 1
                if check_uri(mc.get("audio_asset", {}).get("uri", "")) == "success":
                    music_success += 1

        # --- Ambience beds ---
        amb_planned = 0
        amb_success = 0
        for scene in scenes:
            ab = scene.get("ambience_bed", {})
            if ab.get("ambience_id"):
                amb_planned += 1
                if check_uri(ab.get("audio_asset", {}).get("uri", "")) == "success":
                    amb_success += 1

        # --- Scene mixes ---
        mix_planned = 0
        mix_success = 0
        for scene in scenes:
            mx = scene.get("mix", {})
            if mx.get("mix_id"):
                mix_planned += 1
                if check_uri(mx.get("audio_asset", {}).get("uri", "")) == "success":
                    mix_success += 1

        # --- Final audio ---
        final = content.get("final_audio_asset", {})
        final_ok = check_uri(final.get("uri", "")) == "success"

        # --- Compute scores ---
        narr_rate = narr_success / narr_planned if narr_planned else 0.0
        music_rate = music_success / music_planned if music_planned else 0.0
        mix_rate = mix_success / mix_planned if mix_planned else 0.0

        dimensions = {
            "tts_generation_success": {
                "score": narr_rate,
                "notes": [
                    f"{narr_success}/{narr_planned} narration segments generated",
                    *(
                        [f"{narr_error} segments failed with errors"]
                        if narr_error
                        else []
                    ),
                ],
            },
            "music_generation_success": {
                "score": music_rate,
                "notes": [
                    f"{music_success}/{music_planned} music cues generated",
                ],
            },
            "mix_completeness": {
                "score": (
                    (mix_rate + (1.0 if final_ok else 0.0)) / 2.0
                ),
                "notes": [
                    f"{mix_success}/{mix_planned} scene mixes created",
                    f"ambience: {amb_success}/{amb_planned}",
                    f"final audio: {'OK' if final_ok else 'MISSING'}",
                ],
            },
            "audio_quality": {
                "score": 1.0,
                "notes": ["audio quality check not yet implemented"],
            },
            "timing_accuracy": {
                "score": 1.0,
                "notes": ["timing accuracy check not yet implemented"],
            },
        }

        overall_pass = narr_rate >= self.ASSET_PASS_THRESHOLD and music_rate >= 0.5
        summary = (
            f"Audio asset eval: TTS {narr_success}/{narr_planned} "
            f"({narr_rate:.0%}), music {music_success}/{music_planned}, "
            f"mixes {mix_success}/{mix_planned}, "
            f"final={'OK' if final_ok else 'MISSING'}."
        )

        return {
            "dimensions": dimensions,
            "overall_pass": overall_pass,
            "summary": summary,
        }
