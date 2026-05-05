#!/usr/bin/env python3
"""
Run Sinhala transcription on all audio clips
"""
import sys
from timestamp_extractor import TimestampedClipExtractor

def main():
    print("=" * 60)
    print("Starting Sinhala Transcription")
    print("=" * 60)
    
    # Initialize extractor
    extractor = TimestampedClipExtractor(
        video_path="data/videos/Parliament_Live_01-12-2025.mp4",
        output_base_dir="data/multimodal_dataset"
    )
    
    # Run transcription
    print("\nConfiguration:")
    print("  Model: medium (recommended for Sinhala)")
    print("  Language: Sinhala (si)")
    print("  Audio files: 732 clips")
    print("  Estimated time: 30-40 minutes")
    print("\nThis will:")
    print("  - Transcribe all audio clips to Sinhala text")
    print("  - Extract word-level timestamps")
    print("  - Calculate confidence scores")
    print("  - Save individual .txt files")
    print("  - Update alignment_metadata.json")
    print("\nStarting transcription...\n")
    
    try:
        metadata = extractor.transcribe_audio_clips(
            metadata_path="multimodal_dataset/alignment_metadata.json",
            model_name="medium",  # Better quality for Sinhala
            language="si"         # Sinhala language
        )
        
        print("\n" + "=" * 60)
        print("✅ TRANSCRIPTION COMPLETE!")
        print("=" * 60)
        print(f"Total clips transcribed: {len(metadata.get('clips', []))}")
        print(f"Results saved to: multimodal_dataset/")
        print(f"  - Transcriptions: multimodal_dataset/transcriptions/")
        print(f"  - Metadata: multimodal_dataset/alignment_metadata.json")
        
    except Exception as e:
        print(f"\n❌ Error during transcription: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
