# Sign Language Dataset Collection System

**Focus**: Automated detection and extraction of sign language interpreter regions for dataset creation

---

## Overview

This system automatically detects sign language interpreters in broadcast videos by identifying the **light-colored border** that surrounds their video region, then precisely crops to just the interpreter's visual area for dataset collection.

### Key Feature: Border-Based Detection

Most broadcast videos display sign language interpreters in a **Picture-in-Picture (PiP)** box with a **light-colored static border** (white, light gray, or beige). This system:

1. **Detects the border** - Finds the consistent light-colored rectangle
2. **Extracts the interior** - Crops to the actual interpreter area (excluding border)
3. **Creates dataset** - Segments into training clips

---

## Quick Start

### 1. Setup Environment

```bash
# Activate conda environment
conda activate sli_detector

# Verify installation
python -c "import cv2, numpy; print('✓ Ready')"
```

### 2. Process Video (Assuming video in `videos/` directory)

```bash
# Single video
python quick_start.py videos/your_video.mp4 dataset_output

# All videos in directory
python quick_start.py --batch videos/ dataset_output
```

### 3. Results

```
dataset_output/
├── clips/                    # Training clips (5 seconds each)
├── full_cropped/            # Full video, interpreter only  
├── previews/                # Detection visualization
└── statistics.json          # Dataset metrics
```

---

## Detection Methods

### Primary: Border Detection (Recommended)

**How it works:**
1. Scans corner regions for light-colored rectangles
2. Identifies borders with bright edges and dark interior
3. Extracts the interior region (actual interpreter area)

**Best for:**
- Videos with visible PiP borders (most broadcast content)
- Parliament sessions, news broadcasts
- Any video with consistent colored border

**Usage:**
```python
from sli_detector import SLIDetector

detector = SLIDetector("videos/parliament.mp4")
result = detector.detect(method="border")  # Precise border detection

print(f"Detected region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
print(f"Confidence: {result.confidence:.2f}")
```

### Auto Mode (Default)

Tries border detection first, then falls back to motion/edge if needed.

```python
result = detector.detect(method="auto")  # Smart automatic selection
```

### Fallback Methods

If border detection doesn't work (no visible border):
- **Motion**: Tracks hand movements via optical flow
- **Edge**: Finds rectangular overlays
- **Hybrid**: Combines motion + edge

---

## Precise Cropping

The system crops **exactly the deaf person's visual area** by:

1. **Detecting the border** using color thresholding
2. **Finding the interior region** (excluding border pixels)
3. **Extracting only that area** for clean dataset

### Example

```
Original Frame:          After Border Detection:
┌─────────────────┐     
│                 │     
│    ┏━━━━━┓     │     ┌─────┐  ← Only interpreter
│    ┃ 👤  ┃     │  →  │ 👤  │     (border removed)
│    ┃ 🤚  ┃     │     │ 🤚  │
│    ┗━━━━━┛     │     └─────┘
│                 │     
└─────────────────┘     
```

---

## Usage Examples

### Example 1: Process Parliament Video

```bash
# Download video (if from YouTube)
yt-dlp -f "best[ext=mp4]" -o "videos/%(title)s.%(ext)s" <URL>

# Process with border detection
python quick_start.py videos/Parliament_Live.mp4 parliament_dataset

# Check results
ls parliament_dataset/clips/ | wc -l
```

### Example 2: Custom Python Script

```python
from sli_detector import SLIDetector

# Load video
detector = SLIDetector("videos/signing_video.mp4")

# Detect using border method (most precise)
result = detector.detect(method="border", sample_frames=50)

# Visualize detection
detector.visualize_detection(result, "check_detection.jpg")

# Extract clips (5-second duration)
clips = detector.extract_sli_clips(
    result=result,
    output_dir="my_dataset/clips/",
    clip_duration=5.0,
    overlap=0.5,
    padding=0  # No padding - exact crop
)

print(f"Created {len(clips)} training clips")
```

### Example 3: Fine-tune Border Detection

```python
detector = SLIDetector("videos/video.mp4")

# Try different sample rates
for n_samples in [30, 50, 100]:
    result = detector.detect(method="border", sample_frames=n_samples)
    print(f"{n_samples} frames: confidence={result.confidence:.2f}")

# Use best result
best_result = detector.detect(method="border", sample_frames=100)

# Extract with exact cropping (no padding)
clips = detector.extract_sli_clips(
    result=best_result,
    output_dir="dataset/",
    padding=0  # Exact border crop
)
```

---

## Dataset Quality

### What Gets Extracted

Each clip contains:
- **Duration**: 5 seconds (configurable)
- **Content**: Only the sign language interpreter
- **Quality**: Active signing (static frames filtered)
- **Format**: MP4, same frame rate as source

### Quality Filters

The system automatically:
- ✅ Removes static clips (no signing activity)
- ✅ Validates resolution (not too small)
- ✅ Checks duration (proper length)
- ✅ Filters corrupted frames

### Check Dataset Quality

```bash
# Get statistics
python dataset_utils.py parliament_dataset stats

# Quality report
python dataset_utils.py parliament_dataset quality

# Visual preview
python dataset_utils.py parliament_dataset preview
```

---

## Configuration Parameters

### Detection Parameters

```python
detector.detect(
    method="border",      # "auto", "border", "motion", "edge"
    sample_frames=50      # More = slower but more accurate
)
```

### Clip Extraction Parameters

```python
detector.extract_sli_clips(
    result=result,
    output_dir="clips/",
    clip_duration=5.0,           # Seconds per clip
    overlap=0.5,                 # 0.5 = 50% overlap
    min_motion_threshold=1.0,    # Filter static clips
    padding=0                    # Pixels around region (0=exact)
)
```

**Parameter Guide:**

| Parameter | Recommended | Purpose |
|-----------|-------------|---------|
| `clip_duration` | 3-5 seconds | Gesture/word length |
| `overlap` | 0.3-0.5 | Dataset diversity |
| `min_motion_threshold` | 1.0 | Filter inactive clips |
| `padding` | 0 | Exact crop (no extra) |

---

## Troubleshooting

### Issue: Border Not Detected

**Symptom**: Low confidence or wrong region

**Solutions:**

1. **Check if border exists:**
   ```bash
   # Open video and visually verify border
   vlc videos/your_video.mp4
   ```

2. **Try more sample frames:**
   ```python
   result = detector.detect(method="border", sample_frames=100)
   ```

3. **Visualize detection:**
   ```python
   detector.visualize_detection(result, "debug.jpg")
   # Check debug.jpg to see what was detected
   ```

4. **Use fallback method:**
   ```python
   # If no border, use motion or edge
   result = detector.detect(method="motion")
   ```

### Issue: Wrong Area Cropped

**Solution: Manual specification**

```python
from sli_detector import DetectionResult

# Inspect video first to find exact coordinates
# Then specify manually:
custom_result = DetectionResult(
    x1=920,   # Your coordinates
    y1=450,
    x2=1250,
    y2=690,
    confidence=1.0,
    method="manual"
)

# Use for extraction
clips = detector.extract_sli_clips(custom_result, "output/")
```

### Issue: Clips Include Border

**Solution: Reduce padding**

```python
# Exact crop, no extra pixels
clips = detector.extract_sli_clips(
    result=result,
    padding=0  # No padding around detected region
)

# Or negative padding to crop inward
clips = detector.extract_sli_clips(
    result=result,
    padding=-5  # Crop 5 pixels inside border
)
```

---

## Best Practices

### 1. Verify Detection First

```python
# Always visualize before full extraction
detector.visualize_detection(result, "verify.jpg")
# Open verify.jpg and check if detection is correct
```

### 2. Start with Border Method

```python
# Border detection is most precise for broadcast videos
result = detector.detect(method="border")

if result.confidence < 0.5:
    # Fallback to auto mode
    result = detector.detect(method="auto")
```

### 3. Use Exact Cropping

```python
# For dataset collection, avoid padding
clips = detector.extract_sli_clips(
    result=result,
    padding=0  # Exact interpreter area only
)
```

### 4. Quality Check

```bash
# Always check your dataset
python dataset_utils.py output_dataset quality

# Review statistics
cat output_dataset/statistics.json | python -m json.tool
```

---

## Workflow for Dataset Collection

### Step-by-Step Process

```bash
# 1. Setup
conda activate sli_detector
cd "/path/to/Voice-of-Hands"

# 2. Download videos (if needed)
mkdir -p videos
yt-dlp -f "best[ext=mp4]" -o "videos/%(title)s.%(ext)s" <URL>

# 3. Process all videos
python quick_start.py --batch videos/ raw_dataset

# 4. Quality check
python dataset_utils.py raw_dataset quality

# 5. Organize for training
python -c "
from pathlib import Path
import shutil, random

clips = list(Path('raw_dataset/clips').glob('*.mp4'))
random.shuffle(clips)

# Split 70/15/15
splits = {
    'train': clips[:int(len(clips)*0.7)],
    'val': clips[int(len(clips)*0.7):int(len(clips)*0.85)],
    'test': clips[int(len(clips)*0.85):]
}

for split, files in splits.items():
    Path(f'final_dataset/{split}').mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy(f, f'final_dataset/{split}/{f.name}')
    print(f'{split}: {len(files)} clips')
"

# 6. Your dataset is ready!
ls final_dataset/train/ | wc -l
```

---

## Expected Results

### Parliament Live Example (59 minutes)

**Input:**
- 1 video with light border around interpreter
- Resolution: 1280×720
- Interpreter in bottom-right corner

**Output:**
- **732 clips** extracted
- **Resolution**: 352×258 (interpreter only)
- **Duration**: 5 seconds each
- **Total data**: 1.02 hours
- **Size**: 200 MB
- **Quality**: 100% usable

---

## Command Reference

### Essential Commands

```bash
# Setup (one-time)
conda activate sli_detector

# Process video
python quick_start.py videos/video.mp4 output

# Batch process
python quick_start.py --batch videos/ output

# Check quality
python dataset_utils.py output stats
python dataset_utils.py output quality

# View results
ls output/clips/
du -sh output/
```

### Python API

```python
from sli_detector import SLIDetector

# Load and detect
detector = SLIDetector("videos/video.mp4")
result = detector.detect(method="border")

# Visualize
detector.visualize_detection(result, "check.jpg")

# Extract clips
clips = detector.extract_sli_clips(
    result=result,
    output_dir="dataset/clips/",
    clip_duration=5.0,
    padding=0
)

# Save full cropped video
detector.crop_and_save_sli(
    result=result,
    output_path="dataset/full.mp4",
    padding=0
)
```

---

## Summary

This system provides:

✅ **Precise border detection** - Identifies light-colored borders automatically  
✅ **Exact cropping** - Extracts only the interpreter visual area  
✅ **Dataset generation** - Creates training-ready clips  
✅ **Quality control** - Filters and validates clips  
✅ **Batch processing** - Handle multiple videos efficiently  

**Result**: Clean, high-quality sign language interpreter datasets ready for training recognition models.

---

**For detailed technical documentation**: See `IMPLEMENTATION_GUIDE.md`  
**For troubleshooting**: See `QUICK_REFERENCE.md`  
**For examples**: See `example_extract_sli.py`

---

*Focus: Dataset Collection | Method: Border Detection | Goal: Precise Interpreter Extraction*
