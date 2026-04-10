#!/usr/bin/env python3
"""
Test border detection on Parliament video
"""

import sys
sys.path.insert(0, '/media/spdanuraj/windows 11/Research/Voice_to_Hands/Voice-of-Hands')

from sli_detector import SLIDetector

# Test video
video_path = "videos/Parliament_Live_01-12-2025.mp4"

print("="*60)
print("Testing Border Detection")
print("="*60)

# Initialize detector
detector = SLIDetector(video_path)
print(f"\nVideo: {detector.width}x{detector.height} @ {detector.fps} FPS\n")

# Test border detection
print("Testing border detection method...")
result_border = detector.detect(method="border", sample_frames=50)
print(f"\nBorder Detection:")
print(f"  Confidence: {result_border.confidence:.2f}")
print(f"  Region: ({result_border.x1}, {result_border.y1}) to ({result_border.x2}, {result_border.y2})")
print(f"  Size: {result_border.x2 - result_border.x1}×{result_border.y2 - result_border.y1}")

# Visualize
print("\nCreating visualization...")
detector.visualize_detection(result_border, "test_border_detection.jpg")
print("✓ Saved to: test_border_detection.jpg")

# Test auto mode (should use border now)
print("\n" + "="*60)
print("Testing auto mode (should try border first)...")
result_auto = detector.detect(method="auto", sample_frames=50)
print(f"\nAuto Detection:")
print(f"  Method used: {result_auto.method}")
print(f"  Confidence: {result_auto.confidence:.2f}")
print(f"  Region: ({result_auto.x1}, {result_auto.y1}) to ({result_auto.x2}, {result_auto.y2})")
print(f"  Size: {result_auto.x2 - result_auto.x1}×{result_auto.y2 - result_auto.y1}")

print("\n" + "="*60)
print("Testing complete!")
print("Review test_border_detection.jpg to verify detection")
print("="*60)
