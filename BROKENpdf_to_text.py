# BROKEN Fix generate_image_description
# image description too short

import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm
import numpy as np

# Example: Adding basic functionality to simulate symbolic descriptions.
def generate_symbolic_description(image):
    # Example heuristic-based description based on image color analysis or size
    # Here we're using a simple check on the image size to generate a symbolic description.
    width, height = image.size
    aspect_ratio = width / height

    if aspect_ratio > 1:
        return "{;_;} looks like a long face"  # Example for a wide image
    elif aspect_ratio < 1:
        return "{:O} looks like a surprised face"  # Example for a tall image
    else:
        return "{•_•} looks like a neutral face"  # Example for a square image

# 1. Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in tqdm(range(len(reader.pages)), desc="Extracting Text"):
            text += reader.pages[page_num].extract_text() or ''
        return text

# 2. Function to extract images from PDF using pdf2image
def extract_images_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    return images

# 3. Function to generate image descriptions using BLIP
def generate_image_description(image):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=20)  # Adjust max_new_tokens as needed
    description = processor.decode(out[0], skip_special_tokens=True)

    # Generate a more abstract symbolic description
    symbolic_description = generate_symbolic_description(image)

    return f"{description} (Symbolic: {symbolic_description})"  # Combine descriptions

# 4. Combine text and image descriptions into one final document
def convert_pdf_to_text_with_image_descriptions(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    images = extract_images_from_pdf(pdf_path)

    image_descriptions = []
    for idx, image in tqdm(enumerate(images), total=len(images), desc="Generating Image Descriptions"):
        description = generate_image_description(image)
        image_descriptions.append(f"[Image {idx}: {description}]")

    for idx, description in enumerate(image_descriptions):
        text = text.replace(f"[Image {idx}]", description)

    return text

# Example usage
if __name__ == "__main__":
    file_name = "go_games"
    pdf_path = f"{file_name}.pdf"
    final_text = convert_pdf_to_text_with_image_descriptions(pdf_path)

    with open(f"{file_name}.txt", "w") as output_file:
        output_file.write(final_text)

    print(f"PDF text with image descriptions has been saved to {file_name}.txt")
