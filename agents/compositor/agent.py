"""CompositorAgent — plan and execute final video composition.

Input:  CompositorAgentInput (screenplay + video + audio + subtitle JSON texts
        and direct file paths)
Output: CompositorAgentOutput (composition plan + final delivery asset)

The LLM plans the composition: transitions between shots, color grading,
subtitle styling.  The materializer then executes the plan using FFmpeg
to produce the final deliverable video.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import CompositorAgentInput, CompositorAgentOutput


COMPOSITOR_OUTPUT_TEMPLATE = """{
  "content": {
    "plan": {
      "transitions": [
        {
          "from_shot_id": "sh_001",
          "to_shot_id": "sh_002",
          "transition_type": "crossfade",
          "duration_ms": 500
        }
      ],
      "color_grade": {
        "brightness": 0.0,
        "contrast": 0.05,
        "saturation": 0.0
      },
      "subtitle_style": {
        "font_size": 24,
        "font_color": "#FFFFFF",
        "outline_color": "#000000",
        "position": "bottom",
        "burn_in": true
      },
      "output_resolution": "1920x1080",
      "output_fps": 30
    }
  }
}"""


class CompositorAgent(BaseAgent[CompositorAgentInput, CompositorAgentOutput]):

    async def generate(
        self,
        input_data: CompositorAgentInput,
        *,
        rework_notes: str = "",
    ) -> CompositorAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are CompositorAgent: plan the final video composition by "
            "reading the screenplay, video package, audio package, and "
            "subtitle tracks.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make "
            "composition impossible. Concretely, reject when:\n"
            "  * video_json_text is empty AND video_file_path is empty — "
            "I have no video to composite. The video is the mandatory "
            "input; without it there is no deliverable to produce. "
            "(Audio, subtitles, and screenplay are optional augmentations "
            "of the video.)\n"
            "Do NOT reject merely because the video_package JSON lacks "
            "shot_segments / clips / an assembled-video manifest. Existing-"
            "video edit flows (imported mp4 going through transcription + "
            "subtitle + audio-mix) legitimately have no VideoAgent output "
            "to produce that structure; as long as a real video_file_path "
            "is present, treat the video as a single clip and plan "
            "accordingly (see TRANSITIONS rule below).\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: e.g. 'no video package or video file provided — "
            "compositor needs a base video to work on'.\n"
            "  * missing_labels: ['video_package'] (the audio_package, "
            "subtitle_tracks, and screenplay labels are optional).\n"
            "  * offending_fields: e.g. ['video_file_path'].\n"
            "If only audio or only subtitles are missing — DO NOT reject; "
            "compose with whatever tracks are present (a video without "
            "audio or without subtitles is a perfectly valid deliverable).\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive raw JSON text blobs for:\n"
            "- Screenplay (scene/shot structure — absent on existing-video "
            "edit flows)\n"
            "- Video package — on newly-created films this is the assembled "
            "VideoAgent output (scenes with shot_segments + per-clip timing, "
            "clips carry Kling-baked dialogue+foley). On existing-video edit "
            "flows it can be a scene-level description (e.g. VideoAnalysis "
            "output) or any minimal JSON describing the imported mp4 — in "
            "that case there are no shot_segments to plan transitions "
            "between.\n"
            "- Audio package (final film-wide audio mix: video track "
            "amix'd with optional global music + ambience)\n"
            "- Zero or more subtitle artifacts (one per language — "
            "bilingual / multilingual flows pass multiple; the "
            "materializer stacks them into the final video, so your "
            "subtitle_style applies globally to every track)\n\n"
            "=== COMPOSITION PLANNING RULES ===\n"
            "1. TRANSITIONS: For each pair of consecutive shots in the "
            "video package, decide the transition type. Use 'cut' for most "
            "shot-to-shot transitions within a scene. Use 'crossfade' "
            "(500-1000ms) for scene changes. Use 'fade_black' (800-1200ms) "
            "for dramatic scene endings. If the video package has zero or "
            "one shot_segments (e.g. existing-video flow with a single "
            "imported clip), return ``transitions: []`` — do not invent "
            "shot IDs, do not fabricate cuts that don't exist in the "
            "source.\n"
            "2. COLOR GRADE: Set a consistent color grade that matches the "
            "screenplay's overall mood. Keep adjustments subtle (-0.1 to 0.1).\n"
            "3. SUBTITLE STYLE: Choose appropriate font size and colors "
            "based on the video resolution. White with black outline is the "
            "default. Set burn_in=true for final delivery.\n"
            "4. RESOLUTION: Match the source video resolution. Default "
            "1920x1080.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: CompositorAgentInput) -> str:
        parts = [
            "Plan the final video composition from the following inputs.\n\n"
        ]

        if input_data.screenplay_json_text:
            parts.append(
                "=== SCREENPLAY ===\n"
                f"{input_data.screenplay_json_text}\n"
                "=== END SCREENPLAY ===\n\n"
            )

        if input_data.video_json_text:
            parts.append(
                "=== VIDEO PACKAGE ===\n"
                f"{input_data.video_json_text}\n"
                "=== END VIDEO PACKAGE ===\n\n"
            )

        if input_data.audio_json_text:
            parts.append(
                "=== AUDIO PACKAGE ===\n"
                f"{input_data.audio_json_text}\n"
                "=== END AUDIO PACKAGE ===\n\n"
            )

        for i, sub_text in enumerate(input_data.subtitle_json_texts, start=1):
            if not sub_text:
                continue
            parts.append(
                f"=== SUBTITLE ARTIFACT #{i} ===\n"
                f"{sub_text}\n"
                f"=== END SUBTITLE ARTIFACT #{i} ===\n\n"
            )

        parts.append(
            "Produce the composition plan in EXACTLY this shape:\n\n"
            f"{COMPOSITOR_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> CompositorAgentOutput:
        return CompositorAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: CompositorAgentOutput) -> None:
        plan = output.content.plan
        output.metrics.transition_count = len(plan.transitions)
        output.metrics.has_subtitles = plan.subtitle_style.burn_in
        output.metrics.has_audio = True  # always true if audio_package provided
