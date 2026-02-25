"""Concrete image generator backed by OpenRouter image service."""

from __future__ import annotations

from typing import Any, Dict

from ....base_generator import GeneratorMetadata
from ..base_service_generator import BaseServiceImageGenerator


class OpenRouterImageGenerator(BaseServiceImageGenerator):
    """Generate/edit images via `ImageService` (OpenRouter backend)."""

    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="openrouter_image_generator",
            name="OpenRouter Image Generator",
            description="Concrete image generator using OpenRouter Gemini image model",
            capabilities=["text_to_image", "image_to_image"],
            input_schema={
                "prompt": {"type": "string", "required": True},
                "images": {"type": "array", "required": False},
            },
            output_schema={
                "images": {"type": "array", "description": "Generated image data URLs"},
                "metadata": {"type": "object"},
            },
        )

    def generate(self, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        images = kwargs.get("images", [])
        if images:
            refs = [self.decode_image_input(x) for x in images]
            image_bytes = self.run_service_edit(refs, prompt)
            mode = "image_to_image"
        else:
            image_bytes = self.run_service_generate(prompt)
            mode = "text_to_image"

        data_url = self.to_image_data_url(image_bytes)
        return {
            "images": [data_url],
            "metadata": {"mode": mode, "bytes": len(image_bytes)},
        }
