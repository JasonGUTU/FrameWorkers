"""
Inference Module - Language Model Inference and Prompt Processing Tools

This module provides:
- Universal model calling interface (LiteLLM wrapper)
- Custom model interface support (Ollama, etc.)
- Multimodal support (image encoding/decoding)
- Prompt processing tools (message compression, history persistence)
- Prompt templates and composition utilities
"""

from .core.llm_client import LLMClient, ModelConfig
from .core.custom_model import CustomModelClient
from .multimodal.image_utils import ImageUtils
from .multimodal.multimodal_utils import MultimodalUtils
from .prompt.message_utils import MessageUtils
from .prompt.history import MessageHistory
from .prompt.templates import PromptTemplate, TemplateManager
from .config.model_config import ModelRegistry, get_model_config
from .generation.base_generator import BaseImageGenerator, BaseVideoGenerator, GeneratorMetadata
from .generation.image_generator_registry import ImageGeneratorRegistry, get_image_generator_registry
from .generation.video_generator_registry import VideoGeneratorRegistry, get_video_generator_registry

__version__ = "0.1.0"
__all__ = [
    "LLMClient",
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
    "BaseImageGenerator",
    "BaseVideoGenerator",
    "GeneratorMetadata",
    "ImageGeneratorRegistry",
    "VideoGeneratorRegistry",
    "get_image_generator_registry",
    "get_video_generator_registry",
]
