# Voice-of-Hands: Multimodal Sign Language Dataset Collection System

**Last Updated**: May 5, 2026  
**Purpose**: Automatically detect and crop sign language interpreter regions from broadcast news videos, extract active signing clips, transcribe aligned audio, and build a multimodal dataset for sign language research.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Pipeline: How to Run](#pipeline-how-to-run)
   - [Step 1 – Crop Interpreter Region](#step-1--crop-interpreter-region)
   - [Step 2 – Detect Active Signing Clips](#step-2--detect-active-signing-clips)
   - [Step 3 – Extract Audio & Transcribe](#step-3--extract-audio--transcribe)
   - [Step 4 – Generate Visualization (demo7.mp4)](#step-4--generate-visualization-demo7mp4)
5. [Command Reference](#command-reference)
6. [Output Structure](#output-structure)

---

## Project Overview

This system processes broadcast news videos containing a sign language interpreter in a bordered inset window. It:

1. **Detects and crops** the interpreter region using border detection
2. **Extracts 5-second clips** from the cropped video
3. **Detects active signing** vs idle periods using MediaPipe pose/hand landmarks
4. **Extracts aligned audio** for each active clip
5. **Transcribes Sinhala speech** using OpenAI Whisper with word-level timestamps
6. **Builds a multimodal dataset** with aligned video, audio, and text

---

## Project Structure

```
Voice-of-Hands/
│
├── src/                               # All source code
│   ├── detection/
│   │   ├── sli_detector.py            # SLI border region detector (OpenCV)
│   │   ├── sign_activity_detector.py  # MediaPipe-based active signing detector
│   │   └── diagnose_rest_detection.py # Diagnostic tool for rest/idle tuning
│   │
│   ├── dataset/
│   │   ├── dataset_utils.py           # Dataset creation and analysis utilities
│   │   ├── scrapper.py                # Video downloader / scraper
│   │   ├── timestamp_extractor.py     # Clip extraction with timestamps
│   │   ├── run_audio_extraction.py    # Audio extraction pipeline runner
│   │   ├── run_transcription.py       # Whisper transcription pipeline runner
│   │   └── fix_audio_only_clips.py    # Fix clips that contain only audio
│   │
│   └── utils/
│       ├── quick_start.py             # One-command pipeline entry point
│       ├── crop_video_by_time.py      # Crop video by time range
│       ├── crop_video_spatial.py      # Spatial crop utility
│       ├── convert_to_pdf.py          # Convert docs to PDF
│       ├── md_to_pdf.py               # Markdown to PDF converter
│       └── setup.sh                   # Environment setup script
│
├── data/
│   ├── videos/                        # Input source videos (demo*.mp4, raw footage)
│   └── multimodal_dataset/            # Final aligned multimodal dataset
│       ├── alignment_metadata.json    # Audio-video-text alignment metadata
│       ├── audio_clips/               # Extracted audio per clip
│       ├── video_clips/               # Extracted video clips
│       └── transcriptions/            # Whisper transcription text files
│
├── outputs/
│   ├── active_clips/
│   │   ├── clips/                     # Active signing clips (MediaPipe output)
│   │   ├── clips_fixed/               # Fixed clips (audio-corrected)
│   │   ├── clips_viz/                 # Visualization overlay clips
│   │   └── clips_with_audio/          # Active clips with synchronized audio
│   ├── detection_results/             # Detector output runs (results, results3–7)
│   ├── signer_dataset/                # Cropped signer dataset outputs
│   └── transcription_log.txt          # Whisper transcription run log
│
├── docs/
│   ├── guides/                        # Usage guides and quickstart docs
│   │   ├── HOW_TO_RUN.md
│   │   ├── SIGN_ACTIVITY_DETECTOR_USAGE.md
│   │   ├── IMPROVED_DETECTION_QUICKSTART.md
│   │   └── AUDIO_ALIGNMENT_QUICKSTART.md
│   ├── methodology/                   # Algorithm and strategy documentation
│   │   ├── 5-Second_Clip_Duration_Strategy.md
│   │   ├── AUDIO_SIGN_ALIGNMENT_METHODOLOGY.md
│   │   ├── HORIZONTAL_IDLE_DETECTION.md
│   │   └── SIMPLIFIED_REST_DETECTION.txt
│   ├── diagrams/                      # Flowcharts and layout diagrams
│   │   ├── flowchart.mmd / .html
│   │   ├── SLI_Detection_Process_Flowchart.pdf
│   │   ├── VISUALIZATION_LAYOUT.txt
│   │   └── HORIZONTAL_DETECTION_DIAGRAM.txt
│   ├── analysis/                      # Planning and analysis documents
│   │   ├── Implementation_vs_Specification_Analysis.md
│   │   ├── PENDING_TASKS.md
│   │   ├── PROJECT_DEVELOPMENT_TIMELINE.md
│   │   └── PROCESS_FLOWCHART_AND_TECHNOLOGIES.md
│   ├── journal_paper/                 # IEEE journal paper (LaTeX)
│   │   ├── voice_of_hands_paper.tex
│   │   ├── references.bib
│   │   ├── JOURNAL_PAPER_DRAFT.md
│   │   └── compile.sh
│   ├── research/                      # Literature review and research docs
│   │   ├── LITERATURE_REWIEW/
│   │   └── research_docs/
│   └── presentation/                  # Slides and Q&A documents
│
├── experiments/                       # Test runs and parameter experiments (test_*)
├── Dataset_Creation/                  # Early dataset creation scripts
├── version_01/                        # Legacy version
├── 1/  2/                             # Raw signer dataset outputs
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

```bash
# 1. Clone repository
git clone https://github.com/MLSP-Research-Group-UOJ/Voice-of-Hands.git
cd Voice-of-Hands

# 2. Create and activate conda environment
conda create -n voice_to_hands python=3.10 -y
conda activate voice_to_hands

# 3. Install dependencies
pip install -r requirements.txt
conda install -c conda-forge ffmpeg

# 4. Verify MediaPipe and ffmpeg
python -c "import mediapipe; print('MediaPipe OK')"
ffmpeg -version
```

**Requirements**: Python 3.10+, ffmpeg, CUDA GPU (optional, speeds up Whisper)

---

## Pipeline: How to Run

### Step 1 – Crop Interpreter Region

Detects the sign language interpreter inset window and crops it from the broadcast video.

```bash
# Basic crop
python src/utils/quick_start.py data/videos/input_video.mp4 outputs/signer_dataset/run1

# High-quality 256×256 output, starting at 8 minutes
python src/utils/quick_start.py data/videos/input_video.mp4 outputs/signer_dataset/run1 \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

**Output**: `outputs/signer_dataset/run1/clips/` — 5-second cropped clips with audio

---

### Step 2 – Detect Active Signing Clips

Uses MediaPipe Holistic (pose + hands) to identify frames where the interpreter is actively signing vs at rest. Extracts only the active segments.

```bash
# Extract active signing clips from a cropped video
python src/detection/sign_activity_detector.py \
    data/videos/demo.mp4 \
    outputs/active_clips/clips/ \
    --threshold 0.02 \
    --min-duration 1.0

# Analyze only (no extraction, produces motion_analysis.json)
python src/detection/sign_activity_detector.py \
    data/videos/demo.mp4 \
    outputs/active_clips/clips/ \
    --analyze-only
```

**Key parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--threshold` | 0.015 | Motion energy threshold (lower = more sensitive) |
| `--min-duration` | 1.0 | Minimum active segment length (seconds) |
| `--min-idle` | 0.5 | Minimum idle gap to split segments (seconds) |
| `--no-horizontal-idle` | off | Disable horizontal rest position detection |

---

### Step 3 – Extract Audio & Transcribe

Extracts Sinhala audio from each active clip and transcribes it using OpenAI Whisper with word-level timestamps.

```bash
# Extract audio aligned to video clips
python src/dataset/run_audio_extraction.py

# Run Whisper transcription (Sinhala, medium model)
python src/dataset/run_transcription.py
```

**Output**: `data/multimodal_dataset/` — audio clips, transcription text files, and `alignment_metadata.json`

---

### Step 4 – Generate Visualization (demo7.mp4)

`demo7.mp4` is a **full visualization recording** of the sign activity detection pipeline applied to `demo.mp4` (347 seconds). It was created with:

```bash
python src/detection/sign_activity_detector.py \
    data/videos/demo.mp4 \
    outputs/active_clips/clips_viz/ \
    --save-visualization data/videos/demo7.mp4 \
    --analyze-only
```

The output video overlays:
- **MediaPipe skeleton** — pose landmarks + hand keypoints drawn on each frame
- **Motion energy graph** — real-time graph at the bottom showing movement over time
- **Active/Idle status label** — live annotation showing current signing state
- **Threshold line** — visual indicator of the motion detection threshold

> The visualization is re-encoded at lower bitrate, which is why `demo7.mp4` (28 MB) is much smaller than the original `demo.mp4` (98 MB) despite being the same duration.

**Demo video progression**:

| File | Duration | Description |
|------|----------|-------------|
| `demo.mp4` | 347s / 98MB | Original source video (full broadcast) |
| `demo2.mp4` | 82s / 5.7MB | Cropped interpreter region test |
| `demo3.mp4` | ~0s | Corrupt/empty test output |
| `demo4.mp4` | 145s / 10MB | Cropped video with audio test |
| `demo5.mp4` | 1.4s / 111KB | Single active clip extraction test |
| `demo6.mp4` | 35s / 2.3MB | Multi-clip extraction test |
| `demo7.mp4` | 347s / 28MB | **Full MediaPipe visualization of demo.mp4** |

---

## Command Reference

### Crop and extract SLI clips (full pipeline)
```bash
python src/utils/quick_start.py <input_video> <output_dir> [options]
```

### Detect active signing segments
```bash
python src/detection/sign_activity_detector.py <input_video> <output_dir> [options]
```

### Extract audio aligned to clips
```bash
python src/dataset/run_audio_extraction.py
```

### Transcribe audio clips (Sinhala Whisper)
```bash
python src/dataset/run_transcription.py
```

### Fix audio-only clips
```bash
python src/dataset/fix_audio_only_clips.py \
    outputs/active_clips/clips_with_audio/ \
    outputs/active_clips/clips_fixed/ \
    data/videos/source_video.mp4
```

### Crop video by time range
```bash
python src/utils/crop_video_by_time.py <input> <output> <start_sec> <end_sec>
```

---

## Output Structure

```
outputs/signer_dataset/run1/
├── clips/            # 5-second video clips with audio
├── full_cropped/     # Full duration cropped video
├── previews/         # Detection visualization frames
└── statistics.json   # Clip count, resolution, duration stats

data/multimodal_dataset/
├── alignment_metadata.json   # Per-clip audio-video-text alignment
├── audio_clips/              # .wav audio per clip
├── video_clips/              # .mp4 video per clip
└── transcriptions/           # .txt Whisper output per clip
```

---
