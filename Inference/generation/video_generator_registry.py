"""
Video Generator Registry - Discovers and manages all video generators

Provides automatic discovery and registration mechanism for video generators.
"""

import os
import importlib
import inspect
from typing import Dict, List, Optional, Type, Any, Union
from pathlib import Path

from .base_generator import BaseVideoGenerator


class VideoGeneratorRegistry:
    """
    Registry for discovering and managing all video generators
    
    Automatically scans for generators and provides unified interface for video generation.
    """
    
    def __init__(self, generators_dir: Optional[str] = None):
        """
        Initialize the video generator registry
        
        Args:
            generators_dir: Directory containing generator subdirectories.
                          If None, uses default location: Inference/generation/video_generators/
        """
        if generators_dir is None:
            # Default to Inference/generation/video_generators/
            current_file = Path(__file__)
            generators_dir = current_file.parent / "video_generators"
        
        self.generators_dir = Path(generators_dir)
        self._generators: Dict[str, BaseVideoGenerator] = {}
        self._generator_classes: Dict[str, Type[BaseVideoGenerator]] = {}
        
        # Create directory if it doesn't exist
        self.generators_dir.mkdir(parents=True, exist_ok=True)
        
        # Discover generators
        self._discover_generators()
    
    def _discover_generators(self):
        """Discover all generators in the generators directory"""
        if not self.generators_dir.exists():
            return
        
        # Iterate through subdirectories
        for item in self.generators_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Skip __pycache__ and hidden directories
            if item.name.startswith('_') or item.name.startswith('.'):
                continue
            
            # Try to import the generator
            try:
                self._load_generator_from_directory(item)
            except Exception as e:
                # Log error but continue discovering other generators
                print(f"Warning: Failed to load video generator from {item.name}: {e}")
                continue
    
    def _load_generator_from_directory(self, generator_dir: Path):
        """
        Load a generator from a directory
        
        Args:
            generator_dir: Path to the generator directory
        """
        generator_name = generator_dir.name
        
        # Try to import the generator module
        # Expected structure: generator_dir/generator.py or generator_dir/__init__.py
        module_paths = [
            (generator_dir / "generator.py", "generator"),
            (generator_dir / "__init__.py", "__init__")
        ]
        
        for module_path, module_file in module_paths:
            if not module_path.exists():
                continue
            
            try:
                # Add generator directory to sys.path for imports
                import sys
                generator_parent = str(generator_dir.parent)
                if generator_parent not in sys.path:
                    sys.path.insert(0, generator_parent)
                
                # Import strategies
                import_strategies = [
                    f"video_generators.{generator_name}.{module_file}",
                    f"video_generators.{generator_name}",
                ]
                
                for module_name in import_strategies:
                    try:
                        module = importlib.import_module(module_name)
                        
                        # Find all classes that inherit from BaseVideoGenerator
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if (issubclass(obj, BaseVideoGenerator) and 
                                obj != BaseVideoGenerator and 
                                obj.__module__ == module.__name__):
                                
                                # Instantiate the generator
                                generator_instance = obj()
                                generator_id = generator_instance.metadata.id
                                
                                # Register the generator
                                self._generators[generator_id] = generator_instance
                                self._generator_classes[generator_id] = obj
                                return  # Successfully loaded, exit
                    except ImportError as e:
                        continue
                
            except Exception as e:
                print(f"Warning: Failed to load generator from {generator_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def register_generator(self, generator: BaseVideoGenerator):
        """
        Manually register a generator
        
        Args:
            generator: Generator instance to register
        """
        generator_id = generator.metadata.id
        self._generators[generator_id] = generator
        self._generator_classes[generator_id] = type(generator)
    
    def get_generator(self, generator_id: str) -> Optional[BaseVideoGenerator]:
        """
        Get a generator instance by ID
        
        Args:
            generator_id: ID of the generator
            
        Returns:
            BaseVideoGenerator instance or None if not found
        """
        return self._generators.get(generator_id)
    
    def get_generator_class(self, generator_id: str) -> Optional[Type[BaseVideoGenerator]]:
        """
        Get a generator class by ID
        
        Args:
            generator_id: ID of the generator
            
        Returns:
            Generator class or None if not found
        """
        return self._generator_classes.get(generator_id)
    
    def list_generators(self) -> List[str]:
        """
        List all registered generator IDs
        
        Returns:
            List of generator IDs
        """
        return list(self._generators.keys())
    
    def generate(
        self,
        generator_id: str,
        prompt: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        videos: Optional[List[Union[str, Path]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using a registered generator
        
        This is the unified interface for video generation. It automatically
        validates inputs based on the generator's input_schema and extracts
        parameters. Supports text, images, and/or videos as input.
        
        Args:
            generator_id: ID of the generator to use
            prompt: Text prompt (optional, depends on generator)
            images: List of input image paths or base64 strings (optional)
            videos: List of input video paths or base64 strings (optional)
            **kwargs: Additional parameters defined in generator's input_schema
            
        Returns:
            Dict containing generated video data matching generator's output_schema
            
        Raises:
            ValueError: If generator not found or inputs invalid
            RuntimeError: If generation fails
        """
        generator = self.get_generator(generator_id)
        if not generator:
            raise ValueError(f"Video generator '{generator_id}' not found")
        
        # Build inputs dictionary
        inputs = {}
        if prompt is not None:
            inputs["prompt"] = prompt
        if images is not None:
            inputs["images"] = images
        if videos is not None:
            inputs["videos"] = videos
        inputs.update(kwargs)
        
        # Validate inputs
        validated_inputs = generator.validate_inputs(inputs)
        
        # Generate video
        result = generator.generate(**validated_inputs)
        
        return result
    
    def get_all_generators_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered generators
        
        Returns:
            List of generator information dictionaries
        """
        return [generator.get_info() for generator in self._generators.values()]
    
    def reload(self):
        """Reload all generators from the directory"""
        self._generators.clear()
        self._generator_classes.clear()
        self._discover_generators()


# Global registry instance
_registry: Optional[VideoGeneratorRegistry] = None


def get_video_generator_registry() -> VideoGeneratorRegistry:
    """
    Get the global video generator registry instance
    
    Returns:
        VideoGeneratorRegistry: Global registry instance
    """
    global _registry
    if _registry is None:
        _registry = VideoGeneratorRegistry()
    return _registry
