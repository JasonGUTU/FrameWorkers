"""CompositorAgent — plan and execute final video composition.

Input:  CompositorAgentInput (screenplay + video + audio + subtitle JSON texts
        and direct file paths)
Output: CompositorAgentOutput (composition plan + final delivery asset)

The LLM plans the composition: color grading and subtitle styling.
The materializer then executes the plan using FFmpeg to produce the
final deliverable video.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import CompositorAgentInput, CompositorAgentOutput


COMPOSITOR_OUTPUT_TEMPLATE = """{
  "content": {
    "plan": {
      "color_grade": {
        "brightness": 0.0,
        "contrast": 0.05,
        "saturation": 0.0
      },
      "subtitle_style": {
        "font_size": 24,
        "font_color": "#FFFFFF",
        "outline_color": "#000000",
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
        self.recompute_metrics(output, input_data)
        return output

    def system_prompt(self) -> str:
        return (
            "You are CompositorAgent: plan the final video composition by "
            "reading the screenplay, video package, audio package, and "
            "subtitle tracks.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make "
            "composition impossible. Two mutually exclusive video tracks "
            "are valid:\n"
            "  (a) ``video_file_path`` (any upstream mp4 — raw upload, "
            "edited clip, or newly-assembled film), optionally accompanied "
            "by a ``video_package`` JSON manifest carrying shot_segments "
            "as structural context for the planning LLM. The mp4 file IS "
            "the visual track; the JSON is supplementary context.\n"
            "  (b) ``illustration_image_paths`` + ``segment_timing`` — an "
            "illustrated-storytelling slideshow: an ordered image "
            "sequence plus per-segment durations. The materializer ffmpeg-"
            "concats the images using the durations to synthesize the "
            "video track.\n"
            "Reject when:\n"
            "  * BOTH video tracks are empty — i.e. video_file_path is "
            "empty AND illustration_image_paths is empty. (video_json_"
            "text is supplementary context, NOT a renderable track on "
            "its own — a non-empty manifest without a real mp4 cannot "
            "be composited.) Emit reason='no video source provided' with "
            "missing_labels=['video_file', 'illustration_sequence'].\n"
            "  * BOTH video tracks are present simultaneously (a non-"
            "empty video_file_path AND non-empty illustration_image_"
            "paths) — ambiguous: which track do you render? Emit reason="
            "'ambiguous video source: both assembled video and "
            "illustration sequence routed in' with missing_labels=[] "
            "and offending_fields=['video_file_path', "
            "'illustration_image_paths'].\n"
            "  * Slideshow mode (b) but ``segment_timing`` is empty — no "
            "way to derive per-image durations. Emit reason='illustration "
            "sequence provided but segment_timing missing' with "
            "missing_labels=['segment_timing'].\n"
            "Do NOT reject merely because the video_package JSON is "
            "empty or lacks shot_segments / clips / an assembled-video "
            "manifest. As long as ``video_file_path`` is non-empty there "
            "IS a video to composite; treat it as a single clip and plan "
            "accordingly. Existing-video edit flows (raw upload OR style "
            "transfer / extension / inpainting output going through "
            "transcription + subtitle + audio-mix) legitimately have no "
            "shot_segments structure.\n"
            "If only audio or only subtitles are missing — DO NOT reject; "
            "compose with whatever tracks are present (a video without "
            "audio or without subtitles is a perfectly valid deliverable).\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive raw JSON text blobs for:\n"
            "- Screenplay (scene/shot structure — absent on existing-video "
            "edit flows and on illustrated-storytelling flows)\n"
            "- Video package — on newly-created films this is the assembled "
            "VideoAgent output (scenes with shot_segments + per-clip timing, "
            "clips carry in-clip baked dialogue+foley). On existing-video edit "
            "flows it can be a scene-level description (e.g. VideoAnalysis "
            "output) or any minimal JSON describing the imported mp4. "
            "ABSENT on illustrated-storytelling flows (the video track is "
            "instead an image sequence — see below).\n"
            "- Segment timing JSON (illustrated-storytelling ONLY): "
            "``segment_timings[]`` with start_sec / end_sec / duration_sec "
            "per segment. Use this to understand pacing; do NOT emit it as "
            "output — the materializer reads it directly.\n"
            "- Audio package (final film-wide audio mix OR narrator "
            "voiceover on storytelling flows)\n"
            "- Zero or more subtitle artifacts (one per language — "
            "bilingual / multilingual flows pass multiple; the "
            "materializer stacks them into the final video, so your "
            "subtitle_style applies globally to every track)\n\n"
            "=== COMPOSITION PLANNING RULES ===\n"
            "1. COLOR GRADE: Set a consistent color grade that matches the "
            "screenplay's overall mood. Keep adjustments subtle (-0.1 to 0.1).\n"
            "2. SUBTITLE STYLE: Choose appropriate font size and colors "
            "based on the video resolution. White with black outline is the "
            "default. Set burn_in=true for final delivery.\n"
            "3. RESOLUTION: Match the source video resolution. Default "
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
                "=== VIDEO PACKAGE (structural manifest) ===\n"
                f"{input_data.video_json_text}\n"
                "=== END VIDEO PACKAGE ===\n\n"
            )

        if input_data.video_file_path:
            parts.append(
                "=== VIDEO FILE PATH (the actual mp4 the materializer "
                "will composite) ===\n"
                f"{input_data.video_file_path}\n"
                "=== END VIDEO FILE PATH ===\n\n"
            )

        if input_data.illustration_image_paths:
            parts.append(
                "=== ILLUSTRATED-STORYTELLING SLIDESHOW ===\n"
                f"{len(input_data.illustration_image_paths)} still "
                "illustration(s) will be concatenated by the materializer. "
                "This is slideshow mode — the materializer handles image "
                "pacing from segment_timing.\n"
                "=== END ILLUSTRATED-STORYTELLING SLIDESHOW ===\n\n"
            )

        if input_data.segment_timing_json_text:
            parts.append(
                "=== SEGMENT TIMING (slideshow pacing; materializer-owned) ===\n"
                f"{input_data.segment_timing_json_text}\n"
                "=== END SEGMENT TIMING ===\n\n"
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

    def recompute_metrics(
        self,
        output: CompositorAgentOutput,
        input_data: CompositorAgentInput,
    ) -> None:
        plan = output.content.plan
        output.metrics.has_subtitles = plan.subtitle_style.burn_in
        output.metrics.has_audio = bool(
            input_data.audio_file_path or input_data.audio_json_text
        )
