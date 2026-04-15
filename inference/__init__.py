"""
Inference Module - Language Model Inference and Media Generation.

This module provides:
- Universal model calling interface (LiteLLM wrapper)
- Image / video / audio generation services
"""

from .clients import (
    BaseLLMClient,
    LLMClient,
    Message,
    MessageRole,
    ModelConfig,
)
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
