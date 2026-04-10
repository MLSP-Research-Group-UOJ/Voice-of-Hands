# Version 01 - Test Scripts and Alternative Implementations

This folder contains test scripts, demos, and alternative implementations that were used during development and testing. These scripts are fully functional and can be run anytime for testing or experimentation.

---

## Contents

### Test Scripts

**`test_border_margins.py`** - Test different border margin values
```bash
python test_border_margins.py videos/video.mp4
```
Tests margins: 0.10, 0.15, 0.20 and shows detected sizes

**`test_start_time.py`** - Test start_time parameter
```bash
python test_start_time.py videos/video.mp4 480
```
Verifies detection starts from specified time (e.g., 8 minutes)

**`test_crop_adjust.py`** - Test crop_adjust parameter
```bash
python test_crop_adjust.py videos/video.mp4 480
```
Demonstrates how crop_adjust changes final crop size

**`test_simple_border.py`** - Simple border detection test
```bash
python test_simple_border.py videos/video.mp4
```
Basic test of border detection functionality

**`test_cli_sizes.py`** - Test CLI size options
```bash
python test_cli_sizes.py
```
Tests --size parameter with original/128/256 options

**`test_256_output.py`** - Test 256×256 output
```bash
python test_256_output.py videos/video.mp4
```
Specific test for 256×256 resize output

**`test_border_exact_size.py`** - Test exact border cropping
```bash
python test_border_exact_size.py videos/video.mp4
```
Verifies border detection produces exact interior size

### Demo Scripts

**`demo_size_options.py`** - Demonstrate size options
```bash
python demo_size_options.py videos/video.mp4
```
Shows comparison of original/128/256 output sizes

**`demo_border_margins.py`** - Demonstrate border margins
```bash
python demo_border_margins.py videos/video.mp4
```
Compares different border margin settings

### Visualization Tools

**`preview_border_detection.py`** - Generate visual previews
```bash
# Basic preview
python preview_border_detection.py videos/video.mp4

# Preview from 8 minutes
python preview_border_detection.py videos/video.mp4 480

# Preview with crop adjustment
python preview_border_detection.py videos/video.mp4 480 10
```
Creates comprehensive preview showing:
- Different border margins (5%, 10%, 15%, 20%)
- Crop adjustment effect
- Multiple output sizes (original, 128×128, 256×256)

Saves to: `border_detection_preview_*.jpg`

---

## Usage Notes

### Running Test Scripts

All test scripts can be run directly from the version_01 folder:

```bash
cd version_01
python test_border_margins.py ../videos/Parliament_Live_01-12-2025.mp4
```

Or from the main folder:

```bash
python version_01/test_border_margins.py videos/Parliament_Live_01-12-2025.mp4
```

### Common Test Video

Most tests use: `videos/Parliament_Live_01-12-2025.mp4`
- Duration: 59:54
- Resolution: 1280×720
- Interpreter region: ~177×177 full box, 124×124 interior (15% margin)

---

## Development Timeline

These scripts were created during system development to:

1. **Verify border detection accuracy** - Test different margin values
2. **Test parameter combinations** - Ensure parameters work independently
3. **Generate visual documentation** - Create preview images for analysis
4. **Validate audio preservation** - Test ffmpeg integration
5. **Performance testing** - Measure processing speed and quality

---

## Key Findings from Tests

### Border Margin Effect
- 5% margin: 160×160 pixels (largest crop)
- 10% margin: 142×142 pixels
- 15% margin: 124×124 pixels (default)
- 20% margin: 106×106 pixels (tightest crop)

### Crop Adjust Effect (with 15% margin)
- +0px: 124×124 pixels (no adjustment)
- +10px: 144×144 pixels (+20px total size)
- +20px: 164×164 pixels (+40px total size)
- -5px: 114×114 pixels (-10px total size)

### Quality Analysis (256×256 output)
- 124×124 → 256×256: 2.06× upscale (noticeable blur)
- 142×142 → 256×256: 1.80× upscale (moderate blur)
- 180×180 → 256×256: 1.42× upscale (minimal blur) ✅ Recommended
- 200×200 → 256×256: 1.28× upscale (excellent quality) ✅ Best

---

## Experimental Features

Some scripts test features that may be integrated into the main system:

- Multi-margin preview generation
- Adaptive crop sizing based on motion
- Alternative detection methods (motion, edge, pose)
- Quality metrics calculation

---

## Maintenance

These scripts are kept for:
- **Regression testing**: Verify updates don't break functionality
- **Feature experimentation**: Test new ideas before integration
- **Documentation**: Visual examples for understanding system behavior
- **Troubleshooting**: Debug issues with specific parameters

All scripts are maintained and functional. They can be run anytime without modifications.

---

## Moving Forward

To use test scripts on new videos:

1. Add video to `../videos/` folder
2. Run desired test script
3. Check output in main folder or specified output directory
4. Review generated previews/images for visual confirmation

Example workflow:
```bash
# Test new video
python version_01/test_border_margins.py videos/new_video.mp4

# Generate preview
python version_01/preview_border_detection.py videos/new_video.mp4 0

# Test with parameters
python version_01/test_crop_adjust.py videos/new_video.mp4 0
```

---

**Version**: 1.0  
**Created**: During development (January-February 2026)  
**Purpose**: Testing, validation, and experimentation  
**Status**: Fully functional, maintained for reference
