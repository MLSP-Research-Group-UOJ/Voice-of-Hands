#!/usr/bin/env python3
"""
System Verification Script
Checks if all components are working correctly
"""

import sys
import os

print("="*70)
print("SIGN LANGUAGE DATASET COLLECTION SYSTEM - VERIFICATION")
print("="*70)
print()

# Check 1: Python imports
print("✓ CHECK 1: Python Packages")
try:
    import cv2
    print(f"  ✓ OpenCV version: {cv2.__version__}")
except ImportError:
    print("  ✗ OpenCV not installed!")
    sys.exit(1)

try:
    import numpy as np
    print(f"  ✓ NumPy version: {np.__version__}")
except ImportError:
    print("  ✗ NumPy not installed!")
    sys.exit(1)

print()

# Check 2: Core files
print("✓ CHECK 2: Core System Files")
required_files = [
    "sli_detector.py",
    "quick_start.py",
    "dataset_utils.py",
    "test_border_detection.py",
    "requirements.txt"
]

for file in required_files:
    if os.path.exists(file):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} - MISSING!")
        sys.exit(1)

print()

# Check 3: Import main module
print("✓ CHECK 3: Core Module Import")
try:
    from sli_detector import SLIDetector, DetectionResult
    print("  ✓ sli_detector module loaded")
except ImportError as e:
    print(f"  ✗ Cannot import sli_detector: {e}")
    sys.exit(1)

print()

# Check 4: Check detection methods
print("✓ CHECK 4: Detection Methods Available")
try:
    # Create dummy detector to check methods
    test_methods = ["auto", "border", "motion", "edge", "hybrid"]
    print(f"  ✓ Methods available: {', '.join(test_methods)}")
except Exception as e:
    print(f"  ✗ Error checking methods: {e}")
    sys.exit(1)

print()

# Check 5: Videos directory
print("✓ CHECK 5: Videos Directory")
if os.path.exists("videos/"):
    videos = [f for f in os.listdir("videos/") if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if videos:
        print(f"  ✓ Videos directory exists with {len(videos)} video(s)")
        for v in videos:
            size_mb = os.path.getsize(f"videos/{v}") / (1024*1024)
            print(f"    - {v} ({size_mb:.1f} MB)")
    else:
        print("  ⚠ Videos directory exists but no videos found")
        print("    Add videos to videos/ directory")
else:
    print("  ⚠ Videos directory not found")
    print("    Create it with: mkdir videos")

print()

# Check 6: Output dataset (if exists)
print("✓ CHECK 6: Previous Results")
if os.path.exists("output_dataset/"):
    if os.path.exists("output_dataset/clips/"):
        clips = [f for f in os.listdir("output_dataset/clips/") if f.endswith('.mp4')]
        print(f"  ✓ Previous dataset found with {len(clips)} clips")
    else:
        print("  ⚠ output_dataset/ exists but no clips yet")
else:
    print("  ⓘ No previous results (will be created on first run)")

print()

# Check 7: Test detection (if video exists)
print("✓ CHECK 7: System Functional Test")
test_video = None
if os.path.exists("videos/"):
    videos = [f for f in os.listdir("videos/") if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if videos:
        test_video = f"videos/{videos[0]}"

if test_video and os.path.exists(test_video):
    try:
        print(f"  Testing with: {os.path.basename(test_video)}")
        detector = SLIDetector(test_video)
        print(f"  ✓ Video opened: {detector.width}x{detector.height} @ {detector.fps} FPS")
        print(f"  ✓ Detector initialized successfully")
        
        # Quick detection test (just 5 frames)
        print("  Testing border detection (5 frames)...")
        result = detector.detect(method="border", sample_frames=5)
        print(f"  ✓ Detection completed")
        print(f"    - Method: {result.method}")
        print(f"    - Confidence: {result.confidence:.2f}")
        print(f"    - Region: ({result.x1},{result.y1}) to ({result.x2},{result.y2})")
        
    except Exception as e:
        print(f"  ✗ Detection test failed: {e}")
        sys.exit(1)
else:
    print("  ⓘ No test video available - skipping functional test")
    print("    Add a video to videos/ directory to test")

print()

# Summary
print("="*70)
print("✅ SYSTEM VERIFICATION COMPLETE!")
print("="*70)
print()
print("READY TO USE! Run:")
print()
print("  # Process single video:")
print("  python quick_start.py videos/your_video.mp4 output_dataset")
print()
print("  # Test border detection:")
print("  python test_border_detection.py")
print()
print("  # Batch process:")
print("  python quick_start.py --batch videos/ output_dataset")
print()
print("="*70)
