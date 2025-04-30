from PIL import Image
import os

def slice_image_grid(input_image_path, slices_x, slices_y):
    # Output directory name
    output_dir = "sliced_image"

    # Open the image
    with Image.open(input_image_path) as img:
        width, height = img.size

        slices_x += 1
        slices_y += 1

        # Calculate dimensions for each slice
        slice_width = width // slices_x
        slice_height = height // slices_y

        # Ensure output folder exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Counter for naming slices
        count = 0

        # Loop through all possible slices in a grid pattern
        for i in range(slices_y):
            for j in range(slices_x):
                # Define the area to crop
                left = j * slice_width
                top = i * slice_height
                right = left + slice_width if j != slices_x - 1 else width
                bottom = top + slice_height if i != slices_y - 1 else height

                # Crop the image
                cropped_img = img.crop((left, top, right, bottom))

                # Save the cropped image
                cropped_img.save(f"{output_dir}/slice_{count}.png")
                count += 1

if __name__ == "__main__":

    input_image = "image.png"
    slices_x = 2  # Number of slices horizontally
    slices_y = 2  # Number of slices vertically

    slice_image_grid(input_image, slices_x, slices_y)
