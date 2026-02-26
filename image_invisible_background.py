import os
from PIL import Image
from rembg import remove

def remove_background(image_path):
    try:
        with Image.open(image_path) as input_image:
            output = remove(input_image)
            base, _ = os.path.splitext(image_path)
            output_path = base + '.png'
            output.save(output_path)
            print(f"Saved {output_path}")

    except Exception as e:
        print(f"Error on {image_path}: {e}")
        return 1;

if __name__ == "__main__":
    folder = "/home/monk/Repos/pctoolbelt/"
    count = 0

    for image in os.listdir(folder):
        if image.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(folder, image)
            print(f"Processing {image}{count+1}...")
            if remove_background(path) == 1:
                break
            count += 1
    print(f"Done. Processed {count} images.")

