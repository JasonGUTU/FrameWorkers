"""Evaluator for AudioAgent output (Audio Package).

All three layers (output-internal only — no cross-validation against
upstream artifacts):

Layer 1 -- structural checks:
  - Narration segments must have text + speaker
  - Metrics consistency (scene_count, narration_segment_count)
  - Required content (non-empty scenes, music mood, ambience description)

Layer 2 -- creative assessment:
  - narration_alignment: narration is internally well-formed (clear
    speakers, coherent text)
  - music_mood_fit: music cue moods are coherent with the audio
    package's own scene tone

Layer 3 -- post-materialization asset checks:
  - tts_generation_success: narration segment success rate
  - music_generation_success: music cue success rate
  - mix_completeness: scene mixes + final audio assembly
  - audio_quality: (TODO) waveform analysis (SNR, clipping)
"""

from __future__ import annotations

from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import AudioAgentOutput


class AudioEvaluator(BaseEvaluator[AudioAgentOutput]):

    creative_dimensions = [
        ("narration_clarity", "Are the narration segments internally well-formed: clear speaker assignments, coherent text, no obvious gaps?"),
        ("music_mood_fit", "Do the music cue moods cohere with each scene's described tone? Does the ambience description fit?"),
    ]

    async def evaluate_creative(self, output: AudioAgentOutput) -> dict[str, Any]:
        """Drop ``narration_clarity`` from the dimensions when the audio
        package has no narration at all.

        Without this override the L2 LLM is asked to grade narration
        clarity on a purely visual short (e.g. e2e1's watchmaker brief,
        which intentionally has zero dialogue), looks at an empty
        ``narration_segments`` list, and *non-deterministically* either
        scores it 0 / declares ``overall_pass=false`` ("I can't grade
        what isn't there") or vacuously passes — flaking the e2e tests
        ~50% of the time. Empty narration is a valid creative choice,
        so we just don't ask the LLM about it in that case.
        """
        has_narration = any(
            scene.narration_segments for scene in output.content.scenes
        )
        if has_narration:
            return await super().evaluate_creative(output)

        # Vacuous case: shadow the class attribute with an instance attr
        # that omits narration_clarity, then restore in finally so the
        # next call (e.g. on a different output with real narration)
        # falls back to the full class-level list.
        self.creative_dimensions = [
            (name, desc)
            for (name, desc) in type(self).creative_dimensions
            if name != "narration_clarity"
        ]
        try:
            return await super().evaluate_creative(output)
        finally:
            try:
                del self.creative_dimensions
            except AttributeError:
                pass

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: AudioAgentOutput) -> list[str]:
        """Rule-based structural validation for Audio Package."""
        errors: list[str] = []
        c = output.content

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

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(
            errors, "narration_segment_count", output.metrics.narration_segment_count,
            sum(len(s.narration_segments) for s in c.scenes),
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
        # Final delivery (muxed video+audio) is checked only if the agent's
        # own output declares one. We do not look at upstream video artifacts.
        delivery = content.get("final_delivery_asset", {})
        delivery_ok = check_uri(delivery.get("uri", "")) == "success"
        delivery_expected = bool(delivery.get("uri"))

        # --- Compute scores ---
        # Vacuous case: when nothing is planned (e.g. a purely visual short
        # with no dialogue → 0 narration segments) the dimension is
        # vacuously satisfied. The previous default of 0.0 turned an
        # intentional silence into a hard failure.
        narr_rate = narr_success / narr_planned if narr_planned else 1.0
        music_rate = music_success / music_planned if music_planned else 1.0
        mix_rate = mix_success / mix_planned if mix_planned else 1.0

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
                    (
                        f"final delivery muxed: {'OK' if delivery_ok else 'MISSING'}"
                        if delivery_expected
                        else "final delivery muxed: SKIPPED(no shared video uri)"
                    ),
                ],
            },
            "audio_quality": {
                "score": 1.0,
                "notes": ["audio quality check not yet implemented"],
            },
        }

        # final_ok and delivery_ok are now load-bearing on overall_pass —
        # previously they were only in the summary string, so a run could
        # produce no final mix at all and still report overall_pass=True.
        overall_pass = (
            narr_rate >= self.ASSET_PASS_THRESHOLD
            and music_rate >= 0.5
        )
        if scenes:
            overall_pass = overall_pass and final_ok
        if delivery_expected:
            overall_pass = overall_pass and delivery_ok
        summary = (
            f"Audio asset eval: TTS {narr_success}/{narr_planned} "
            f"({narr_rate:.0%}), music {music_success}/{music_planned}, "
            f"mixes {mix_success}/{mix_planned}, "
            f"final_audio={'OK' if final_ok else 'MISSING'}, "
            f"final_delivery={'OK' if delivery_ok else 'MISSING' if delivery_expected else 'SKIPPED'}."
        )

        return {
            "dimensions": dimensions,
            "overall_pass": overall_pass,
            "summary": summary,
        }
