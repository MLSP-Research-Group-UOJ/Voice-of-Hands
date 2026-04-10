#!/usr/bin/env python3
"""
Quick test to verify border detection crops exactly without padding
"""

import cv2
from sli_detector import SLIDetector

# Test with Parliament video
video_path = "videos/Parliament_Live_01-12-2025.mp4"

print("="*60)
print("Testing Border Detection - Exact Crop (No Padding)")
print("="*60)

# Create detector
detector = SLIDetector(video_path)

# Test border detection
print("\n1. Running border detection...")
result = detector.detect(method="border", sample_frames=30)

print(f"\nDetection Result:")
print(f"  Method: {result.method}")
print(f"  Confidence: {result.confidence:.2f}")
print(f"  Detected Region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
print(f"  Size: {result.x2-result.x1}×{result.y2-result.y1}")

# Test cropping with explicitly set padding
print(f"\n2. Testing crop function with padding=10 (should auto-set to 0)...")

# Create a short test video (first 5 seconds)
test_output = "test_border_crop_exact.mp4"
success = detector.crop_and_save_sli(
    result, 
    test_output,
    padding=10,  # Should be auto-changed to 0 for border method
    duration=5.0
)

if success:
    # Check the output video dimensions
    test_cap = cv2.VideoCapture(test_output)
    if test_cap.isOpened():
        width = int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        test_cap.release()
        
        detected_width = result.x2 - result.x1
        detected_height = result.y2 - result.y1
        
        print(f"\n3. Verification:")
        print(f"  Detected region size: {detected_width}×{detected_height}")
        print(f"  Output video size: {width}×{height}")
        
        if width == detected_width and height == detected_height:
            print(f"\n✅ SUCCESS! Crop is EXACT - no padding added")
            print(f"   The cropped video matches detected border exactly!")
        elif abs(width - detected_width) <= 2 and abs(height - detected_height) <= 2:
            print(f"\n✅ SUCCESS! Crop is within 2 pixels (codec rounding)")
            print(f"   Difference: {abs(width-detected_width)}×{abs(height-detected_height)} pixels")
        else:
            padding_added_x = (width - detected_width) // 2
            padding_added_y = (height - detected_height) // 2
            print(f"\n❌ ISSUE: Extra padding was added")
            print(f"   Padding added: ~{padding_added_x}×{padding_added_y} pixels on each side")
            print(f"   Expected: {detected_width}×{detected_height}")
            print(f"   Got: {width}×{height}")
        
        print(f"\nTest output saved: {test_output}")
    else:
        print("❌ Could not open test output video")
else:
    print("❌ Crop failed")

print("\n" + "="*60)
