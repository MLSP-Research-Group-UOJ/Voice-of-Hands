#!/usr/bin/env python3
"""
Simple test: Use quick_start with border detection
"""

from sli_detector import process_video_for_dataset

video_path = "videos/Parliament_Live_01-12-2025.mp4"
output_dir = "test_border_124"

print("="*60)
print("Testing Border Detection: Exact 124×124 Size")
print("="*60)
print("\nProcessing with border detection (auto will select border)...\n")

# Process with auto mode (will use border if confidence is good enough)
results = process_video_for_dataset(
    video_path=video_path,
    output_dir=output_dir,
    detection_method="border",  # Force border detection
    clip_duration=3.0,
    min_confidence=0.2,  # Accept low confidence
    save_full_video=True,
    create_preview=False
)

print("\n" + "="*60)
print("Checking output dimensions...")
print("="*60)

import cv2
import os

# Check a clip
if results["clips"]:
    first_clip = results["clips"][0]
    cap = cv2.VideoCapture(first_clip)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"\nClip dimensions: {w}×{h}")
        if w == 124 and h == 124:
            print("✅ SUCCESS! Border detection clips are exact 124×124")
        elif abs(w-124) <= 2 and abs(h-124) <= 2:
            print(f"✅ SUCCESS! Within 2px of 124×124 (codec rounding)")
        else:
            print(f"❌ Expected ~124×124, got {w}×{h}")

# Check full video
if results["full_video"]:
    cap = cv2.VideoCapture(results["full_video"])
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"\nFull video dimensions: {w}×{h}")
        if w == 124 and h == 124:
            print("✅ SUCCESS! Full video is exact 124×124")
        elif abs(w-124) <= 2 and abs(h-124) <= 2:
            print(f"✅ SUCCESS! Within 2px of 124×124 (codec rounding)")
        else:
            print(f"❌ Expected ~124×124, got {w}×{h}")

print("\n" + "="*60)
