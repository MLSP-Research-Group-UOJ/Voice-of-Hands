from __future__ import annotations

from dataclasses import asdict, dataclass

FEATURE_VERSION = "slsl-holistic-v1.0"


@dataclass(frozen=True)
class HolisticConfig:
    model_complexity: int = 1
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    static_image_mode: bool = False
    smooth_landmarks: bool = True
    enable_segmentation: bool = False
    refine_face_landmarks: bool = False

    def kwargs(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class QualityThresholds:
    poor_pose: float = 0.30
    poor_face: float = 0.30
    poor_any_hand: float = 0.20
    poor_zero_frames: float = 0.70
    review_pose: float = 0.60
    review_face: float = 0.60
    review_any_hand: float = 0.50
    review_zero_frames: float = 0.30

