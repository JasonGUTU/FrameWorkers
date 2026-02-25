"""Video generator registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..base_generator import BaseVideoGenerator
from ..base_registry import BaseGeneratorRegistry


class VideoGeneratorRegistry(BaseGeneratorRegistry[BaseVideoGenerator]):
    """Registry for discovering and managing video generators."""

    base_generator_cls = BaseVideoGenerator
    package_root = __package__ + ".generators" if __package__ else "inference.generation.video_generators.generators"
    registry_label = "video"

    def __init__(self, generators_dir: Optional[str] = None):
        if generators_dir is None:
            generators_dir = Path(__file__).parent / "generators"
        super().__init__(generators_dir=generators_dir)

    def generate(
        self,
        generator_id: str,
        prompt: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        videos: Optional[List[Union[str, Path]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {}
        if prompt is not None:
            inputs["prompt"] = prompt
        if images is not None:
            inputs["images"] = images
        if videos is not None:
            inputs["videos"] = videos
        inputs.update(kwargs)
        return self._generate_with_inputs(generator_id=generator_id, inputs=inputs)


_registry: Optional[VideoGeneratorRegistry] = None


def get_video_generator_registry() -> VideoGeneratorRegistry:
    global _registry
    if _registry is None:
        _registry = VideoGeneratorRegistry()
    return _registry
