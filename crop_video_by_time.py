#!/usr/bin/env python3
"""
Simple script to crop a video with given start and end times.

Usage:
    python crop_video_by_time.py input_video.mp4 00:00:10 00:00:20 output_video.mp4
    python crop_video_by_time.py input_video.mp4 10 20 output_video.mp4
"""

import subprocess
import sys
import os
from pathlib import Path


def format_time(time_str):
    """
    Convert time string to ffmpeg format.
    Accepts: seconds (10), MM:SS (01:30), or HH:MM:SS (00:01:30)
    """
    try:
        # If it's just a number, treat it as seconds
        if time_str.replace('.', '').isdigit():
            seconds = float(time_str)
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        # Otherwise assume it's already in proper format
        return time_str
    except:
        return time_str


def crop_video(input_path, start_time, end_time, output_path):
    """
    Crop video from start_time to end_time using ffmpeg.
    
    Args:
        input_path: Path to input video file
        start_time: Start time (seconds or HH:MM:SS format)
        end_time: End time (seconds or HH:MM:SS format)
        output_path: Path to output video file
    """
    # Validate input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist!")
        return False
    
    # Format times
    start = format_time(start_time)
    end = format_time(end_time)
    
    # Calculate duration
    # Convert to seconds for duration calculation
    def time_to_seconds(time_str):
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS.mmm
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:  # MM:SS
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(time_str)
    
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    duration = end_seconds - start_seconds
    
    if duration <= 0:
        print("Error: End time must be greater than start time!")
        return False
    
    print(f"Cropping video:")
    print(f"  Input: {input_path}")
    print(f"  Start: {start}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Output: {output_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # FFmpeg command to crop video
    # -ss: start time
    # -t: duration
    # -i: input file
    # -c copy: copy codec (fast, no re-encoding)
    # For more accurate cuts, use: -c:v libx264 -c:a aac
    command = [
        'ffmpeg',
        '-ss', start,
        '-i', input_path,
        '-t', str(duration),
        '-c', 'copy',  # Use 'copy' for fast processing without re-encoding
        '-y',  # Overwrite output file if exists
        output_path
    ]
    
    try:
        # Run ffmpeg command
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Video cropped successfully: {output_path}")
            return True
        else:
            print(f"Error cropping video:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in PATH!")
        print("Please install ffmpeg first:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  MacOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print(f"  {sys.argv[0]} <input_video> <start_time> <end_time> [output_video]")
        print("\nExamples:")
        print(f"  {sys.argv[0]} input.mp4 10 20 output.mp4")
        print(f"  {sys.argv[0]} input.mp4 00:00:10 00:00:20 output.mp4")
        print(f"  {sys.argv[0]} input.mp4 1:30 2:45 output.mp4")
        print(f"  {sys.argv[0]} input.mp4 0:01:30 0:02:45")
        print("\nTime format: seconds (10) or MM:SS (01:30) or HH:MM:SS (00:01:30)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]
    
    # Generate output filename if not provided
    if len(sys.argv) >= 5:
        output_path = sys.argv[4]
    else:
        # Create output filename based on input
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_cropped{input_file.suffix}")
    
    success = crop_video(input_path, start_time, end_time, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
