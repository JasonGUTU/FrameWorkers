"""
Model Configuration and Registry

Provides model registry and configuration management for all supported models.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ModelInfo:
    """Information about a model"""
    name: str
    provider: str  # e.g., "openai", "anthropic", "ollama", "custom"
    model_id: str  # The actual model identifier
    supports_streaming: bool = True
    supports_multimodal: bool = False
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    description: Optional[str] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """
    Registry for all available models
    
    Maintains a list of supported models and their configurations.
    """
    
    # Common OpenAI models
    OPENAI_MODELS = {
        "gpt-5": ModelInfo(
            name="GPT-5",
            provider="openai",
            model_id="gpt-5",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=16384,
            context_window=200000,
            description="OpenAI GPT-5 model"
        ),
        "gpt-5-mini": ModelInfo(
            name="GPT-5 Mini",
            provider="openai",
            model_id="gpt-5-mini",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=16384,
            context_window=200000,
            description="OpenAI GPT-5 Mini model"
        ),
        "gpt-4o": ModelInfo(
            name="GPT-4o",
            provider="openai",
            model_id="gpt-4o",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=16384,
            context_window=128000,
            description="OpenAI GPT-4o model with multimodal support"
        ),
        "gpt-4o-mini": ModelInfo(
            name="GPT-4o Mini",
            provider="openai",
            model_id="gpt-4o-mini",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=16384,
            context_window=128000,
            description="OpenAI GPT-4o Mini model"
        ),
        "gpt-4-turbo": ModelInfo(
            name="GPT-4 Turbo",
            provider="openai",
            model_id="gpt-4-turbo",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=4096,
            context_window=128000,
            description="OpenAI GPT-4 Turbo model"
        ),
        "gpt-4": ModelInfo(
            name="GPT-4",
            provider="openai",
            model_id="gpt-4",
            supports_streaming=True,
            supports_multimodal=False,
            max_tokens=4096,
            context_window=8192,
            description="OpenAI GPT-4 model"
        ),
        "gpt-3.5-turbo": ModelInfo(
            name="GPT-3.5 Turbo",
            provider="openai",
            model_id="gpt-3.5-turbo",
            supports_streaming=True,
            supports_multimodal=False,
            max_tokens=4096,
            context_window=16385,
            description="OpenAI GPT-3.5 Turbo model"
        ),
    }
    
    # Anthropic models
    ANTHROPIC_MODELS = {
        "claude-3-5-sonnet-20241022": ModelInfo(
            name="Claude 3.5 Sonnet",
            provider="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=8192,
            context_window=200000,
            description="Anthropic Claude 3.5 Sonnet model"
        ),
        "claude-3-opus-20240229": ModelInfo(
            name="Claude 3 Opus",
            provider="anthropic",
            model_id="claude-3-opus-20240229",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=4096,
            context_window=200000,
            description="Anthropic Claude 3 Opus model"
        ),
        "claude-3-sonnet-20240229": ModelInfo(
            name="Claude 3 Sonnet",
            provider="anthropic",
            model_id="claude-3-sonnet-20240229",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=4096,
            context_window=200000,
            description="Anthropic Claude 3 Sonnet model"
        ),
        "claude-3-haiku-20240307": ModelInfo(
            name="Claude 3 Haiku",
            provider="anthropic",
            model_id="claude-3-haiku-20240307",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=4096,
            context_window=200000,
            description="Anthropic Claude 3 Haiku model"
        ),
    }
    
    # Google models
    GOOGLE_MODELS = {
        "gemini-pro": ModelInfo(
            name="Gemini Pro",
            provider="google",
            model_id="gemini-pro",
            supports_streaming=True,
            supports_multimodal=False,
            max_tokens=8192,
            context_window=32768,
            description="Google Gemini Pro model"
        ),
        "gemini-pro-vision": ModelInfo(
            name="Gemini Pro Vision",
            provider="google",
            model_id="gemini-pro-vision",
            supports_streaming=True,
            supports_multimodal=True,
            max_tokens=4096,
            context_window=16384,
            description="Google Gemini Pro Vision model"
        ),
    }
    
    # Ollama models (custom/local models)
    OLLAMA_MODELS = {
        "llama2": ModelInfo(
            name="Llama 2",
            provider="ollama",
            model_id="llama2",
            supports_streaming=True,
            supports_multimodal=False,
            description="Meta Llama 2 via Ollama"
        ),
        "llama3": ModelInfo(
            name="Llama 3",
            provider="ollama",
            model_id="llama3",
            supports_streaming=True,
            supports_multimodal=False,
            description="Meta Llama 3 via Ollama"
        ),
        "mistral": ModelInfo(
            name="Mistral",
            provider="ollama",
            model_id="mistral",
            supports_streaming=True,
            supports_multimodal=False,
            description="Mistral model via Ollama"
        ),
        "codellama": ModelInfo(
            name="Code Llama",
            provider="ollama",
            model_id="codellama",
            supports_streaming=True,
            supports_multimodal=False,
            description="Code Llama via Ollama"
        ),
    }
    
    def __init__(self):
        """Initialize the model registry"""
        self._models: Dict[str, ModelInfo] = {}
        self._load_default_models()
    
    def _load_default_models(self):
        """Load all default models into registry"""
        all_models = {
            **self.OPENAI_MODELS,
            **self.ANTHROPIC_MODELS,
            **self.GOOGLE_MODELS,
            **self.OLLAMA_MODELS,
        }
        self._models.update(all_models)
    
    def register_model(self, model_info: ModelInfo):
        """
        Register a custom model
        
        Args:
            model_info: ModelInfo object containing model details
        """
        self._models[model_info.model_id] = model_info
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get model information by ID
        
        Args:
            model_id: Model identifier
            
        Returns:
            ModelInfo if found, None otherwise
        """
        return self._models.get(model_id)
    
    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """
        List all registered model IDs
        
        Args:
            provider: Optional provider filter (e.g., "openai", "anthropic")
            
        Returns:
            List of model IDs
        """
        if provider:
            return [
                model_id for model_id, info in self._models.items()
                if info.provider == provider
            ]
        return list(self._models.keys())
    
    def list_models_by_provider(self) -> Dict[str, List[str]]:
        """
        List all models grouped by provider
        
        Returns:
            Dictionary mapping provider to list of model IDs
        """
        result: Dict[str, List[str]] = {}
        for model_id, info in self._models.items():
            if info.provider not in result:
                result[info.provider] = []
            result[info.provider].append(model_id)
        return result
    
    def get_all_models_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered models
        
        Returns:
            Dictionary mapping model_id to model information
        """
        return {
            model_id: {
                "name": info.name,
                "provider": info.provider,
                "model_id": info.model_id,
                "supports_streaming": info.supports_streaming,
                "supports_multimodal": info.supports_multimodal,
                "max_tokens": info.max_tokens,
                "context_window": info.context_window,
                "description": info.description,
                "custom_config": info.custom_config,
            }
            for model_id, info in self._models.items()
        }


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_model_config(model_id: str) -> Optional[ModelInfo]:
    """
    Get model configuration by ID
    
    Args:
        model_id: Model identifier
        
    Returns:
        ModelInfo if found, None otherwise
    """
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry.get_model(model_id)
