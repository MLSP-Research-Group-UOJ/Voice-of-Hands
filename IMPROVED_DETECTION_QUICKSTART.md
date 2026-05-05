# Improved Horizontal Idle Detection - Quick Start

## What Changed?

**OLD** ❌: Only checked if wrists were at similar Y positions
- Problem: Hands raised near face were detected as "horizontal idle"

**NEW** ✓: Checks if **forearms (elbow to wrist) are horizontal** 
- Solution: Prevents false positives when hands are raised

## How It Works Now

The system checks **5 conditions** for horizontal idle:

1. **Left forearm horizontal**: `abs(left_elbow.y - left_wrist.y) < 0.15`
2. **Right forearm horizontal**: `abs(right_elbow.y - right_wrist.y) < 0.15`
3. **Hands separated**: `abs(left_wrist.x - right_wrist.x) > 0.15`
4. **Left hand not raised**: `left_wrist.y >= left_elbow.y - 0.1`
5. **Right hand not raised**: `right_wrist.y >= right_elbow.y - 0.1`

**ALL 5 must be true** for idle detection.

## Usage Examples

### Extract clips (default with improved detection)
```bash
python sign_activity_detector.py video.mp4 output_clips/ --threshold 0.02
```

### Visualize to see it working
```bash
python sign_activity_detector.py video.mp4 output_clips/ \
    --visualize \
    --threshold 0.02
```

Watch for the status labels:
- **IDLE (Horizontal Hands)** - Orange: Forearms horizontal, hands resting
- **IDLE (Low Motion)** - Gray: Motion below threshold
- **ACTIVE SIGNING** - Green: Active signing detected

### Adjust sensitivity

**Stricter detection** (less likely to mark as idle):
```bash
python sign_activity_detector.py video.mp4 output/ \
    --horizontal-y-threshold 0.10  # Forearms must be very horizontal
```

**Looser detection** (more likely to mark as idle):
```bash
python sign_activity_detector.py video.mp4 output/ \
    --horizontal-y-threshold 0.20  # Allow more angle variation
```

### Disable if needed
```bash
python sign_activity_detector.py video.mp4 output/ --no-horizontal-idle
```

## What Gets Filtered Now

✓ **Correctly filtered as IDLE:**
- Hands resting at waist/lap with forearms horizontal
- Rest positions with hands lowered
- Breathing movements while in rest position

✓ **Correctly marked as ACTIVE:**
- Hands raised near face/neck (your image 2)
- Hands moving for signing
- Forearms at angles (actively signing)
- One or both hands raised above elbows

## Test Your Video

```bash
# Quick analysis to see the difference
python sign_activity_detector.py your_video.mp4 test_output/ \
    --analyze-only \
    --threshold 0.02

# Compare with horizontal detection disabled
python sign_activity_detector.py your_video.mp4 test_output2/ \
    --analyze-only \
    --threshold 0.02 \
    --no-horizontal-idle
```

Compare the "Active segments found" count to see the improvement!

## Files Created

- `sign_activity_detector.py` - Updated with improved detection
- `HORIZONTAL_IDLE_DETECTION.md` - Full documentation  
- `HORIZONTAL_DETECTION_DIAGRAM.txt` - Visual diagrams
- `test_horizontal_logic.py` - Logic explanation
- `IMPROVED_DETECTION_QUICKSTART.md` - This file

## Summary

The improved detection now **prevents false positives** when hands are raised near the face by checking:
1. Each forearm's angle (elbow→wrist must be horizontal)
2. Hand position (wrists must be at/below elbows)

This matches the actual rest position more accurately!
