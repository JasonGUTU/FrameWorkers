"""VideoAgent — full video-package generation from a screenplay + keyframes JSON text blob.

Input:  VideoAgentInput (``screenplay_json_text`` + ``keyframes_metadata_json_text``
        — both opaque JSON text blobs, shape-agnostic; ``shot_stills`` — typed
        image reference list)
Output: VideoAgentOutput (VideoPackage with scenes → shot_segments, each
        shot carrying a per-shot ``semantic_context`` mirroring the relevant
        screenplay + keyframe fields, plus transitions)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives both
upstream JSON text blobs and produces the complete VideoAgentOutput in a
single pass. See CLAUDE.md §7 (Postel's Law at the agent layer) for the
rationale: no Python-side upstream dict walk, no shape assumption, zero
string-keyed coupling between this agent and the producer agents' schemas.

Output contract: all content-level invariants (scene_id / shot_id reuse from
upstream, per-shot ``semantic_context`` mirroring, transition plans) are
owned by the LLM via the template + system prompt and enforced by
VideoEvaluator's structural checks. ``recompute_metrics`` does NOT rewrite
any LLM-authored field — it only derives summary counts.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import VideoAgentInput, VideoAgentOutput


VIDEO_OUTPUT_TEMPLATE = """{
  "content": {
    "scenes": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "scene_context": {
          "location_id": "<from screenplay scene.scene_consistency_pack.location_lock.location_id>",
          "time_of_day": "<from screenplay scene.scene_consistency_pack.location_lock.time_of_day>",
          "environment_notes": ["<from screenplay scene.scene_consistency_pack.location_lock.environment_notes>"],
          "style_notes": ["<from screenplay scene.scene_consistency_pack.style_lock.global_style_notes>"],
          "must_avoid": ["<from screenplay scene.scene_consistency_pack.style_lock.must_avoid>"]
        },
        "shot_segments": [
          {
            "shot_id": "sh_001",
            "duration_sec": 5,
            "semantic_context": {
              "shot_type": "<copied from screenplay shot.shot_type>",
              "visual_goal": "<copied from screenplay shot.visual_goal>",
              "action_focus": "<copied from screenplay shot.action_focus>",
              "characters_in_frame": ["<character_ids from screenplay shot.characters_in_frame>"],
              "camera_angle": "<copied from screenplay shot.camera.angle>",
              "camera_movement": "<copied from screenplay shot.camera.movement>",
              "framing_notes": "<copied from screenplay shot.camera.framing_notes>",
              "video_motion_hints": ["<from keyframes_metadata: each keyframe's video_motion_hint for this shot>"],
              "dialogue_text": "<for dialogue/narration/monologue shots: copy screenplay shot.text verbatim; for action shots: empty string>",
              "emotion_hint": "<for spoken shots: copy screenplay shot.emotion_hint verbatim; empty otherwise>"
            }
          }
        ],
        "transition_plan": [
          {
            "from_shot_id": "sh_001",
            "to_shot_id": "sh_002",
            "transition_type": "cut"
          }
        ]
      }
    ]
  }
}"""


class VideoAgent(BaseAgent[VideoAgentInput, VideoAgentOutput]):

    async def generate(
        self,
        input_data: VideoAgentInput,
        *,
        rework_notes: str = "",
    ) -> VideoAgentOutput:
        """Single full-output LLM call from two JSON text blobs."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are VideoAgent: turn a screenplay + a keyframe-planning "
            "document into a complete video package (scenes → shot "
            "segments, each carrying the per-shot semantic context that "
            "the video generation service needs).\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the screenplay or "
            "keyframes_metadata makes your job impossible. Concretely, "
            "reject when ANY of these is true after you have read both "
            "JSON blobs carefully:\n"
            "  * screenplay_json_text is empty, whitespace-only, or an "
            "empty JSON object — there is no shot timeline to mirror.\n"
            "  * Zero shots across the whole screenplay: every scene's "
            "shots list is empty / missing. With no shots, there are no "
            "ShotSegments to produce.\n"
            "  * keyframes_metadata_json_text is empty or carries no "
            "keyframes for ANY shot — the per-shot video_motion_hints "
            "field is what drives the I2V model, so without keyframes "
            "nothing can be generated.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. "
            "'keyframes_metadata has no keyframes for any screenplay "
            "shot — nothing to feed the video generator').\n"
            "  * missing_labels: list whichever inputs are unusable, "
            "e.g. ['screenplay'] or ['keyframes_metadata'] or both.\n"
            "  * offending_fields: e.g. ['content.scenes[].shots', "
            "'content.scenes[].shots[].keyframes'].\n"
            "If the screenplay or keyframes_metadata is merely sparse "
            "(short visual_goals, missing camera details, thin keyframe "
            "notes) — DO NOT reject; mirror what is present and leave "
            "downstream fields empty where the source is empty.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive TWO raw JSON text blobs inside the user "
            "message: the upstream screenplay and the upstream "
            "keyframes_metadata (keyframe planning document). Do NOT "
            "assume specific field names in advance. READ the JSON, "
            "understand whatever shape it happens to have, and extract "
            "the elements you need. Typical fields: scenes[] with shots[] "
            "(shot_id, shot_type, visual_goal, action_focus, camera, "
            "characters_in_frame, keyframe_plan), scene_consistency_pack "
            "(location_lock, style_lock); and in keyframes_metadata: "
            "content.scenes[].shots[].keyframes[] (video_motion_hint). "
            "But the exact names and nesting may vary. Reason from the "
            "text, not from assumed keys.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. Use empty string for unknowns, never null.\n\n"
            "=== SCENE-LEVEL vs SHOT-LEVEL (CRITICAL) ===\n"
            "Put scene-level fields (location_id, time_of_day, "
            "environment_notes, style_notes, must_avoid) on "
            "``VideoScene.scene_context`` ONCE per scene. Do NOT repeat "
            "them per shot_segment — the materializer merges "
            "scene_context into each shot's semantic context before "
            "generation, so duplicating them wastes tokens and creates "
            "drift.\n\n"
            "=== SHOT MIRRORING (CRITICAL) ===\n"
            "For every shot in the screenplay, produce ONE ShotSegment "
            "with the same shot_id. Mirror the following into its "
            "``semantic_context`` sub-object (COPY VERBATIM from the "
            "corresponding upstream field):\n"
            "  * shot_type, visual_goal, action_focus — from screenplay "
            "shot\n"
            "  * characters_in_frame — from screenplay shot (copy the "
            "list)\n"
            "  * camera_angle, camera_movement, framing_notes — from "
            "screenplay shot.camera.{angle, movement, framing_notes}\n"
            "  * video_motion_hints — from the SECOND JSON blob "
            "(keyframes_metadata): find the matching shot by shot_id in "
            "content.scenes[*].shots[], collect each of its keyframes' "
            "video_motion_hint into the list.\n"
            "  * dialogue_text — from screenplay shot.text, ONLY for "
            "shots whose block_type is 'dialogue', 'narration', or "
            "'monologue'. Copy the line VERBATIM, character-for-"
            "character, in whatever language it is written (Chinese "
            "characters stay Chinese). For action shots leave it an "
            "empty string.\n"
            "  * emotion_hint — from screenplay shot.emotion_hint, "
            "copied verbatim (calm / neutral / sad / angry / whispered / "
            "excited / warm / tense / urgent, or empty).\n\n"
            "=== PER-SHOT DURATION (CRITICAL) ===\n"
            "Set ``duration_sec`` for every shot_segment. This drives the "
            "Kling image-to-video backend, which accepts ONLY 5 or 10 "
            "seconds per clip — any other number is silently snapped to "
            "the nearest of the two (≤ 5.5 → 5, > 5.5 → 10).\n"
            "Choose per shot:\n"
            "  * Default to 5. Most action / dialogue / reaction beats "
            "land cleanly in 5s.\n"
            "  * Pick 10 when ANY of the following holds:\n"
            "    - The mirrored ``dialogue_text`` is longer than ~12 "
            "Chinese characters / ~15 English words (the comfortable "
            "ceiling for natural 5s speech). Long lines need 10s or the "
            "voiceover gets clipped. Count the dialogue you just mirrored "
            "into ``semantic_context.dialogue_text`` — if it exceeds the "
            "threshold, this shot needs 10s.\n"
            "    - A slow camera move or an extended atmospheric beat "
            "the screenplay calls out (e.g. ``camera.movement = 'slow "
            "dolly'``, ``framing_notes`` mentioning held silence).\n"
            "    - The screenplay's scene-level "
            "``estimated_duration_seconds`` divided by the scene's shot "
            "count is closer to 10 than 5.\n"
            "Output the value as an integer or float in {5, 10}; never "
            "emit 6, 7, 8, or any other intermediate value.\n\n"
            "Do NOT summarize, paraphrase, or rewrite these fields. This "
            "is a MIRROR — the same values must appear verbatim so "
            "downstream consistency holds. In particular, dialogue_text "
            "is passed straight into the video-generation backend's "
            "prompt and drives on-screen speech synthesis + lip-sync; "
            "any paraphrase here "
            "shows up as the wrong line being spoken.\n\n"
            "=== ID CONVENTIONS ===\n"
            "scene_id: reuse the screenplay's scene_id verbatim "
            "(sc_001 style).\n"
            "scene.order: 1, 2, 3, … matching the screenplay's scene "
            "order.\n"
            "shot_id: reuse the screenplay's shot_id verbatim (sh_NNN, "
            "globally sequential across the whole video — same as "
            "screenplay's numbering).\n\n"
            "=== TRANSITIONS ===\n"
            "For each scene, produce a transition_plan with one entry "
            "per consecutive shot pair inside that scene. Default "
            "transition_type is 'cut'. transition_plan is empty when the "
            "scene has ≤ 1 shot.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "Every shot MUST have a semantic_context with shot_id "
            "(implicit via its parent), visual_goal non-empty.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: VideoAgentInput) -> str:
        return (
            "Read the two upstream documents below and produce a complete "
            "video package.\n\n"
            "=== SCREENPLAY (raw JSON — read the shape before writing) ===\n"
            f"{input_data.screenplay_json_text}\n"
            "=== END SCREENPLAY ===\n\n"
            "=== KEYFRAMES METADATA (raw JSON) ===\n"
            f"{input_data.keyframes_metadata_json_text}\n"
            "=== END KEYFRAMES METADATA ===\n\n"
            "For every screenplay shot, produce ONE shot_segment with "
            "its semantic_context mirrored verbatim from the upstream. "
            "Put scene-level fields on VideoScene.scene_context once "
            "per scene — do not repeat them per shot. For "
            "video_motion_hints, look up the matching shot in the "
            "keyframes_metadata JSON.\n\n"
            "Produce the full video package JSON in EXACTLY this shape:\n\n"
            f"{VIDEO_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> VideoAgentOutput:
        return VideoAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: VideoAgentOutput) -> None:
        """Derive summary metrics from content — pure derived data, zero rewrites.

        All LLM-authored fields (scene_id, shot_id, order, semantic_context,
        transition_plan, …) are left untouched; VideoEvaluator enforces
        their invariants via structural checks + rework. The ``metrics``
        field is hidden from the user-message template, so populating it
        here is derivation, not a silent patch-up of LLM output.
        """
        c = output.content
        output.metrics.scene_count = len(c.scenes)
        output.metrics.shot_segment_count = sum(
            len(s.shot_segments) for s in c.scenes
        )
