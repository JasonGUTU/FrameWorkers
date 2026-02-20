"""
Basic Usage Examples for Inference Module

This file demonstrates basic usage of the Inference module.
"""

from Inference import LLMClient, MessageHistory, ImageUtils, TemplateManager


def example_basic_call():
    """Basic model call example"""
    print("=== Example 1: Basic Model Call ===")
    
    # Initialize client
    client = LLMClient(default_model="gpt-3.5-turbo")
    
    # Make a call
    response = client.call(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ]
    )
    
    print("Response:", response["choices"][0]["message"]["content"])
    print()


def example_with_history():
    """Example with message history"""
    print("=== Example 2: Using Message History ===")
    
    client = LLMClient(default_model="gpt-3.5-turbo")
    history = MessageHistory(storage_path="./example_history.json")
    
    # Add system message
    history.add_message(role="system", content="You are a helpful assistant.")
    
    # User message
    history.add_message(role="user", content="My name is Alice.")
    
    # Get response
    response = client.call(messages=history.get_formatted_messages())
    assistant_reply = response["choices"][0]["message"]["content"]
    
    # Save assistant reply
    history.add_message(role="assistant", content=assistant_reply)
    
    print("Assistant:", assistant_reply)
    print("History stats:", history.get_statistics())
    print()


def example_with_templates():
    """Example with prompt templates"""
    print("=== Example 3: Using Prompt Templates ===")
    
    client = LLMClient(default_model="gpt-3.5-turbo")
    manager = TemplateManager(storage_path="./example_templates")
    
    # Create a template
    manager.create_template(
        name="greeting",
        template="Hello, {name}! Welcome to {place}.",
        description="Simple greeting template"
    )
    
    # Format and use template
    prompt = manager.format_template("greeting", name="Bob", place="Python World")
    print("Formatted prompt:", prompt)
    
    # Use in API call
    response = client.call(
        messages=[{"role": "user", "content": prompt}]
    )
    print("Response:", response["choices"][0]["message"]["content"])
    print()


def example_image_encoding():
    """Example of image encoding (requires an image file)"""
    print("=== Example 4: Image Encoding ===")
    
    try:
        # This example requires an actual image file
        # Replace "example_image.png" with your image path
        image_path = "example_image.png"
        
        # Encode image to base64
        base64_str = ImageUtils.encode_image_to_base64(image_path)
        print(f"Image encoded (first 50 chars): {base64_str[:50]}...")
        
        # Get image info
        info = ImageUtils.get_image_info(image_path)
        print("Image info:", info)
        
    except FileNotFoundError:
        print("Image file not found. Please provide a valid image path.")
    print()


def example_model_info():
    """Example of querying model information"""
    print("=== Example 5: Model Information ===")
    
    from Inference import ModelRegistry
    
    registry = ModelRegistry()
    
    # List all models
    print("All models:", registry.list_models()[:5], "...")  # Show first 5
    
    # List by provider
    print("OpenAI models:", registry.list_models(provider="openai"))
    
    # Get model info
    model_info = registry.get_model("gpt-4o")
    if model_info:
        print(f"GPT-4o info:")
        print(f"  Name: {model_info.name}")
        print(f"  Multimodal: {model_info.supports_multimodal}")
        print(f"  Max tokens: {model_info.max_tokens}")
    print()


if __name__ == "__main__":
    print("Inference Module - Basic Usage Examples\n")
    
    # Run examples
    example_basic_call()
    example_with_history()
    example_with_templates()
    example_image_encoding()
    example_model_info()
    
    print("Examples completed!")
