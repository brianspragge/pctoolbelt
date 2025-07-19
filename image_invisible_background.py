import os
from PIL import Image
from rembg import remove

def remove_background(image_path):
    with Image.open(image_path) as input_image:
        output = remove(input_image)
        output.save(image_path)  # overwrite original

if __name__ == "__main__":
    folder = "/home/monk/frames/"
    for image in os.listdir(folder):
        if image.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(folder, image)
            print(f"Processing {image}...")
            remove_background(path)
    print("Done.")

