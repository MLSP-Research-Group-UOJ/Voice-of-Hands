# Research Improvement Suggestions

This folder contains Q&A discussions, analysis, and recommendations for improving the Sign Language Interpreter (SLI) dataset collection system.

---

## Contents

### 1. [Crop Settings Impact Analysis](crop_settings_impact_analysis.md)
**Topic**: Border margin, crop adjustment, and video resizing impact on sign language transcription

**Key Questions Addressed**:
- How do border margin and crop adjust parameters affect video quality?
- What's the impact of upscaling on sign language transcription systems?
- What are the optimal settings for dataset collection?

**Main Findings**:
- 5% border margin + 10-20px crop adjust provides best balance
- Larger crops improve transcription by capturing more context
- Upscaling from 180×180 to 256×256 (1.42×) is acceptable quality
- Recommended: `--border-margin 0.05 --crop-adjust 20 --size 256`

---

## Overview of System Parameters

### Border Detection Parameters

| Parameter | Type | Range | Description | Impact |
|-----------|------|-------|-------------|--------|
| `--border-margin` | float | 0.0-0.5 | % of border to exclude | Controls initial detection size |
| `--crop-adjust` | int | any | Pixels to add/remove | Fine-tunes final crop size |
| `--size` | string | original/128/256 | Output resolution | Determines final video dimensions |
| `--start-time` | float | 0+ | Seconds to skip | Skips intro/non-relevant content |

### Quality vs Context Trade-offs

```
Smaller Crop (15% margin)  →  Less context, more upscaling, tighter crop
Larger Crop (5% margin)    →  More context, less upscaling, wider coverage
```

---

## Quick Reference Commands

### Recommended Production Settings
```bash
# Best quality for sign language transcription
python quick_start.py video.mp4 output \
    --border-margin 0.05 \
    --crop-adjust 20 \
    --size 256 \
    --start-time 480
```

### Testing Different Configurations
```bash
# Tight crop (default)
python quick_start.py video.mp4 output_tight --border-margin 0.15 --size 256

# Balanced crop
python quick_start.py video.mp4 output_balanced --border-margin 0.10 --crop-adjust 10 --size 256

# Wide crop (recommended)
python quick_start.py video.mp4 output_wide --border-margin 0.05 --crop-adjust 20 --size 256
```

---

## Future Improvements to Consider

1. **Adaptive Crop Sizing**: Automatically adjust crop based on signing space usage
2. **Motion-Based Expansion**: Expand crop when hands move to edges
3. **Quality Metrics**: Add PSNR/SSIM measurements for upscaling quality
4. **Multi-Scale Output**: Generate multiple resolutions (128, 256, 512) simultaneously
5. **Border Removal**: Intelligent detection and removal of static border frames

---

## Contributing

To add new research findings or improvement suggestions:

1. Create a new markdown file with descriptive name
2. Follow the format: Question → Analysis → Recommendations → Conclusion
3. Update this README with a reference to your document
4. Include command examples and comparative data where applicable

---

## Related Documentation

- Main README: `../README.md`
- SLI Detector Documentation: `../README_SLI_DETECTOR.md` (if exists)
- Quick Start Guide: See `../quick_start.py --help`

---

**Last Updated**: February 27, 2026
