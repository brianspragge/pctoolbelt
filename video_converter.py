import ffmpeg
import os

def convert_video(input_path, output_format):
    # Ensure the input file exists
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return
    
    # Define the output path by changing the file extension
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}.{output_format}"
    
    try:
        # Run the FFmpeg conversion
        ffmpeg.input(input_path).output(output_path).run()
        print(f"Conversion successful! Saved as {output_path}")
    except ffmpeg.Error as e:
        print("Error during conversion:", e)

if __name__ == '__main__':
    # Set the input file path and desired output format
    input_file = "video.avi"  # Replace with your .avi file path
    output_format = "mp4"  # Set to "mp4" or "mov"

    # Validate output format
    if output_format not in ('mp4', 'mov'):
        print("Invalid format. Please choose 'mp4' or 'mov'.")
    else:
        convert_video(input_file, output_format)
