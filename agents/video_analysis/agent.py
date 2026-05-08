"""VideoAnalysisAgent — deep structured analysis of video content.

Input:  VideoAnalysisAgentInput (source_video_path)
Output: VideoAnalysisAgentOutput (scene segments + summary + entities)

Uses a vision-capable LLM to analyze video content: detect scene
boundaries, describe each scene, identify entities, and produce an
overall summary.

Frame sampling
--------------
Inline-video attachment (Gemini's OpenAI-compat data URL path) caps at
20 MB and the model further samples its inline video at ~1fps with a
context-budget cap, so long / high-bitrate clips were silently truncated
to ~the first 20-40s. Instead, this agent now ffprobe's the duration,
ffmpeg-extracts evenly-spaced still frames (1 every 2s, capped at 30
frames), and attaches them as image inputs with their timestamps quoted
in the user prompt. This trades frame-to-frame motion fidelity for
full-duration coverage — appropriate because the agent's task
(scene detection / entity ID / summary) is frame-level, not motion-level.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any

from ..base_agent import INPUT_REJECTION_RULE, BaseAgent, _maybe_parse_rejection
from ..common_schema import UpstreamInputRejected
from .schema import VideoAnalysisAgentInput, VideoAnalysisAgentOutput

logger = logging.getLogger(__name__)


# Sampling: one frame every _FRAME_SAMPLE_INTERVAL_SEC, clamped to
# [_FRAME_MIN_COUNT, _FRAME_MAX_COUNT]. A 60s clip → 30 frames @ 2s
# (saturates max). A 120s clip → 30 frames @ 4s. A 5s clip → 8 frames
# @ ~0.6s (forced minimum so short clips still get enough coverage
# for scene detection to work).
_FRAME_SAMPLE_INTERVAL_SEC = 2.0
_FRAME_MIN_COUNT = 8
_FRAME_MAX_COUNT = 30


def _ffprobe_duration_sec(video_path: str) -> float | None:
    """Return video duration in seconds, or None when ffprobe is missing
    / the file is unreadable / format=duration is empty.
    """
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        proc = subprocess.run(
            [
                ffprobe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True, check=False, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    out = (proc.stdout or "").strip()
    try:
        d = float(out)
    except ValueError:
        return None
    return d if d > 0 else None


def _extract_sample_frames(
    video_path: str, out_dir: str,
) -> list[tuple[str, float]]:
    """ffmpeg-extract evenly-spaced still frames covering the entire video.

    Returns ``[(frame_path, timestamp_sec), ...]`` sorted by timestamp.
    Empty list when ffprobe / ffmpeg fails completely (the agent then
    falls back to attaching nothing and the LLM hits the input-rejection
    path on its own).

    Sampling: pick N in ``[_FRAME_MIN_COUNT, _FRAME_MAX_COUNT]`` based
    on ``duration / _FRAME_SAMPLE_INTERVAL_SEC``; sample N timestamps
    uniformly across ``[epsilon, duration - epsilon]`` so we don't seek
    past EOF or land on a black initial frame.
    """
    duration = _ffprobe_duration_sec(video_path)
    if duration is None:
        logger.warning(
            "VideoAnalysis: ffprobe could not read duration of %s",
            video_path,
        )
        return []

    target_n = int(round(duration / _FRAME_SAMPLE_INTERVAL_SEC))
    target_n = max(_FRAME_MIN_COUNT, min(_FRAME_MAX_COUNT, target_n))

    epsilon = min(0.5, duration * 0.05)
    if target_n == 1 or duration <= 2 * epsilon:
        timestamps = [duration / 2.0]
    else:
        step = (duration - 2 * epsilon) / (target_n - 1)
        timestamps = [epsilon + i * step for i in range(target_n)]

    frames: list[tuple[str, float]] = []
    for i, ts in enumerate(timestamps, start=1):
        out_path = os.path.join(out_dir, f"frame_{i:03d}.png")
        # ``-ss`` before ``-i`` is fast-seek (keyframe-aligned, may snap
        # to nearest keyframe — acceptable here since we only need
        # representative frames, not exact timestamps).
        proc = subprocess.run(
            [
                "ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", video_path,
                "-vframes", "1", "-q:v", "2", out_path,
            ],
            capture_output=True, check=False, text=True, timeout=30,
        )
        if proc.returncode == 0 and os.path.isfile(out_path):
            frames.append((out_path, ts))
        else:
            tail = (proc.stderr or "").strip()[-200:]
            logger.warning(
                "VideoAnalysis: ffmpeg failed to extract frame %d/%d "
                "at %.2fs: %s",
                i, len(timestamps), ts, tail,
            )
    return frames


VIDEO_ANALYSIS_OUTPUT_TEMPLATE = """{
  "content": {
    "video_summary": {
      "title": "<suggested title>",
      "summary": "<2-4 sentence overall summary>",
      "genre": "<genre/category>",
      "language": "<detected spoken language or empty>",
      "duration_seconds": 0
    },
    "scenes": [
      {
        "scene_id": "scene_001",
        "start_time": 0.0,
        "end_time": 10.5,
        "description": "<visual description of what happens in this scene>",
        "setting": "<location / environment>",
        "mood": "<emotional tone>",
        "entities": ["<person/object 1>", "<person/object 2>"],
        "tension_score": 0.3,
        "is_climax_candidate": false
      }
    ]
  }
}"""


class VideoAnalysisAgent(BaseAgent[VideoAnalysisAgentInput, VideoAnalysisAgentOutput]):

    async def generate(
        self,
        input_data: VideoAnalysisAgentInput,
        *,
        rework_notes: str = "",
    ) -> VideoAnalysisAgentOutput:
        system = INPUT_REJECTION_RULE + self.system_prompt()

        # Empty / missing path → no media; LLM will hit the
        # input-rejection escape hatch via system_prompt rules.
        path = input_data.source_video_path or ""
        if not path or not os.path.isfile(path):
            user = self.build_user_prompt(input_data, frames=[])
            if rework_notes:
                user += self._rework_section(rework_notes)
            raw = await self.llm.chat_json(system, user, media_attachments=None)
            rejection = _maybe_parse_rejection(raw)
            if rejection is not None:
                raise UpstreamInputRejected(rejection)
            output = self.parse_output(raw)
            self.recompute_metrics(output)
            return output

        # Frame extraction lives inside a TemporaryDirectory: chat_json
        # synchronously base64-reads each frame (see default_client's
        # _build_multimodal_user_content) before the LLM call returns,
        # so the await completes before tempdir cleanup.
        with tempfile.TemporaryDirectory(prefix="fw_video_analysis_") as frames_dir:
            frames = _extract_sample_frames(path, frames_dir)
            user = self.build_user_prompt(input_data, frames=frames)
            if rework_notes:
                user += self._rework_section(rework_notes)
            media = [
                {"type": "image", "path": fpath}
                for fpath, _ts in frames
            ]
            raw = await self.llm.chat_json(
                system, user, media_attachments=media or None,
            )
            rejection = _maybe_parse_rejection(raw)
            if rejection is not None:
                raise UpstreamInputRejected(rejection)
            output = self.parse_output(raw)
            self.recompute_metrics(output)
            return output

    def system_prompt(self) -> str:
        return (
            "You are VideoAnalysisAgent: analyze video content and produce "
            "a structured breakdown.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the source media is "
            "unusable. Concretely, reject when:\n"
            "  * source_video_path is empty / whitespace-only — there is "
            "no video to analyze.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: e.g. 'source_video_path is empty — no video "
            "file to analyze'.\n"
            "  * missing_labels: ['source_video'] (my only input label).\n"
            "  * offending_fields: ['source_video_path'].\n"
            "If the path looks unusual but is non-empty — DO NOT reject; "
            "the vision model will surface a real failure if the video is "
            "unreadable or unsupported. Short / sparse / abstract video "
            "content is still analyzable.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You receive a sequence of evenly-spaced sampled frames "
            "covering the ENTIRE source video, NOT the raw video itself. "
            "The user message lists each frame's timestamp (in seconds "
            "from video start). Use those timestamps to anchor scene "
            "boundaries (start_time / end_time) in your output. Frames "
            "between the samples are not provided — describe what you "
            "see across consecutive samples AS A SCENE rather than as "
            "discrete frames; if the visual content is similar across "
            "many adjacent samples, that is one continuous scene "
            "spanning their timestamp range.\n\n"
            "=== YOUR TASK ===\n"
            "Analyze the provided sampled frames and produce:\n"
            "1. A high-level video_summary with title, summary, genre, and "
            "language detection (note: language detection from frames "
            "alone is unreliable when there's no on-screen text — emit "
            "empty string when uncertain).\n"
            "2. A list of scene segments with detected boundaries, visual "
            "descriptions, settings, mood, and entities.\n\n"
            "=== SCENE DETECTION RULES ===\n"
            "1. A scene changes when there's a significant shift in "
            "location, time, or visual content (not just camera angle).\n"
            "2. scene_id format: scene_NNN (3-digit zero-padded, starting "
            "at scene_001).\n"
            "3. Timestamps should be in seconds with one decimal place.\n"
            "4. Description should capture WHAT HAPPENS visually, not just "
            "what's there (actions, movements, interactions).\n"
            "5. Entities: list specific people (by appearance if name "
            "unknown), objects, animals that are prominent in the scene.\n"
            "6. tension_score: 0.0–1.0 scalar for narrative / dramatic "
            "intensity. Calibration — quiet dialogue / exposition ≈ 0.1–0.3, "
            "rising conflict / suspense ≈ 0.4–0.6, action peaks / emotional "
            "climaxes / shocking reversals ≈ 0.7–1.0.\n"
            "7. is_climax_candidate: true ONLY for scenes that look like "
            "climaxes, major reversals, or emotional peaks of the whole "
            "video. Typically 1–3 per video; emit zero for slice-of-life / "
            "purely informational footage with no dramatic arc. Use "
            "sparingly — flagging every high-tension scene defeats the "
            "purpose.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(
        self,
        input_data: VideoAnalysisAgentInput,
        *,
        frames: list[tuple[str, float]] | None = None,
    ) -> str:
        frames = frames or []
        if frames:
            ts_lines = "\n".join(
                f"  Frame {i + 1}: timestamp {ts:.2f}s"
                for i, (_path, ts) in enumerate(frames)
            )
            last_ts = frames[-1][1]
            timing_section = (
                f"\n=== ATTACHED FRAME TIMESTAMPS ===\n"
                f"{len(frames)} sampled frames covering ~{last_ts:.1f}s "
                f"of source video. Anchor scene boundaries to these "
                f"timestamps:\n"
                f"{ts_lines}\n"
                f"=== END ATTACHED FRAME TIMESTAMPS ===\n\n"
            )
        else:
            timing_section = ""
        return (
            f"Analyze this video: {input_data.source_video_path}\n"
            f"{timing_section}"
            "Produce a structured analysis in EXACTLY this shape:\n\n"
            f"{VIDEO_ANALYSIS_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> VideoAnalysisAgentOutput:
        return VideoAnalysisAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: VideoAnalysisAgentOutput) -> None:
        c = output.content
        output.metrics.scene_count = len(c.scenes)
        output.metrics.duration_seconds = c.video_summary.duration_seconds
        output.metrics.entity_count = sum(
            len(s.entities) for s in c.scenes
        )
