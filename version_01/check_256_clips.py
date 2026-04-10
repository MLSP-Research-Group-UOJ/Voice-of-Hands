#!/usr/bin/env python3
"""
Quick test - check if existing clips are 256×256
"""

import cv2
import os

# Check existing output
output_dir = "output_dataset/clips"

if os.path.exists(output_dir):
    clips = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
    
    if clips:
        print("="*60)
        print("Checking OLD clips (should be original size)")
        print("="*60)
        
        first_old_clip = os.path.join(output_dir, clips[0])
        cap = cv2.VideoCapture(first_old_clip)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            print(f"\nOld clip dimensions: {w}×{h} pixels")
            print(f"File: {clips[0]}")

# Check the test output
test_dir = "test_output_256/clips"
if os.path.exists(test_dir):
    clips = sorted([f for f in os.listdir(test_dir) if f.endswith('.mp4')])
    
    if clips:
        print("\n" + "="*60)
        print("Checking NEW clips (should be 256×256)")
        print("="*60)
        
        for i, clip_name in enumerate(clips[:3]):  # Check first 3
            clip_path = os.path.join(test_dir, clip_name)
            cap = cv2.VideoCapture(clip_path)
            if cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                
                status = "✅" if (w == 256 and h == 256) else "❌"
                print(f"\n{status} Clip {i+1}: {clip_name}")
                print(f"   Dimensions: {w}×{h}")
                print(f"   Frames: {frames}")
        
        print(f"\n{'='*60}")
        print(f"Total clips: {len(clips)}")
        print("="*60)
else:
    print("No test output found yet - test still running or not started")
    print("Run: python test_256_output.py")
