"""
Inference Module - Language Model Inference and Input Processing Tools.

This module provides:
- Universal model calling interface (LiteLLM wrapper)
- Custom model interface support (Ollama, etc.)
- Input processing support (text/image helpers)
"""

from .runtime.base_client import (
    BaseLLMClient,
    CustomModelClient,
    GPT5ChatClient,
    LLMClient,
    Message,
    MessageRole,
    ModelConfig,
)
from .input_processing.image_utils import ImageUtils
from .input_processing.message_utils import InputUtils, MessageUtils, MultimodalUtils
from .config.model_config import ModelRegistry, get_model_config
from .generation.base_generator import (
    BaseAudioGenerator,
    BaseImageGenerator,
    BaseVideoGenerator,
    GeneratorMetadata,
)
from .generation.base_registry import BaseGeneratorRegistry
from .generation.image_generators.registry import (
    ImageGeneratorRegistry,
    get_image_generator_registry,
)
from .generation.video_generators.registry import (
    VideoGeneratorRegistry,
    get_video_generator_registry,
)
from .generation.audio_generators.registry import (
    AudioGeneratorRegistry,
    get_audio_generator_registry,
)
from .generation.image_generators.service import ImageService, MockImageService
from .generation.video_generators.service import VideoService, MockVideoService
from .generation.audio_generators.service import AudioService, MockAudioService

__version__ = "0.1.0"
__all__ = [
    "LLMClient",
    "BaseLLMClient",
    "GPT5ChatClient",
    "Message",
    "MessageRole",
    "ModelConfig",
    "CustomModelClient",
    "ImageUtils",
    "InputUtils",
    "MessageUtils",
    "MultimodalUtils",
    "ModelRegistry",
    "get_model_config",
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
