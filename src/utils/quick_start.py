#!/usr/bin/env python3
"""
Quick Start Script for SLI Detection and Dataset Creation

This script provides the simplest way to get started:
1. Process a single video
2. Extract SLI clips for dataset
3. Get statistics

Usage:
    python quick_start.py <video_path> <output_dir>

Example:
    python quick_start.py my_news_video.mp4 my_dataset
"""

import sys
import os
from pathlib import Path


def quick_start(video_path: str, output_dir: str, output_size: str = "original", border_margin: float = 0.15, start_time: float = 0, crop_adjust: int = 0):
    """
    Process a video and create a sign language dataset with one command.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save results
        output_size: Output resolution - "original", "128", or "256"
        border_margin: Border exclusion margin (0.0-0.5)
        start_time: Start processing from this time in seconds (e.g., 480 = 8 minutes)
        crop_adjust: Adjust crop size in pixels (e.g., 10 = expand by 10px, -5 = shrink by 5px)
    """
    
    # Print welcome banner
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   Sign Language Interpreter Detection & Dataset Creation        ║
║   Quick Start Script                                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Validate input
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        return False
    
    print(f"📹 Input video: {video_path}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📐 Output size: {output_size}")
    print(f"🗒️  Border margin: {border_margin:.0%} on each side")
    if start_time > 0:
        print(f"⏱️  Start time: {start_time/60:.1f} minutes ({start_time:.0f} seconds)")
    if crop_adjust != 0:
        action = "expand" if crop_adjust > 0 else "shrink"
        print(f"📏 Crop adjust: {action} by {abs(crop_adjust)} pixels on each side")
    print()
    
    # Import required modules
    try:
        from sli_detector import process_video_for_dataset
        from dataset_utils import DatasetAnalyzer
    except ImportError as e:
        print(f"❌ Error: Could not import required modules")
        print(f"   {e}")
        print("\n💡 Make sure you're running this from the correct directory")
        return False
    
    # Process video
    print("🚀 Starting processing...\n")
    
    try:
        results = process_video_for_dataset(
            video_path=video_path,
            output_dir=output_dir,
            detection_method="auto",        # Automatic method selection
            clip_duration=5.0,              # 5-second clips
            min_confidence=0.2,             # Allow lower confidence for border detection
            save_full_video=True,           # Save full cropped video
            create_preview=True,            # Create detection preview
            output_size=output_size,        # Output resolution
            border_margin=border_margin,    # Border exclusion margin
            start_time=start_time,          # Start time in seconds
            crop_adjust=crop_adjust         # Crop size adjustment in pixels
        )
    except Exception as e:
        print(f"\n❌ Error during processing:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print results
    print("\n" + "="*60)
    print("✅ PROCESSING COMPLETE!")
    print("="*60)
    
    print(f"\n📊 Results:")
    print(f"   Detection confidence: {results['detection']['confidence']:.2%}")
    print(f"   Detection method: {results['detection']['method']}")
    print(f"   Bounding box: {results['detection']['bbox']}")
    print(f"   Clips extracted: {len(results['clips'])}")
    
    if results['clips']:
        print(f"\n📂 Output files:")
        print(f"   Clips directory: {os.path.join(output_dir, 'clips')}")
        print(f"   Preview image: {results['preview']}")
        if results['full_video']:
            print(f"   Full cropped video: {results['full_video']}")
    
    # Run dataset analysis
    print(f"\n📈 Analyzing dataset...\n")
    
    try:
        analyzer = DatasetAnalyzer(output_dir)
        stats = analyzer.get_dataset_statistics()
        analyzer.print_statistics(stats)
        
        # Save statistics
        stats_file = os.path.join(output_dir, "statistics.json")
        analyzer.save_statistics(stats_file)
        
        # Create preview grid
        preview_grid = os.path.join(output_dir, "preview_grid.jpg")
        analyzer.create_preview_grid(preview_grid, num_samples=min(16, len(results['clips'])))
        
    except Exception as e:
        print(f"⚠️  Warning: Could not analyze dataset: {e}")
    
    # Print next steps
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your dataset is ready")
    print("="*60)
    
    print(f"""
📚 Next Steps:

1. View detection preview:
   Open: {results['preview']}

2. Browse extracted clips:
   cd {os.path.join(output_dir, 'clips')}
   ls

3. View dataset preview grid:
   Open: {os.path.join(output_dir, 'preview_grid.jpg')}

4. Check detailed statistics:
   cat {os.path.join(output_dir, 'statistics.json')}

5. Process more videos:
   python quick_start.py another_video.mp4 {output_dir}
   
6. Advanced usage:
   See README_SLI_DETECTOR.md for more options

""")
    
    return True


def batch_quick_start(input_dir: str, output_dir: str):
    """
    Process all videos in a directory.
    
    Args:
        input_dir: Directory containing video files
        output_dir: Directory to save results
    """
    import glob
    from sli_detector import batch_process_videos
    
    print(f"\n🔍 Searching for videos in: {input_dir}")
    
    # Find all video files
    patterns = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV']
    video_files = []
    
    for pattern in patterns:
        video_files.extend(glob.glob(os.path.join(input_dir, pattern)))
    
    if not video_files:
        print(f"❌ No video files found in: {input_dir}")
        return False
    
    print(f"📹 Found {len(video_files)} videos")
    print()
    
    # Process batch
    print("🚀 Starting batch processing...\n")
    
    try:
        results = batch_process_videos(
            video_paths=video_files,
            output_base_dir=output_dir,
            detection_method="auto",
            clip_duration=5.0,
            save_full_videos=False  # Skip full videos to save space
        )
        
        total_clips = sum(len(r['clips']) for r in results)
        
        print(f"\n✅ Batch processing complete!")
        print(f"   Videos processed: {len(results)}")
        print(f"   Total clips: {total_clips}")
        print(f"   Output directory: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during batch processing:")
        print(f"   {e}")
        return False


def main():
    """Main entry point"""
    
    if len(sys.argv) < 3:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  Quick Start - Sign Language Interpreter Dataset Creation       ║
╚══════════════════════════════════════════════════════════════════╝

Usage:
  python quick_start.py <video_path> <output_dir> [options]
  python quick_start.py --batch <input_dir> <output_dir>

Examples:
  # Process single video (original size, e.g., 124×124)
  python quick_start.py news_video.mp4 my_dataset
  
  # Process with 128×128 output
  python quick_start.py news_video.mp4 my_dataset --size 128
  
  # Process with 256×256 output (for DNN training)
  python quick_start.py news_video.mp4 my_dataset --size 256
  
  # Adjust border margin (15% default, 10% = larger crop, 20% = smaller crop)
  python quick_start.py news_video.mp4 my_dataset --border-margin 0.10
  
  # Combine options
  python quick_start.py news_video.mp4 my_dataset --size 256 --border-margin 0.20
  
  # Start processing from 8 minutes into the video
  python quick_start.py news_video.mp4 my_dataset --start-time 480
  
  # Expand crop by 20 pixels on each side
  python quick_start.py news_video.mp4 my_dataset --crop-adjust 20
  
  # Process all videos in a directory
  python quick_start.py --batch raw_videos/ my_dataset

Options:
  --size <original|128|256>   Output resolution (default: original)
                              - original: Keep detected size (e.g., 124×124)
                              - 128: Resize to 128×128
                              - 256: Resize to 256×256 (best for DNN)
  --border-margin <0.0-0.5>   Border exclusion amount (default: 0.15)
                              - 0.15: 15% border on each side (default)
                              - 0.10: 10% border (larger crop area)
                              - 0.20: 20% border (smaller crop area)
  --start-time <seconds>      Start processing from this time in seconds
                              - Example: 480 = start from 8 minutes
                              - Example: 300 = start from 5 minutes
                              - Default: 0 (start from beginning)
  --crop-adjust <pixels>      Adjust crop size by adding/removing pixels
                              - Positive: expand crop (e.g., 20 = +20px each side)
                              - Negative: shrink crop (e.g., -10 = -10px each side)
                              - Default: 0 (use exact detected size)
  --batch                    Process all videos in a directory
  --help                     Show this help message

Requirements:
  - opencv-python
  - numpy
  - mediapipe (optional, for pose detection)

Install:
  pip install opencv-python numpy mediapipe

For more advanced usage, see README_SLI_DETECTOR.md
        """)
        sys.exit(0)
    
    # Check for batch mode
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 4:
            print("❌ Error: Batch mode requires input and output directories")
            print("Usage: python quick_start.py --batch <input_dir> <output_dir>")
            sys.exit(1)
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3]
        success = batch_quick_start(input_dir, output_dir)
    
    elif sys.argv[1] in ["--help", "-h"]:
        main()
        return
    
    else:
        # Single video mode
        video_path = sys.argv[1]
        output_dir = sys.argv[2]
        
        # Parse optional arguments
        output_size = "original"
        border_margin = 0.15
        start_time = 0  # Start from beginning by default
        crop_adjust = 0  # No adjustment by default
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--size" and i + 1 < len(sys.argv):
                size_value = sys.argv[i + 1].lower()
                if size_value in ["original", "128", "256"]:
                    output_size = size_value
                else:
                    print(f"⚠️  Warning: Invalid size '{sys.argv[i+1]}', using 'original'")
                    print("   Valid options: original, 128, 256")
                i += 2
            elif sys.argv[i] == "--border-margin" and i + 1 < len(sys.argv):
                try:
                    margin_value = float(sys.argv[i + 1])
                    if 0.0 <= margin_value <= 0.5:
                        border_margin = margin_value
                    else:
                        print(f"⚠️  Warning: border-margin must be 0.0-0.5, using default 0.15")
                except ValueError:
                    print(f"⚠️  Warning: Invalid border-margin '{sys.argv[i+1]}', using default 0.15")
                i += 2
            elif sys.argv[i] == "--start-time" and i + 1 < len(sys.argv):
                try:
                    time_value = float(sys.argv[i + 1])
                    if time_value >= 0:
                        start_time = time_value
                    else:
                        print(f"⚠️  Warning: start-time must be >= 0, using default 0")
                except ValueError:
                    print(f"⚠️  Warning: Invalid start-time '{sys.argv[i+1]}', using default 0")
                i += 2
            elif sys.argv[i] == "--crop-adjust" and i + 1 < len(sys.argv):
                try:
                    adjust_value = int(sys.argv[i + 1])
                    crop_adjust = adjust_value
                except ValueError:
                    print(f"⚠️  Warning: Invalid crop-adjust '{sys.argv[i+1]}', using default 0")
                i += 2
            else:
                i += 1
        
        success = quick_start(video_path, output_dir, output_size, border_margin, start_time, crop_adjust)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
