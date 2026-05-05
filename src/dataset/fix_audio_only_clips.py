#!/usr/bin/env python3
"""
Fix clips that only have audio by re-extracting with proper video encoding.

Usage:
    python fix_audio_only_clips.py active_clips_with_audio/ fixed_clips/ source_video.mp4
"""

import os
import sys
import json
import subprocess

def fix_clips(input_dir, output_dir, source_video):
    """Re-extract clips from source video with proper video+audio encoding."""
    
    # Load metadata
    metadata_file = os.path.join(input_dir, 'activity_metadata.json')
    if not os.path.exists(metadata_file):
        print(f"Error: {metadata_file} not found")
        return
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Re-extracting {len(metadata['clips'])} clips with proper video encoding...")
    print(f"Source: {source_video}")
    print(f"Output: {output_dir}\n")
    
    for i, clip_info in enumerate(metadata['clips']):
        start = clip_info['start']
        duration = clip_info['duration']
        
        clip_name = os.path.basename(clip_info['path'])
        output_path = os.path.join(output_dir, clip_name)
        
        print(f"[{i+1}/{len(metadata['clips'])}] {clip_name} ({duration:.1f}s)", end="")
        
        try:
            subprocess.run([
                'ffmpeg', '-y', '-loglevel', 'error',
                '-i', source_video,
                '-ss', str(start),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ], check=True, timeout=60)
            print(" ✓")
        except Exception as e:
            print(f" ✗ Error: {e}")
    
    # Copy metadata
    output_metadata = os.path.join(output_dir, 'activity_metadata.json')
    # Update paths in metadata
    fixed_metadata = metadata.copy()
    for clip in fixed_metadata['clips']:
        clip['path'] = os.path.join(output_dir, os.path.basename(clip['path']))
    
    with open(output_metadata, 'w') as f:
        json.dump(fixed_metadata, f, indent=2)
    
    print(f"\n✓ Done! Fixed clips saved to: {output_dir}")
    print(f"Metadata: {output_metadata}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("""
Usage:
    python fix_audio_only_clips.py <input_dir> <output_dir> <source_video>

Example:
    python fix_audio_only_clips.py \\
        active_clips_with_audio/ \\
        active_clips_fixed/ \\
        output_signer_dataset/full_cropped/output_short_sli_cropped.mp4
""")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    source_video = sys.argv[3]
    
    fix_clips(input_dir, output_dir, source_video)
