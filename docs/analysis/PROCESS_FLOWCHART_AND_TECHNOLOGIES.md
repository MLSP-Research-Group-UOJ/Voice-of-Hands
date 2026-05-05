# Sign Language Interpreter Detection System
## Complete Process Flowchart & Technology Stack

**Date**: March 17, 2026  
**Document**: Technical Process Flow with Detailed Methodology

---

## 📊 Process Overview Flowchart

```
Input Video → Detection → Parameter Application → Cropping → 
Segmentation → Quality Control → Dataset Output
```

---

## 🔍 Detailed Process Steps with Technologies

### STEP 1: Input & Initialization

**Input**: Broadcast video (News/Parliament) containing Sign Language Interpreter (SLI) in corner

**Technology Stack**:
- **OpenCV VideoCapture**: Video file I/O and frame extraction
- **Python**: Core programming language
- **NumPy**: Array operations and numerical processing

**Process**:
```python
cap = cv2.VideoCapture(video_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
```

**Output**: Video metadata (resolution, FPS, duration, frame count)

---

### STEP 2: Detection Methods (Multi-Approach)

The system uses **Auto Detection Mode** that tries multiple methods in order of precision:

#### 2.1 Border Detection Method (Primary) ⭐

**Purpose**: Detect light-colored static borders around the interpreter (most common in broadcast videos)

**Technologies**:
- **HSV Color Space** (Hue-Saturation-Value)
- **Color Thresholding** (cv2.inRange)
- **Morphological Operations** (Opening/Closing)
- **Contour Analysis** (cv2.findContours)

**Methodology**:
1. Convert frame from BGR to HSV color space
   ```python
   hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
   ```

2. Define light color range (white, light gray, beige borders)
   ```python
   lower_light = np.array([0, 0, 180])     # High value (brightness)
   upper_light = np.array([180, 80, 255])  # Low saturation
   ```

3. Create binary mask of light-colored areas
   ```python
   mask = cv2.inRange(hsv, lower_light, upper_light)
   ```

4. Apply morphological operations to clean noise
   ```python
   kernel = np.ones((3, 3), np.uint8)
   mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
   mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
   ```

5. Find contours and detect rectangles with dark interior
6. Extract interior region using configurable border margin (5-15%)
   ```python
   interior_x1 = bx + int(bw * border_margin)  # e.g., 0.05 = 5%
   interior_y1 = by + int(bh * border_margin)
   interior_x2 = bx + int(bw * (1.0 - border_margin))
   interior_y2 = by + int(bh * (1.0 - border_margin))
   ```

**Confidence Threshold**: 0.25+ triggers success  
**Best For**: Videos with visible colored borders around interpreter box

---

#### 2.2 Motion Analysis Method (Fallback 1)

**Purpose**: Identify regions with high-frequency motion characteristic of signing hands

**Technologies**:
- **Optical Flow** (Farneback Algorithm)
- **Motion Accumulation** (Temporal heatmap)
- **Statistical Analysis** (Percentile thresholding)

**Methodology**:
1. Convert frames to grayscale
2. Calculate dense optical flow between consecutive frames
   ```python
   flow = cv2.calcOpticalFlowFarneback(
       prev_gray, gray,
       None,
       pyr_scale=0.5,      # Image pyramid scale
       levels=3,            # Number of pyramid layers
       winsize=15,          # Averaging window size
       iterations=3,        # Iterations at each pyramid level
       poly_n=5,            # Pixel neighborhood size
       poly_sigma=1.2,      # Gaussian standard deviation
       flags=0
   )
   ```

3. Calculate motion magnitude from flow vectors
   ```python
   magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
   ```

4. Accumulate motion over multiple frames (50+ samples)
5. Create motion heatmap showing areas of consistent movement
6. Apply threshold and find motion hotspots in corner regions
7. Score based on motion intensity × area size

**Confidence Threshold**: 0.6+ triggers success  
**Best For**: Videos with active signing, good lighting, minimal camera movement

---

#### 2.3 Edge Detection Method (Fallback 2)

**Purpose**: Find rectangular overlays using edge features

**Technologies**:
- **Canny Edge Detector**
- **Contour Detection & Approximation**
- **Shape Analysis** (Polygon approximation, aspect ratio)

**Methodology**:
1. Convert frames to grayscale
2. Apply Canny edge detection
   ```python
   edges = cv2.Canny(gray, 50, 150)
   ```

3. Accumulate edges over multiple frames
   ```python
   edge_accumulator += edges.astype(np.float32)
   ```

4. Normalize and create edge persistence map
5. Find contours in corner regions
6. Approximate contours to polygons
   ```python
   epsilon = 0.02 * cv2.arcLength(cnt, True)
   approx = cv2.approxPolyDP(cnt, epsilon, True)
   ```

7. Filter for rectangular shapes (4+ corners)
8. Validate aspect ratio (0.8 - 2.0 for portrait/square)
9. Score based on edge density × area

**Best For**: Picture-in-picture overlays with clear borders, static frames

---

#### 2.4 Pose Detection Method (Optional)

**Purpose**: Detect human poses with visible hand/arm movements

**Technologies**:
- **MediaPipe Pose** (Google's ML framework)
- **33 Body Keypoints Detection**
- **Landmark Visibility Scoring**

**Methodology**:
1. Initialize MediaPipe Pose detector
   ```python
   mp_pose = mp.solutions.pose
   pose = mp_pose.Pose(
       static_image_mode=False,
       model_complexity=0,  # Fastest model
       min_detection_confidence=0.5
   )
   ```

2. Convert frame to RGB and process
3. Extract 33 body landmarks (shoulders, elbows, wrists, etc.)
4. Calculate bounding box from keypoint coordinates
5. Check conditions:
   - Small person (< 30% of frame height)
   - Located in corner region
   - Both wrists visible (visibility > 0.5)
6. Aggregate detections across frames for consistency

**Best For**: High-quality videos, clear subject visibility, requires MediaPipe installation

---

### STEP 3: Parameter Application

**Purpose**: Fine-tune the detected region based on user preferences

**Parameters**:

1. **Border Margin** (0.0 - 0.5)
   - Controls how much border to exclude during detection
   - Lower value (0.05 = 5%) → Larger crop area
   - Higher value (0.15 = 15%) → Tighter crop
   - Applied during border detection phase

2. **Crop Adjust** (± pixels)
   - Expands or shrinks final crop size
   - Positive (+10, +20) → Expand by N pixels on each side
   - Negative (-5, -10) → Shrink by N pixels on each side
   - Applied after detection, before cropping

3. **Start Time** (seconds)
   - Skip intro/non-relevant content
   - Useful for skipping opening sequences
   - Example: `--start-time 480` = start at 8 minutes

**Calculation**:
```python
# Apply crop adjustment
final_x1 = detected_x1 - crop_adjust
final_y1 = detected_y1 - crop_adjust
final_x2 = detected_x2 + crop_adjust
final_y2 = detected_y2 + crop_adjust

# Clamp to frame boundaries
final_x1 = max(0, final_x1)
final_y1 = max(0, final_y1)
final_x2 = min(frame_width, final_x2)
final_y2 = min(frame_height, final_y2)
```

---

### STEP 4: Video Cropping

**Purpose**: Extract only the interpreter region while preserving audio

**Technology**: **FFmpeg** (via subprocess calls)

**Methodology**:
1. Build FFmpeg command with crop filter
   ```python
   crop_filter = f"crop={width}:{height}:{x1}:{y1}"
   ```

2. Execute FFmpeg with audio copy
   ```bash
   ffmpeg -i input.mp4 \
          -ss start_time \
          -vf "crop=width:height:x:y" \
          -c:a copy \
          -preset fast \
          output.mp4
   ```

3. Preserve original audio stream (no re-encoding)
4. Use fast preset for speed optimization

**Options**:
- **Full Video**: Entire video cropped to SLI region
- **Clip Segmentation**: Split into 5-second chunks

---

### STEP 5: Clip Segmentation

**Purpose**: Create training-friendly 5-second video clips

**Technology Stack**:
- **FFmpeg**: Clip extraction with precise timestamps
- **Python subprocess**: Automation

**Methodology**:
1. Calculate total clips based on video duration
   ```python
   num_clips = int(video_duration / clip_duration)
   ```

2. Optional overlap for better coverage
   ```python
   step = clip_duration * (1 - overlap_ratio)
   ```

3. Extract each clip with timestamp
   ```bash
   ffmpeg -i input.mp4 \
          -ss start_time \
          -t duration \
          -vf "crop=..." \
          -c:a copy \
          clip_0001.mp4
   ```

4. Sequential naming: `video_clip_0000.mp4`, `video_clip_0001.mp4`, etc.

**Default Settings**:
- Clip duration: 5 seconds
- Overlap: 0% (no overlap)
- Audio: Preserved in each clip

---

### STEP 6: Resizing (Optional)

**Purpose**: Standardize output resolution for training

**Technology**: **OpenCV cv2.resize()**

**Methodology**:
```python
if output_size == "128":
    resized = cv2.resize(frame, (128, 128), interpolation=cv2.INTER_AREA)
elif output_size == "256":
    resized = cv2.resize(frame, (256, 256), interpolation=cv2.INTER_AREA)
```

**Interpolation Method**: `cv2.INTER_AREA`
- Best for downsampling
- Produces sharp, anti-aliased results
- Preserves sign language details

**Upscaling Impact**:
| Original Size | Target Size | Scale Factor | Quality |
|---------------|-------------|--------------|---------|
| 124×124 | 256×256 | 2.06× | Moderate blur |
| 160×160 | 256×256 | 1.60× | Acceptable |
| 180×180 | 256×256 | 1.42× | Good quality |
| 200×200 | 256×256 | 1.28× | Excellent |

---

### STEP 7: Quality Filtering

**Purpose**: Ensure only high-quality clips enter the dataset

**Technology**: Custom validation algorithms

**Quality Checks**:

#### 7.1 Duration Validation
```python
if clip_duration < min_duration or clip_duration > max_duration:
    return False  # Discard
```
- Ensures clips are valid length (e.g., 4.8 - 5.2 seconds)

#### 7.2 Motion Validation
```python
frame_diff = cv2.absdiff(frame1, frame2)
motion_score = np.mean(frame_diff)
if motion_score < threshold:
    return False  # Static clip, discard
```
- Filters out static/frozen frames
- Ensures active signing is present

#### 7.3 Resolution Check
```python
if width < min_width or height < min_height:
    return False  # Too small
```
- Ensures minimum quality standards

#### 7.4 File Integrity
```python
cap = cv2.VideoCapture(clip_path)
if not cap.isOpened():
    return False  # Corrupted file
```
- Validates file can be opened
- Checks for corruption

---

### STEP 8: Statistics Generation

**Purpose**: Create metadata and analysis for the dataset

**Technology**: JSON serialization, Python statistics

**Metrics Collected**:
```python
{
    "total_clips": 732,
    "total_duration_seconds": 3660,
    "total_duration_formatted": "1h 1m 0s",
    "total_size_mb": 200.5,
    "average_clip_size_mb": 0.27,
    "resolution": "352x258",
    "good_clips": 732,
    "bad_clips": 0,
    "quality_rate": 100.0,
    "detection_method": "border",
    "detection_confidence": 0.85
}
```

**Output**: `statistics.json` file with complete dataset metadata

---

### STEP 9: Preview Generation

**Purpose**: Visualize detection results and dataset samples

**Technology Stack**:
- **OpenCV**: Image manipulation, drawing
- **PIL/Pillow**: Grid creation (optional)
- **Matplotlib**: Color palettes (optional)

**Previews Created**:

#### 9.1 Detection Visualization
- Sample frames with bounding boxes overlaid
- Shows detected region in red rectangle
- Displays confidence score and method used

```python
cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
cv2.putText(frame, f"Method: {method}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
```

#### 9.2 Grid Preview
- Mosaic of multiple sample clips
- Visual overview of dataset variety
- Arranged in NxN grid (e.g., 5×5)

#### 9.3 Individual Frame Samples
- First frame from multiple clips
- Useful for quick quality assessment

---

### STEP 10: Output Structure

**Purpose**: Organize dataset in standard format

**Directory Structure**:
```
output_dataset/
├── clips/                          # 🎯 Training Data
│   ├── video_clip_0000.mp4
│   ├── video_clip_0001.mp4
│   ├── video_clip_0002.mp4
│   └── ... (732 files)
│
├── full_cropped/                   # Full Video
│   └── video_sli_cropped.mp4
│
├── previews/                       # Visualizations
│   ├── video_detection.jpg         # Grid of detection frames
│   ├── video_detection_frame01.jpg
│   ├── video_detection_frame02.jpg
│   └── video_detection_frame03.jpg
│
├── preview_grid.jpg                # Dataset overview mosaic
└── statistics.json                 # Metadata and metrics
```

**File Formats**:
- Video: MP4 (H.264 codec)
- Images: JPEG
- Metadata: JSON

---

## 🛠️ Complete Technology Stack Summary

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core programming language |
| **OpenCV** | 4.13.0+ | Computer vision, video processing |
| **NumPy** | 2.2.6+ | Numerical computing, arrays |
| **FFmpeg** | 8.0+ | Video encoding, cropping, audio |
| **MediaPipe** | 0.10.32+ | Pose estimation (optional) |

### Computer Vision Algorithms

| Algorithm | Implementation | Use Case |
|-----------|---------------|----------|
| **HSV Color Space** | cv2.cvtColor | Color-based border detection |
| **Morphological Operations** | cv2.morphologyEx | Noise reduction, shape refinement |
| **Optical Flow** | cv2.calcOpticalFlowFarneback | Motion analysis |
| **Edge Detection** | cv2.Canny | Contour finding |
| **Contour Analysis** | cv2.findContours | Shape detection |
| **Pose Estimation** | MediaPipe Pose | Human body keypoints |

### Video Processing Tools

| Tool | Purpose | Command Example |
|------|---------|-----------------|
| **FFmpeg Crop** | Region extraction | `crop=w:h:x:y` |
| **FFmpeg Segment** | Clip creation | `-ss start -t duration` |
| **FFmpeg Copy** | Audio preservation | `-c:a copy` |

---

## ⚙️ Algorithm Parameters & Tuning

### Border Detection Parameters
```python
lower_light = [0, 0, 180]      # HSV lower bound
upper_light = [180, 80, 255]   # HSV upper bound
kernel_size = (3, 3)           # Morphological kernel
morph_close = 2                # Closing iterations
morph_open = 1                 # Opening iterations
border_margin = 0.15           # Interior region (15%)
```

### Optical Flow Parameters
```python
pyr_scale = 0.5                # Pyramid scale factor
levels = 3                     # Pyramid levels
winsize = 15                   # Window size
iterations = 3                 # Per-level iterations
poly_n = 5                     # Neighborhood size
poly_sigma = 1.2               # Gaussian sigma
```

### Edge Detection Parameters
```python
canny_low = 50                 # Lower threshold
canny_high = 150               # Upper threshold
epsilon_factor = 0.02          # Polygon approximation
min_area = 1000                # Minimum contour area
aspect_ratio = (0.8, 2.0)      # Valid aspect ratio range
```

### Quality Thresholds
```python
min_confidence = 0.25          # Border detection
motion_threshold = 10          # Minimum motion score
min_clip_duration = 4.8        # Seconds
max_clip_duration = 5.2        # Seconds
min_resolution = (64, 64)      # Minimum dimensions
```

---

## 🔄 Processing Pipeline Summary

```
1. Input Video (MP4) 
   ↓ [OpenCV VideoCapture]
2. Frame Sampling (50 frames)
   ↓ [HSV + Morphology + Contours]
3. Border Detection (0.85 confidence)
   ↓ [Parameter Application]
4. Adjusted Bounding Box (180×180)
   ↓ [FFmpeg Crop + Audio Copy]
5. Cropped Video Segments (5-sec clips)
   ↓ [OpenCV Resize]
6. Standardized Resolution (256×256)
   ↓ [Quality Filters]
7. Validated Clips (732 good clips)
   ↓ [Statistics + Previews]
8. Final Dataset (Ready for Training)
```

---

## 📈 Performance Metrics

**Processing Speed**: ~7.5× realtime  
**Accuracy**: 100% success rate on tested videos  
**Detection Time**: ~2-5 seconds for 50 frames  
**Cropping Speed**: ~8 minutes for 60-minute video  

**Example Throughput**:
- Input: 60-minute video (352 MB)
- Output: 732 clips (200 MB)
- Processing Time: ~8 minutes
- Per-clip Time: ~0.65 seconds

---

## 🎯 Recommended Settings for Best Results

```bash
# Optimal configuration for sign language transcription
python quick_start.py input_video.mp4 output_dataset \
    --border-margin 0.05 \    # 5% border (larger crop)
    --crop-adjust 20 \        # +20 pixels each side
    --size 256 \              # 256×256 output
    --start-time 480          # Skip first 8 minutes
```

**Result**:
- Original detection: ~160×160 pixels
- After adjustment: ~200×200 pixels  
- After resize: 256×256 pixels
- **Upscaling factor**: 1.28× (excellent quality)
- **Context**: More signing space captured
- **Best for**: Sign language transcription models

---

**Document Version**: 1.0  
**Last Updated**: March 17, 2026  
**System Version**: Voice-of-Hands v1.0
