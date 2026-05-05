#!/usr/bin/env python3
"""
Extract audio from existing clips and create metadata
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def extract_audio_from_existing_clips(clips_dir, original_video, output_dir, fps=30.0, clip_duration=5.0):
    """
    Extract audio segments for existing clips and create metadata
    """
    print("="*70)
    print("Audio Extraction from Existing Clips")
    print("="*70)
    
    # Create output directories
    audio_dir = os.path.join(output_dir, "audio_clips")
    transcriptions_dir = os.path.join(output_dir, "transcriptions")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcriptions_dir, exist_ok=True)
    
    # Get sorted list of clips
    clip_files = sorted([f for f in os.listdir(clips_dir) if f.endswith('.mp4')])
    
    print(f"\nFound: {len(clip_files)} video clips")
    print(f"Original video: {original_video}")
    print(f"Output directory: {output_dir}")
    print(f"Clip duration: {clip_duration}s")
    print()
    
    metadata = {
        "dataset_info": {
            "original_video": original_video,
            "video_name": Path(original_video).stem,
            "created_date": datetime.now().isoformat(),
            "clip_duration": clip_duration,
            "fps": fps,
            "total_clips": len(clip_files)
        },
        "clips": []
    }
    
    successful = 0
    failed = 0
    
    for i, clip_file in enumerate(clip_files):
        # Calculate timestamp based on clip index (5 seconds per clip)
        start_time = i * clip_duration
        end_time = start_time + clip_duration
        
        clip_id = f"{i:04d}"
        audio_filename = clip_file.replace('.mp4', '.wav')
        text_filename = clip_file.replace('.mp4', '.txt')
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # Skip if audio already exists
        if os.path.exists(audio_path):
            audio_extracted = True
            successful += 1
        else:
            # Extract audio using ffmpeg
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-loglevel', 'error',
                    '-i', original_video,
                    '-ss', str(start_time),
                    '-t', str(clip_duration),
                    '-vn',  # No video
                    '-acodec', 'pcm_s16le',  # PCM 16-bit
                    '-ar', '16000',  # 16kHz (optimal for ASR)
                    '-ac', '1',  # Mono
                    audio_path
                ], check=True, timeout=30)
                
                audio_extracted = True
                successful += 1
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Timeout extracting audio for clip {i}")
                audio_extracted = False
                audio_filename = None
                failed += 1
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Failed to extract audio for clip {i}")
                audio_extracted = False
                audio_filename = None
                failed += 1
            except Exception as e:
                print(f"  ⚠️  Error for clip {i}: {e}")
                audio_extracted = False
                audio_filename = None
                failed += 1
        
        # Add to metadata
        metadata["clips"].append({
            "clip_id": clip_id,
            "filename": clip_file,
            "audio_filename": audio_filename,
            "text_filename": text_filename,
            "timestamp": {
                "start_seconds": round(start_time, 3),
                "end_seconds": round(end_time, 3),
                "duration": clip_duration
            },
            "audio_extracted": audio_extracted,
            "transcription": None,  # Will be filled by ASR
            "transcription_confidence": None
        })
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(clip_files)} clips processed ({successful} successful, {failed} failed)")
    
    # Save metadata
    metadata_path = os.path.join(output_dir, "alignment_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ Audio Extraction Complete!")
    print("="*70)
    print(f"Total clips processed: {len(clip_files)}")
    print(f"Audio extracted: {successful}")
    print(f"Failed: {failed}")
    print(f"\nOutput files:")
    print(f"  📂 Audio clips: {audio_dir}/")
    print(f"  📄 Metadata: {metadata_path}")
    print(f"\nNext step: Run transcription with:")
    print(f"  python run_audio_transcription.py")
    
    return metadata

if __name__ == '__main__':
    # Configuration
    clips_dir = "1/clips"
    original_video = "data/videos/Parliament_Live_01-12-2025.mp4"
    output_dir = "data/multimodal_dataset"
    
    # Check if files exist
    if not os.path.exists(clips_dir):
        print(f"❌ Clips directory not found: {clips_dir}")
        sys.exit(1)
    
    if not os.path.exists(original_video):
        print(f"❌ Original video not found: {original_video}")
        sys.exit(1)
    
    # Run extraction
    metadata = extract_audio_from_existing_clips(
        clips_dir=clips_dir,
        original_video=original_video,
        output_dir=output_dir,
        fps=30.0,
        clip_duration=5.0
    )
    
    print("\n" + "="*70)
    print("🎯 Dataset Ready for Research!")
    print("="*70)
