from PIL import Image
from rembg import remove

def remove_background(input_path, output_path):
    with Image.open(input_path) as input_image:
        output = remove(input_image)
        output.save(output_path)

if __name__ == "__main__":
    remove_background('input_image.png', 'output_image.png')
