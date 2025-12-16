import os
from huggingface_hub import InferenceClient
from PIL import Image
import uuid

def generate_image_tool(prompt: str) -> str:
    """
    Generates an image using black-forest-labs/FLUX.1-schnell via Hugging Face API.
    Returns the file path of the generated image.
    """
    api_token = os.getenv("HF_TOKEN")
    if not api_token:
        return "Error: HF_TOKEN not found in environment."

    IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"
    client = InferenceClient(token=api_token)

    try:
        # Ensure directory exists
        output_dir = os.path.join("src", "image-generator", "generated_images")
        os.makedirs(output_dir, exist_ok=True)
        
        image = client.text_to_image(prompt, model=IMAGE_MODEL)
        
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        
        return f"Image generated successfully at: {filepath}"
    except Exception as e:
        return f"Error generating image: {str(e)}"
