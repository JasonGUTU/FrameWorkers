"""Audio generator registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..base_generator import BaseAudioGenerator
from ..base_registry import BaseGeneratorRegistry


class AudioGeneratorRegistry(BaseGeneratorRegistry[BaseAudioGenerator]):
    """Registry for discovering and managing audio generators."""

    base_generator_cls = BaseAudioGenerator
    package_root = __package__ + ".generators" if __package__ else "inference.generation.audio_generators.generators"
    registry_label = "audio"

    def __init__(self, generators_dir: Optional[str] = None):
        if generators_dir is None:
            generators_dir = Path(__file__).parent / "generators"
        super().__init__(generators_dir=generators_dir)

    def generate(
        self,
        generator_id: str,
        text: Optional[str] = None,
        prompt: Optional[str] = None,
        audio_clips: Optional[List[Union[str, Path]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {}
        if text is not None:
            inputs["text"] = text
        if prompt is not None:
            inputs["prompt"] = prompt
        if audio_clips is not None:
            inputs["audio_clips"] = audio_clips
        inputs.update(kwargs)
        return self._generate_with_inputs(generator_id=generator_id, inputs=inputs)


_registry: Optional[AudioGeneratorRegistry] = None


def get_audio_generator_registry() -> AudioGeneratorRegistry:
    global _registry
    if _registry is None:
        _registry = AudioGeneratorRegistry()
    return _registry
