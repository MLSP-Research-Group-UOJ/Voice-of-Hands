#!/usr/bin/env python3
"""
Diagnostic tool to understand why horizontal idle detection might fail.

This explains the 5 conditions needed for "Rest: YES" to appear.
"""

print("=" * 70)
print("HORIZONTAL IDLE DETECTION - DIAGNOSTIC GUIDE")
print("=" * 70)
print()

print("WHY 'Rest: NO' MIGHT SHOW EVEN WHEN HANDS ARE RESTING:")
print("=" * 70)
print()

print("The system requires ALL 5 conditions to be TRUE:")
print()

print("1. BOTH HANDS DETECTED by MediaPipe")
print("   - MediaPipe must detect BOTH left and right hands")
print("   - If only 1 hand is detected → 'Rest: NO'")
print("   - Common issue: Hand partially occluded or poor lighting")
print()

print("2. LEFT FOREARM HORIZONTAL")
print("   - |left_elbow.y - left_wrist.y| < 0.15")
print("   - If > 0.15 → forearm too angled → 'Rest: NO'")
print("   - 0.15 = 15% of frame height")
print()

print("3. RIGHT FOREARM HORIZONTAL")
print("   - |right_elbow.y - right_wrist.y| < 0.15")
print("   - If > 0.15 → forearm too angled → 'Rest: NO'")
print()

print("4. HANDS SEPARATED")
print("   - |left_wrist.x - right_wrist.x| > 0.15")
print("   - If < 0.15 → hands too close → 'Rest: NO'")
print("   - Prevents overlapping hands from being detected as rest")
print()

print("5. HANDS NOT RAISED")
print("   - left_wrist.y >= left_elbow.y - 0.1")
print("   - right_wrist.y >= right_elbow.y - 0.1")
print("   - If wrists above elbows → hands raised → 'Rest: NO'")
print("   - Prevents hands near face from being detected as rest")
print()

print("=" * 70)
print("COMMON REASONS FOR FALSE NEGATIVES:")
print("=" * 70)
print()

print("Issue 1: ONLY ONE HAND DETECTED")
print("  Problem: MediaPipe didn't detect both hands")
print("  Solution: Improve lighting, ensure both hands visible")
print("  Debug msg: 'Rest fail: Only 1 hand detected'")
print()

print("Issue 2: FOREARM ANGLE TOO STEEP")
print("  Problem: Forearm Y-difference > 0.15 (15% of frame)")
print("  Solution: Lower threshold with --horizontal-y-threshold 0.20")
print("  Debug msg: 'Rest fail: L:0.18' or 'R:0.16'")
print()

print("Issue 3: HANDS TOO CLOSE TOGETHER")
print("  Problem: Hand X-separation < 0.15 (15% of frame)")
print("  Solution: Lower min distance with --horizontal-min-distance 0.10")
print("  Debug msg: 'Rest fail: Sep:0.12'")
print()

print("Issue 4: HANDS SLIGHTLY RAISED")
print("  Problem: Wrists slightly above elbows")
print("  Solution: Threshold allows 0.1 tolerance, might need adjustment")
print("  Debug msg: 'Rest fail: Raised'")
print()

print("=" * 70)
print("HOW TO FIX:")
print("=" * 70)
print()

print("OPTION 1: Relax the thresholds")
print("  python sign_activity_detector.py video.mp4 output/ \\")
print("      --visualize \\")
print("      --horizontal-y-threshold 0.20 \\  # More lenient (default: 0.15)")
print("      --horizontal-min-distance 0.10   # Closer hands OK (default: 0.15)")
print()

print("OPTION 2: Check the debug message in visualization")
print("  - Look at Row 6 in the info overlay")
print("  - It will show: 'Rest fail: [reason]'")
print("  - Examples:")
print("    * 'Rest fail: L:0.18' → Left forearm angle is 0.18 (> 0.15 threshold)")
print("    * 'Rest fail: Sep:0.12' → Hands separated by 0.12 (< 0.15 min)")
print("    * 'Rest fail: Only 1 hand detected' → MediaPipe sees 1 hand")
print()

print("OPTION 3: Test with relaxed settings")
print("  python sign_activity_detector.py \\")
print("      output_signer_dataset/full_cropped/output_short_sli_cropped.mp4 \\")
print("      test_rest/ \\")
print("      --visualize \\")
print("      --threshold 0.02 \\")
print("      --horizontal-y-threshold 0.25 \\  # Very lenient")
print("      --horizontal-min-distance 0.08   # Hands can be closer")
print()

print("=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print()
print("1. Run with visualization to see debug message")
print("2. Check what condition is failing")
print("3. Adjust thresholds accordingly")
print("4. Re-test until 'Rest: YES' appears correctly")
print()
print("=" * 70)
