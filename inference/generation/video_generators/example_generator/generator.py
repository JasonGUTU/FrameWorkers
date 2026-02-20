"""
Example Video Generator

This is a template/example for creating custom video generators.
Copy this file and modify it to implement your own video generation logic.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import base64

from ...base_generator import BaseVideoGenerator, GeneratorMetadata


class ExampleVideoGenerator(BaseVideoGenerator):
    """
    Example video generator implementation
    
    This generator demonstrates how to:
    1. Define input_schema with all accepted parameters (text, images, videos)
    2. Implement the generate() method
    3. Return results matching output_schema
    
    To create your own generator:
    1. Copy this file to a new directory under video_generators/
    2. Rename the class and update metadata
    3. Implement your generation logic in generate()
    4. The generator will be automatically discovered and registered
    """
    
    def get_metadata(self) -> GeneratorMetadata:
        """
        Define generator metadata and input/output schemas
        
        The input_schema defines all parameters that can be passed to generate().
        Supports text, images, and/or videos as input.
        """
        return GeneratorMetadata(
            id="example_video_generator",
            name="Example Video Generator",
            description="Example template for video generation - modify this to create your own generator",
            version="1.0.0",
            author="Inference Module",
            capabilities=["text_to_video", "image_to_video", "video_to_video"],
            input_schema={
                "prompt": {
                    "type": "string",
                    "required": False,
                    "description": "Text prompt describing the video to generate"
                },
                "images": {
                    "type": "array",
                    "required": False,
                    "description": "List of input images (paths or base64 strings) for image-to-video generation"
                },
                "videos": {
                    "type": "array",
                    "required": False,
                    "description": "List of input videos (paths or base64 strings) for video-to-video generation"
                },
                "duration": {
                    "type": "integer",
                    "required": False,
                    "default": 5,
                    "description": "Duration of the generated video in seconds"
                },
                "fps": {
                    "type": "integer",
                    "required": False,
                    "default": 24,
                    "description": "Frames per second for the generated video"
                },
                "width": {
                    "type": "integer",
                    "required": False,
                    "default": 1280,
                    "description": "Width of the generated video in pixels"
                },
                "height": {
                    "type": "integer",
                    "required": False,
                    "default": 720,
                    "description": "Height of the generated video in pixels"
                },
                "style": {
                    "type": "string",
                    "required": False,
                    "default": "realistic",
                    "description": "Style of the video (e.g., 'realistic', 'anime', 'cartoon')"
                },
                "seed": {
                    "type": "integer",
                    "required": False,
                    "description": "Random seed for reproducibility"
                },
            },
            output_schema={
                "video": {
                    "type": "string",
                    "description": "Base64 encoded video data"
                },
                "video_path": {
                    "type": "string",
                    "description": "Path to saved video file"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata about the generation"
                }
            }
        )
    
    def generate(self, **kwargs) -> Dict[str, Any]:
        """
        Generate video based on inputs
        
        This method receives validated parameters based on input_schema.
        Supports text-only, image-to-video, video-to-video, or combinations.
        Implement your actual generation logic here (API calls, local model, etc.).
        
        Args:
            **kwargs: Validated parameters from input_schema:
                - prompt: str (optional)
                - images: List[str] (optional)
                - videos: List[str] (optional)
                - duration: int (default: 5)
                - fps: int (default: 24)
                - width: int (default: 1280)
                - height: int (default: 720)
                - style: str (default: "realistic")
                - seed: int (optional)
        
        Returns:
            Dict matching output_schema:
                - video: str (base64 encoded video)
                - video_path: str (path to saved file)
                - metadata: Dict (additional info)
        """
        # Extract validated parameters
        prompt = kwargs.get("prompt")
        images = kwargs.get("images", [])
        videos = kwargs.get("videos", [])
        duration = kwargs.get("duration", 5)
        fps = kwargs.get("fps", 24)
        width = kwargs.get("width", 1280)
        height = kwargs.get("height", 720)
        style = kwargs.get("style", "realistic")
        seed = kwargs.get("seed")
        
        # Determine generation mode
        if videos:
            mode = "video_to_video"
        elif images:
            mode = "image_to_video"
        elif prompt:
            mode = "text_to_video"
        else:
            raise ValueError("At least one of 'prompt', 'images', or 'videos' must be provided")
        
        # TODO: Implement your actual generation logic here
        # Examples:
        # - Call an API (Runway ML, Pika Labs, etc.)
        # - Use a local model (AnimateDiff, etc.)
        # - Process input images/videos
        
        # For now, this is a placeholder that returns dummy data
        print(f"[ExampleVideoGenerator] Generating video ({mode})")
        if prompt:
            print(f"  Prompt: {prompt}")
        if images:
            print(f"  Input images: {len(images)}")
        if videos:
            print(f"  Input videos: {len(videos)}")
        print(f"  Duration: {duration}s, FPS: {fps}, Size: {width}x{height}")
        print(f"  Style: {style}")
        if seed:
            print(f"  Seed: {seed}")
        
        # Placeholder: Return dummy video path
        # In real implementation, this would be the actual generated video
        output_dir = Path("./generated_videos")
        output_dir.mkdir(exist_ok=True)
        video_path = output_dir / "generated_video.mp4"
        
        # Create a dummy video file (or save actual generated video)
        self._create_dummy_video(video_path, duration, fps, width, height)
        
        # Read video as base64 (optional)
        video_base64 = self._video_to_base64(video_path)
        
        return {
            "video": video_base64,
            "video_path": str(video_path),
            "metadata": {
                "mode": mode,
                "prompt": prompt,
                "duration": duration,
                "fps": fps,
                "width": width,
                "height": height,
                "style": style,
                "seed": seed,
                "num_input_images": len(images),
                "num_input_videos": len(videos),
            }
        }
    
    def _create_dummy_video(self, output_path: Path, duration: int, fps: int, width: int, height: int):
        """
        Create a dummy video file for demonstration
        
        In real implementation, this would call your actual generation API/model.
        """
        try:
            import cv2
            import numpy as np
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            num_frames = duration * fps
            for i in range(num_frames):
                # Create a simple frame with gradient
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:, :, 0] = int(255 * (i / num_frames))  # Blue gradient
                frame[:, :, 1] = int(255 * ((num_frames - i) / num_frames))  # Green gradient
                
                # Add text
                cv2.putText(frame, f"Frame {i+1}/{num_frames}", 
                           (width//4, height//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                out.write(frame)
            
            out.release()
        except ImportError:
            # Fallback: create empty file
            output_path.touch()
            print("Warning: OpenCV not available, created empty video file")
    
    def _video_to_base64(self, video_path: Path) -> str:
        """Convert video file to base64 string"""
        try:
            with open(video_path, 'rb') as f:
                video_data = f.read()
            base64_str = base64.b64encode(video_data).decode('utf-8')
            return f"data:video/mp4;base64,{base64_str}"
        except Exception as e:
            print(f"Warning: Failed to encode video: {e}")
            return ""
