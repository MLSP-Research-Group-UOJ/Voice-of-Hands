# Audio-Sign Language Alignment - Quick Start Guide

**Purpose**: Extract video clips with synchronized audio for multimodal sign language dataset creation

---

## 🎯 What You'll Get

A complete multimodal dataset with:
- Sign language video clips (256×256)
- Corresponding audio segments (16kHz WAV)
- Speech-to-text transcriptions
- Precise timestamp alignment
- JSON metadata for research

---

## 📁 Output Structure

```
multimodal_dataset/
├── video_clips/                    # SLI video clips
│   ├── video_clip_0000.mp4
│   ├── video_clip_0001.mp4
│   └── ...
│
├── audio_clips/                    # Audio segments
│   ├── video_clip_0000.wav
│   ├── video_clip_0001.wav
│   └── ...
│
├── transcriptions/                 # Speech transcriptions
│   ├── video_clip_0000.txt
│   ├── video_clip_0001.txt
│   └── ...
│
└── alignment_metadata.json         # Complete metadata
```

---

## 🚀 Method 1: Create New Dataset with Timestamps

### Step 1: Install Dependencies

```bash
# Activate your environment
source .venv/bin/activate

# Install Whisper for transcription
pip install openai-whisper
```

### Step 2: Detect SLI Region (if not done already)

```python
from sli_detector import SLIDetector

# Detect interpreter region
detector = SLIDetector("videos/news_video.mp4")
result = detector.detect(method="auto")

print(f"Detected region: ({result.x1}, {result.y1}) to ({result.x2}, {result.y2})")
```

### Step 3: Extract Clips with Timestamps

```python
from timestamp_extractor import TimestampedClipExtractor

# Initialize extractor
extractor = TimestampedClipExtractor(
    video_path="videos/news_video.mp4",
    output_base_dir="multimodal_dataset"
)

# Extract clips with metadata
metadata = extractor.extract_clips_with_metadata(
    crop_region={
        'x1': result.x1, 'y1': result.y1,
        'x2': result.x2, 'y2': result.y2
    },
    clip_duration=5.0,          # 5-second clips
    start_time=480.0,           # Start at 8 minutes
    end_time=None,              # Until end (or specify time)
    overlap=0.0,                # No overlap
    output_size=(256, 256),     # Output resolution
    extract_audio=True,         # Extract audio segments
    min_motion_threshold=5.0    # Filter static clips
)

print(f"Extracted {len(metadata['clips'])} clips")
```

### Step 4: Transcribe Audio

```python
# For Sinhala (recommended for Sri Lankan Parliament)
metadata = extractor.transcribe_audio_clips(
    metadata_path="multimodal_dataset/alignment_metadata.json",
    model_name="medium",  # Use medium or large for better Sinhala support
    language="si"         # Sinhala language code
)

# For auto-detection (if mixed Sinhala/English/Tamil)
metadata = extractor.transcribe_audio_clips(
    metadata_path="multimodal_dataset/alignment_metadata.json",
    model_name="medium",
    language=None  # Auto-detect language
)

print("Transcription complete!")
```

### Step 5: Explore Results

```python
import json

# Load metadata
with open("multimodal_dataset/alignment_metadata.json", 'r') as f:
    metadata = json.load(f)

# Check a sample clip
clip = metadata['clips'][0]
print(f"Clip ID: {clip['clip_id']}")
print(f"Time: {clip['timestamp']['start_seconds']}s - {clip['timestamp']['end_seconds']}s")
print(f"Transcription: {clip['transcription']}")
print(f"Confidence: {clip['transcription_confidence']}")
```

---

## 🔄 Method 2: Add Timestamps to Existing Clips

If you already have clips from previous runs:

```python
from timestamp_extractor import extract_from_existing_clips

# Extract audio and create metadata for existing clips
extract_from_existing_clips(
    clips_dir="output_128/clips",
    original_video="videos/Parliament_Live_01-12-2025.mp4",
    output_dir="multimodal_output",
    fps=30.0,
    clip_duration=5.0
)

# Then transcribe
from timestamp_extractor import TimestampedClipExtractor
extractor = TimestampedClipExtractor(
    "videos/Parliament_Live_01-12-2025.mp4",
    "multimodal_output"
)
extractor.transcribe_audio_clips(
    "multimodal_output/alignment_metadata.json",
    model_name="medium",
    language="si"  # Sinhala language
)
```

---

## 📊 Metadata Format

Each clip in `alignment_metadata.json` contains:

```json
{
  "clip_id": "0042",
  "filename": "video_clip_0042.mp4",
  "audio_filename": "video_clip_0042.wav",
  "text_filename": "video_clip_0042.txt",
  "timestamp": {
    "start_seconds": 690.0,
    "end_seconds": 695.0,
    "start_frame": 20700,
    "end_frame": 20850,
    "duration": 5.0
  },
  "crop_region": {
    "x1": 1065, "y1": 452,
    "x2": 1265, "y2": 652,
    "width": 200, "height": 200
  },
  "transcription": "The finance minister announces the new budget allocation...",
  "transcription_confidence": 0.89,
  "word_timestamps": [
    {"word": "The", "start": 690.0, "end": 690.2, "probability": 0.95},
    {"word": "finance", "start": 690.2, "end": 690.6, "probability": 0.92},
    ...
  ],
  "motion_score": 32.5,
  "quality_passed": true
}
```

---

## 🔬 Research Use Cases

### 1. **Sign Language Translation Model Training**

```python
# Load aligned data
for clip in metadata['clips']:
    video_path = f"multimodal_dataset/video_clips/{clip['filename']}"
    audio_path = f"multimodal_dataset/audio_clips/{clip['audio_filename']}"
    text = clip['transcription']
    
    # Train model: video -> text or audio -> video
```

### 2. **Temporal Lag Analysis**

Analyze delay between speech and signing:

```python
# Compare speech timing to sign language actions
for clip in metadata['clips']:
    speech_words = clip['word_timestamps']
    # Analyze when each word appears vs when it's signed
    # (requires manual annotation or pose tracking)
```

### 3. **Dataset Statistics**

```python
import json

with open("multimodal_dataset/alignment_metadata.json", 'r') as f:
    data = json.load(f)

total_duration = sum(c['timestamp']['duration'] for c in data['clips'])
print(f"Total duration: {total_duration/60:.1f} minutes")
print(f"Total clips: {len(data['clips'])}")
print(f"Avg transcription confidence: {sum(c['transcription_confidence'] for c in data['clips'])/len(data['clips']):.2f}")
```

---

## 💡 Tips & Best Practices

### Whisper Model Selection

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| tiny | Fastest | 68% | ~1GB | Quick testing (poor for Sinhala) |
| base | Fast | 72% | ~1GB | Development (poor for Sinhala) |
| small | Medium | 76% | ~2GB | English/common languages |
| medium | Slow | 79% | ~5GB | **Sinhala recommended** ✅ |
| large | Slowest | 84% | ~10GB | Best Sinhala quality |

**For Sinhala Parliament videos**: Use `medium` or `large` models for acceptable quality.

### Audio Quality

- 16kHz sample rate is optimal for ASR
- Mono audio reduces file size
- PCM format ensures no compression artifacts

### Clip Duration

- **5 seconds**: Good for short phrases
- **10 seconds**: Better for complete sentences
- **3 seconds**: If vocabulary is limited

### Overlap Strategy

- **0% overlap**: No redundancy, faster processing
- **25% overlap**: Captures boundary effects
- **50% overlap**: Maximum coverage, more data

### Language Support

Whisper supports **99 languages** including South Asian languages:

| Language | Code | Quality | Notes |
|----------|------|---------|-------|
| **Sinhala** | `'si'` | Good (medium+) | Requires medium/large model |
| Tamil | `'ta'` | Good | Well-supported |
| English | `'en'` | Excellent | Best performance |
| Hindi | `'hi'` | Excellent | Well-supported |

**For Sri Lankan Parliament broadcasts:**
```python
# Option 1: Force Sinhala (if mostly Sinhala)
extractor.transcribe_audio_clips(
    "multimodal_dataset/alignment_metadata.json",
    model_name="medium",
    language="si"
)

# Option 2: Auto-detect (if mixed Sinhala/English/Tamil)
extractor.transcribe_audio_clips(
    "multimodal_dataset/alignment_metadata.json",
    model_name="medium",
    language=None  # Auto-detects per clip
)
```

---

## 🐛 Troubleshooting

### Issue: "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Issue: Whisper import error
```bash
pip install --upgrade openai-whisper
# Or use specific version
pip install openai-whisper==20231117
```

### Issue: Out of memory during transcription
```python
# Use smaller model
metadata = extractor.transcribe_audio_clips(
    metadata_path="...",
    model_name="tiny"  # or "base"
)
```

### Issue: Audio extraction fails
- Check original video has audio track
- Try: `ffmpeg -i video.mp4` to inspect streams
- Ensure start_time < video duration

---

## 📝 Complete Workflow Example

```python
#!/usr/bin/env python3
"""Complete pipeline: detection -> extraction -> transcription"""

from sli_detector import SLIDetector
from timestamp_extractor import TimestampedClipExtractor

# 1. Detect SLI region
print("Step 1: Detecting SLI region...")
detector = SLIDetector("videos/news.mp4")
result = detector.detect(method="auto", start_time=480)

# 2. Extract clips with audio
print("\nStep 2: Extracting clips with timestamps...")
extractor = TimestampedClipExtractor(
    "videos/news.mp4",
    "research_dataset"
)

metadata = extractor.extract_clips_with_metadata(
    crop_region={
        'x1': result.x1, 'y1': result.y1,
        'x2': result.x2, 'y2': result.y2
    },
    clip_duration=5.0,
    start_time=480.0,
    extract_audio=True
)

# 3. Transcribe
print("\nStep 3: Transcribing audio...")
metadata = extractor.transcribe_audio_clips(
    "research_dataset/alignment_metadata.json",
    model_name="medium",  # Use medium for Sinhala
    language="si"         # Sinhala language
)

print("\n✅ Complete! Dataset ready at: research_dataset/")
```

---

## 📚 Next Steps

1. **Validate alignment**: Manually check 10-20 random samples
2. **Filter low-confidence**: Remove clips with confidence < 0.7
3. **Annotate signing**: Add manual sign language annotations
4. **Train model**: Use for sign language translation research
5. **Publish dataset**: Share with research community (check ethics)

---

## 📖 References

- **Whisper Documentation**: https://github.com/openai/whisper
- **Sign Language Datasets**: Phoenix-2014, CSL, WLASL
- **Related Paper**: "How2Sign: A Large-scale Multimodal Dataset"

---

**Need Help?** Check [AUDIO_SIGN_ALIGNMENT_METHODOLOGY.md](AUDIO_SIGN_ALIGNMENT_METHODOLOGY.md) for detailed research methodology.
