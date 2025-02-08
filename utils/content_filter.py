from transformers import pipeline
from PIL import Image
import requests
from io import BytesIO

# Load the text classification model
content_filter = pipeline("text-classification",  model="allenai/longformer-base-4096")

# Load the image classification model
image_filter = pipeline("image-classification", model="Falconsai/nsfw_image_detection")

def check_text_content(text):
    """
    Check if the text contains inappropriate content.
    Returns True if the text is safe, False otherwise.
    """
    # Truncate the text to the first 512 tokens
    truncated_text = " ".join(text.split()[:512])  # Simple truncation
    results = content_filter(truncated_text)
    for result in results:
        if result['label'] in ['toxic', 'obscene', 'threat', 'insult', 'identity_hate'] and result['score'] > 0.8:
            return False  # Content is inappropriate
    return True  # Content is safe

def check_image_content(image_url):
    """
    Check if an image contains inappropriate content.
    Returns True if the image is safe, False otherwise.
    """
    try:
        # Download the image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        # Classify the image
        results = image_filter(image)
        for result in results:
            if result['label'] == 'nsfw' and result['score'] > 0.8:
                return False  # Image is inappropriate
        return True  # Image is safe
    except Exception as e:
        print(f"Error checking image: {e}")
        return True  # Assume safe if there's an error