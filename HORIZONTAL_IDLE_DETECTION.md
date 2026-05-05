# Horizontal Idle Detection for Sign Language Activity

## Overview

The sign activity detector now includes **horizontal idle detection** as an additional condition to identify when the signer is in an idle/rest position. This works alongside the existing motion threshold detection.

## How It Works

### Detection Logic

The system now uses **TWO conditions** to determine if a frame is idle:

1. **Motion Threshold** (existing): Low motion energy between frames
2. **Horizontal Hands** (NEW): Both hands detected in horizontal rest position

A frame is marked as **IDLE** if:
- Motion energy < threshold, OR
- Hands are in horizontal position (even with some motion)

A frame is marked as **ACTIVE** if:
- Motion energy ≥ threshold AND hands are NOT in horizontal position

### Horizontal Position Detection

Hands are considered in horizontal rest position when **ALL** conditions are met:

1. **Both forearms are horizontal**: The angle from elbow to wrist is parallel to the bottom of the frame
   - Left forearm: `abs(left_elbow.y - left_wrist.y) < threshold`
   - Right forearm: `abs(right_elbow.y - right_elbow.y) < threshold`

2. **Hands are separated**: X-coordinate distance > minimum (default: 0.15)

3. **Hands are not raised**: Wrists are at or below elbow height (not raised near face)
   - Prevents false positives when hands are near face/neck

This accurately detects the typical rest position where:
- Forearms are horizontal (parallel to ground)
- Hands are resting at waist/lap level
- Elbows are at similar height or above wrists

## Usage

### Basic Usage (Horizontal Detection Enabled by Default)

```bash
# Extract active clips with both motion and horizontal idle detection
python sign_activity_detector.py video.mp4 output_clips/ --threshold 0.02
```

### Disable Horizontal Idle Detection

```bash
# Use only motion threshold (old behavior)
python sign_activity_detector.py video.mp4 output_clips/ --no-horizontal-idle
```

### Adjust Horizontal Detection Sensitivity

```bash
# Fine-tune horizontal detection parameters
python sign_activity_detector.py video.mp4 output_clips/ \
    --threshold 0.02 \
    --horizontal-y-threshold 0.12 \      # Stricter horizontal alignment (default: 0.15)
    --horizontal-min-distance 0.20       # Require wider hand separation (default: 0.15)
```

### Visualization

When using `--visualize`, the status display shows:
- **ACTIVE SIGNING** (Green) - Active signing detected
- **IDLE (Horizontal Hands)** (Orange) - Horizontal rest position detected
- **IDLE (Low Motion)** (Gray) - Low motion detected

```bash
# Visualize with horizontal idle detection
python sign_activity_detector.py video.mp4 output_clips/ \
    --visualize \
    --threshold 0.02
```

## Command-Line Options

### New Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--no-horizontal-idle` | flag | False | Disable horizontal hands detection |
| `--horizontal-y-threshold` | float | 0.15 | Max Y difference for horizontal detection (0-1) |
| `--horizontal-min-distance` | float | 0.15 | Min X distance between hands (0-1) |

### Coordinate System

- All coordinates are normalized (0.0 to 1.0)
- `horizontal-y-threshold`: 0.15 = hands within 15% of frame height
- `horizontal-min-distance`: 0.15 = hands at least 15% of frame width apart

## Examples

### Conservative Detection (Less Idle Filtering)

```bash
# Only mark as idle if hands are very close to horizontal
python sign_activity_detector.py video.mp4 output/ \
    --horizontal-y-threshold 0.08 \      # Very strict horizontal alignment
    --horizontal-min-distance 0.20       # Wider separation required
```

### Aggressive Detection (More Idle Filtering)

```bash
# Mark as idle even with less perfect horizontal alignment
python sign_activity_detector.py video.mp4 output/ \
    --horizontal-y-threshold 0.25 \      # Allow more variation
    --horizontal-min-distance 0.10       # Allow closer hands
```

### Analysis Only

```bash
# Analyze impact of horizontal detection without extracting clips
python sign_activity_detector.py video.mp4 output/ \
    --analyze-only \
    --threshold 0.02
```

Compare with:

```bash
# Without horizontal detection
python sign_activity_detector.py video.mp4 output/ \
    --analyze-only \
    --threshold 0.02 \
    --no-horizontal-idle
```

## Integration with Existing Features

### Works With All Features

- ✓ Motion threshold (`--threshold`)
- ✓ Minimum duration (`--min-duration`)
- ✓ Visualization (`--visualize`)
- ✓ Save visualization (`--save-visualization`)
- ✓ Analyze only mode (`--analyze-only`)

### Code Integration

```python
from sign_activity_detector import SignActivityDetector

# Enable horizontal idle detection
detector = SignActivityDetector(
    motion_threshold=0.02,
    min_active_duration=2.0,
    detect_horizontal_idle=True,           # Enable horizontal detection
    horizontal_y_threshold=0.15,           # Y alignment tolerance
    horizontal_min_distance=0.15           # Min X distance
)

analysis = detector.analyze_video('video.mp4')
clips = detector.extract_active_clips('video.mp4', 'output/', analysis)
```

## Benefits

1. **Better Idle Detection**: Catches rest positions that might have small motion
2. **Non-Destructive**: Adds to existing motion detection, doesn't replace it
3. **Configurable**: Can be disabled or tuned per video
4. **Visual Feedback**: Shows reason for idle classification in visualization

## Technical Details

### Implementation

The detection is implemented in `_is_horizontal_idle_position()` method which:
1. Checks if both pose landmarks (elbows) and hand landmarks (wrists) are detected
2. Extracts elbow positions from pose landmarks (indices 13=left, 14=right)
3. Extracts wrist positions from hand landmarks (index 0)
4. Calculates if each forearm is horizontal: `abs(elbow.y - wrist.y) < threshold`
5. Verifies hands are separated horizontally: `abs(left_wrist.x - right_wrist.x) > min_distance`
6. Checks hands are not raised above elbows: `wrist.y >= elbow.y - 0.1`
7. Returns True only if ALL conditions are met

This prevents false positives such as:
- Hands raised near face (as shown in your second image)
- Hands positioned vertically or diagonally
- One hand horizontal while other is not

### Activity Logic

```python
# In analyze_video() method:
is_horizontal_idle = self._is_horizontal_idle_position(hand_results)
is_active = smoothed_energy > self.motion_threshold and not is_horizontal_idle
```

This means:
- High motion + horizontal hands = IDLE (rest position with breathing/small movements)
- High motion + non-horizontal hands = ACTIVE (actual signing)
- Low motion + any hand position = IDLE (static or not signing)

## Troubleshooting

### Too Many Frames Marked Idle

Increase Y threshold or decrease min distance:
```bash
--horizontal-y-threshold 0.20 --horizontal-min-distance 0.10
```

### Not Enough Idle Detection

Decrease Y threshold or increase min distance:
```bash
--horizontal-y-threshold 0.10 --horizontal-min-distance 0.20
```

### Disable If Not Needed

```bash
--no-horizontal-idle
```
