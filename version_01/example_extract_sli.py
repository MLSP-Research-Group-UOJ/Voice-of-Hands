#!/usr/bin/env python3
"""
Example script demonstrating SLI region detection and dataset creation.

This script shows three different usage patterns:
1. Single video processing - Extract clips from one video
2. Batch processing - Process multiple videos at once
3. Custom pipeline - Full control over detection and extraction
"""

import os
from sli_detector import (
    SLIDetector, 
    process_video_for_dataset, 
    batch_process_videos,
    detect_sli_region
)


def example_1_single_video():
    """Example 1: Process a single video file"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Video Processing")
    print("="*70)
    
    # Input video
    video_path = "path/to/your/news_video.mp4"
    
    # Output directory
    output_dir = "dataset/single_video_output"
    
    # Process video with all defaults
    results = process_video_for_dataset(
        video_path=video_path,
        output_dir=output_dir,
        detection_method="auto",      # Try motion, fallback to edge
        clip_duration=5.0,             # 5-second clips
        min_confidence=0.5,            # Minimum detection confidence
        save_full_video=True,          # Also save full cropped video
        create_preview=True            # Create detection visualization
    )
    
    # Print results
    print("\nResults:")
    print(f"  Detected region: {results['detection']['bbox']}")
    print(f"  Confidence: {results['detection']['confidence']:.2f}")
    print(f"  Clips saved: {len(results['clips'])}")
    print(f"  Preview: {results['preview']}")
    print(f"  Full video: {results['full_video']}")
    
    return results


def example_2_batch_processing():
    """Example 2: Process multiple videos in batch"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Video Processing")
    print("="*70)
    
    # List of video files
    video_paths = [
        "videos/news1.mp4",
        "videos/news2.mp4",
        "videos/news3.mp4",
        # Add more videos...
    ]
    
    # Output directory
    output_base_dir = "dataset/batch_output"
    
    # Process all videos
    results = batch_process_videos(
        video_paths=video_paths,
        output_base_dir=output_base_dir,
        detection_method="hybrid",      # Use hybrid detection
        clip_duration=3.0,              # 3-second clips
        save_full_videos=False          # Skip full video to save space
    )
    
    # Summary
    total_clips = sum(len(r['clips']) for r in results)
    print(f"\nDataset Summary:")
    print(f"  Videos processed: {len(results)}")
    print(f"  Total clips: {total_clips}")
    print(f"  Average clips per video: {total_clips/len(results):.1f}")
    
    return results


def example_3_custom_pipeline():
    """Example 3: Custom processing with fine control"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Pipeline with Full Control")
    print("="*70)
    
    video_path = "path/to/your/news_video.mp4"
    
    # Step 1: Initialize detector
    detector = SLIDetector(video_path)
    print(f"Video Info: {detector.width}x{detector.height} @ {detector.fps} FPS")
    
    # Step 2: Try different detection methods
    print("\nTrying multiple detection methods...")
    
    methods = ["motion", "edge", "hybrid"]
    best_result = None
    best_confidence = 0
    
    for method in methods:
        result = detector.detect(method=method, sample_frames=30)
        print(f"  {method:8s}: confidence={result.confidence:.3f}, "
              f"bbox=({result.x1},{result.y1})-({result.x2},{result.y2})")
        
        if result.confidence > best_confidence:
            best_confidence = result.confidence
            best_result = result
    
    print(f"\nBest method: {best_result.method} (confidence: {best_result.confidence:.3f})")
    
    # Step 3: Visualize detection
    os.makedirs("output/previews", exist_ok=True)
    detector.visualize_detection(best_result, "output/previews/detection.jpg")
    
    # Step 4: Extract clips with custom parameters
    clips = detector.extract_sli_clips(
        result=best_result,
        output_dir="output/custom_clips",
        clip_duration=4.0,              # 4-second clips
        overlap=0.5,                    # 50% overlap between clips
        min_motion_threshold=2.0,       # Higher threshold for more active clips
        padding=15                      # More padding around detected region
    )
    
    print(f"\nExtracted {len(clips)} clips")
    
    # Step 5: Save full cropped video with custom time range
    detector.crop_and_save_sli(
        result=best_result,
        output_path="output/sli_full_00-30.mp4",
        padding=10,
        start_time=0,                   # Start at beginning
        duration=30,                    # Extract first 30 seconds only
        apply_smoothing=True
    )
    
    print("\nCustom pipeline complete!")
    
    return clips


def example_4_directory_scan():
    """Example 4: Automatically find and process all videos in a directory"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Process All Videos in Directory")
    print("="*70)
    
    input_dir = "raw_videos"
    output_dir = "dataset/processed"
    
    # Find all video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
    video_paths = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_paths.append(os.path.join(root, file))
    
    print(f"Found {len(video_paths)} videos in {input_dir}")
    
    if video_paths:
        results = batch_process_videos(
            video_paths=video_paths,
            output_base_dir=output_dir,
            detection_method="auto",
            clip_duration=5.0
        )
        
        print(f"\nProcessed {len(results)} videos successfully")
    
    return video_paths


def example_5_specific_time_ranges():
    """Example 5: Extract SLI from specific time ranges"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Extract Specific Time Ranges")
    print("="*70)
    
    video_path = "path/to/your/news_video.mp4"
    
    # Detect SLI region once
    detector = SLIDetector(video_path)
    result = detector.detect(method="auto")
    
    # Extract multiple time ranges
    time_ranges = [
        (0, 30),      # First 30 seconds
        (60, 90),     # 1:00 to 1:30
        (120, 180),   # 2:00 to 3:00
    ]
    
    os.makedirs("output/time_ranges", exist_ok=True)
    
    for i, (start, end) in enumerate(time_ranges):
        output_path = f"output/time_ranges/segment_{i+1}_{start}-{end}.mp4"
        duration = end - start
        
        print(f"\nExtracting segment {i+1}: {start}s to {end}s")
        detector.crop_and_save_sli(
            result=result,
            output_path=output_path,
            start_time=start,
            duration=duration,
            padding=10
        )
    
    print("\nAll segments extracted!")


def main():
    """Run examples"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  Sign Language Interpreter Detection & Dataset Creation         ║
║  Example Usage Scripts                                           ║
╚══════════════════════════════════════════════════════════════════╝

Choose an example to run:

1. Single video processing (simple)
2. Batch processing (multiple videos)
3. Custom pipeline (full control)
4. Process entire directory
5. Extract specific time ranges

Press Ctrl+C to exit
""")
    
    try:
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            example_1_single_video()
        elif choice == "2":
            example_2_batch_processing()
        elif choice == "3":
            example_3_custom_pipeline()
        elif choice == "4":
            example_4_directory_scan()
        elif choice == "5":
            example_5_specific_time_ranges()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Quick test mode - uncomment to run without menu
    # example_1_single_video()
    
    # Interactive mode
    main()
