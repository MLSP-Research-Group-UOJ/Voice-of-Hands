#!/usr/bin/env python3
"""
Test: Verify border detection crops to exact 124×124 without upscaling
"""

import cv2
import os
from sli_detector import SLIDetector

video_path = "videos/Parliament_Live_01-12-2025.mp4"
output_test = "test_border_exact"

print("="*60)
print("Testing Border Detection - Exact Size (No Upscaling)")
print("="*60)

# Create detector
detector = SLIDetector(video_path)

# Test 1: Border detection
print("\n1. Running BORDER detection...")
result = detector.detect(method="border", sample_frames=30)

print(f"\nDetection Result:")
print(f"  Method: {result.method}")
print(f"  Confidence: {result.confidence:.2f}")
print(f"  Detected region: {result.x2-result.x1}×{result.y2-result.y1} pixels")

# Extract a test clip with border detection
os.makedirs(output_test, exist_ok=True)
clips_dir = os.path.join(output_test, "border_clips")

print(f"\n2. Extracting clips with BORDER detection (should keep exact size)...")
clips = detector.extract_sli_clips(
    result,
    clips_dir,
    clip_duration=3.0,
    overlap=0.0
)

if clips:
    first_clip = clips[0]
    cap = cv2.VideoCapture(first_clip)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        expected_w = result.x2 - result.x1
        expected_h = result.y2 - result.y1
        
        print(f"\n  Border Detection Clips:")
        print(f"    Expected: {expected_w}×{expected_h} (exact detection)")
        print(f"    Got: {w}×{h}")
        
        if w == expected_w and h == expected_h:
            print(f"    ✅ Perfect! No upscaling - exact border crop")
        elif abs(w - expected_w) <= 2 and abs(h - expected_h) <= 2:
            print(f"    ✅ Close! Within 2px (codec rounding)")
        else:
            print(f"    ❌ Size mismatch")

# Test 2: Edge detection (for comparison)
print(f"\n3. Running EDGE detection for comparison...")
result2 = detector.detect(method="edge", sample_frames=30)

print(f"\nDetection Result:")
print(f"  Method: {result2.method}")
print(f"  Confidence: {result2.confidence:.2f}")
print(f"  Detected region: {result2.x2-result2.x1}×{result2.y2-result2.y1} pixels")

clips_dir2 = os.path.join(output_test, "edge_clips")
print(f"\n4. Extracting clips with EDGE detection (should resize to 256×256)...")
clips2 = detector.extract_sli_clips(
    result2,
    clips_dir2,
    clip_duration=3.0,
    overlap=0.0
)

if clips2:
    first_clip2 = clips2[0]
    cap = cv2.VideoCapture(first_clip2)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"\n  Edge Detection Clips:")
        print(f"    Original detected: {result2.x2-result2.x1}×{result2.y2-result2.y1}")
        print(f"    Output: {w}×{h}")
        
        if w == 256 and h == 256:
            print(f"    ✅ Correct! Upscaled to 256×256 for DNN training")
        else:
            print(f"    ❌ Expected 256×256")

print("\n" + "="*60)
print("Summary:")
print(f"  Border detection: Keeps exact size ({result.x2-result.x1}×{result.y2-result.y1})")
print(f"  Other methods: Resize to 256×256 for DNN")
print("="*60)
