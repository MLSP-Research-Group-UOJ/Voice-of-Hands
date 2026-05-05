# 🚀 Voice-of-Hands: Complete Guide to Running and Getting Outputs

**Project**: Multimodal Sign Language Dataset Collection System  
**Version**: 1.0  
**Date**: April 2026  
**Purpose**: Extract sign language interpreter video clips with aligned audio transcriptions

---

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Complete Workflow](#complete-workflow)
4. [Expected Outputs](#expected-outputs)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

This system automatically creates a multimodal sign language dataset from broadcast news videos by:

1. **Video Processing**: Detects and crops sign language interpreter regions
2. **Clip Extraction**: Creates 5-second video clips for training
3. **Audio Extraction**: Extracts corresponding audio for each clip
4. **Transcription**: Transcribes audio to Sinhala text with word-level timestamps
5. **Metadata Generation**: Creates alignment metadata for audio-sign pairs

### Key Features

- ✅ Automatic border detection for interpreter regions
- ✅ Audio preservation with temporal alignment
- ✅ Sinhala language transcription using OpenAI Whisper
- ✅ Word-level timestamps for fine-grained alignment
- ✅ Quality control and statistics
- ✅ Batch processing support

---

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- ffmpeg (for video/audio processing)
- CUDA-compatible GPU (optional, for faster transcription)

### Step 1: Setup Environment

```bash
# Create conda environment
conda create -n voice_to_hands python=3.10 -y

# Activate environment
conda activate voice_to_hands

# Navigate to project directory
cd "/media/spdanuraj/windows 11/Research/Voice_to_Hands/Voice-of-Hands"
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install additional requirements for audio processing
pip install openai-whisper torch torchaudio

# Install ffmpeg
conda install -c conda-forge ffmpeg -y
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "import cv2, numpy, whisper; print('✅ All packages installed successfully')"

# Check ffmpeg
ffmpeg -version
```

---

## 🎬 Complete Workflow

### Pipeline Overview

```
Input Video → SLI Detection → Clip Extraction → Audio Extraction → Transcription → Multimodal Dataset
```

### Step 1: Video Processing & Clip Extraction

**Purpose**: Detect interpreter region and create 5-second video clips

```bash
# Process a single video with default settings
python quick_start.py videos/Parliament_Live_01-12-2025.mp4 output_dataset

# Advanced usage with custom parameters
python quick_start.py videos/your_video.mp4 output_dataset \
    --size 256 \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --start-time 480
```

**Parameters Explained**:
- `--size`: Output resolution (`original`, `128`, or `256`)
- `--border-margin`: Border exclusion (0.05 = 5%, larger crop area)
- `--crop-adjust`: Pixel adjustment (+20 = expand by 20px)
- `--start-time`: Skip intro (480 = start at 8 minutes)

**Output from Step 1**:
```
output_dataset/
├── clips/                          # 5-second video clips
│   ├── video_clip_0000.mp4
│   ├── video_clip_0001.mp4
│   └── ...
├── full_cropped/                   # Full cropped video
│   └── video_sli_cropped.mp4
├── previews/                       # Detection visualizations
│   └── video_detection.jpg
└── statistics.json                 # Processing statistics
```

---

### Step 2: Audio Extraction from Clips

**Purpose**: Extract audio segments matching each video clip with precise timestamps

```bash
# Extract audio from existing clips
python run_audio_extraction.py
```

**What this does**:
- Takes each 5-second video clip
- Extracts the corresponding audio segment
- Saves audio files (.mp3 or .wav)
- Creates initial alignment metadata

**Output from Step 2**:
```
multimodal_dataset/
├── audio_clips/                    # Extracted audio files
│   ├── clip_0000.mp3
│   ├── clip_0001.mp3
│   └── ...
├── video_clips/                    # Symlink to clips
│   ├── clip_0000.mp4
│   ├── clip_0001.mp4
│   └── ...
└── alignment_metadata.json         # Initial metadata
```

**Sample Metadata** (`alignment_metadata.json`):
```json
{
  "dataset_info": {
    "original_video": "Parliament_Live_01-12-2025.mp4",
    "created_date": "2026-04-10T...",
    "clip_duration": 5.0,
    "total_clips": 732
  },
  "clips": [
    {
      "clip_id": "clip_0000",
      "video_file": "clip_0000.mp4",
      "audio_file": "clip_0000.mp3",
      "start_time": 0.0,
      "end_time": 5.0
    }
  ]
}
```

---

### Step 3: Sinhala Transcription

**Purpose**: Transcribe audio to Sinhala text with word-level timestamps

```bash
# Run transcription (will take 30-40 minutes for 732 clips)
python run_transcription.py
```

**What this does**:
- Uses OpenAI Whisper (medium model) for Sinhala transcription
- Extracts word-level timestamps for fine-grained alignment
- Calculates confidence scores
- Saves individual transcription files
- Updates alignment metadata

**Output from Step 3**:
```
multimodal_dataset/
├── audio_clips/                    # Audio files
├── video_clips/                    # Video clips
├── transcriptions/                 # Transcription text files
│   ├── clip_0000.txt
│   ├── clip_0001.txt
│   └── ...
└── alignment_metadata.json         # Complete metadata with transcriptions
```

**Updated Metadata** (after transcription):
```json
{
  "clips": [
    {
      "clip_id": "clip_0000",
      "video_file": "clip_0000.mp4",
      "audio_file": "clip_0000.mp3",
      "transcription_file": "clip_0000.txt",
      "start_time": 0.0,
      "end_time": 5.0,
      "transcription": {
        "text": "මම අද පාර්ලිමේන්තුවට කියන්නේ...",
        "language": "si",
        "words": [
          {"word": "මම", "start": 0.12, "end": 0.34, "confidence": 0.95},
          {"word": "අද", "start": 0.36, "end": 0.58, "confidence": 0.92}
        ],
        "avg_confidence": 0.89
      }
    }
  ]
}
```

**Sample Transcription File** (`clip_0000.txt`):
```
මම අද පාර්ලිමේන්තුවට කියන්නේ මේ විෂයේ ගැන සලකා බලන්න කියලා
```

---

## 📊 Expected Outputs

### Final Dataset Structure

After completing all three steps, you'll have:

```
Voice-of-Hands/
├── output_dataset/                 # From Step 1: Video processing
│   ├── clips/                      # 732 video clips (5 sec each)
│   ├── full_cropped/               # Cropped full video
│   ├── previews/                   # Visual detection results
│   └── statistics.json
│
└── multimodal_dataset/             # From Steps 2 & 3: Audio & Transcription
    ├── audio_clips/                # 732 audio files
    │   ├── clip_0000.mp3
    │   └── ...
    ├── video_clips/                # Symlink to video clips
    │   ├── clip_0000.mp4
    │   └── ...
    ├── transcriptions/             # 732 text files
    │   ├── clip_0000.txt
    │   └── ...
    └── alignment_metadata.json     # Complete alignment data
```

### Output Statistics

**Example Statistics** (`statistics.json`):
```json
{
  "processing_info": {
    "video_name": "Parliament_Live_01-12-2025",
    "detection_method": "border",
    "border_margin": 0.05,
    "crop_adjust_px": 20,
    "output_size": "256x256",
    "start_offset_seconds": 480
  },
  "detection_results": {
    "detected_region": [100, 50, 200, 200],
    "confidence": 0.95
  },
  "dataset_stats": {
    "total_clips": 732,
    "clip_duration": 5.0,
    "total_duration": 3660.0,
    "avg_file_size_mb": 1.2
  }
}
```

### Quality Metrics

- **Total clips**: 732
- **Dataset duration**: ~1 hour of aligned data
- **Average transcription confidence**: 85-90%
- **Storage required**: ~2-3 GB (video + audio + metadata)

---

## 🔄 Processing Different Videos

### Process Multiple Videos (Batch Mode)

```bash
# Place all videos in videos/ directory
# Run in batch mode
python quick_start.py --batch videos/ batch_output
```

### Custom Pipeline for Each Video

```bash
# Step 1: Video processing
python quick_start.py videos/video1.mp4 dataset1

# Step 2: Audio extraction (update paths in script)
# Edit run_audio_extraction.py to use correct paths
python run_audio_extraction.py

# Step 3: Transcription (update paths in script)
# Edit run_transcription.py to use correct paths
python run_transcription.py
```

---

## 🎯 Use Cases for the Dataset

1. **Sign Language Recognition**: Train models to recognize Sinhala sign language gestures
2. **Audio-to-Sign Translation**: Learn mappings from spoken Sinhala to sign language
3. **Sign-to-Audio Translation**: Generate audio from sign language video
4. **Temporal Analysis**: Study timing differences between speech and signing
5. **Multimodal Learning**: Pre-training for vision-language models

---

## 🐛 Troubleshooting

### Issue: Video not processing

```bash
# Check if video file exists
ls -lh videos/your_video.mp4

# Check if ffmpeg is installed
ffmpeg -version

# Try with lower resolution
python quick_start.py videos/your_video.mp4 output --size 128
```

### Issue: Audio extraction fails

```bash
# Verify ffmpeg audio codecs
ffmpeg -codecs | grep mp3

# Check if clips directory exists and has files
ls output_dataset/clips/ | wc -l
```

### Issue: Transcription is slow

```bash
# Check if GPU is available
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Use smaller Whisper model
# Edit run_transcription.py and change model_name to "base" or "small"
```

### Issue: Out of memory during transcription

```bash
# Process clips in batches
# Edit run_transcription.py to process fewer clips at a time
# Or use a smaller Whisper model ("base" instead of "medium")
```

---

## 📖 Additional Documentation

- [README.md](README.md) - Quick start and overview
- [AUDIO_SIGN_ALIGNMENT_METHODOLOGY.md](AUDIO_SIGN_ALIGNMENT_METHODOLOGY.md) - Research methodology
- [AUDIO_ALIGNMENT_QUICKSTART.md](AUDIO_ALIGNMENT_QUICKSTART.md) - Quick reference
- [resource_doc/](resource_doc/) - Detailed technical documentation

---

## 🎓 Research Context

This system supports research in:
- **Multimodal Learning**: Parallel corpus of sign language and audio
- **Low-Resource Languages**: Sinhala sign language dataset creation
- **Accessibility**: Tools for deaf/hard-of-hearing community
- **Machine Translation**: Audio ↔ Sign language translation

---

## 📝 Citation

If you use this system in your research, please cite:

```
Voice-of-Hands: Multimodal Sign Language Dataset Collection System
Version 1.0, April 2026
Automatic Detection and Alignment of Sign Language Interpretation with Audio Transcription
```

---

## 📧 Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review the documentation in `resource_doc/`
3. Check existing output examples in sample datasets

---

**Last Updated**: April 10, 2026  
**Status**: ✅ Production Ready
