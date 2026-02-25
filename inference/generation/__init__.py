"""Generation modules - image/video/audio generation with plugin system."""

from .base_generator import (
    BaseAudioGenerator,
    BaseImageGenerator,
    BaseVideoGenerator,
    GeneratorMetadata,
)
from .base_registry import BaseGeneratorRegistry
from .image_generators.registry import ImageGeneratorRegistry, get_image_generator_registry
from .video_generators.registry import VideoGeneratorRegistry, get_video_generator_registry
from .audio_generators.registry import AudioGeneratorRegistry, get_audio_generator_registry
from .image_generators.service import ImageService, MockImageService
from .video_generators.service import VideoService, MockVideoService
from .audio_generators.service import AudioService, MockAudioService

__all__ = [
    "BaseAudioGenerator",
    "BaseImageGenerator",
    "BaseVideoGenerator",
    "BaseGeneratorRegistry",
    "GeneratorMetadata",
    "AudioGeneratorRegistry",
    "ImageGeneratorRegistry",
    "VideoGeneratorRegistry",
    "get_audio_generator_registry",
    "get_image_generator_registry",
    "get_video_generator_registry",
    "ImageService",
    "MockImageService",
    "VideoService",
    "MockVideoService",
    "AudioService",
    "MockAudioService",
]
