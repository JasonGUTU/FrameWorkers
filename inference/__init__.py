"""
Inference Module - Language Model Inference and Prompt Processing Tools

This module provides:
- Universal model calling interface (LiteLLM wrapper)
- Custom model interface support (Ollama, etc.)
- Multimodal support (image encoding/decoding)
- Prompt processing tools (message compression, history persistence)
- Prompt templates and composition utilities
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
from .multimodal.image_utils import ImageUtils
from .multimodal.multimodal_utils import MultimodalUtils
from .prompt.message_utils import MessageUtils
from .prompt.history import MessageHistory
from .prompt.templates import PromptTemplate, TemplateManager
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
    "MultimodalUtils",
    "MessageUtils",
    "MessageHistory",
    "PromptTemplate",
    "TemplateManager",
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
