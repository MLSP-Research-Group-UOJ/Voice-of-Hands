from __future__ import annotations

import os
from pathlib import Path
import numpy as np

REQUIRED_KEYS = {"features", "presence_mask", "fps", "num_frames", "duration_sec",
                 "source_filename", "feature_version"}


def validate_arrays(features: np.ndarray, mask: np.ndarray, fps: float, expected_dim: int) -> None:
    if features.ndim != 2 or features.shape[1] != expected_dim:
        raise ValueError(f"features must be [T, {expected_dim}]")
    if mask.shape != (features.shape[0], 4) or mask.dtype != np.uint8:
        raise ValueError("presence_mask must be uint8 [T, 4]")
    if features.dtype != np.float32 or not np.isfinite(features).all():
        raise ValueError("features must be finite float32")
    if not np.isfinite(fps) or fps <= 0 or features.shape[0] <= 0:
        raise ValueError("FPS and decoded frame count must be positive")


def validate_npz(path: Path, expected_dim: int) -> tuple[bool, str]:
    try:
        with np.load(path, allow_pickle=False) as data:
            if not REQUIRED_KEYS.issubset(data.files):
                return False, "missing required keys"
            validate_arrays(data["features"], data["presence_mask"], float(data["fps"]), expected_dim)
            if int(data["num_frames"]) != data["features"].shape[0]:
                return False, "num_frames mismatch"
        return True, ""
    except Exception as exc:
        return False, str(exc)


def atomic_save_npz(path: Path, **arrays: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp.npz")
    try:
        np.savez_compressed(temp, **arrays)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

