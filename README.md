# Voice-of-Hands: Sign Language Interpreter (SLI) Video Cropping System

**Date**: February 27, 2026  
**Purpose**: Automatically detect and crop sign language interpreter regions from broadcast videos with audio preservation

---

## Quick Start

### Basic Usage

```bash
# Process video with default settings
python quick_start.py input_video.mp4 output_folder

# Process from 8 minutes with larger crop
python quick_start.py input_video.mp4 output_folder \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

---

## System Features

✅ **Automatic Border Detection**: Precisely detects light-colored static borders around interpreters  
✅ **Audio Preservation**: Maintains original audio in cropped videos using ffmpeg  
✅ **Flexible Crop Control**: Adjustable border margin and pixel-level crop adjustment  
✅ **Multiple Output Sizes**: Original, 128×128, or 256×256 resolution  
✅ **Start Time Offset**: Skip intro/non-relevant content  
✅ **Detection Visualization**: Saves sample frames with bounding boxes and parameters  
✅ **Batch Processing**: Process multiple videos at once  

---

## Command Line Options

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `video_path` | string | Path to input video file | `videos/news.mp4` |
| `output_dir` | string | Output folder for results | `output` |
| `--size` | string | Output resolution: `original`, `128`, or `256` | `--size 256` |
| `--border-margin` | float | Border exclusion (0.0-0.5, default: 0.15) | `--border-margin 0.05` |
| `--crop-adjust` | int | Adjust crop size in pixels (±) | `--crop-adjust 20` |
| `--start-time` | float | Start time in seconds | `--start-time 480` |
| `--batch` | flag | Process all videos in folder | `--batch` |

---

## Understanding the Parameters

### Border Margin (Percentage-Based)
Controls how much border to **exclude** during detection.

- `0.05` (5%) → Larger crop, includes more area
- `0.15` (15%) → Default, balanced crop
- `0.20` (20%) → Smaller crop, tighter on interpreter

**Effect**: Lower margin = more context captured

### Crop Adjust (Pixel-Based)
Fine-tunes the final crop size **after** detection.

- **Positive** (+10, +20): Expands crop by N pixels on each side
- **Negative** (-5, -10): Shrinks crop by N pixels on each side
- **Zero** (0): Use exact detected size

**Effect**: Independent of margin, direct pixel control

### Combined Example

```bash
# 5% margin (160×160) + 20px adjust = 200×200 → resize to 256×256
python quick_start.py video.mp4 output \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

Result: 1.28× upscaling (excellent quality for sign language transcription)

---

## Output Structure

```
output_folder/
├── clips/                          # 5-second video clips
│   ├── video_clip_0000.mp4
│   ├── video_clip_0001.mp4
│   └── ...
├── full_cropped/                   # Full cropped video with audio
│   └── video_sli_cropped.mp4
└── previews/                       # Detection visualization
    ├── video_detection.jpg         # Grid of sample frames
    ├── video_detection_frame01.jpg # Individual frame 1
    ├── video_detection_frame02.jpg # Individual frame 2
    └── ...
```

### Detection Preview Images

Each preview frame shows:
- ✅ Green bounding box around detected region
- ✅ Detection method and confidence level
- ✅ Crop size (width × height)
- ✅ Border margin and crop adjust values
- ✅ Frame number and position

---

## Recommended Settings for Sign Language Transcription

### Option 1: High Quality (Recommended)
```bash
python quick_start.py video.mp4 output \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```
- Original: 200×200 pixels
- Final: 256×256 pixels
- Upscaling: 1.28× (minimal quality loss)
- Best for: Training data, high accuracy needed

### Option 2: Balanced
```bash
python quick_start.py video.mp4 output \
    --border-margin 0.10 \
    --crop-adjust 10 \
    --size 256 \
    --start-time 480
```
- Original: 162×162 pixels
- Final: 256×256 pixels
- Upscaling: 1.58×
- Best for: General use, good quality

### Option 3: Compact
```bash
python quick_start.py video.mp4 output \
    --border-margin 0.15 \
    --size 128 \
    --start-time 480
```
- Original: 124×124 pixels
- Final: 128×128 pixels
- Upscaling: 1.03× (minimal)
- Best for: Fast processing, storage optimization

---

## Audio Preservation

The system automatically preserves audio from the original video using ffmpeg:

1. Crops video frames (OpenCV)
2. Extracts audio from original video
3. Combines cropped video + audio (ffmpeg)
4. Outputs final video with synchronized audio

**Requirements**: ffmpeg must be installed
```bash
# Check if ffmpeg is available
ffmpeg -version

# Install on Ubuntu/Debian
sudo apt install ffmpeg

# Install on Conda
conda install -c conda-forge ffmpeg
```

If ffmpeg is not available, videos will be saved without audio.

---

## Batch Processing

Process all videos in a folder:

```bash
python quick_start.py --batch input_videos/ output_dataset
```

This will:
- Find all video files (mp4, avi, mov, mkv)
- Process each video with the same settings
- Organize outputs by video name

---

## Examples

### Example 1: Process parliament video from 8 minutes
```bash
python quick_start.py videos/Parliament_Live_01-12-2025.mp4 output_parliament \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

### Example 2: Quick test with small output
```bash
python quick_start.py videos/test.mp4 output_test \
    --size 128 \
    --start-time 0
```

### Example 3: Maximum quality
```bash
python quick_start.py videos/video.mp4 output_hq \
    --border-margin 0.05 \
    --crop-adjust 30 \
    --size 256 \
    --start-time 0
```

---

## Troubleshooting

### Issue: No audio in output
**Solution**: Install ffmpeg
```bash
conda install -c conda-forge ffmpeg
```

### Issue: Crop too large/small
**Solution**: Adjust parameters
```bash
# Larger crop
--border-margin 0.05 --crop-adjust 20

# Smaller crop
--border-margin 0.20 --crop-adjust -5
```

### Issue: Detection quality low
**Solution**: Check confidence in preview images. Try different detection methods if needed.

---

## File Organization

### Main Files
- `quick_start.py` - Main command-line interface
- `sli_detector.py` - Core detection and cropping engine
- `dataset_utils.py` - Dataset analysis utilities (if exists)

### Archived Files
- `version_01/` - Previous versions and test scripts
  - All test_*.py files
  - Demo scripts
  - Preview generation tools

### Documentation
- `resource_doc/` - Research notes and improvement suggestions
  - `research_improvement_suggestions/` - Q&A and analysis documents

---

## Technical Details

### Detection Method
- **Border Detection**: Analyzes HSV color space to find light-colored static borders
- **Sampling**: Analyzes 50 frames across video for consistency
- **Confidence**: Based on detection stability across frames
- **Fallback**: Uses edge detection if border detection fails

### Video Processing
- **Input**: Any resolution, 25fps standard
- **Codec**: MP4V for video, AAC for audio
- **Interpolation**: INTER_CUBIC for high-quality resizing
- **Frame Skip**: Configurable via start_time parameter

### Performance
- **Processing Speed**: ~100 frames/second on average CPU
- **Memory Usage**: Minimal (frame-by-frame processing)
- **Disk Space**: Depends on output size and clip duration

---

## Support

For issues or questions, check:
1. `resource_doc/` for research notes and recommendations
2. `version_01/` for alternative implementations
3. Generated preview images in `output/previews/` for debugging

---

**System Version**: 1.0  
**Last Updated**: February 27, 2026  
**Requires**: Python 3.10+, OpenCV 4.13+, NumPy 2.2+, ffmpeg (for audio)
