#!/usr/bin/env python3
"""
Quick Test: Verify the --size option works
"""

import subprocess
import cv2
import os

print("="*70)
print("Testing Size Options via Command Line")
print("="*70)

# Test 1: Original size (default)
print("\n[Test 1] Default (original size)")
print("-" * 70)
result = subprocess.run([
    "python", "quick_start.py",
    "videos/Parliament_Live_01-12-2025.mp4",
    "test_cli_original"
], capture_output=True, text=True, timeout=120)

if result.returncode == 0:
    # Check output
    clip_path = "test_cli_original/clips/Parliament_Live_01-12-2025_clip_0000.mp4"
    if os.path.exists(clip_path):
        cap = cv2.VideoCapture(clip_path)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            print(f"✅ Success: Output size = {w}×{h}")
        else:
            print("❌ Could not open clip")
    else:
        print("❌ Clip not found")
else:
    print(f"❌ Command failed: {result.returncode}")

# Test 2: 128×128
print("\n[Test 2] --size 128")
print("-" * 70)
result = subprocess.run([
    "python", "quick_start.py",
    "videos/Parliament_Live_01-12-2025.mp4",
    "test_cli_128",
    "--size", "128"
], capture_output=True, text=True, timeout=120)

if result.returncode == 0:
    clip_path = "test_cli_128/clips/Parliament_Live_01-12-2025_clip_0000.mp4"
    if os.path.exists(clip_path):
        cap = cv2.VideoCapture(clip_path)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            if w == 128 and h == 128:
                print(f"✅ Success: Output size = {w}×{h}")
            else:
                print(f"❌ Wrong size: {w}×{h} (expected 128×128)")
        else:
            print("❌ Could not open clip")
    else:
        print("❌ Clip not found")
else:
    print(f"❌ Command failed: {result.returncode}")

# Test 3: 256×256
print("\n[Test 3] --size 256")
print("-" * 70)
result = subprocess.run([
    "python", "quick_start.py",
    "videos/Parliament_Live_01-12-2025.mp4",
    "test_cli_256",
    "--size", "256"
], capture_output=True, text=True, timeout=120)

if result.returncode == 0:
    clip_path = "test_cli_256/clips/Parliament_Live_01-12-2025_clip_0000.mp4"
    if os.path.exists(clip_path):
        cap = cv2.VideoCapture(clip_path)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            if w == 256 and h == 256:
                print(f"✅ Success: Output size = {w}×{h}")
            else:
                print(f"❌ Wrong size: {w}×{h} (expected 256×256)")
        else:
            print("❌ Could not open clip")
    else:
        print("❌ Clip not found")
else:
    print(f"❌ Command failed: {result.returncode}")

print("\n" + "="*70)
print("Testing Complete!")
print("="*70)
