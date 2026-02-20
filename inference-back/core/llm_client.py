"""
Universal LLM Client - LiteLLM Wrapper

Provides a unified interface for calling all language models through LiteLLM,
enabling OpenAI-compatible API calls to any supported model.
"""

from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import os

try:
    import litellm
    from litellm import completion, acompletion, stream, astream
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None

from ..config.model_config import ModelRegistry, get_model_config


class MessageRole(str, Enum):
    """Message role types"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class ModelConfig:
    """Configuration for model calls"""
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False
    timeout: Optional[float] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Chat message structure"""
    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class LLMClient:
    """
    Universal LLM Client using LiteLLM
    
    Provides OpenAI-compatible interface for all supported models.
    """
    
    def __init__(self, default_model: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize LLM Client
        
        Args:
            default_model: Default model to use if not specified in calls
            config_path: Path to configuration file for model settings
        """
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is not installed. Please install it with: pip install litellm"
            )
        
        self.default_model = default_model or os.getenv("INFERENCE_DEFAULT_MODEL", "gpt-3.5-turbo")
        self.model_registry = ModelRegistry()
        self.config_path = config_path
        
        # Load configuration if provided
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from file"""
        from ..utils.config_loader import ConfigLoader
        config = ConfigLoader.load(config_path)
        
        # Set default model from config
        if "default_model" in config:
            self.default_model = config["default_model"]
        
        # Set environment variables for API keys
        if "api_keys" in config:
            for provider, key in config["api_keys"].items():
                env_var = f"{provider.upper()}_API_KEY"
                if not os.getenv(env_var):
                    os.environ[env_var] = key
    
    def call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call language model (synchronous)
        
        Args:
            messages: List of messages (Message objects or dicts)
            model: Model identifier (uses default if not specified)
            config: ModelConfig object with call parameters
            **kwargs: Additional parameters to pass to LiteLLM
            
        Returns:
            Response dictionary containing choices, usage, etc.
        """
        model = model or self.default_model
        
        # Convert Message objects to dicts
        formatted_messages = self._format_messages(messages)
        
        # Build call parameters
        call_params = self._build_call_params(model, config, **kwargs)
        
        # Make the call
        response = completion(
            model=model,
            messages=formatted_messages,
            **call_params
        )
        
        return self._format_response(response)
    
    async def acall(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call language model (asynchronous)
        
        Args:
            messages: List of messages (Message objects or dicts)
            model: Model identifier (uses default if not specified)
            config: ModelConfig object with call parameters
            **kwargs: Additional parameters to pass to LiteLLM
            
        Returns:
            Response dictionary containing choices, usage, etc.
        """
        model = model or self.default_model
        
        # Convert Message objects to dicts
        formatted_messages = self._format_messages(messages)
        
        # Build call parameters
        call_params = self._build_call_params(model, config, **kwargs)
        
        # Make the async call
        response = await acompletion(
            model=model,
            messages=formatted_messages,
            **call_params
        )
        
        return self._format_response(response)
    
    def stream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream call to language model (synchronous)
        
        Args:
            messages: List of messages (Message objects or dicts)
            model: Model identifier (uses default if not specified)
            config: ModelConfig object with call parameters
            **kwargs: Additional parameters to pass to LiteLLM
            
        Yields:
            Response chunks as dictionaries
        """
        model = model or self.default_model
        
        # Convert Message objects to dicts
        formatted_messages = self._format_messages(messages)
        
        # Build call parameters
        call_params = self._build_call_params(model, config, stream=True, **kwargs)
        
        # Stream the call
        for chunk in stream(
            model=model,
            messages=formatted_messages,
            **call_params
        ):
            yield self._format_chunk(chunk)
    
    async def astream_call(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream call to language model (asynchronous)
        
        Args:
            messages: List of messages (Message objects or dicts)
            model: Model identifier (uses default if not specified)
            config: ModelConfig object with call parameters
            **kwargs: Additional parameters to pass to LiteLLM
            
        Yields:
            Response chunks as dictionaries
        """
        model = model or self.default_model
        
        # Convert Message objects to dicts
        formatted_messages = self._format_messages(messages)
        
        # Build call parameters
        call_params = self._build_call_params(model, config, stream=True, **kwargs)
        
        # Stream the async call
        async for chunk in astream(
            model=model,
            messages=formatted_messages,
            **call_params
        ):
            yield self._format_chunk(chunk)
    
    def _format_messages(self, messages: List[Union[Message, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Convert Message objects to dicts"""
        formatted = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted.append({
                    "role": msg.role,
                    "content": msg.content,
                    **({k: v for k, v in {
                        "name": msg.name,
                        "tool_calls": msg.tool_calls,
                        "tool_call_id": msg.tool_call_id,
                    }.items() if v is not None})
                })
            else:
                formatted.append(msg)
        return formatted
    
    def _build_call_params(
        self,
        model: str,
        config: Optional[ModelConfig],
        **kwargs
    ) -> Dict[str, Any]:
        """Build parameters for LiteLLM call"""
        params = {}
        
        # Get model info for defaults
        model_info = self.model_registry.get_model(model)
        
        # Apply config if provided
        if config:
            params.update({
                "temperature": config.temperature,
                "max_tokens": config.max_tokens or (model_info.max_tokens if model_info else None),
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
                "stop": config.stop,
                "stream": config.stream,
                "timeout": config.timeout,
            })
            
            # Add custom headers and extra params
            if config.custom_headers:
                params["extra_headers"] = config.custom_headers
            if config.extra_params:
                params.update(config.extra_params)
            
            # Set API key and base URL if provided
            if config.api_key:
                # Set environment variable for LiteLLM
                provider = model_info.provider if model_info else "openai"
                env_var = f"{provider.upper()}_API_KEY"
                os.environ[env_var] = config.api_key
            
            if config.base_url:
                params["api_base"] = config.base_url
        
        # Override with kwargs
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return params
    
    def _format_response(self, response: Any) -> Dict[str, Any]:
        """Format LiteLLM response to standard format"""
        if hasattr(response, 'model_dump'):
            # Pydantic model
            return response.model_dump()
        elif hasattr(response, 'dict'):
            # Pydantic v1
            return response.dict()
        elif isinstance(response, dict):
            return response
        else:
            # Convert to dict
            return {
                "choices": getattr(response, 'choices', []),
                "usage": getattr(response, 'usage', {}),
                "model": getattr(response, 'model', ''),
                "id": getattr(response, 'id', ''),
            }
    
    def _format_chunk(self, chunk: Any) -> Dict[str, Any]:
        """Format streaming chunk to standard format"""
        if hasattr(chunk, 'model_dump'):
            return chunk.model_dump()
        elif hasattr(chunk, 'dict'):
            return chunk.dict()
        elif isinstance(chunk, dict):
            return chunk
        else:
            return {
                "choices": getattr(chunk, 'choices', []),
                "model": getattr(chunk, 'model', ''),
                "id": getattr(chunk, 'id', ''),
            }
    
    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Get list of available models
        
        Args:
            provider: Optional provider filter
            
        Returns:
            List of model IDs
        """
        return self.model_registry.list_models(provider=provider)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information dictionary or None
        """
        model_info = self.model_registry.get_model(model_id)
        if model_info:
            return {
                "name": model_info.name,
                "provider": model_info.provider,
                "model_id": model_info.model_id,
                "supports_streaming": model_info.supports_streaming,
                "supports_multimodal": model_info.supports_multimodal,
                "max_tokens": model_info.max_tokens,
                "context_window": model_info.context_window,
                "description": model_info.description,
            }
        return None
