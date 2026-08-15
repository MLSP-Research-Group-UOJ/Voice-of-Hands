from __future__ import annotations

from typing import Any, Iterable
import numpy as np

POSE_INDICES = [0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
POSE_NAMES = ["nose", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
              "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index",
              "right_index", "left_thumb", "right_thumb"]
FACE_INDICES = [46, 53, 52, 65, 55, 276, 283, 282, 295, 285, 33, 133, 159, 145,
                362, 263, 386, 374, 1, 61, 291, 13, 14, 78, 308]
FACE_REGIONS = (["left_eyebrow"] * 5 + ["right_eyebrow"] * 5 + ["left_eye"] * 4 +
                ["right_eye"] * 4 + ["nose"] + ["mouth"] * 6)
HAND_NAMES = ["wrist", "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
              "index_mcp", "index_pip", "index_dip", "index_tip", "middle_mcp",
              "middle_pip", "middle_dip", "middle_tip", "ring_mcp", "ring_pip",
              "ring_dip", "ring_tip", "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip"]
PRESENCE_ORDER = ["pose_present", "left_hand_present", "right_hand_present", "face_present"]
FEATURE_DIM = len(POSE_INDICES) * 4 + 21 * 3 * 2 + len(FACE_INDICES) * 3 + 4


def _select(group: Any, indices: Iterable[int], width: int) -> np.ndarray:
    out = np.zeros((len(list(indices)), width), np.float32)
    if group is None:
        return out
    for row, idx in enumerate(indices):
        lm = group.landmark[idx]
        values = [lm.x, lm.y, lm.z]
        if width == 4:
            values.append(getattr(lm, "visibility", 0.0))
        out[row] = values
    return out


def build_frame(results: Any) -> tuple[np.ndarray, np.ndarray, bool]:
    """Build one shoulder-normalized vector; bool reports a valid shoulder reference."""
    pose_group = getattr(results, "pose_landmarks", None)
    left_group = getattr(results, "left_hand_landmarks", None)
    right_group = getattr(results, "right_hand_landmarks", None)
    face_group = getattr(results, "face_landmarks", None)
    pose = _select(pose_group, POSE_INDICES, 4)
    left = _select(left_group, range(21), 3)
    right = _select(right_group, range(21), 3)
    face = _select(face_group, FACE_INDICES, 3)
    shoulder_ok = False
    if pose_group is not None:
        ls, rs = pose_group.landmark[11], pose_group.landmark[12]
        scale = float(np.hypot(ls.x - rs.x, ls.y - rs.y))
        valid = np.isfinite([ls.x, ls.y, ls.z, rs.x, rs.y, rs.z, scale]).all()
        if valid and scale > 1e-6:
            origin = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2, (ls.z + rs.z) / 2], np.float32)
            for array, present in ((pose[:, :3], True), (left, left_group is not None),
                                   (right, right_group is not None), (face, face_group is not None)):
                if present:
                    array[:] = (array - origin) / scale
            shoulder_ok = True
    presence = np.array([pose_group is not None, left_group is not None,
                         right_group is not None, face_group is not None], np.uint8)
    vector = np.concatenate([pose.ravel(), left.ravel(), right.ravel(), face.ravel(),
                             presence.astype(np.float32)]).astype(np.float32)
    if vector.size != FEATURE_DIM or not np.isfinite(vector).all():
        raise ValueError("Invalid feature vector")
    return vector, presence, shoulder_ok


def feature_columns() -> list[str]:
    cols = [f"pose.{name}.{c}" for name in POSE_NAMES for c in ("x", "y", "z", "visibility")]
    cols += [f"left_hand.{name}.{c}" for name in HAND_NAMES for c in "xyz"]
    cols += [f"right_hand.{name}.{c}" for name in HAND_NAMES for c in "xyz"]
    cols += [f"face.{idx}.{region}.{c}" for idx, region in zip(FACE_INDICES, FACE_REGIONS) for c in "xyz"]
    return cols + PRESENCE_ORDER

