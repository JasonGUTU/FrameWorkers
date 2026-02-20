"""
Example Image Generator

This is a template/example for creating custom image generators.
Copy this file and modify it to implement your own image generation logic.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import base64

from ...base_generator import BaseImageGenerator, GeneratorMetadata


class ExampleImageGenerator(BaseImageGenerator):
    """
    Example image generator implementation
    
    This generator demonstrates how to:
    1. Define input_schema with all accepted parameters
    2. Implement the generate() method
    3. Return results matching output_schema
    
    To create your own generator:
    1. Copy this file to a new directory under image_generators/
    2. Rename the class and update metadata
    3. Implement your generation logic in generate()
    4. The generator will be automatically discovered and registered
    """
    
    def get_metadata(self) -> GeneratorMetadata:
        """
        Define generator metadata and input/output schemas
        
        The input_schema defines all parameters that can be passed to generate().
        The system will automatically validate and extract these parameters.
        """
        return GeneratorMetadata(
            id="example_image_generator",
            name="Example Image Generator",
            description="Example template for image generation - modify this to create your own generator",
            version="1.0.0",
            author="Inference Module",
            capabilities=["text_to_image", "image_to_image"],
            input_schema={
                "prompt": {
                    "type": "string",
                    "required": True,
                    "description": "Text prompt describing the image to generate"
                },
                "images": {
                    "type": "array",
                    "required": False,
                    "description": "List of input images (paths or base64 strings) for image-to-image generation"
                },
                "width": {
                    "type": "integer",
                    "required": False,
                    "default": 1024,
                    "description": "Width of the generated image in pixels"
                },
                "height": {
                    "type": "integer",
                    "required": False,
                    "default": 1024,
                    "description": "Height of the generated image in pixels"
                },
                "num_images": {
                    "type": "integer",
                    "required": False,
                    "default": 1,
                    "description": "Number of images to generate"
                },
                "style": {
                    "type": "string",
                    "required": False,
                    "default": "realistic",
                    "description": "Style of the image (e.g., 'realistic', 'anime', 'cartoon')"
                },
                "seed": {
                    "type": "integer",
                    "required": False,
                    "description": "Random seed for reproducibility"
                },
            },
            output_schema={
                "images": {
                    "type": "array",
                    "description": "List of generated images (base64 encoded strings)"
                },
                "image_paths": {
                    "type": "array",
                    "description": "List of paths to saved image files"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata about the generation"
                }
            }
        )
    
    def generate(self, **kwargs) -> Dict[str, Any]:
        """
        Generate image(s) based on inputs
        
        This method receives validated parameters based on input_schema.
        Implement your actual generation logic here (API calls, local model, etc.).
        
        Args:
            **kwargs: Validated parameters from input_schema:
                - prompt: str (required)
                - images: List[str] (optional)
                - width: int (default: 1024)
                - height: int (default: 1024)
                - num_images: int (default: 1)
                - style: str (default: "realistic")
                - seed: int (optional)
        
        Returns:
            Dict matching output_schema:
                - images: List[str] (base64 encoded images)
                - image_paths: List[str] (paths to saved files)
                - metadata: Dict (additional info)
        """
        # Extract validated parameters
        prompt = kwargs.get("prompt")
        images = kwargs.get("images", [])
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        num_images = kwargs.get("num_images", 1)
        style = kwargs.get("style", "realistic")
        seed = kwargs.get("seed")
        
        # TODO: Implement your actual generation logic here
        # Examples:
        # - Call an API (OpenAI DALL-E, Stability AI, etc.)
        # - Use a local model (Stable Diffusion, etc.)
        # - Process input images for image-to-image
        
        # For now, this is a placeholder that returns dummy data
        print(f"[ExampleImageGenerator] Generating {num_images} image(s)")
        print(f"  Prompt: {prompt}")
        print(f"  Size: {width}x{height}")
        print(f"  Style: {style}")
        if images:
            print(f"  Input images: {len(images)}")
        if seed:
            print(f"  Seed: {seed}")
        
        # Placeholder: Return dummy base64 image
        # In real implementation, this would be the actual generated image
        dummy_image_base64 = self._create_dummy_image_base64(width, height)
        
        # Save to file (optional)
        output_dir = Path("./generated_images")
        output_dir.mkdir(exist_ok=True)
        image_paths = []
        for i in range(num_images):
            image_path = output_dir / f"generated_{i}.png"
            self._save_base64_image(dummy_image_base64, image_path)
            image_paths.append(str(image_path))
        
        return {
            "images": [dummy_image_base64] * num_images,
            "image_paths": image_paths,
            "metadata": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_images": num_images,
                "style": style,
                "seed": seed,
                "has_input_images": len(images) > 0,
            }
        }
    
    def _create_dummy_image_base64(self, width: int, height: int) -> str:
        """
        Create a dummy base64 image for demonstration
        
        In real implementation, this would call your actual generation API/model.
        """
        # Create a simple colored image using PIL
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (width, height), color='lightblue')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple pattern
            draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], fill='white')
            draw.text((width//2 - 50, height//2 - 10), "Example", fill='black')
            
            # Convert to base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            
            return f"data:image/png;base64,{base64_str}"
        except ImportError:
            # Fallback if PIL not available
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    def _save_base64_image(self, base64_str: str, output_path: Path):
        """Save base64 image to file"""
        try:
            from PIL import Image
            import io
            
            # Remove data URI prefix if present
            if ',' in base64_str:
                base64_str = base64_str.split(',', 1)[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_str)
            img = Image.open(io.BytesIO(image_data))
            img.save(output_path)
        except Exception as e:
            print(f"Warning: Failed to save image: {e}")
