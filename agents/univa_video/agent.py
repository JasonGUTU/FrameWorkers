"""UnivaVideoAgent -- per-shot I2V plan, mirroring upstream UniVA exactly.

Mirrors UniVA's Stage 4 (image-to-video per shot) + Stage 6 (FFmpeg merge).
LLM-free: the per-shot video prompt is the same deterministic concatenation
that ``mcp_tools/video_gen.py:storyvideo_gen`` uses upstream — no I2V prompt
refinement step. The materializer does the actual I2V calls and FFmpeg merge.

This was previously a skeleton-first agent with a per-shot LLM refine pass
using ``i2v_refine_prompt.txt``. That extra step was removed to keep the FW
migrated pipeline behaviorally aligned with upstream UniVA, so two-side
comparisons isolate only model-backend differences.
"""

from __future__ import annotations

import logging
from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    UnivaVideoInput,
    UnivaVideoOutput,
    UnivaVideoContent,
    UnivaVideoMetrics,
    UnivaShotVideo,
    UnivaVideoAsset,
)

logger = logging.getLogger(__name__)


def _compose_video_prompt(shot: dict) -> str:
    """Same formula as UniVA upstream's keyframe/video prompt composition."""
    setting = shot.get("setting_description", "")
    plot = shot.get("plot_correspondence", "")
    static_desc = shot.get("static_shot_description", "")
    perspective = shot.get("shot_perspective_design", {})
    distance = perspective.get("distance", "")
    angle = perspective.get("angle", "")
    lens = perspective.get("lens", "")
    return f"{setting} {plot} {static_desc} {distance}, {angle}, {lens}"


class UnivaVideoAgent(BaseAgent[UnivaVideoInput, UnivaVideoOutput]):
    """LLM-free skeleton agent: deterministic per-shot prompts, no refinement."""

    async def generate(
        self,
        input_data: UnivaVideoInput,
        *,
        rework_notes: str = "",
    ) -> UnivaVideoOutput:
        """LLM-free: deterministic per-shot prompts from the storyboard."""
        output = self.build_skeleton(input_data)
        self.recompute_metrics(output)
        return output

    def build_skeleton(self, input_data: UnivaVideoInput) -> UnivaVideoOutput:
        shots = input_data.storyboard.get("shots", [])

        shot_videos = []
        for shot in shots:
            shot_videos.append(UnivaShotVideo(
                shot_id=shot.get("id", 0),
                video_prompt=_compose_video_prompt(shot),
                video_asset=UnivaVideoAsset(),
            ))

        return UnivaVideoOutput(
            content=UnivaVideoContent(
                shot_videos=shot_videos,
                final_video_asset=UnivaVideoAsset(),
            ),
            metrics=UnivaVideoMetrics(
                shot_count=len(shot_videos),
            ),
        )

    def recompute_metrics(self, output: UnivaVideoOutput) -> None:
        c = output.content
        shots = c.shot_videos
        shot_count = len(shots)
        output.metrics.shot_count = shot_count
