"""AudioAgent — full audio-package generation from a screenplay JSON text blob.

Input:  AudioAgentInput (``screenplay_json_text`` — the upstream screenplay
        payload serialized as raw JSON text, shape-agnostic;
        ``final_video_path`` — direct file path to the finished MP4 for
        delivery mux)
Output: AudioAgentOutput (AudioPackage with narration segments, music cues,
        ambience beds, per-scene mixes, final audio, final delivery, metrics)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives the
upstream screenplay as an indented JSON text blob and produces the complete
AudioAgentOutput JSON in a single pass — no skeleton-first split, no
Python-side screenplay traversal. See CLAUDE.md §7 (Postel's Law at the
agent layer) for the rationale.

Output contract: all content-level invariants (scene_id reuse, sc_NNN /
narr_NNN / aud_narr_*_NN id formats, verbatim narration text, non-empty
music_cue.mood + ambience_bed.description, …) are owned by the LLM via the
template + system prompt and enforced by AudioEvaluator's structural
checks. Rework surfaces any drift instead of a silent Python-side patch-up.
``recompute_metrics`` does NOT rewrite any LLM-authored field — it only
derives summary counts.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import AudioAgentInput, AudioAgentOutput


AUDIO_OUTPUT_TEMPLATE = """{
  "content": {
    "scenes": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "narration_segments": [
          {
            "segment_id": "narr_001",
            "linked_shot_id": "sh_001",
            "speaker": "<character_name from the shot, or 'Narrator' for narration blocks>",
            "text": "<VERBATIM spoken line copied from the screenplay shot's text field>",
            "audio_asset": {
              "asset_id": "aud_narr_sc_001_01",
              "uri": "placeholder",
              "format": "wav",
              "sample_rate": 44100
            }
          }
        ],
        "music_cue": {
          "cue_id": "music_sc_001",
          "scene_id": "sc_001",
          "mood": "<3-6 keywords: musical mood + instrumentation>",
          "audio_asset": {
            "asset_id": "aud_music_sc_001",
            "uri": "placeholder",
            "format": "wav",
            "sample_rate": 44100
          }
        },
        "ambience_bed": {
          "ambience_id": "amb_sc_001",
          "scene_id": "sc_001",
          "description": "<short description of ambient sounds>",
          "audio_asset": {
            "asset_id": "aud_amb_sc_001",
            "uri": "placeholder",
            "format": "wav",
            "sample_rate": 44100
          }
        },
        "mix": {
          "mix_id": "mix_sc_001",
          "scene_id": "sc_001",
          "audio_asset": {
            "asset_id": "aud_mix_sc_001",
            "uri": "placeholder",
            "format": "wav",
            "sample_rate": 44100
          }
        }
      }
    ],
    "final_audio_asset": {
      "asset_id": "aud_final",
      "uri": "placeholder",
      "format": "wav",
      "sample_rate": 44100
    },
    "final_delivery_asset": {
      "asset_id": "delivery_final",
      "uri": "placeholder",
      "format": "mp4"
    }
  }
}"""


class AudioAgent(BaseAgent[AudioAgentInput, AudioAgentOutput]):

    async def generate(
        self,
        input_data: AudioAgentInput,
        *,
        rework_notes: str = "",
    ) -> AudioAgentOutput:
        """Single full-output LLM call from the screenplay JSON text blob."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are AudioAgent: turn a screenplay into a complete audio "
            "package (narration, music cues, ambience beds, per-scene "
            "mixes).\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream screenplay as a RAW JSON TEXT "
            "BLOB inside the user message. Do NOT assume specific field "
            "names in advance. READ the JSON, understand whatever shape it "
            "happens to have, and extract the elements you need. Typical "
            "fields you may encounter include content.scenes[] with each "
            "scene containing shots[] (with block_type, text, character_id, "
            "character_name), heading, summary, scene_end — but the exact "
            "names and nesting may vary. Reason from the text, not from "
            "assumed keys.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. Use empty string for unknowns, never null. Your "
            "output will be validated against a strict Pydantic schema.\n\n"
            "=== NARRATION EXTRACTION (CRITICAL) ===\n"
            "For each scene in the screenplay, walk its shots IN ORDER. "
            "For each shot whose block_type is 'dialogue', 'narration', or "
            "'monologue', produce ONE narration_segment. Action shots "
            "(block_type=='action') produce NO narration segment — skip "
            "them. For each extracted segment:\n"
            "  * text: copy the shot's spoken line VERBATIM. Do NOT "
            "paraphrase, summarize, or translate. The exact same string "
            "must appear in the audio package as in the upstream "
            "screenplay.\n"
            "  * speaker: copy the shot's character_name. For narration "
            "blocks with empty character_name, use 'Narrator'.\n"
            "  * linked_shot_id: the shot's shot_id (e.g. 'sh_007').\n"
            "  * segment_id: narr_001, narr_002, … GLOBALLY sequential "
            "across the entire audio package (not per-scene), 3-digit "
            "zero-padded, starting at narr_001.\n"
            "  * audio_asset.asset_id: aud_narr_{scene_id}_{NN} where NN "
            "is the per-scene 2-digit index starting at 01 inside each "
            "scene.\n\n"
            "Scenes with zero dialogue/narration/monologue shots have an "
            "empty narration_segments list — that is valid.\n\n"
            "=== ID CONVENTIONS ===\n"
            "scene_id: reuse the screenplay's scene_id verbatim "
            "(sc_001 style).\n"
            "scene.order: 1, 2, 3, … matching the screenplay's scene order "
            "exactly.\n"
            "music_cue.cue_id: music_{scene_id} (e.g. music_sc_001).\n"
            "music_cue.scene_id: matches the parent scene.\n"
            "ambience_bed.ambience_id: amb_{scene_id}.\n"
            "mix.mix_id: mix_{scene_id}.\n"
            "audio_asset.uri: always 'placeholder' — the materializer "
            "fills it after calling the generation service.\n\n"
            "=== CREATIVE FIELDS ===\n"
            "music_cue.mood: 3-6 keywords describing musical mood and "
            "instrumentation (e.g. 'melancholic, ambient, solo piano'), "
            "derived from the scene's tone / summary / scene_end fields in "
            "the screenplay.\n"
            "ambience_bed.description: short description of the scene's "
            "ambient sounds (e.g. 'Ocean waves crashing, distant "
            "seagulls, wind'), derived from the scene's location / "
            "heading / environment notes in the screenplay.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "Every scene MUST have music_cue, ambience_bed, and mix. "
            "music_cue.mood and ambience_bed.description MUST be non-empty "
            "strings. final_audio_asset and final_delivery_asset are "
            "top-level placeholders; their asset_ids are fixed as "
            "'aud_final' and 'delivery_final'.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: AudioAgentInput) -> str:
        return (
            "Read the upstream screenplay below and produce a complete "
            "audio package that scores it.\n\n"
            "=== SCREENPLAY (raw JSON — read the shape before writing) ===\n"
            f"{input_data.screenplay_json_text}\n"
            "=== END SCREENPLAY ===\n\n"
            "Extract narration text VERBATIM from each "
            "dialogue/narration/monologue shot. Write music mood + "
            "ambience description per scene. Generate all ids per the "
            "conventions in the system prompt.\n\n"
            "Produce the full audio package JSON in EXACTLY this shape:\n\n"
            f"{AUDIO_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> AudioAgentOutput:
        return AudioAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: AudioAgentOutput) -> None:
        """Derive summary metrics from content — pure derived data, zero rewrites.

        All LLM-authored fields (scene_id, segment_id, asset_id, narration
        text, mood, description, scene.order, …) are left untouched;
        AudioEvaluator enforces their invariants via structural checks +
        rework. The ``metrics`` field is hidden from the user-message
        template, so populating it here is derivation, not a silent
        patch-up of LLM output.
        """
        c = output.content
        output.metrics.scene_count = len(c.scenes)
        output.metrics.narration_segment_count = sum(
            len(s.narration_segments) for s in c.scenes
        )
