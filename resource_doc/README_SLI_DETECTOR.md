# Sign Language Interpreter Detection & Dataset Creation

A comprehensive system for automatically detecting, cropping, and extracting sign language interpreter (SLI) regions from broadcast news videos. Built with state-of-the-art 2026 computer vision techniques.

## 🎯 Features

- **Multi-Method Detection**: Motion heatmaps, edge detection, pose estimation, and hybrid approaches
- **Automatic Cropping**: Precisely extract SLI regions with configurable padding
- **Dataset Creation**: Generate training datasets with automatic clip segmentation
- **Quality Control**: Built-in tools for analyzing and validating datasets
- **Batch Processing**: Process multiple videos efficiently
- **Temporal Consistency**: Smooth detection across frames
- **Motion Filtering**: Automatically filter static/inactive clips

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install opencv-python numpy

# Optional: For pose-based detection
pip install mediapipe
```

### Basic Usage

```python
from sli_detector import process_video_for_dataset

# Process a single video
results = process_video_for_dataset(
    video_path="news_video.mp4",
    output_dir="dataset/output",
    clip_duration=5.0,
    detection_method="auto"
)

print(f"Extracted {len(results['clips'])} clips")
```

## 📚 Documentation

### Detection Methods

#### 1. **Motion Heatmap** (Recommended for most cases)
Uses optical flow to identify regions with high-frequency motion (signing hands).

```python
detector = SLIDetector("video.mp4")
result = detector.detect(method="motion", sample_frames=50)
```

**Best for**: Videos with static backgrounds, clear separation between interpreter and news anchor.

#### 2. **Edge Detection**
Identifies rectangular overlays/boxes in corners using edge analysis.

```python
result = detector.detect(method="edge", sample_frames=50)
```

**Best for**: Videos with visible PiP borders, consistent screen layouts.

#### 3. **Pose-Based** (Requires MediaPipe)
Detects humans and filters for small persons in corners with visible hand keypoints.

```python
result = detector.detect(method="pose", sample_frames=30)
```

**Best for**: High-quality videos, when interpreter is clearly visible.

#### 4. **Hybrid** (Auto mode)
Combines motion detection with edge detection fallback.

```python
result = detector.detect(method="auto")  # or method="hybrid"
```

**Best for**: Unknown video types, maximum robustness.

### Core Functions

#### `process_video_for_dataset()`
Complete pipeline for single video processing.

```python
results = process_video_for_dataset(
    video_path="input.mp4",
    output_dir="dataset/output",
    detection_method="auto",          # auto, motion, edge, pose, hybrid
    clip_duration=5.0,                # seconds per clip
    min_confidence=0.5,               # minimum detection confidence
    save_full_video=True,             # save full cropped video
    create_preview=True               # create detection visualization
)
```

**Returns:**
```python
{
    'video_path': 'input.mp4',
    'detection': {
        'bbox': (x1, y1, x2, y2),
        'confidence': 0.85,
        'method': 'motion'
    },
    'clips': ['clip_0001.mp4', 'clip_0002.mp4', ...],
    'full_video': 'cropped_full.mp4',
    'preview': 'detection.jpg'
}
```

#### `batch_process_videos()`
Process multiple videos in batch.

```python
results = batch_process_videos(
    video_paths=['video1.mp4', 'video2.mp4', ...],
    output_base_dir="dataset/batch",
    detection_method="auto",
    clip_duration=5.0,
    save_full_videos=False
)
```

#### `SLIDetector` Class
Low-level API for custom pipelines.

```python
detector = SLIDetector("video.mp4")

# Detect region
result = detector.detect(method="auto")

# Crop and save full video
detector.crop_and_save_sli(
    result=result,
    output_path="output.mp4",
    padding=10,
    start_time=0,
    duration=30  # extract first 30 seconds
)

# Extract clips
clips = detector.extract_sli_clips(
    result=result,
    output_dir="clips/",
    clip_duration=4.0,
    overlap=0.5,
    min_motion_threshold=2.0
)

# Visualize detection
detector.visualize_detection(result, "preview.jpg")
```

## 📊 Dataset Management

### Analyze Dataset

```bash
python dataset_utils.py dataset/output stats
```

**Output:**
```
DATASET STATISTICS
══════════════════════════════════════════════════════════════
📊 General Information:
  Total clips: 348
  Total duration: 29.0 minutes
  Total size: 1.23 GB
  Average file size: 3.61 MB
  
🎬 Resolutions:
  320x240: 348 clips (100.0%)
  
⚡ Frame Rates:
  25 FPS: 348 clips (100.0%)
══════════════════════════════════════════════════════════════
```

### Quality Check

```bash
python dataset_utils.py dataset/output quality
```

Checks for:
- Resolution too small
- Duration too short/long
- Corrupted files
- Low motion (static clips)

### Find Duplicates

```bash
python dataset_utils.py dataset/output duplicates
```

### Create Preview Grid

```bash
python dataset_utils.py dataset/output preview
```

Creates a visual grid of sample frames from your dataset.

## 🎬 Example Workflows

### Workflow 1: Quick Dataset Creation

```python
from sli_detector import batch_process_videos
import glob

# Find all videos
videos = glob.glob("raw_videos/*.mp4")

# Process all
results = batch_process_videos(
    video_paths=videos,
    output_base_dir="dataset",
    clip_duration=5.0
)

print(f"Created dataset with {sum(len(r['clips']) for r in results)} clips")
```

### Workflow 2: Custom Processing

```python
from sli_detector import SLIDetector

detector = SLIDetector("news_video.mp4")

# Try all methods and pick best
methods = ["motion", "edge", "hybrid"]
results = [detector.detect(method=m) for m in methods]
best = max(results, key=lambda r: r.confidence)

print(f"Best method: {best.method} (confidence: {best.confidence:.2f})")

# Extract with custom parameters
clips = detector.extract_sli_clips(
    result=best,
    output_dir="custom_clips/",
    clip_duration=3.0,
    overlap=0.3,
    min_motion_threshold=1.5,
    padding=15
)
```

### Workflow 3: Specific Time Ranges

```python
detector = SLIDetector("long_video.mp4")
result = detector.detect(method="auto")

# Extract multiple segments
segments = [
    ("intro", 0, 30),
    ("main", 60, 180),
    ("outro", 240, 270)
]

for name, start, end in segments:
    detector.crop_and_save_sli(
        result=result,
        output_path=f"segments/{name}.mp4",
        start_time=start,
        duration=end - start
    )
```

## 🔧 Advanced Configuration

### Detection Parameters

```python
# Fine-tune detection
result = detector.detect(
    method="motion",
    sample_frames=100  # More frames = better accuracy, slower
)
```

### Clip Extraction Parameters

```python
clips = detector.extract_sli_clips(
    result=result,
    output_dir="clips/",
    clip_duration=5.0,           # Length of each clip
    overlap=0.5,                 # 50% overlap between clips
    min_motion_threshold=1.0,    # Filter static clips
    padding=10                   # Pixels around detected region
)
```

### Quality Control Thresholds

```python
from dataset_utils import DatasetAnalyzer

analyzer = DatasetAnalyzer("dataset/")
report = analyzer.check_quality(
    min_resolution=(200, 200),   # Minimum size
    min_duration=1.0,            # Minimum length
    max_duration=30.0            # Maximum length
)
```

## 📁 Output Structure

```
dataset/
├── clips/                      # Short video clips
│   ├── video1_clip_0001.mp4
│   ├── video1_clip_0002.mp4
│   └── ...
├── full_cropped/              # Full cropped videos (optional)
│   └── video1_sli_cropped.mp4
├── previews/                  # Detection visualizations
│   └── video1_detection.jpg
├── preview_grid.jpg           # Dataset sample grid
└── statistics.json            # Dataset statistics
```

## 🎓 Technical Details

### Detection Pipeline

1. **Sampling**: Uniformly sample N frames from video
2. **Feature Extraction**: 
   - Motion: Optical flow (Farneback)
   - Edge: Canny edge detection
   - Pose: MediaPipe keypoint detection
3. **Region Proposal**: Focus on corner regions (typical SLI locations)
4. **Scoring**: Rank regions by motion, edge density, or pose confidence
5. **Refinement**: Select most consistent region across frames

### Motion Detection Details

- Uses dense optical flow (Farneback algorithm)
- Accumulates motion magnitude over sampled frames
- Creates motion heatmap highlighting active regions
- Finds contours in high-motion areas
- Scores by motion intensity × area

### Edge Detection Details

- Applies Canny edge detection
- Accumulates edges over frames for temporal consistency
- Finds rectangular contours in corner regions
- Filters by aspect ratio (sign language boxes are typically portrait/square)
- Scores by edge density × area

### Pose Detection Details

- Uses MediaPipe Pose (lightweight model for speed)
- Detects all humans in frame
- Filters for:
  - Small bounding box (<30% of screen height)
  - Corner location
  - Visible wrists (key indicator of signing)
- Calculates median bounding box across frames

## 🐛 Troubleshooting

### Low Detection Confidence

```python
# Try different methods
for method in ["motion", "edge", "hybrid", "pose"]:
    result = detector.detect(method=method)
    print(f"{method}: {result.confidence:.2f}")
```

### No Clips Generated

Check motion threshold:
```python
# Lower threshold to include more clips
clips = detector.extract_sli_clips(
    result=result,
    min_motion_threshold=0.5  # Lower = more permissive
)
```

### Incorrect Region Detected

Visualize to debug:
```python
# Create preview to see what was detected
detector.visualize_detection(result, "debug_preview.jpg")
```

### Out of Memory

Process in batches:
```python
# Sample fewer frames
result = detector.detect(sample_frames=20)  # Default: 50
```

## 📖 References

This implementation is based on state-of-the-art techniques as of 2026:

1. **Optical Flow**: Farneback, G. (2003). Two-Frame Motion Estimation Based on Polynomial Expansion.
2. **Pose Estimation**: MediaPipe Pose (Google Research, 2020-2023 updates)
3. **Sign Language Detection**: Various CVPR/ICCV papers on SLI localization (2020-2026)

## 📝 Citation

If you use this code in your research, please cite:

```bibtex
@software{sli_detector_2026,
  title={Sign Language Interpreter Detection and Dataset Creation},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/voice-of-hands}
}
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add YOLO-based detection for even better accuracy
- [ ] Implement RTMPose for faster pose estimation
- [ ] Add support for stereo/3D video
- [ ] Multi-language subtitle detection
- [ ] Real-time processing mode

## 📄 License

MIT License - feel free to use in your research and projects.

## 🙏 Acknowledgments

Built with:
- OpenCV (computer vision)
- NumPy (numerical computing)
- MediaPipe (pose estimation)

---

**Need help?** Open an issue or contact: [your-email@example.com]

**Dataset ready?** Start training your sign language recognition model! 🎉
