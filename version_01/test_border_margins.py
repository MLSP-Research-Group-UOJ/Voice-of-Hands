#!/usr/bin/env python3
"""
Quick test: Verify border margin works
"""

from sli_detector import SLIDetector

video_path = "videos/Parliament_Live_01-12-2025.mp4"

print("="*70)
print("Testing Border Margin Parameter")
print("="*70)

margins = [0.10, 0.15, 0.20]

for margin in margins:
    print(f"\n{'='*70}")
    print(f"Border Margin: {margin:.0%} ({margin:.2f}) on each side")
    print("-" * 70)
    
    detector = SLIDetector(video_path, border_margin=margin)
    result = detector.detect(method="border", sample_frames=30)
    
    width = result.x2 - result.x1
    height = result.y2 - result.y1
    
    print(f"  Detected region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
    print(f"  Interior size: {width}×{height} pixels")
    print(f"  Confidence: {result.confidence:.2f}")

print("\n" + "="*70)
print("Explanation:")
print("  • If full border box = 177×177 pixels:")
print(f"    - 10% margin: interior = {int(177 * 0.8)}×{int(177 * 0.8)} = {int(177 * 0.8)**2:,} pixels")
print(f"    - 15% margin: interior = {int(177 * 0.7)}×{int(177 * 0.7)} = {int(177 * 0.7)**2:,} pixels")
print(f"    - 20% margin: interior = {int(177 * 0.6)}×{int(177 * 0.6)} = {int(177 * 0.6)**2:,} pixels")
print("\n  Lower margin = MORE area captured")
print("  Higher margin = LESS area captured (tighter crop)")
print("="*70)
