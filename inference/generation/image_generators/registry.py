"""Image generator registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..base_generator import BaseImageGenerator
from ..base_registry import BaseGeneratorRegistry


class ImageGeneratorRegistry(BaseGeneratorRegistry[BaseImageGenerator]):
    """Registry for discovering and managing image generators."""

    base_generator_cls = BaseImageGenerator
    package_root = __package__ + ".generators" if __package__ else "inference.generation.image_generators.generators"
    registry_label = "image"

    def __init__(self, generators_dir: Optional[str] = None):
        if generators_dir is None:
            generators_dir = Path(__file__).parent / "generators"
        super().__init__(generators_dir=generators_dir)

    def generate(
        self,
        generator_id: str,
        prompt: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {}
        if prompt is not None:
            inputs["prompt"] = prompt
        if images is not None:
            inputs["images"] = images
        inputs.update(kwargs)
        return self._generate_with_inputs(generator_id=generator_id, inputs=inputs)


_registry: Optional[ImageGeneratorRegistry] = None


def get_image_generator_registry() -> ImageGeneratorRegistry:
    global _registry
    if _registry is None:
        _registry = ImageGeneratorRegistry()
    return _registry
