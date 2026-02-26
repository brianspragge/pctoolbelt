import os
from PIL import Image

def shrink_image(image_path, size=(32, 32)):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.LANCZOS)
        img.save(image_path)

if __name__ == "__main__":
    folder  = "/home/monk/Repos/pctoolbelt/"
    size    = (64, 117)  # define size here

    for image in os.listdir(folder):
        if image.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(folder, image)
            print(f"Shrinking {image} to {size[0]}x{size[1]}...")
            shrink_image(path, size)
    print("Done.")

