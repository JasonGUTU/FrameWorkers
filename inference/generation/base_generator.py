"""
Base Generator Classes - Abstract base classes for image and video generators

Provides abstract base classes that all generators must inherit from,
with automatic parameter validation based on input_schema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class GeneratorMetadata:
    """Metadata for a generator"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BaseImageGenerator(ABC):
    """
    Abstract base class for all image generators
    
    Every image generator must inherit from this class and implement the required methods.
    The input_schema in metadata defines what parameters are accepted, and the system
    will automatically validate and extract these parameters.
    
    Example:
        class MyImageGenerator(BaseImageGenerator):
            def get_metadata(self) -> GeneratorMetadata:
                return GeneratorMetadata(
                    id="my_image_generator",
                    name="My Image Generator",
                    description="Generates images using my custom method",
                    input_schema={
                        "prompt": {"type": "string", "required": True, "description": "Text prompt"},
                        "images": {"type": "array", "required": False, "description": "Input images"},
                        "width": {"type": "integer", "required": False, "default": 1024},
                        "height": {"type": "integer", "required": False, "default": 1024},
                    },
                    output_schema={
                        "image": {"type": "string", "description": "Base64 encoded image"},
                        "image_path": {"type": "string", "description": "Path to saved image"},
                    }
                )
            
            def generate(self, **kwargs) -> Dict[str, Any]:
                # Extract validated parameters
                prompt = kwargs.get("prompt")
                images = kwargs.get("images", [])
                width = kwargs.get("width", 1024)
                height = kwargs.get("height", 1024)
                
                # Generate image...
                return {"image": "...", "image_path": "..."}
    """
    
    def __init__(self):
        """Initialize the generator"""
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> GeneratorMetadata:
        """
        Return generator metadata
        
        Returns:
            GeneratorMetadata: Metadata describing this generator
            
        The input_schema should define all parameters that can be passed to generate(),
        with their types, whether they're required, defaults, and descriptions.
        """
        pass
    
    @abstractmethod
    def generate(self, **kwargs) -> Dict[str, Any]:
        """
        Generate image(s) based on inputs
        
        Args:
            **kwargs: Parameters defined in input_schema
            
        Returns:
            Dict[str, Any]: Generated image data matching output_schema
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize inputs against the generator's input_schema
        
        Args:
            inputs: Input data dictionary
            
        Returns:
            Dict[str, Any]: Validated and normalized inputs with defaults applied
            
        Raises:
            ValueError: If inputs are invalid
        """
        schema = self.metadata.input_schema
        if not schema:
            return inputs
        
        validated = {}
        
        # Process each field in schema
        for field_name, field_spec in schema.items():
            if not isinstance(field_spec, dict):
                continue
            
            field_type = field_spec.get("type", "string")
            required = field_spec.get("required", False)
            default = field_spec.get("default")
            
            # Check if field is provided
            if field_name in inputs:
                value = inputs[field_name]
                # Type validation
                if not self._validate_type(value, field_type):
                    raise ValueError(
                        f"Field '{field_name}' must be of type {field_type}, got {type(value).__name__}"
                    )
                validated[field_name] = value
            elif required:
                raise ValueError(f"Required field '{field_name}' is missing")
            elif default is not None:
                validated[field_name] = default
        
        return validated
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        if expected_type in type_mapping:
            expected_python_type = type_mapping[expected_type]
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, skip validation
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this generator"""
        return self.metadata.input_schema
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this generator"""
        return self.metadata.output_schema
    
    def get_info(self) -> Dict[str, Any]:
        """Get complete information about this generator"""
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "capabilities": self.metadata.capabilities,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
        }


class BaseVideoGenerator(ABC):
    """
    Abstract base class for all video generators
    
    Similar to BaseImageGenerator, but for video generation.
    Supports inputs of text, images, and/or videos.
    
    Example:
        class MyVideoGenerator(BaseVideoGenerator):
            def get_metadata(self) -> GeneratorMetadata:
                return GeneratorMetadata(
                    id="my_video_generator",
                    name="My Video Generator",
                    description="Generates videos",
                    input_schema={
                        "prompt": {"type": "string", "required": False},
                        "images": {"type": "array", "required": False},
                        "videos": {"type": "array", "required": False},
                        "duration": {"type": "integer", "required": False, "default": 5},
                    },
                    output_schema={
                        "video": {"type": "string", "description": "Base64 encoded video"},
                        "video_path": {"type": "string", "description": "Path to saved video"},
                    }
                )
            
            def generate(self, **kwargs) -> Dict[str, Any]:
                prompt = kwargs.get("prompt")
                images = kwargs.get("images", [])
                videos = kwargs.get("videos", [])
                # Generate video...
                return {"video": "...", "video_path": "..."}
    """
    
    def __init__(self):
        """Initialize the generator"""
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> GeneratorMetadata:
        """
        Return generator metadata
        
        Returns:
            GeneratorMetadata: Metadata describing this generator
        """
        pass
    
    @abstractmethod
    def generate(self, **kwargs) -> Dict[str, Any]:
        """
        Generate video(s) based on inputs
        
        Args:
            **kwargs: Parameters defined in input_schema
            
        Returns:
            Dict[str, Any]: Generated video data matching output_schema
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize inputs against the generator's input_schema
        
        Args:
            inputs: Input data dictionary
            
        Returns:
            Dict[str, Any]: Validated and normalized inputs with defaults applied
            
        Raises:
            ValueError: If inputs are invalid
        """
        schema = self.metadata.input_schema
        if not schema:
            return inputs
        
        validated = {}
        
        # Process each field in schema
        for field_name, field_spec in schema.items():
            if not isinstance(field_spec, dict):
                continue
            
            field_type = field_spec.get("type", "string")
            required = field_spec.get("required", False)
            default = field_spec.get("default")
            
            # Check if field is provided
            if field_name in inputs:
                value = inputs[field_name]
                # Type validation
                if not self._validate_type(value, field_type):
                    raise ValueError(
                        f"Field '{field_name}' must be of type {field_type}, got {type(value).__name__}"
                    )
                validated[field_name] = value
            elif required:
                raise ValueError(f"Required field '{field_name}' is missing")
            elif default is not None:
                validated[field_name] = default
        
        return validated
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        if expected_type in type_mapping:
            expected_python_type = type_mapping[expected_type]
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, skip validation
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this generator"""
        return self.metadata.input_schema
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this generator"""
        return self.metadata.output_schema
    
    def get_info(self) -> Dict[str, Any]:
        """Get complete information about this generator"""
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "capabilities": self.metadata.capabilities,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
        }


class BaseAudioGenerator(ABC):
    """
    Abstract base class for all audio generators.

    Similar to BaseImageGenerator/BaseVideoGenerator, but for audio generation.
    Typical inputs include text/script/scene metadata; outputs are usually
    encoded audio payloads and/or file paths.
    """

    def __init__(self):
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> GeneratorMetadata:
        """Return generator metadata."""
        pass

    @abstractmethod
    def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate audio data based on validated inputs."""
        pass

    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize inputs against metadata.input_schema."""
        schema = self.metadata.input_schema
        if not schema:
            return inputs

        validated: Dict[str, Any] = {}
        for field_name, field_spec in schema.items():
            if not isinstance(field_spec, dict):
                continue

            field_type = field_spec.get("type", "string")
            required = field_spec.get("required", False)
            default = field_spec.get("default")

            if field_name in inputs:
                value = inputs[field_name]
                if not self._validate_type(value, field_type):
                    raise ValueError(
                        f"Field '{field_name}' must be of type {field_type}, got {type(value).__name__}"
                    )
                validated[field_name] = value
            elif required:
                raise ValueError(f"Required field '{field_name}' is missing")
            elif default is not None:
                validated[field_name] = default

        return validated

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        if expected_type in type_mapping:
            return isinstance(value, type_mapping[expected_type])
        return True

    def get_input_schema(self) -> Dict[str, Any]:
        return self.metadata.input_schema

    def get_output_schema(self) -> Dict[str, Any]:
        return self.metadata.output_schema

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "capabilities": self.metadata.capabilities,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
        }
