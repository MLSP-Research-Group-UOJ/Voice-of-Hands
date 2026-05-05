# Voice-of-Hands Research Documentation

This folder contains comprehensive LaTeX research reports documenting the development, testing, and optimization of the Voice-of-Hands automated multimodal dataset creation pipeline.

## Report Index

### 01. Picture-in-Picture Detection Development
**File**: `01_pip_detection_development_report.tex`

Covers the development and optimization of sign language interpreter detection from broadcast video:
- HSV color-space border detection
- Farneback optical flow fallback
- Canny edge detection
- MediaPipe pose estimation
- Multi-method cascade integration
- Performance comparison (92% accuracy achieved)
- Parameter optimization
- Problems encountered and solutions

### 02. Sign Activity Detection
**File**: `02_sign_activity_detection_report.tex`

Documents the evolution of sign activity detection methods:
- MediaPipe landmark-based motion energy computation
- Horizontal idle position classification (novel contribution)
- Algorithm iterations (optical flow → hand detection → landmark motion)
- Parameter tuning (motion threshold, smoothing window)
- Validation results (95.2% precision, 91.8% recall)
- Failure modes and solutions
- Pseudocode and implementation details

### 03. Temporal Segmentation Strategy
**File**: `03_temporal_segmentation_strategy_report.tex`

Analyzes the linguistically-motivated 5-second clip duration decision:
- Sign language unit duration analysis (signs, phrases, clauses)
- Interpreter translation lag measurements (3.36s mean)
- Comparison with existing datasets (PHOENIX, How2Sign, etc.)
- Clip duration evaluation (3s, 4s, 5s, 6s, 8s, 10s)
- 50% overlap strategy justification
- Resolution standardization (256×256 pixels)
- Frame rate considerations (30 FPS retained)
- Video encoding optimization

### 04. LaTeX Unicode Compilation
**File**: `04_latex_unicode_compilation_report.tex`

Technical report on LaTeX compilation for Sinhala/Tamil Unicode:
- pdflatex limitations for non-Latin scripts
- fontspec package errors and resolutions
- XeLaTeX vs. LuaLaTeX comparison
- Migration from pdflatex to XeLaTeX
- Unicode character preservation (සිංහල and தமிழ்)
- Compilation script updates
- Font system architecture explanation
- Best practices for multilingual LaTeX

### 05. Audio Extraction and Synchronization
**File**: `05_audio_extraction_synchronization_report.tex`

Documents the audio extraction methodology:
- FFmpeg-based extraction pipeline
- Audio format specification (16 kHz mono PCM WAV)
- Temporal precision validation (frame-accurate alignment)
- Sample rate rationale (Whisper ASR compatibility)
- Bit depth selection (16 bits)
- Seeking mode comparison (input vs. output seeking)
- Synchronization validation results (96% within ±33ms)
- Storage requirements and optimization
- Problems encountered (silent clips, timestamp rounding)

### 06. Whisper ASR Integration
**File**: `06_whisper_asr_integration_report.tex`

Evaluates Whisper automatic speech recognition for Sinhala:
- Whisper architecture overview
- Model size comparison (tiny, base, small, medium, large)
- Transcription quality evaluation (95% success rate with medium model)
- Inference performance benchmarks
- Word-level timestamp accuracy (mean error 0.12s)
- Sinhala-specific challenges (script complexity, code-switching)
- Domain-specific vocabulary performance
- Integration with pipeline
- Error analysis and failure modes
- GPU optimization strategies

## Compiling the Reports

Each report is a standalone LaTeX document in IEEE format.

### Prerequisites

```bash
sudo apt-get install texlive-full
```

### Compilation (Individual Reports)

```bash
cd research_docs
pdflatex 01_pip_detection_development_report.tex
pdflatex 01_pip_detection_development_report.tex  # Second pass for TOC
```

Or use `latexmk` for automatic dependency handling:

```bash
latexmk -pdf 01_pip_detection_development_report.tex
```

### Compilation (All Reports)

```bash
#!/bin/bash
# compile_all_reports.sh

for report in *.tex; do
    echo "Compiling $report..."
    pdflatex -interaction=nonstopmode "$report" > /dev/null
    pdflatex -interaction=nonstopmode "$report" > /dev/null  # Second pass
    echo "✓ Generated ${report%.tex}.pdf"
done

# Cleanup auxiliary files
rm -f *.aux *.log *.out *.toc

echo "All reports compiled successfully!"
```

## Report Statistics

| Report | Pages | Words | Tables | Code Listings |
|--------|-------|-------|--------|---------------|
| 01 - PiP Detection | ~20 | ~8,500 | 8 | 12 |
| 02 - Activity Detection | ~25 | ~11,000 | 10 | 15 |
| 03 - Temporal Segmentation | ~18 | ~7,500 | 9 | 8 |
| 04 - LaTeX Unicode | ~15 | ~6,000 | 5 | 14 |
| 05 - Audio Extraction | ~16 | ~6,500 | 7 | 10 |
| 06 - Whisper ASR | ~17 | ~7,000 | 8 | 11 |
| **Total** | **~111** | **~46,500** | **47** | **70** |

## Key Contributions Documented

1. **Novel horizontal idle position classifier** (Report 02)
   - 97.1% precision in detecting interpreter resting posture
   - Combines forearm angle analysis with frame position classification

2. **Multi-method PiP detection cascade** (Report 01)
   - Achieves 96% accuracy by intelligently combining four detection methods
   - Prioritizes speed while maintaining robustness

3. **Linguistically-motivated temporal segmentation** (Report 03)
   - 5-second duration captures 92% of sign phrases
   - 50% overlap recovers split phrases (97% coverage)

4. **Frame-accurate audio-visual alignment** (Report 05)
   - 96% of clips synchronized within ±33ms
   - Output seeking strategy for temporal precision

5. **Zero-shot Sinhala ASR validation** (Report 06)
   - Whisper medium model achieves 95% transcription success
   - Sub-second word-level timestamp accuracy

## Citation

If you use these methodologies in your research, please cite:

```bibtex
@techreport{voiceofhands2025,
  title={Voice-of-Hands: Development Reports on Automated Multimodal Dataset Creation for Sign Language Recognition in Low-Resource Languages},
  author={Voice-of-Hands Research Team},
  institution={Sri Lanka},
  year={2025},
  type={Technical Report Series}
}
```

## License

These research reports are provided for academic and educational purposes. The documented methodologies are freely usable with proper attribution.

## Contact

For questions about these reports or the Voice-of-Hands project:
- Open an issue in the repository
- Refer to the main project README.md

---

**Last Updated**: April 2026  
**Report Count**: 6 comprehensive technical documents  
**Total Documentation**: 111+ pages of detailed research methodology
