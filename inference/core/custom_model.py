"""
Custom Model Client - Interface for Custom/Self-developed Models

Provides interface for connecting custom models, especially through Ollama.
"""

from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator
import os
import json
import requests
from .llm_client import LLMClient, Message, ModelConfig


class CustomModelClient(LLMClient):
    """
    Client for custom/self-developed models
    
    Extends LLMClient to provide specific support for custom models,
    especially those served through Ollama or custom endpoints.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize Custom Model Client
        
        Args:
            base_url: Base URL for custom model API (e.g., Ollama endpoint)
            default_model: Default model to use
            api_key: API key if required
            config_path: Path to configuration file
        """
        # Set default base URL for Ollama if not provided
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Initialize parent with custom base URL
        super().__init__(default_model=default_model, config_path=config_path)
        
        self.base_url = base_url
        self.api_key = api_key
        
        # Configure LiteLLM for Ollama
        if "ollama" in base_url.lower() or "localhost" in base_url.lower():
            self._setup_ollama()
    
    def _setup_ollama(self):
        """Setup Ollama-specific configuration"""
        # Register Ollama models with LiteLLM
        # LiteLLM supports Ollama via ollama/ prefix
        try:
            import litellm
            # Set base URL for Ollama
            os.environ["OLLAMA_API_BASE"] = self.base_url
        except ImportError:
            pass
    
    def register_custom_model(
        self,
        model_id: str,
        name: str,
        provider: str = "custom",
        supports_streaming: bool = True,
        supports_multimodal: bool = False,
        max_tokens: Optional[int] = None,
        context_window: Optional[int] = None,
        description: Optional[str] = None
    ):
        """
        Register a custom model
        
        Args:
            model_id: Unique model identifier
            name: Display name for the model
            provider: Provider name (default: "custom")
            supports_streaming: Whether model supports streaming
            supports_multimodal: Whether model supports multimodal inputs
            max_tokens: Maximum tokens in response
            context_window: Context window size
            description: Model description
        """
        from ..config.model_config import ModelInfo
        
        model_info = ModelInfo(
            name=name,
            provider=provider,
            model_id=model_id,
            supports_streaming=supports_streaming,
            supports_multimodal=supports_multimodal,
            max_tokens=max_tokens,
            context_window=context_window,
            description=description or f"Custom model: {name}"
        )
        
        self.model_registry.register_model(model_info)
    
    def call_ollama(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Ollama model directly (alternative to LiteLLM)
        
        This provides a direct interface to Ollama API without LiteLLM.
        
        Args:
            messages: List of messages
            model: Model identifier (e.g., "llama2", "llama3")
            config: ModelConfig object
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        model = model or self.default_model
        
        # Format messages for Ollama
        formatted_messages = self._format_messages(messages)
        
        # Build request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
        }
        
        # Add config parameters
        if config:
            if config.temperature is not None:
                payload["options"] = payload.get("options", {})
                payload["options"]["temperature"] = config.temperature
            if config.max_tokens:
                payload["options"] = payload.get("options", {})
                payload["options"]["num_predict"] = config.max_tokens
        
        # Add kwargs
        payload.update(kwargs)
        
        # Make request to Ollama
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=config.timeout if config else 60.0
        )
        response.raise_for_status()
        
        return response.json()
    
    def stream_ollama(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        model: Optional[str] = None,
        config: Optional[ModelConfig] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream call to Ollama model directly
        
        Args:
            messages: List of messages
            model: Model identifier
            config: ModelConfig object
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        model = model or self.default_model
        
        # Format messages for Ollama
        formatted_messages = self._format_messages(messages)
        
        # Build request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": True,
        }
        
        # Add config parameters
        if config:
            if config.temperature is not None:
                payload["options"] = payload.get("options", {})
                payload["options"]["temperature"] = config.temperature
            if config.max_tokens:
                payload["options"] = payload.get("options", {})
                payload["options"]["num_predict"] = config.max_tokens
        
        # Add kwargs
        payload.update(kwargs)
        
        # Stream request to Ollama
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=config.timeout if config else 60.0
        )
        response.raise_for_status()
        
        # Yield chunks
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    yield chunk
                except json.JSONDecodeError:
                    continue
    
    def list_ollama_models(self) -> List[str]:
        """
        List available Ollama models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Warning: Failed to list Ollama models: {e}")
            return []
    
    def pull_ollama_model(self, model_name: str) -> bool:
        """
        Pull/download an Ollama model
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300.0  # Long timeout for model download
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Warning: Failed to pull Ollama model {model_name}: {e}")
            return False
