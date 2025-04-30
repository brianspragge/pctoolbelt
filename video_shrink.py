import os
import ffmpeg
import subprocess
import math

# Global variable for desired file size in megabytes
DESIRED_MB = 10.0  # Target size in MB (e.g., 10.0 = 10 MB)

# Supported video formats and their extensions
SUPPORTED_FORMATS = {
    "MP4": "mp4",
    "AVI": "avi",
    "MOV": "mov",
    "MKV": "mkv",
    "WEBM": "webm",
    "FLV": "flv",
    "WMV": "wmv",
    "MPEG": "mpeg"
}

def get_file_size_mb(file_path):
    """Return file size in megabytes."""
    try:
        return os.path.getsize(file_path) / 1_000_000
    except OSError:
        return 0

def get_video_duration(input_path):
    """Get video duration in seconds using ffmpeg."""
    try:
        probe = ffmpeg.probe(input_path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        print(f"Error probing video duration: {e.stderr.decode()}")
        return None
    except KeyError:
        print("Error: Could not retrieve video duration.")
        return None

def resize_video_to_target_size(input_path, output_dir=".", desired_mb=DESIRED_MB):
    """
    Downsize video to approximate desired file size, preserving input format.
    Uses binary search to adjust bitrate.
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' not found.")
            return None

        # Probe input video to get format
        probe = ffmpeg.probe(input_path)
        input_format = probe['format']['format_name'].split(',')[0].upper()
        if input_format not in SUPPORTED_FORMATS:
            # Map common format names to supported ones
            format_map = {
                "QUICKTIME": "MOV",
                "MATROSKA": "MKV",
                "MPEGTS": "MPEG"
            }
            input_format = format_map.get(input_format, input_format)
            if input_format not in SUPPORTED_FORMATS:
                print(f"Error: Unsupported input format '{input_format}'. Supported: {list(SUPPORTED_FORMATS.keys())}")
                return None

        output_ext = SUPPORTED_FORMATS[input_format]
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"output_video.{output_ext}")
        temp_path = os.path.join(output_dir, f"temp_output.{output_ext}")

        # Get video duration
        duration = get_video_duration(input_path)
        if duration is None:
            return None

        # Calculate target bitrate (kbps)
        target_bytes = desired_mb * 1_000_000
        target_bitrate_kbps = (target_bytes * 8) / (duration * 1000)  # kbps
        min_bitrate = 100  # Minimum bitrate (kbps)
        max_bitrate = target_bitrate_kbps * 2  # Upper bound for binary search

        # Binary search for bitrate
        tolerance = 0.05  # Allow ±5% of target size
        max_iterations = 10
        for _ in range(max_iterations):
            bitrate = (min_bitrate + max_bitrate) / 2
            if bitrate < 100:  # Prevent unreasonably low bitrate
                min_bitrate = bitrate
                continue

            # Encode video with specified bitrate
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                temp_path,
                **{
                    "c:v": "libx264" if output_ext in ["mp4", "mov", "mkv", "avi"] else "vp9" if output_ext == "webm" else "mpeg4",
                    "b:v": f"{int(bitrate)}k",
                    "c:a": "aac" if output_ext in ["mp4", "mov", "mkv", "webm"] else "mp3",
                    "b:a": "128k",  # Fixed audio bitrate
                    "preset": "medium",
                    "y": None  # Overwrite output
                }
            )

            try:
                ffmpeg.run(stream, quiet=True)
            except ffmpeg.Error as e:
                print(f"Error during encoding: {e.stderr.decode()}")
                return None

            # Check file size
            current_mb = get_file_size_mb(temp_path)
            if abs(current_mb - desired_mb) < tolerance * desired_mb:
                break
            elif current_mb > desired_mb:
                max_bitrate = bitrate
            else:
                min_bitrate = bitrate

        # Final save
        os.rename(temp_path, output_path)
        print(f"Successfully created {output_path} (~{current_mb:.2f} MB)")
        return output_path

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return None
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"Error during video resizing: {e}")
        return None

if __name__ == "__main__":
    input_file = None
    # Look for input_video with any extension
    for ext in SUPPORTED_FORMATS.values():
        candidate = f"input_video.{ext}"
        if os.path.exists(candidate):
            input_file = candidate
            break

    if input_file:
        print(f"Found input file: {input_file}")
        result = resize_video_to_target_size(input_file)
        if result:
            print(f"Conversion complete: {result}")
        else:
            print("Conversion failed.")
    else:
        print(f"Error: No input_video.<type> found (tried {', '.join(SUPPORTED_FORMATS.values())}).")
