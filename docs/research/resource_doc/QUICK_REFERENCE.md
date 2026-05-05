# 🚀 Quick Reference Card - SLI Detection System

## One-Liner Commands

### Setup & Installation
```bash
conda create -n sli_detector python=3.10 -y && conda activate sli_detector && pip install -r requirements.txt
```

### Download Video from YouTube
```bash
yt-dlp -f "best[ext=mp4]" -o "videos/%(title)s.%(ext)s" <YOUTUBE_URL>
```

### Process Single Video (Main Command)
```bash
python quick_start.py videos/Parliament_Live_01-12-2025.mp4 output_dataset
```

### Process All Videos in Directory
```bash
python quick_start.py --batch videos/ output_dataset
```

### Check Dataset Statistics
```bash
python dataset_utils.py output_dataset stats
```

---

## File Locations (Assuming video in videos/ directory)

### Input
- **Your videos**: `videos/your_video.mp4`

### Output
- **Extracted clips**: `output_dataset/clips/`
- **Full cropped video**: `output_dataset/full_cropped/`
- **Detection preview**: `output_dataset/previews/`
- **Statistics**: `output_dataset/statistics.json`
- **Preview grid**: `output_dataset/preview_grid.jpg`

---

## Python Quick Examples

### Basic Usage
```python
from sli_detector import process_video_for_dataset

results = process_video_for_dataset(
    video_path="videos/your_video.mp4",
    output_dir="output_dataset"
)

print(f"Extracted {len(results['clips'])} clips")
```

### Custom Detection
```python
from sli_detector import SLIDetector

detector = SLIDetector("videos/your_video.mp4")
result = detector.detect(method="auto")
clips = detector.extract_sli_clips(result, "output_clips/")
```

---

## Detection Methods

| Method | Speed | Best For | Command |
|--------|-------|----------|---------|
| `auto` | Fast | Unknown videos | `method="auto"` |
| `motion` | Fast | Active signing | `method="motion"` |
| `edge` | Fastest | PiP with borders | `method="edge"` |
| `pose` | Slower | High quality | `method="pose"` |
| `hybrid` | Medium | Maximum accuracy | `method="hybrid"` |

---

## Conda Environment Commands

```bash
# Activate
conda activate sli_detector

# Deactivate
conda deactivate

# List packages
conda list

# Remove environment
conda env remove -n sli_detector
```

---

## Common Parameters

### extract_sli_clips()
- **clip_duration**: `3.0`, `5.0`, `10.0` (seconds)
- **overlap**: `0.0` to `0.9` (0.5 = 50%)
- **min_motion_threshold**: `0.5` (low), `1.0` (medium), `2.0` (high)
- **padding**: `10`, `15`, `20` (pixels)

### process_video_for_dataset()
- **detection_method**: `"auto"`, `"motion"`, `"edge"`, `"pose"`
- **clip_duration**: `5.0` (default)
- **min_confidence**: `0.3` to `0.7` (default: 0.5)
- **save_full_video**: `True` or `False`

---

## Troubleshooting One-Liners

### Fix Import Errors
```bash
conda activate sli_detector && pip install opencv-python numpy mediapipe
```

### Test Installation
```python
python -c "import cv2, numpy, mediapipe; print('✓ All OK')"
```

### Check Video Properties
```python
python -c "import cv2; v=cv2.VideoCapture('videos/video.mp4'); print(f'{int(v.get(3))}x{int(v.get(4))} @ {v.get(5)} FPS')"
```

---

## File Structure

```
Voice-of-Hands/
├── videos/                    # Place videos here
├── output_dataset/            # Results appear here
│   ├── clips/                 # Training data →
│   ├── full_cropped/
│   ├── previews/
│   └── statistics.json
├── sli_detector.py            # Main code
├── quick_start.py             # Easy interface
└── IMPLEMENTATION_GUIDE.md    # Full docs
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| **PROJECT_SUMMARY.md** | What was built, results |
| **IMPLEMENTATION_GUIDE.md** | Technical details, algorithms |
| **README_SLI_DETECTOR.md** | Complete API reference |
| **GETTING_STARTED.md** | Beginner's guide |
| **WORKFLOW_VISUAL.py** | Visual diagrams |

---

## Useful Checks

### Count Clips
```bash
ls output_dataset/clips/*.mp4 | wc -l
```

### Check Total Size
```bash
du -sh output_dataset/
```

### View First 5 Clips
```bash
ls output_dataset/clips/ | head -5
```

### Play Random Clip
```bash
vlc "$(ls output_dataset/clips/*.mp4 | shuf -n 1)"
```

---

## Expected Results (10-min video)

- **Processing time**: ~3.5 minutes
- **Clips generated**: ~300-400
- **Dataset size**: ~100-200 MB
- **Detection confidence**: 0.6-0.9

---

## Support

- **Full docs**: See `IMPLEMENTATION_GUIDE.md`
- **Quick start**: See `GETTING_STARTED.md`
- **Examples**: See `example_extract_sli.py`
- **Visual guide**: Run `python WORKFLOW_VISUAL.py`

---

## Success Indicators

✅ Process completes without errors  
✅ Clips directory contains 100+ files  
✅ Detection confidence > 0.3  
✅ statistics.json created  
✅ Preview images generated  

---

**Keep this file handy for quick reference!** 📌
