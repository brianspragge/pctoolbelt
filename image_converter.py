from PIL import Image
import os
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()  # Enable HEIC input/output support
except ImportError:
    print("Warning: pillow_heif not installed. HEIC support disabled. Install with: pip install pillow_heif")

# Global variable to specify output format
TYPE = "PNG"  # Options: HEIC, ICO, PNG, JPEG, BMP, GIF, TIFF, WEBP, etc.

# Supported output formats and their extensions
SUPPORTED_FORMATS = {
    "HEIC": "heic",
    "ICO": "ico",
    "PNG": "png",
    "JPEG": "jpg",
    "BMP": "bmp",
    "GIF": "gif",
    "TIFF": "tiff",
    "WEBP": "webp"
}

def convert_image(input_path, output_format, output_dir=".", ico_sizes=[(16, 16), (32, 32), (64, 64), (256, 256)]):
    """
    Convert an input image to the specified output format.
    """
    output_format = output_format.upper()
    if output_format not in SUPPORTED_FORMATS:
        print(f"Error: Unsupported output format '{output_format}'. Choose from {list(SUPPORTED_FORMATS.keys())}")
        return None
    
    output_ext = SUPPORTED_FORMATS[output_format]
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"output_image.{output_ext}")
    
    try:
        # Open and validate input image
        with Image.open(input_path) as img:
            input_format = img.format
            print(f"Detected input format: {input_format}")
            
            # Convert to appropriate mode if needed
            if output_format in ["JPEG", "BMP"] and img.mode not in ["RGB", "L"]:
                img = img.convert("RGB")
            elif output_format == "ICO" and img.mode != "RGBA":
                img = img.convert("RGBA")  # ICO prefers RGBA
            elif output_format == "HEIC" and img.mode not in ["RGB", "RGBA"]:
                img = img.convert("RGB")  # HEIC typically uses RGB
            
            # Handle ICO specifically
            if output_format == "ICO":
                images = []
                for size in ico_sizes:
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    images.append(resized_img)
                images[0].save(
                    output_path,
                    format="ICO",
                    bitmap_format="bmp",  # Reliable for ICO
                    sizes=ico_sizes
                )
            else:
                # Save other formats, including HEIC
                img.save(output_path, format=output_format)
            
            print(f"Successfully created {output_path}")
            return output_path
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return None
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None

if __name__ == "__main__":
    input_file = None
    # Look for input_image with any extension, including HEIC
    for ext in ["png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp", "heic", "HEIC"]:
        candidate = f"input_image.{ext}"
        if os.path.exists(candidate):
            input_file = candidate
            break
    
    if input_file:
        print(f"Found input file: {input_file}")
        result = convert_image(input_file, TYPE)
        if result:
            print(f"Conversion complete: {result}")
        else:
            print("Conversion failed.")
    else:
        print("Error: No input_image.<type> found (tried png, jpg, jpeg, bmp, gif, tiff, webp, heic).")
