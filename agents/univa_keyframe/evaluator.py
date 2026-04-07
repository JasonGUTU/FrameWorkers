"""Evaluator for UnivaKeyFrameAgent output (output-internal only)."""

from __future__ import annotations

from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import UnivaKeyFrameOutput


class UnivaKeyFrameEvaluator(BaseEvaluator[UnivaKeyFrameOutput]):

    creative_dimensions = [
        ("prompt_quality", "Are the refined character prompts detailed and suitable for image generation?"),
    ]

    def check_structure(self, output: UnivaKeyFrameOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.character_images:
            errors.append("character_images list is empty")

        if not c.shot_keyframes:
            errors.append("shot_keyframes list is empty")

        for ci in c.character_images:
            if not ci.refined_prompt:
                errors.append(f"character {ci.char_id} has empty refined_prompt")

        for kf in c.shot_keyframes:
            if not kf.keyframe_prompt:
                errors.append(f"shot {kf.shot_id} has empty keyframe_prompt")

        return errors

    def evaluate_asset(self, asset_dict: dict[str, Any]) -> dict[str, Any]:
        """L3: check that generated images have valid URIs."""
        content = asset_dict.get("content", {})
        total = 0
        ok = 0

        for ci in content.get("character_images", []):
            total += 1
            uri = (ci.get("image_asset") or {}).get("uri", "")
            if check_uri(uri):
                ok += 1

        for kf in content.get("shot_keyframes", []):
            total += 1
            uri = (kf.get("image_asset") or {}).get("uri", "")
            if check_uri(uri):
                ok += 1

        rate = ok / total if total else 0.0
        passed = rate >= 0.8
        return {
            "overall_pass": passed,
            "summary": f"{ok}/{total} images generated ({rate:.0%})",
            "dimensions": {
                "image_success_rate": {"score": rate, "notes": [f"{ok}/{total} succeeded"]},
            },
        }
