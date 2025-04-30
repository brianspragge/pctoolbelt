import os
import ffmpeg
import subprocess
import re
import math
import argparse
from tqdm import tqdm

DEFAULT_SIZE_MB = 10.0
TIMEOUT_SECONDS = 120
FORMATS = {"MP4": "mp4", "MOV": "mov", "MKV": "mkv"}
RESOLUTIONS = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}

def parse_size(size_str):
    size_str = size_str.upper()
    match = re.match(r'^(\d*\.?\d+)(MB|GB)$', size_str)
    if not match:
        raise ValueError("Invalid size: use '10MB' or '1GB'")
    value, unit = float(match.group(1)), match.group(2)
    return value if unit == "MB" else value * 1000

def get_file_size_mb(file_path):
    try:
        return os.path.getsize(file_path) / 1_000_000
    except OSError:
        return 0

def probe_video(file_path):
    print(f"Probing: {file_path}")
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        return duration, int(video['width']), int(video['height'])
    except Exception as e:
        print(f"Probe error: {e}")
        return None, 0, 0

def get_scale_filter(width, height, target_width, target_height):
    if target_width >= width and target_height >= height:
        return None
    aspect = width / height
    new_width = min(target_width, width)
    new_height = int(new_width / aspect)
    if new_height > target_height:
        new_height = target_height
        new_width = int(new_height * aspect)
    new_width -= new_width % 2
    new_height -= new_height % 2
    return f"scale={new_width}:{new_height}"

def encode_video(input_path, output_path, bitrate, duration, output_ext, scale_filter=None):
    print(f"Encoding: {input_path} -> {output_path} at {bitrate:.0f} kbps")
    ffmpeg_path = "/usr/bin/ffmpeg"
    try:
        cmd = [
            ffmpeg_path, "-y", "-i", input_path,
            "-c:v", "libx264", "-b:v", f"{int(bitrate)}k",
            "-c:a", "aac", "-b:a", "128k",
            "-preset", "veryfast", "-threads", "4",
            "-progress", "pipe:2", "-loglevel", "info",
            output_path
        ]
        if scale_filter:
            cmd.extend(["-vf", scale_filter])

        with open("ffmpeg_log.txt", "a") as log:
            log.write(f"Command: {' '.join(cmd)}\n")
            print(f"Command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ
            )

            time_regex = re.compile(r"out_time_ms=(\d+)")
            progress_bar = tqdm(total=duration, desc="Encoding", unit="s")
            stderr_lines = []
            try:
                while True:
                    line = process.stderr.readline()
                    if not line and process.poll() is not None:
                        break
                    stderr_lines.append(line)
                    log.write(line)
                    match = time_regex.search(line)
                    if match:
                        current_time = int(match.group(1)) / 1_000_000
                        progress_bar.n = min(current_time, duration)
                        progress_bar.refresh()
            finally:
                progress_bar.close()
                stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
                log.write(f"Stdout: {stdout}\nStderr: {stderr}\n")

            if process.returncode != 0:
                print(f"FFmpeg error (code {process.returncode}): {''.join(stderr_lines[-10:])}")
                return False

        if not os.path.exists(output_path):
            print(f"Error: Output '{output_path}' not created")
            return False
        return True
    except Exception as e:
        print(f"Encode error: {e}")
        with open("ffmpeg_log.txt", "a") as log:
            log.write(f"Error: {e}\n")
        return False

def resize_video(input_path, size_mb, resolution=None, bitrate=None, format="mp4"):
    input_path = os.path.abspath(input_path)
    size = get_file_size_mb(input_path)
    print(f"Input size: {size:.2f} MB")
    if size == 0:
        print("Error: Invalid input file")
        return None
    if size_mb >= size:
        print(f"Error: Target size ({size_mb} MB) too large")
        return None

    duration, width, height = probe_video(input_path)
    if duration is None:
        return None
    print(f"Input: {width}x{height}, {duration:.2f}s")

    probe = ffmpeg.probe(input_path)
    fmt = next((f for f in probe['format']['format_name'].split(',') if f == 'mp4'), 'mp4').upper()
    output_ext = FORMATS.get(fmt, format)

    output_dir = os.path.dirname(input_path)
    output_path = os.path.join(output_dir, f"output_video.{output_ext}")
    temp_path = os.path.join(output_dir, f"temp_output.{output_ext}")
    print(f"Output extension: {output_ext}")

    target_width, target_height = RESOLUTIONS[resolution] if resolution in RESOLUTIONS else (width, height)
    print(f"Resolution: {target_width}x{target_height}")
    scale_filter = get_scale_filter(width, height, target_width, target_height)

    if bitrate:
        success = encode_video(input_path, output_path, bitrate, duration, output_ext, scale_filter)
        if not success:
            return None
        final_size = get_file_size_mb(output_path)
        print(f"Created: {output_path} (~{final_size:.2f} MB)")
        return output_path

    target_bitrate = (size_mb * 8000) / duration
    min_bitrate, max_bitrate = 100, target_bitrate * 2
    tolerance, max_iter = 0.05, 5
    first_iter = True

    for i in range(max_iter):
        bitrate = (min_bitrate + max_bitrate) / 2 if first_iter else bitrate
        if bitrate < 100:
            min_bitrate = bitrate
            continue
        print(f"Bitrate: {bitrate:.0f} kbps (iter {i+1}/{max_iter})")
        success = encode_video(input_path, temp_path, bitrate, duration, output_ext, scale_filter)
        if not success:
            return None
        current_size = get_file_size_mb(temp_path)
        print(f"Size: {current_size:.2f} MB")
        if abs(current_size - size_mb) < tolerance * size_mb:
            break
        if first_iter:
            first_iter = False
            if current_size > 0:
                bitrate *= size_mb / current_size
                min_bitrate = max(100, bitrate * 0.8)
                max_bitrate = bitrate * 1.2
                print(f"New bitrate: {bitrate:.0f} kbps")
            else:
                max_bitrate = bitrate
        else:
            if current_size > size_mb:
                max_bitrate = bitrate
            else:
                min_bitrate = bitrate

    try:
        os.rename(temp_path, output_path)
        print(f"Created: {output_path} (~{current_size:.2f} MB)")
        return output_path
    except OSError as e:
        print(f"Rename error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--downscale", choices=RESOLUTIONS.keys())
    parser.add_argument("--bitrate", type=float)
    parser.add_argument("--size", default=f"{DEFAULT_SIZE_MB}MB")
    parser.add_argument("--format", default="mp4", choices=FORMATS.values())
    args = parser.parse_args()

    size_mb = parse_size(args.size)
    input_path = None
    for ext in FORMATS.values():
        path = os.path.abspath(f"input_video.{ext}")
        if os.path.isfile(path):
            input_path = path
            print(f"Found: {input_path}")
            break
    if not input_path:
        print("Error: No input_video found")
        return

    output = resize_video(input_path, size_mb, args.downscale, args.bitrate, args.format)
    print("Conversion " + ("complete: " + output if output else "failed"))

if __name__ == "__main__":
    main()
