"""
Generation Example - Demonstrates how to use image and video generators

This example shows how to:
1. Use registered generators
2. Create custom generators
3. Handle different input types
"""

from Inference import (
    ImageGeneratorRegistry,
    VideoGeneratorRegistry,
    get_image_generator_registry,
    get_video_generator_registry
)


def example_list_generators():
    """List all available generators"""
    print("=== Example 1: List Available Generators ===\n")
    
    # Get registries
    image_registry = get_image_generator_registry()
    video_registry = get_video_generator_registry()
    
    # List image generators
    print("Image Generators:")
    image_generators = image_registry.list_generators()
    if image_generators:
        for gen_id in image_generators:
            gen = image_registry.get_generator(gen_id)
            print(f"  - {gen_id}: {gen.metadata.name}")
            print(f"    Description: {gen.metadata.description}")
            print(f"    Capabilities: {', '.join(gen.metadata.capabilities)}")
    else:
        print("  No image generators found")
    
    print()
    
    # List video generators
    print("Video Generators:")
    video_generators = video_registry.list_generators()
    if video_generators:
        for gen_id in video_generators:
            gen = video_registry.get_generator(gen_id)
            print(f"  - {gen_id}: {gen.metadata.name}")
            print(f"    Description: {gen.metadata.description}")
            print(f"    Capabilities: {', '.join(gen.metadata.capabilities)}")
    else:
        print("  No video generators found")
    
    print()


def example_image_generation():
    """Example of image generation"""
    print("=== Example 2: Image Generation ===\n")
    
    registry = get_image_generator_registry()
    
    # List available generators
    generators = registry.list_generators()
    if not generators:
        print("No image generators available. Make sure example_generator is in image_generators/")
        return
    
    generator_id = generators[0]
    print(f"Using generator: {generator_id}\n")
    
    # Generate image with text prompt only
    print("Generating image from text prompt...")
    try:
        result = registry.generate(
            generator_id=generator_id,
            prompt="A beautiful sunset over the ocean",
            width=1024,
            height=1024,
            style="realistic"
        )
        print(f"Generated {len(result.get('images', []))} image(s)")
        print(f"Saved to: {result.get('image_paths', [])}")
        print(f"Metadata: {result.get('metadata', {})}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Generate image with input images (image-to-image)
    print("Generating image from input images...")
    try:
        result = registry.generate(
            generator_id=generator_id,
            prompt="Transform this image into a painting",
            images=["path/to/input_image.jpg"],  # Replace with actual image path
            width=1024,
            height=1024,
            style="artistic"
        )
        print(f"Generated {len(result.get('images', []))} image(s)")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_video_generation():
    """Example of video generation"""
    print("=== Example 3: Video Generation ===\n")
    
    registry = get_video_generator_registry()
    
    # List available generators
    generators = registry.list_generators()
    if not generators:
        print("No video generators available. Make sure example_generator is in video_generators/")
        return
    
    generator_id = generators[0]
    print(f"Using generator: {generator_id}\n")
    
    # Generate video from text prompt
    print("Generating video from text prompt...")
    try:
        result = registry.generate(
            generator_id=generator_id,
            prompt="A cat walking on the beach",
            duration=5,
            fps=24,
            width=1280,
            height=720
        )
        print(f"Generated video saved to: {result.get('video_path')}")
        print(f"Metadata: {result.get('metadata', {})}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Generate video from images (image-to-video)
    print("Generating video from images...")
    try:
        result = registry.generate(
            generator_id=generator_id,
            prompt="Animate this image",
            images=["path/to/input_image.jpg"],  # Replace with actual image path
            duration=3,
            fps=24
        )
        print(f"Generated video saved to: {result.get('video_path')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Generate video from video (video-to-video)
    print("Generating video from input video...")
    try:
        result = registry.generate(
            generator_id=generator_id,
            prompt="Apply artistic style",
            videos=["path/to/input_video.mp4"],  # Replace with actual video path
            duration=5,
            style="artistic"
        )
        print(f"Generated video saved to: {result.get('video_path')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_get_generator_info():
    """Example of getting generator information"""
    print("=== Example 4: Generator Information ===\n")
    
    registry = get_image_generator_registry()
    generators = registry.list_generators()
    
    if generators:
        generator_id = generators[0]
        generator = registry.get_generator(generator_id)
        
        print(f"Generator: {generator.metadata.name}")
        print(f"ID: {generator.metadata.id}")
        print(f"Description: {generator.metadata.description}")
        print(f"Version: {generator.metadata.version}")
        print(f"Capabilities: {', '.join(generator.metadata.capabilities)}")
        print()
        
        print("Input Schema:")
        input_schema = generator.get_input_schema()
        for param_name, param_spec in input_schema.items():
            param_type = param_spec.get("type", "unknown")
            required = param_spec.get("required", False)
            default = param_spec.get("default", "N/A")
            description = param_spec.get("description", "")
            print(f"  - {param_name} ({param_type})")
            print(f"    Required: {required}, Default: {default}")
            print(f"    Description: {description}")
        
        print()
        
        print("Output Schema:")
        output_schema = generator.get_output_schema()
        for field_name, field_spec in output_schema.items():
            field_type = field_spec.get("type", "unknown")
            description = field_spec.get("description", "")
            print(f"  - {field_name} ({field_type})")
            print(f"    Description: {description}")
    
    print()


def example_custom_parameters():
    """Example of using custom parameters"""
    print("=== Example 5: Custom Parameters ===\n")
    
    registry = get_image_generator_registry()
    generators = registry.list_generators()
    
    if generators:
        generator_id = generators[0]
        
        # All parameters defined in input_schema are automatically accepted
        print("Using custom parameters from input_schema...")
        try:
            result = registry.generate(
                generator_id=generator_id,
                prompt="A futuristic city",
                width=2048,  # Custom width
                height=1024,  # Custom height
                num_images=2,  # Generate multiple images
                style="futuristic",  # Custom style
                seed=42  # Custom seed for reproducibility
            )
            print(f"Successfully generated with custom parameters")
            print(f"Result: {result.get('metadata', {})}")
        except Exception as e:
            print(f"Error: {e}")
    
    print()


if __name__ == "__main__":
    print("Inference Module - Generation Examples\n")
    print("=" * 50)
    print()
    
    # Run examples
    example_list_generators()
    example_get_generator_info()
    example_image_generation()
    example_video_generation()
    example_custom_parameters()
    
    print("=" * 50)
    print("\nExamples completed!")
    print("\nTo create your own generator:")
    print("1. Copy example_generator/ to a new directory")
    print("2. Modify generator.py to implement your generation logic")
    print("3. Update metadata and input/output schemas")
    print("4. The generator will be automatically discovered and registered")
