from PIL import Image
import os
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()  # Enable HEIC support
except ImportError:
    print("Warning: pillow_heif not installed. HEIC support disabled. Install with: pip install pillow_heif")

# Global variable for desired file size in megabytes
DESIRED_MB = 1.0  # Target size in MB (e.g., 1.0 = 1 MB)

# Supported formats and their extensions
SUPPORTED_FORMATS = {
    "PNG": "png",
    "JPEG": "jpg",
    "BMP": "bmp",
    "GIF": "gif",
    "TIFF": "tiff",
    "WEBP": "webp",
    "HEIF": "heic"  # HEIC format
}

def get_file_size_mb(file_path):
    """Return file size in megabytes."""
    try:
        return os.path.getsize(file_path) / 1_000_000
    except OSError:
        return 0

def resize_to_target_size(input_path, output_dir=".", desired_mb=DESIRED_MB):
    """
    Resize input image to approximate desired file size, preserving input format.
    """
    try:
        # Open and validate input image
        with Image.open(input_path) as img:
            input_format = img.format
            if input_format not in SUPPORTED_FORMATS:
                print(f"Error: Unsupported input format '{input_format}'. Supported: {list(SUPPORTED_FORMATS.keys())}")
                return None
            
            output_ext = SUPPORTED_FORMATS[input_format]
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, f"output_image.{output_ext}")
            
            # Store original mode
            original_mode = img.mode
            
            # Initial dimensions
            orig_width, orig_height = img.size
            aspect_ratio = orig_width / orig_height
            orig_area = orig_width * orig_height
            
            # Estimate initial scale (rough guess based on compression)
            # Assume ~50% compression efficiency for starters
            target_bytes = desired_mb * 1_000_000
            est_scale = (target_bytes / (orig_area * 4 * 0.5)) ** 0.5  # Approx. bytes per pixel
            min_scale, max_scale = 0.1, 2.0  # Bounds for binary search
            
            # Binary search for scale
            tolerance = 0.05  # Allow ±5% of target size
            max_iterations = 10
            for _ in range(max_iterations):
                scale = (min_scale + max_scale) / 2
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                if new_width < 1 or new_height < 1:
                    min_scale = scale
                    continue
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save with appropriate settings
                save_kwargs = {}
                if input_format in ["JPEG", "WEBP"]:
                    save_kwargs["quality"] = 85  # Start with decent quality
                elif input_format == "HEIF":
                    save_kwargs["quality"] = 50  # HEIC default for balance
                
                # Convert mode if needed
                save_img = resized_img
                if input_format in ["JPEG", "HEIF"] and save_img.mode not in ["RGB", "L"]:
                    save_img = save_img.convert("RGB")
                elif input_format == "BMP" and save_img.mode not in ["RGB", "L"]:
                    save_img = save_img.convert("RGB")
                elif input_format in ["PNG", "WEBP"] and save_img.mode != original_mode:
                    save_img = save_img.convert(original_mode)
                
                # Save to temporary file to check size
                temp_path = os.path.join(output_dir, f"temp_output.{output_ext}")
                save_img.save(temp_path, format=input_format, **save_kwargs)
                
                # Check file size
                current_mb = get_file_size_mb(temp_path)
                
                # Adjust quality for compressible formats if close
                if input_format in ["JPEG", "WEBP", "HEIF"] and abs(current_mb - desired_mb) < tolerance * desired_mb:
                    quality = save_kwargs.get("quality", 85)
                    while current_mb > desired_mb and quality > 10:
                        quality -= 5
                        save_img.save(temp_path, format=input_format, quality=quality)
                        current_mb = get_file_size_mb(temp_path)
                    if abs(current_mb - desired_mb) < tolerance * desired_mb:
                        break
                
                # Binary search adjustment
                if abs(current_mb - desired_mb) < tolerance * desired_mb:
                    break
                elif current_mb > desired_mb:
                    max_scale = scale
                else:
                    min_scale = scale
            
            # Final save
            os.rename(temp_path, output_path)
            print(f"Successfully created {output_path} (~{current_mb:.2f} MB)")
            return output_path
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return None
    except Exception as e:
        print(f"Error during resizing: {e}")
        return None

if __name__ == "__main__":
    input_file = None
    # Look for input_image with any extension
    for ext in ["png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp", "heic"]:
        candidate = f"input_image.{ext}"
        if os.path.exists(candidate):
            input_file = candidate
            break
    
    if input_file:
        print(f"Found input file: {input_file}")
        result = resize_to_target_size(input_file)
        if result:
            print(f"Conversion complete: {result}")
        else:
            print("Conversion failed.")
    else:
        print("Error: No input_image.<type> found (tried png, jpg, jpeg, bmp, gif, tiff, webp, heic).")
