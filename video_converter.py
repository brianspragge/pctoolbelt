import ffmpeg
import os
import argparse
import subprocess
import re
from tqdm import tqdm

# Supported video formats and their extensions
SUPPORTED_FORMATS = {
    "MP4": "mp4",
    "MOV": "mov",
    "AVI": "avi",
    "MKV": "mkv",
    "WEBM": "webm",
    "FLV": "flv",
    "WMV": "wmv",
    "MPEG": "mpeg"
}

def get_video_file():
    """Find the first video file in the current directory."""
    for ext in SUPPORTED_FORMATS.values():
        candidate = f"input_video.{ext}"
        if os.path.exists(candidate):
            return candidate
    return None

def get_input_format(input_path):
    """Identify the input video format using ffmpeg.probe."""
    try:
        probe = ffmpeg.probe(input_path)
        input_format = probe['format']['format_name'].split(',')[0].upper()
        # Map common format names to supported ones
        format_map = {
            "QUICKTIME": "MOV",
            "MATROSKA": "MKV",
            "MPEGTS": "MPEG"
        }
        return format_map.get(input_format, input_format)
    except ffmpeg.Error as e:
        print(f"Error probing input format: {e.stderr.decode()}")
        return None

def convert_video(input_path, output_format):
    """Convert video to the specified output format."""
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return False

    # Validate output format
    output_format = output_format.lower()
    if output_format not in SUPPORTED_FORMATS.values():
        print(f"Invalid output format '{output_format}'. Supported: {', '.join(SUPPORTED_FORMATS.values())}")
        return False

    # Get input format
    input_format = get_input_format(input_path)
    if not input_format or input_format not in SUPPORTED_FORMATS:
        print(f"Unsupported input format '{input_format}'. Supported: {list(SUPPORTED_FORMATS.keys())}")
        return False

    # Define output path
    base, _ = os.path.splitext(input_path)
    output_path = f"output_video.{output_format}"

    try:
        # Select appropriate codecs
        codec_v = "libx264" if output_format in ["mp4", "mov", "mkv", "avi"] else "vp9" if output_format == "webm" else "mpeg4"
        codec_a = "aac" if output_format in ["mp4", "mov", "mkv", "webm"] else "mp3"

        # Run FFmpeg conversion with progress
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", codec_v, "-c:a", codec_a,
            "-preset", "fast",  # Balance speed and quality
            "-progress", "pipe:2", "-loglevel", "info",
            output_path
        ]

        # Get video duration for progress bar
        probe = ffmpeg.probe(input_path)
        duration = float(probe['format']['duration'])

        # Start FFmpeg subprocess
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8'
        )

        # Progress bar
        from tqdm import tqdm
        time_regex = re.compile(r"out_time_ms=(\d+)")
        with tqdm(total=duration, desc="Converting", unit="s", dynamic_ncols=True) as pbar:
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                match = time_regex.search(line)
                if match:
                    current_time = int(match.group(1)) / 1_000_000
                    pbar.n = min(current_time, duration)
                    pbar.refresh()

        if process.returncode != 0:
            print(f"Error: FFmpeg exited with code {process.returncode}")
            return False

        print(f"Conversion successful! Saved as {output_path}")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert a video to a specified format.")
    parser.add_argument("--format", default="mp4", help="Output format (e.g., mp4, mov)")
    args = parser.parse_args()

    # Find input video
    input_file = get_video_file()
    if input_file:
        print(f"Found input file: {input_file}")
        if convert_video(input_file, args.format):
            print("Conversion complete.")
        else:
            print("Conversion failed.")
    else:
        print(f"Error: No input_video.<type> found (tried {', '.join(SUPPORTED_FORMATS.values())}).")
