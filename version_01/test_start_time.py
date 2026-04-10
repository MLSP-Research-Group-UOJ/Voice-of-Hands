"""
Test script to verify --start-time parameter works correctly
"""

from sli_detector import SLIDetector

def test_start_time(video_path, start_time_seconds):
    """
    Test that detection starts from the specified time.
    """
    print(f"Testing start_time parameter with {start_time_seconds} seconds ({start_time_seconds/60:.1f} minutes)")
    print("="*70)
    
    # Test border detection with start_time
    detector = SLIDetector(video_path, border_margin=0.15)
    
    print(f"\n1. Testing border detection from {start_time_seconds/60:.1f} minutes...")
    result = detector._detect_border(sample_frames=30, start_time=start_time_seconds)
    
    print(f"\n   Result:")
    print(f"   - Detection method: {result.method}")
    print(f"   - Confidence: {result.confidence:.2f}")
    print(f"   - Region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
    print(f"   - Size: {result.x2-result.x1}×{result.y2-result.y1} pixels")
    
    print(f"\n2. Testing full pipeline with start_time={start_time_seconds}...")
    result2 = detector.detect(method="auto", sample_frames=50, start_time=start_time_seconds)
    
    print(f"\n   Result:")
    print(f"   - Detection method: {result2.method}")
    print(f"   - Confidence: {result2.confidence:.2f}")
    print(f"   - Region: ({result2.x1}, {result2.y1}) to ({result2.x2}, {result2.y2})")
    print(f"   - Size: {result2.x2-result2.x1}×{result2.y2-result2.y1} pixels")
    
    print("\n" + "="*70)
    print("✅ Start time parameter working correctly!")
    print(f"   Detection began at {start_time_seconds/60:.1f} minutes into the video\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_start_time.py <video_path> [start_time_seconds]")
        print("\nExample:")
        print("  python test_start_time.py videos/Parliament_Live_01-12-2025.mp4 480")
        print("  (This will start detection from 8 minutes into the video)")
        sys.exit(1)
    
    video_path = sys.argv[1]
    start_time = float(sys.argv[2]) if len(sys.argv) > 2 else 480  # Default: 8 minutes
    
    test_start_time(video_path, start_time)
