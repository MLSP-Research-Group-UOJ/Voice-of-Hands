# MediaPipe SLSL Features

Reproducible landmark extraction for the undergraduate project **Personalized Sign Language to Speech for Assistive Communication**. It processes cropped Sri Lankan Sign Language broadcast-interpreter clips without modifying them. This is not How2Sign and contains no How2Sign data. Landmark extraction is computationally efficient, but fast motion and occlusion can cause missing detections; keep the private RGB clips for validation and future re-extraction. Do not horizontally flip clips without linguistic validation.

## Feature layout

Every decoded frame produces `float32 [257]`: 13 selected pose landmarks × `(x,y,z,visibility)` = 52; all 21 left-hand landmarks × `(x,y,z)` = 63; all 21 right-hand landmarks = 63; 25 selected eyebrow/eye/nose/mouth landmarks = 75; and the four presence values `pose,left_hand,right_hand,face` = 4. `feature_schema.json` gives every ordered column. Coordinates are centered on the shoulder midpoint and divided by 2D shoulder distance; z uses that same scale. If the shoulder reference is unsafe, finite original MediaPipe coordinates are retained and `shoulder_reference_ratio` exposes the fallback. Missing groups are zero-filled without interpolation.

## Windows and VS Code setup

Install 64-bit Python 3.11, open the project folder in VS Code, choose **Python: Select Interpreter**, and select `.venv\Scripts\python.exe`.

```powershell
cd "D:\Research\Voice-of-Hands\mediapipe_slsl_features"
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again. MediaPipe is pinned to 0.10.21 because later releases may not provide `mp.solutions.holistic`. Ensure Microsoft Visual C++ runtime and current GPU/display drivers are installed if MediaPipe fails to import.

## Extract

Smoke test two clips:

```powershell
python scripts\extract_features.py `
  --input-dir "D:\Research\Voice-of-Hands\Active_Clips" `
  --output-dir "D:\Research\Voice-of-Hands\SLSL_Features_Test" `
  --max-clips 2
```

Full recursive extraction with previews for named clip IDs:

```powershell
python scripts\extract_features.py `
  --input-dir "D:\Research\Voice-of-Hands\Active_Clips" `
  --output-dir "D:\Research\Voice-of-Hands\SLSL_Features" `
  --recursive `
  --debug-dir "D:\Research\Voice-of-Hands\SLSL_Features\debug" `
  --debug-clips "YT_videoID_0001" "YT_videoID_0002"
```

Use `--model-complexity`, `--min-detection-confidence`, and `--min-tracking-confidence` to override defaults. Add `--overwrite` only for intentional regeneration. Valid `.npz` files are skipped; corrupt/incomplete files are regenerated. Metadata checkpoints after every clip. After Ctrl+C, rerun the same command.

Each compressed `.npz` contains `features [T,257]`, `presence_mask [T,4]`, `fps`, decoded `num_frames`, `duration_sec`, `source_filename`, and `feature_version`. FPS is preserved as metadata and previews use it. Inspect one file:

```powershell
python -c "import numpy as np; p=np.load(r'D:\Research\Voice-of-Hands\SLSL_Features\YT_videoID_0001.npz'); print(p.files, p['features'].shape, p['presence_mask'].mean(0))"
python scripts\validate_features.py "D:\Research\Voice-of-Hands\SLSL_Features"
```

## Quality interpretation

`extraction_metadata.csv` separately reports pose, face, left hand, right hand, both hands, at least one hand, shoulder-reference, and zero-feature ratios. Defaults mark `poor` below pose/face 0.30, any-hand 0.20, or above zero-frame 0.70; `review` below pose/face 0.60, any-hand 0.50, or above zero-frame 0.30. These are configurable dataclass thresholds, not linguistic validity tests. One-handed signs are not rejected for lacking both hands. Review `poor`/`review` rows and the annotated previews. `quality_summary.json` and `.txt` report totals, duration, frames, averages, category counts, lowest-quality clips, duplicate IDs, and corrupt/missing outputs.

## Merge Sinhala transcripts

The transcript CSV must contain unique `clip_id`; all other columns are validated by name and copied where available. The output is UTF-8 with BOM, unmatched records are written to JSON, duplicates stop the merge, and failed/poor features are excluded unless `--include-poor` is explicit. `split` is always blank: create source-video/session/signer-level splits later to avoid leakage.

```powershell
python scripts\merge_transcripts.py `
  --metadata "D:\Research\Voice-of-Hands\SLSL_Features\extraction_metadata.csv" `
  --transcripts "D:\Research\Voice-of-Hands\transcripts.csv" `
  --output "D:\Research\Voice-of-Hands\SLSL_Features\training_manifest.csv"
```

## Reproducibility, privacy, and copyright

The schema records package versions, MediaPipe configuration, UTC creation time, exact command, normalization, missing-data policy, landmark selection, and column order. Preserve the pinned environment and schema alongside results. Broadcast footage, signer appearance, and transcripts may be personal/copyrighted data: limit access, follow consent/licensing and institutional ethics requirements, and do not publish identifiable video without authorization.

