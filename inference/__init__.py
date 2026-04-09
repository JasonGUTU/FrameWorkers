"""
Inference Module - Language Model Inference and Input Processing Tools.

This module provides:
- Universal model calling interface (LiteLLM wrapper)
- Input processing support (text/image helpers)
"""

from .clients import (
    BaseLLMClient,
    LLMClient,
    Message,
    MessageRole,
    ModelConfig,
)
from .input_processing.image_utils import ImageUtils
from .input_processing.message_utils import InputUtils
from .config.model_config import ModelRegistry, get_model_config
from .generation.image_generators.service import FalImageService, ImageService, MockImageService
from .generation.video_generators.service import (
    FalVideoService,
    MockVideoService,
    VideoService,
    WavespeedVideoService,
)
from .generation.audio_generators.service import AudioService, FalAudioService, MockAudioService

__version__ = "0.1.0"
__all__ = [
    "LLMClient",
    "BaseLLMClient",
    "Message",
    "MessageRole",
    "ModelConfig",
    "ImageUtils",
    "InputUtils",
    "ModelRegistry",
    "get_model_config",
    "FalImageService",
    "ImageService",
    "MockImageService",
    "FalVideoService",
    "WavespeedVideoService",
    "VideoService",
    "MockVideoService",
    "FalAudioService",
    "AudioService",
    "MockAudioService",
]
