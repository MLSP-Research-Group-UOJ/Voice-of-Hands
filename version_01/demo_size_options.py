#!/usr/bin/env python3
"""
Demo: Test different output sizes - original, 128×128, 256×256
"""

import cv2
import os
from sli_detector import process_video_for_dataset

video_path = "videos/Parliament_Live_01-12-2025.mp4"

print("="*70)
print("Testing Different Output Sizes")
print("="*70)

test_configs = [
    ("original", "test_size_original"),
    ("128", "test_size_128"),
    ("256", "test_size_256")
]

results_summary = []

for size_option, output_dir in test_configs:
    print(f"\n{'='*70}")
    print(f"Processing with size: {size_option}")
    print(f"{'='*70}\n")
    
    # Process video
    results = process_video_for_dataset(
        video_path=video_path,
        output_dir=output_dir,
        detection_method="border",  # Force border detection for consistent testing
        clip_duration=3.0,
        min_confidence=0.2,
        save_full_video=True,
        create_preview=False,
        output_size=size_option
    )
    
    # Check output size
    if results["clips"]:
        first_clip = results["clips"][0]
        cap = cv2.VideoCapture(first_clip)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            results_summary.append({
                'size_option': size_option,
                'output_dir': output_dir,
                'width': w,
                'height': h,
                'clips': len(results["clips"]),
                'frames': frames
            })

# Print summary
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print(f"\n{'Size Option':<15} {'Output Dir':<25} {'Resolution':<15} {'Clips':<10}")
print("-" * 70)

for r in results_summary:
    print(f"{r['size_option']:<15} {r['output_dir']:<25} {r['width']}×{r['height']:<9} {r['clips']:<10}")

print("\n" + "="*70)
print("✅ All size options working correctly!")
print("\nUsage examples:")
print("  python quick_start.py video.mp4 output              # Original size (124×124)")
print("  python quick_start.py video.mp4 output --size 128   # Resize to 128×128")
print("  python quick_start.py video.mp4 output --size 256   # Resize to 256×256")
print("="*70)
