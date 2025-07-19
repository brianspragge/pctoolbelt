import os
from PIL import Image

def autocrop_image(image_path, output_path):
    with Image.open(image_path) as img:
        # Ensure image has alpha (transparency) channel
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Get alpha channel or white pixels
        bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
        diff = Image.alpha_composite(bg, img).getbbox()

        if diff:
            cropped = img.crop(diff)
            cropped.save(output_path)
        else:
            print(f"Skipping {image_path} - no content found")

if __name__ == "__main__":
    input_folder = "/home/monk/test/"
    output_folder = "/home/monk/cropped/"
    os.makedirs(output_folder, exist_ok=True)

    for image in os.listdir(input_folder):
        if image.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, image)
            output_path = os.path.join(output_folder, image)
            print(f"Cropping {image}...")
            autocrop_image(input_path, output_path)

    print("Done.")

