#!/usr/bin/env python3
"""
Demo: Test different border margin settings
"""

import subprocess
import cv2
import os

print("="*70)
print("Testing Different Border Margin Settings")
print("="*70)

video_path = "videos/Parliament_Live_01-12-2025.mp4"

test_configs = [
    (0.10, "test_margin_10", "10% border (larger crop)"),
    (0.15, "test_margin_15", "15% border (default)"),
    (0.20, "test_margin_20", "20% border (smaller crop)"),
]

results = []

for margin, output_dir, description in test_configs:
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Border margin: {margin:.0%} on each side")
    print(f"{'='*70}\n")
    
    # Run quick_start with specific border margin
    result = subprocess.run([
        "python", "quick_start.py",
        video_path,
        output_dir,
        "--border-margin", str(margin)
    ], capture_output=True, text=True, timeout=180)
    
    if result.returncode == 0:
        # Check output dimensions
        clip_path = f"{output_dir}/clips/Parliament_Live_01-12-2025_clip_0000.mp4"
        if os.path.exists(clip_path):
            cap = cv2.VideoCapture(clip_path)
            if cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                results.append({
                    'margin': margin,
                    'description': description,
                    'width': w,
                    'height': h
                })
                
                print(f"✅ Success: Output size = {w}×{h}")
            else:
                print("❌ Could not open clip")
        else:
            print("❌ Clip not found")
    else:
        print(f"❌ Command failed")

# Summary
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print(f"\n{'Border Margin':<15} {'Description':<30} {'Output Size':<15}")
print("-" * 70)

for r in results:
    print(f"{r['margin']:.0%} ({r['margin']:.2f}){' '*(8)} {r['description']:<30} {r['width']}×{r['height']}")

print("\n" + "="*70)
print("Understanding Border Margin:")
print("  • Lower value (0.10) = Less border excluded = LARGER crop area")
print("  • Higher value (0.20) = More border excluded = SMALLER crop area")
print("  • Default (0.15) = Balanced crop")
print("\nUsage:")
print("  python quick_start.py video.mp4 output --border-margin 0.10")
print("="*70)
