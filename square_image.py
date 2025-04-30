from PIL import Image

def make_square(image_path, output_path):
    """
    Make an image square by automatically cropping the longer sides.
    
    :param image_path: Path to the input image file.
    :param output_path: Path where the squared image will be saved.
    """
    with Image.open(image_path) as img:
        width, height = img.size
        
        # Determine the size of the square
        size = min(width, height)
        
        # Calculate the left, upper, right, and lower pixels to crop
        if width > height:  # Crop the sides
            left = (width - size) // 2
            top = 0
            right = left + size
            bottom = height
        else:  # Crop the top and bottom
            left = 0
            top = (height - size) // 2
            right = width
            bottom = top + size
        
        # Crop the image
        cropped_img = img.crop((left, top, right, bottom))
        
        # Save the new square image
        cropped_img.save(output_path)

# Example usage
input_image = "image.png"  # replace with your image path
output_image = "image.png"  # replace with desired output path

make_square(input_image, output_image)
