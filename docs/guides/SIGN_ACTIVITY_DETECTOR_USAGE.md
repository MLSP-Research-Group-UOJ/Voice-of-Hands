# Sign Activity Detector - Usage Guide

**Script**: `sign_activity_detector.py`  
**Purpose**: Detect active signing vs idle periods using MediaPipe, extract active clips with audio

---

## Features

✅ **MediaPipe-based Motion Detection** - Tracks hand and body landmarks to detect signing activity  
✅ **Active/Idle Segmentation** - Automatically identifies when the signer is actively signing  
✅ **Audio Preservation** - Extracts clips with synchronized audio  
✅ **Real-time Visualization** - Shows landmarks, motion graph, and activity status  
✅ **Save Visualization Video** - Record the detection process with annotations  

---

## Basic Usage

### 1. Analyze Only (No Extraction)
```bash
python sign_activity_detector.py input_video.mp4 output_dir/ --analyze-only
```
- Creates `motion_analysis.json` with detected segments
- No video clips extracted

### 2. Extract Active Clips (with Audio)
```bash
python sign_activity_detector.py input_video.mp4 output_dir/
```
- Extracts only active signing segments as separate clips
- **Audio is automatically included** in each clip
- Saves metadata JSON

### 3. Live Visualization
```bash
python sign_activity_detector.py input_video.mp4 output_dir/ --visualize --analyze-only
```
- Opens window showing:
  - **Top**: Status, motion energy, threshold, hands detected
  - **Middle**: Video with MediaPipe landmarks (pose + hands)
  - **Bottom**: Motion energy graph over time
- **Controls**:
  - Press **'p'** to pause/resume
  - Press **'q'** to quit

### 4. Save Visualization Video
```bash
python sign_activity_detector.py input_video.mp4 output_dir/ \
  --save-visualization visualization_output.mp4 \
  --analyze-only
```
- Saves the visualization as a video file **with audio**
- Can be used with or without `--visualize` (showing live window)

### 5. Combined: Visualize + Save + Extract
```bash
python sign_activity_detector.py input_video.mp4 output_dir/ \
  --visualize \
  --save-visualization viz.mp4
```
- Shows live visualization
- Saves visualization video with audio
- Extracts active clips with audio

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--threshold` | 0.015 | Motion threshold (lower = more sensitive) |
| `--min-duration` | 1.0 | Minimum active segment duration (seconds) |
| `--min-idle` | 0.5 | Minimum idle gap to split segments (seconds) |
| `--smoothing` | 5 | Motion smoothing window (frames) |
| `--analyze-only` | False | Only analyze, don't extract clips |
| `--visualize` | False | Show live visualization window |
| `--save-visualization` | None | Path to save visualization video |

---

## Examples

### Example 1: Quick Test with Visualization
```bash
python sign_activity_detector.py \
  output_signer_dataset/full_cropped/output_short_sli_cropped.mp4 \
  test_output/ \
  --visualize \
  --threshold 0.02 \
  --min-duration 2.0 \
  --analyze-only
```

### Example 2: Extract Active Clips with Audio
```bash
python sign_activity_detector.py \
  output_signer_dataset/full_cropped/output_short_sli_cropped.mp4 \
  active_signing_clips/ \
  --threshold 0.02 \
  --min-duration 2.0
```
**Output**:
- `active_signing_clips/active_001_10.5s-15.3s.mp4` (with audio)
- `active_signing_clips/active_002_20.1s-25.7s.mp4` (with audio)
- `active_signing_clips/activity_metadata.json`

### Example 3: Save Visualization for Presentation
```bash
python sign_activity_detector.py \
  output_signer_dataset/full_cropped/output_short_sli_cropped.mp4 \
  demo_output/ \
  --save-visualization demo_visualization.mp4 \
  --threshold 0.015 \
  --analyze-only
```
**Output**: `demo_visualization.mp4` - Annotated video showing MediaPipe landmarks and motion detection

---

## Audio Handling

### Active Clips
- **Audio is automatically extracted** from the source video for each active segment
- Uses `ffmpeg` to copy audio streams with timestamps
- Format: AAC codec
- Synchronized with video timestamps

### Visualization Video
- **Audio from source is added** to visualization output
- If audio extraction fails, video is saved without audio (with warning)

---

## Output Files

### Analysis Output
```
output_dir/
├── motion_analysis.json          # Segment timestamps and statistics
└── (clips only if not --analyze-only)
```

### With Clip Extraction
```
output_dir/
├── active_001_10.5s-15.3s.mp4   # Active segment 1 (with audio)
├── active_002_20.1s-25.7s.mp4   # Active segment 2 (with audio)
├── active_003_30.2s-35.8s.mp4   # Active segment 3 (with audio)
└── activity_metadata.json        # Full metadata
```

### Metadata Format
```json
{
  "source_video": "input.mp4",
  "total_duration": 347.0,
  "active_time": 280.5,
  "idle_time": 66.5,
  "hands_detected_pct": 95.3,
  "motion_threshold": 0.015,
  "min_active_duration": 1.0,
  "clips": [
    {
      "path": "output_dir/active_001_10.5s-15.3s.mp4",
      "start": 10.5,
      "end": 15.3,
      "duration": 4.8
    }
  ]
}
```

---

## Troubleshooting

### Audio Not Working
**Problem**: Extracted clips have no audio  
**Solution**: Ensure `ffmpeg` is installed:
```bash
which ffmpeg
# If not found:
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### MediaPipe Import Error
**Problem**: `AttributeError: module 'mediapipe' has no attribute 'solutions'`  
**Solution**: Using MediaPipe 0.10+ (new tasks API), script handles this automatically

### Visualization Window Not Showing
**Problem**: Window doesn't appear  
**Solution**: 
- Check if running in headless environment (use `--save-visualization` instead)
- Try: `export DISPLAY=:0` before running

### Qt Warnings
**Problem**: Lots of `QObject::moveToThread` warnings  
**Solution**: These are harmless, suppress with:
```bash
python sign_activity_detector.py ... 2>&1 | grep -v "QObject"
```

---

## Advanced Tuning

### Adjust Sensitivity
**More sensitive** (detects subtle movements):
```bash
--threshold 0.01 --min-duration 0.5
```

**Less sensitive** (only large movements):
```bash
--threshold 0.03 --min-duration 3.0
```

### For Different Video Types
**Broadcast news** (interpreters pause between segments):
```bash
--threshold 0.015 --min-duration 2.0 --min-idle 1.0
```

**Continuous signing** (minimal pauses):
```bash
--threshold 0.01 --min-duration 0.5 --min-idle 0.3
```

---

## Requirements

- Python 3.7+
- OpenCV (`cv2`)
- MediaPipe 0.10+
- NumPy
- FFmpeg (for audio handling)

Install:
```bash
pip install opencv-python mediapipe numpy
sudo apt-get install ffmpeg
```

---

**Last Updated**: April 14, 2026  
**Version**: 2.0 (with audio support)
