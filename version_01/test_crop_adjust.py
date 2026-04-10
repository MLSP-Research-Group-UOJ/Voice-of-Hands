"""
Test script to demonstrate crop_adjust parameter - adjust crop size without changing border margin
"""

from sli_detector import SLIDetector
import cv2

def test_crop_adjust(video_path, start_time=480):
    """
    Test crop_adjust parameter with different values.
    Shows how crop size changes independent of border margin.
    """
    print("Testing crop_adjust parameter")
    print("="*70)
    print(f"Video: {video_path}")
    print(f"Start time: {start_time/60:.1f} minutes ({start_time} seconds)")
    print(f"Border margin: 0.15 (15% - kept constant)")
    print()
    
    # Test different crop adjustments
    adjustments = [0, 10, 20, -5]
    
    detector = SLIDetector(video_path, border_margin=0.15)
    
    # Get base detection
    print("Step 1: Detect border region with 15% margin...")
    result = detector.detect(method="border", sample_frames=50, start_time=start_time)
    
    base_width = result.x2 - result.x1
    base_height = result.y2 - result.y1
    
    print(f"\nBase detection (margin=0.15, adjust=0):")
    print(f"  Region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
    print(f"  Size: {base_width}×{base_height} pixels")
    print(f"  Confidence: {result.confidence:.2f}")
    print()
    
    print("="*70)
    print("Step 2: Apply different crop adjustments...")
    print("="*70)
    
    for adjust in adjustments:
        # Calculate adjusted box
        x1 = max(0, result.x1 - adjust)
        y1 = max(0, result.y1 - adjust)
        x2 = min(1280, result.x2 + adjust)  # Assuming 1280 width
        y2 = min(720, result.y2 + adjust)   # Assuming 720 height
        
        new_width = x2 - x1
        new_height = y2 - y1
        
        if adjust == 0:
            print(f"\n✅ crop_adjust = {adjust:3d}  (No adjustment)")
        elif adjust > 0:
            print(f"\n✅ crop_adjust = +{adjust:2d}  (Expand by {adjust}px on each side)")
        else:
            print(f"\n✅ crop_adjust = {adjust:3d}  (Shrink by {abs(adjust)}px on each side)")
        
        print(f"   New region: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"   New size: {new_width}×{new_height} pixels")
        print(f"   Change: {new_width - base_width:+d}×{new_height - base_height:+d} pixels")
        
        if adjust != 0:
            percent_change = ((new_width * new_height) / (base_width * base_height) - 1) * 100
            print(f"   Area change: {percent_change:+.1f}%")
    
    print("\n" + "="*70)
    print("Summary:")
    print("="*70)
    print("• border_margin controls how much border to EXCLUDE (percentage)")
    print("• crop_adjust controls final crop size (pixels added/removed)")
    print("• Both parameters work independently")
    print()
    print("Example combinations:")
    print("  --border-margin 0.15 --crop-adjust 0    → 124×124 (default)")
    print("  --border-margin 0.15 --crop-adjust 10   → 144×144 (+20px total)")
    print("  --border-margin 0.15 --crop-adjust 20   → 164×164 (+40px total)")
    print("  --border-margin 0.10 --crop-adjust 10   → 162×162 (less border + expand)")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_crop_adjust.py <video_path> [start_time_seconds]")
        print("\nExample:")
        print("  python test_crop_adjust.py videos/Parliament_Live_01-12-2025.mp4 480")
        sys.exit(1)
    
    video_path = sys.argv[1]
    start_time = float(sys.argv[2]) if len(sys.argv) > 2 else 480
    
    test_crop_adjust(video_path, start_time)
