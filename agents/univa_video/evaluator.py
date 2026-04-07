"""Evaluator for UnivaVideoAgent output (output-internal only)."""

from __future__ import annotations

from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import UnivaVideoOutput


class UnivaVideoEvaluator(BaseEvaluator[UnivaVideoOutput]):

    # No creative LLM scoring: prompts are deterministically composed (mirroring
    # upstream UniVA), so there is nothing for an LLM to creatively score.
    # L1 structural check + L3 asset URI check still run.
    creative_dimensions: list = []

    def check_structure(self, output: UnivaVideoOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.shot_videos:
            errors.append("shot_videos list is empty")

        for sv in c.shot_videos:
            if not sv.video_prompt:
                errors.append(f"shot {sv.shot_id} has empty video_prompt")

        return errors

    def evaluate_asset(self, asset_dict: dict[str, Any]) -> dict[str, Any]:
        """L3: check that generated video clips have valid URIs."""
        content = asset_dict.get("content", {})
        total = 0
        ok = 0

        for sv in content.get("shot_videos", []):
            total += 1
            uri = (sv.get("video_asset") or {}).get("uri", "")
            if check_uri(uri):
                ok += 1

        # Also check final video
        final_uri = (content.get("final_video_asset") or {}).get("uri", "")
        total += 1
        if check_uri(final_uri):
            ok += 1

        rate = ok / total if total else 0.0
        passed = rate >= 0.7
        return {
            "overall_pass": passed,
            "summary": f"{ok}/{total} videos generated ({rate:.0%})",
            "dimensions": {
                "video_success_rate": {"score": rate, "notes": [f"{ok}/{total} succeeded"]},
            },
        }
