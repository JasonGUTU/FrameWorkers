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
]
