from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import cv2
import mediapipe as mp
import numpy as np

from .config import FEATURE_VERSION, HolisticConfig, QualityThresholds
from .io import atomic_save_npz, validate_arrays, validate_npz
from .landmarks import (FACE_INDICES, FACE_REGIONS, FEATURE_DIM, HAND_NAMES, POSE_INDICES,
                        POSE_NAMES, PRESENCE_ORDER, build_frame, feature_columns)

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
METADATA_FIELDS = ["clip_id", "source_filename", "source_video_path", "feature_path", "num_frames",
 "fps", "duration_sec", "feature_dim", "pose_detected_ratio", "left_hand_detected_ratio",
 "right_hand_detected_ratio", "both_hands_detected_ratio", "at_least_one_hand_detected_ratio",
 "face_detected_ratio", "shoulder_reference_ratio", "zero_feature_frame_ratio", "extraction_status",
 "quality_flag", "error", "feature_version"]


def discover_videos(root: Path, recursive: bool) -> list[Path]:
    iterator = root.rglob("*") if recursive else root.glob("*")
    return sorted((p for p in iterator if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS),
                  key=lambda p: p.relative_to(root).as_posix().casefold())


def quality_flag(r: dict[str, float], t: QualityThresholds = QualityThresholds()) -> str:
    if (r["pose"] < t.poor_pose or r["face"] < t.poor_face or r["any_hand"] < t.poor_any_hand
            or r["zero"] > t.poor_zero_frames): return "poor"
    if (r["pose"] < t.review_pose or r["face"] < t.review_face or r["any_hand"] < t.review_any_hand
            or r["zero"] > t.review_zero_frames): return "review"
    return "good"


def _ratios(mask: np.ndarray, shoulder: np.ndarray, features: np.ndarray) -> dict[str, float]:
    return {"pose": float(mask[:, 0].mean()), "left": float(mask[:, 1].mean()),
            "right": float(mask[:, 2].mean()), "both": float((mask[:, 1] & mask[:, 2]).mean()),
            "any_hand": float((mask[:, 1] | mask[:, 2]).mean()), "face": float(mask[:, 3].mean()),
            "shoulder": float(shoulder.mean()), "zero": float((~mask.any(axis=1)).mean())}


def extract_video(path: Path, output: Path, input_root: Path, output_root: Path,
                  cfg: HolisticConfig, debug_path: Path | None = None) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(path)); fps = float(cap.get(cv2.CAP_PROP_FPS))
    if not cap.isOpened() or not np.isfinite(fps) or fps <= 0:
        cap.release(); raise ValueError("Cannot open video or invalid FPS")
    vectors, masks, shoulders = [], [], []
    writer = None
    with mp.solutions.holistic.Holistic(**cfg.kwargs()) as holistic:
        while True:
            ok, frame = cap.read()
            if not ok: break
            result = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            vector, mask, shoulder_ok = build_frame(result)
            vectors.append(vector); masks.append(mask); shoulders.append(shoulder_ok)
            if debug_path:
                if writer is None:
                    debug_path.parent.mkdir(parents=True, exist_ok=True)
                    writer = cv2.VideoWriter(str(debug_path), cv2.VideoWriter_fourcc(*"mp4v"), fps,
                                             (frame.shape[1], frame.shape[0]))
                _draw_debug(frame, result, mask, path.name, len(vectors)); writer.write(frame)
    cap.release()
    if writer: writer.release()
    if not vectors: raise ValueError("Video decoded zero frames")
    features = np.stack(vectors).astype(np.float32); mask_array = np.stack(masks).astype(np.uint8)
    validate_arrays(features, mask_array, fps, FEATURE_DIM)
    duration = features.shape[0] / fps
    atomic_save_npz(output, features=features, presence_mask=mask_array, fps=np.float32(fps),
                    num_frames=np.int64(features.shape[0]), duration_sec=np.float32(duration),
                    source_filename=np.str_(path.name), feature_version=np.str_(FEATURE_VERSION))
    ratios = _ratios(mask_array, np.asarray(shoulders, dtype=bool), features)
    return _row(path, output, input_root, output_root, features.shape[0], fps, duration, ratios,
                "success", quality_flag(ratios), "")


def _draw_debug(frame: np.ndarray, result: Any, mask: np.ndarray, name: str, number: int) -> None:
    h, w = frame.shape[:2]
    groups = [(getattr(result, "pose_landmarks", None), POSE_INDICES, (0, 255, 0)),
              (getattr(result, "left_hand_landmarks", None), range(21), (255, 0, 0)),
              (getattr(result, "right_hand_landmarks", None), range(21), (0, 0, 255)),
              (getattr(result, "face_landmarks", None), FACE_INDICES, (0, 255, 255))]
    for group, indices, color in groups:
        if group:
            for idx in indices:
                lm = group.landmark[idx]; cv2.circle(frame, (int(lm.x*w), int(lm.y*h)), 2, color, -1)
    cv2.putText(frame, f"{name} frame={number} P/L/R/F={mask.tolist()}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 1, cv2.LINE_AA)


def _row(path: Path, output: Path, input_root: Path, output_root: Path, n: int, fps: float,
         duration: float, r: dict[str, float], status: str, flag: str, error: str) -> dict[str, Any]:
    rel = lambda p, root: p.resolve().relative_to(root.resolve()).as_posix()
    return dict(zip(METADATA_FIELDS, [path.stem, path.name, rel(path, input_root), rel(output, output_root), n,
        fps, duration, FEATURE_DIM, r["pose"], r["left"], r["right"], r["both"], r["any_hand"],
        r["face"], r["shoulder"], r["zero"], status, flag, error, FEATURE_VERSION]))


def write_metadata(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_FIELDS); writer.writeheader(); writer.writerows(rows)
    temp.replace(path)


def write_schema(path: Path, cfg: HolisticConfig, command: str) -> None:
    schema = {"dataset_project": "Personalized Sign Language to Speech (SLSL)",
      "feature_version": FEATURE_VERSION, "mediapipe_version": mp.__version__, "opencv_version": cv2.__version__,
      "numpy_version": np.__version__, "feature_dimension": FEATURE_DIM,
      "arrays": {"features": {"shape": ["T", FEATURE_DIM], "dtype": "float32"},
                 "presence_mask": {"shape": ["T", 4], "dtype": "uint8"}},
      "ordered_feature_columns": feature_columns(), "pose": dict(zip(POSE_INDICES, POSE_NAMES)),
      "hands": HAND_NAMES, "face": [{"index": i, "approximate_region": r} for i,r in zip(FACE_INDICES,FACE_REGIONS)],
      "coordinate_order": ["x","y","z"], "normalization": "shoulder midpoint origin; 2D shoulder-distance scale; z uses same scale",
      "normalization_fallback": "If shoulders/scale are invalid, finite unnormalized MediaPipe coordinates are retained and shoulder_reference_ratio records it.",
      "missing_landmarks": "zero-filled; no interpolation", "presence_mask_order": PRESENCE_ORDER,
      "mediapipe_configuration": cfg.kwargs(), "input_video_extensions": sorted(VIDEO_EXTENSIONS),
      "created_utc": datetime.now(timezone.utc).isoformat(), "command": command}
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")


def run(input_dir: Path, output_dir: Path, metadata_path: Path, recursive: bool, overwrite: bool,
        max_clips: int | None, cfg: HolisticConfig, debug_dir: Path | None,
        debug_clips: set[str]) -> list[dict[str, Any]]:
    videos = discover_videos(input_dir, recursive); videos = videos[:max_clips] if max_clips else videos
    rows: list[dict[str, Any]] = []
    for index, video in enumerate(videos, 1):
        print(f"[{index}/{len(videos)}] Processing {video.name}", flush=True)
        output = output_dir / f"{video.stem}.npz"
        if output.exists() and not overwrite:
            valid, reason = validate_npz(output, FEATURE_DIM)
            if valid:
                with np.load(output, allow_pickle=False) as d:
                    mask=d["presence_mask"]; feat=d["features"]; r=_ratios(mask,np.zeros(len(mask),bool),feat)
                    rows.append(_row(video,output,input_dir,output_dir,len(feat),float(d["fps"]),float(d["duration_sec"]),r,"skipped_existing",quality_flag(r),""))
                write_metadata(metadata_path, rows); continue
            print(f"  Existing output invalid; reprocessing: {reason}")
        try:
            debug = debug_dir / f"{video.stem}_preview.mp4" if debug_dir and (not debug_clips or video.stem in debug_clips) else None
            rows.append(extract_video(video, output, input_dir, output_dir, cfg, debug))
        except Exception as exc:
            empty={k:0.0 for k in ("pose","left","right","both","any_hand","face","shoulder","zero")}
            rows.append(_row(video,output,input_dir,output_dir,0,0,0,empty,"failed","failed",str(exc)))
        write_metadata(metadata_path, rows)
    write_schema(output_dir/"feature_schema.json", cfg, " ".join(sys.argv))
    return rows

