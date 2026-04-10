#!/usr/bin/env python3
"""
Test script to verify 256×256 output resolution
"""

import cv2
import os
from sli_detector import SLIDetector

video_path = "videos/Parliament_Live_01-12-2025.mp4"
output_test = "test_output_256"

print("="*60)
print("Testing 256×256 Output Resolution")
print("="*60)

# Create detector
detector = SLIDetector(video_path)

# Run detection
print("\n1. Running detection...")
result = detector.detect(method="auto", sample_frames=30)

print(f"\nDetection Result:")
print(f"  Method: {result.method}")
print(f"  Confidence: {result.confidence:.2f}")
print(f"  Original detected region: {result.x2-result.x1}×{result.y2-result.y1} pixels")

# Test full video crop with 256×256
print(f"\n2. Testing full video crop (first 3 seconds)...")
test_full = os.path.join(output_test, "test_full_256.mp4")
os.makedirs(output_test, exist_ok=True)

success = detector.crop_and_save_sli(
    result,
    test_full,
    duration=3.0,
    target_size=(256, 256)
)

if success:
    cap = cv2.VideoCapture(test_full)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        if w == 256 and h == 256:
            print(f"  ✅ Full video: {w}×{h} - CORRECT!")
        else:
            print(f"  ❌ Full video: {w}×{h} - Expected 256×256")

# Test clip extraction with 256×256
print(f"\n3. Testing clip extraction...")
clips_dir = os.path.join(output_test, "clips")
clips = detector.extract_sli_clips(
    result,
    clips_dir,
    clip_duration=3.0,
    overlap=0.0,
    target_size=(256, 256)
)

if clips:
    print(f"  Generated {len(clips)} clips")
    
    # Check first clip
    first_clip = clips[0]
    cap = cv2.VideoCapture(first_clip)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        if w == 256 and h == 256:
            print(f"  ✅ Clip dimensions: {w}×{h} - CORRECT!")
        else:
            print(f"  ❌ Clip dimensions: {w}×{h} - Expected 256×256")
        
        print(f"  Frames in clip: {frames}")
        print(f"  First clip: {os.path.basename(first_clip)}")

print("\n" + "="*60)
print("Summary:")
print(f"  Original detected: {result.x2-result.x1}×{result.y2-result.y1} pixels")
print(f"  Output resolution: 256×256 pixels")
print(f"  Upscaling factor: {256 / (result.x2-result.x1):.2f}x")
print("="*60)
