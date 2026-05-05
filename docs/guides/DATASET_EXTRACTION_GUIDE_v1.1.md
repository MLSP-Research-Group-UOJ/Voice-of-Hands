# Voice-of-Hands: Dataset Extraction Guide

**Version**: 1.1  
**Date**: May 5, 2026  
**Purpose**: Step-by-step guide to extract sign language video snippets and build the dataset

---

## Overview

The pipeline has **two stages**:

- **Stage 1** (required) — Automatically detect and crop the interpreter window from the broadcast video, then slice it into 5-second clips.
- **Stage 2** (recommended) — Filter out idle/rest frames using MediaPipe, keeping only segments where the signer is actively signing.

The result of Stage 2 is your final clean dataset, as demonstrated in `data/videos/demo7.mp4` which shows the MediaPipe skeleton tracking and active/idle detection working on the full video.

---

## Prerequisites — Run Once

```bash
# Activate environment
conda activate voice_to_hands

# Navigate to project root
cd "/media/spdanuraj/windows 11/Research/Voice_to_Hands/Voice-of-Hands"

# Set Python path so scripts can find each other
export PYTHONPATH=src/detection:src/dataset:src/utils
```

> **Note**: You need to re-run `export PYTHONPATH=...` every time you open a new terminal, or add it to your `~/.bashrc` to make it permanent.

---

## Stage 1 — Crop Interpreter Region + Extract 5-Second Clips

This step detects the bordered interpreter inset in the broadcast video, crops it out, and cuts it into uniform 5-second clips.

```bash
python src/utils/quick_start.py \
    data/videos/YOUR_VIDEO.mp4 \
    outputs/signer_dataset/run1 \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

### What this does
- Automatically detects the sign language interpreter's bordered window region
- Crops just that region from the full broadcast frame
- Cuts the cropped video into **5-second clips** saved to `outputs/signer_dataset/run1/clips/`
- Saves a `preview_grid.jpg` so you can visually verify the crop region
- Saves a `statistics.json` with clip count, resolution, and duration info

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `--border-margin` | `0.15` | How much border to exclude during detection. Lower = larger crop. Try `0.05`–`0.10` for best results |
| `--crop-adjust` | `0` | Expand (`+`) or shrink (`-`) the final crop by N pixels on each side |
| `--size` | `original` | Output resolution: `original`, `128`, or `256`. Use `256` for DNN training |
| `--start-time` | `0` | Skip intro in seconds (e.g., `480` = start at 8 minutes) |

### Tuning Tips

```bash
# If crop is too tight — increase crop-adjust or lower border-margin
python src/utils/quick_start.py data/videos/YOUR_VIDEO.mp4 outputs/signer_dataset/run1 \
    --border-margin 0.10 --crop-adjust 10 --size 256

# If crop includes too much background — increase border-margin
python src/utils/quick_start.py data/videos/YOUR_VIDEO.mp4 outputs/signer_dataset/run1 \
    --border-margin 0.20 --size 256

# Start from beginning of video (no intro skip)
python src/utils/quick_start.py data/videos/YOUR_VIDEO.mp4 outputs/signer_dataset/run1 \
    --border-margin 0.05 --size 256 --start-time 0
```

### Stage 1 Output

```
outputs/signer_dataset/run1/
├── clips/                          # ← 5-second video clips with audio
│   ├── YOUR_VIDEO_clip_0000.mp4
│   ├── YOUR_VIDEO_clip_0001.mp4
│   └── ...
├── full_cropped/
│   └── YOUR_VIDEO_sli_cropped.mp4  # ← full-duration cropped video
├── previews/
│   ├── YOUR_VIDEO_detection.jpg    # ← sample frames with bounding box overlay
│   └── ...
└── statistics.json                 # ← clip count, resolution, total duration
```

**Check this before moving to Stage 2:** Open `previews/YOUR_VIDEO_detection.jpg` to confirm the crop region looks correct.

---

## Stage 2 — Keep Only Active Signing Segments

This step takes the full cropped video from Stage 1 and uses **MediaPipe Holistic** (pose + hand landmarks) to detect when the interpreter is actively signing vs at rest. Only the active segments are extracted as clips.

```bash
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ \
    --threshold 0.02 \
    --min-duration 1.0
```

### What this does
- Tracks hand and body landmarks on every frame using MediaPipe
- Calculates motion energy between frames
- Also detects the horizontal rest position (forearms parallel to ground) as an additional idle indicator
- Extracts only the **actively signing** segments as individual clips
- Saves `activity_metadata.json` with timestamps and motion info per clip

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `--threshold` | `0.015` | Motion energy threshold. Lower = more sensitive (detects subtle movements) |
| `--min-duration` | `1.0` | Minimum length (seconds) for a segment to be kept |
| `--min-idle` | `0.5` | Minimum idle gap (seconds) to split two active segments |
| `--no-horizontal-idle` | off | Disable horizontal rest position detection (use only motion threshold) |

### Tuning Tips

```bash
# Too many clips / over-sensitive — raise threshold
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ --threshold 0.03

# Missing subtle signs — lower threshold
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ --threshold 0.01

# Only use motion (ignore horizontal rest detection)
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ --no-horizontal-idle
```

---

## Stage 2a — Dry Run (Analyze Without Extracting)

Use this to preview which segments will be extracted before committing:

```bash
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ \
    --analyze-only
```

This prints all detected active segments with timestamps and saves `motion_analysis.json`. No video clips are written.

---

## Stage 2b — Save Visualization Video (Verify Quality)

Generate a visualization video like `demo7.mp4` to visually confirm detection quality before building the full dataset:

```bash
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips_viz/ \
    --save-visualization data/videos/my_viz.mp4 \
    --analyze-only
```

Open `data/videos/my_viz.mp4` to see:
- **MediaPipe skeleton** drawn on each frame (pose + hand keypoints)
- **Motion energy graph** at the bottom showing movement over time
- **Active / Idle label** live on each frame
- **Threshold line** showing the cutoff level

Adjust `--threshold` until the active/idle transitions look correct, then run the full extraction.

---

## Final Dataset Output

After both stages, your dataset is in:

```
outputs/active_clips/clips/
├── active_001_23.1s-25.9s.mp4     # active signing clip with audio
├── active_002_35.4s-40.0s.mp4
├── active_003_44.0s-45.0s.mp4
├── ...
└── activity_metadata.json          # timestamps + motion data per clip
```

Each clip is a **labeled active signing segment with synchronized audio**, named with its timestamp in the original video. These are ready for model training.

---

## Quick Reference

```bash
# Full pipeline — single command cheat sheet

export PYTHONPATH=src/detection:src/dataset:src/utils

# Stage 1: Crop + extract 5-second clips
python src/utils/quick_start.py \
    data/videos/YOUR_VIDEO.mp4 outputs/signer_dataset/run1 \
    --border-margin 0.05 --crop-adjust 20 --size 256 --start-time 480

# Stage 2a: Dry run (check segments)
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ --analyze-only

# Stage 2b: Visualize (verify quality)
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips_viz/ \
    --save-visualization data/videos/my_viz.mp4 --analyze-only

# Stage 2: Extract active clips
python src/detection/sign_activity_detector.py \
    outputs/signer_dataset/run1/full_cropped/YOUR_VIDEO_sli_cropped.mp4 \
    outputs/active_clips/clips/ \
    --threshold 0.02 --min-duration 1.0
```

---

**See also**:
- [docs/guides/HOW_TO_RUN.md](HOW_TO_RUN.md) — full system guide
- [docs/guides/SIGN_ACTIVITY_DETECTOR_USAGE.md](SIGN_ACTIVITY_DETECTOR_USAGE.md) — detailed detector parameters
- [docs/methodology/HORIZONTAL_IDLE_DETECTION.md](../methodology/HORIZONTAL_IDLE_DETECTION.md) — how horizontal rest detection works
- [docs/analysis/PENDING_TASKS.md](../analysis/PENDING_TASKS.md) — known issues and future improvements
