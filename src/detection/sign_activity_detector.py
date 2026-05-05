#!/usr/bin/env python3
"""
MediaPipe-based Sign Language Activity Detector

Detects when the signer is actively signing vs idle (not moving).
Extracts only the active signing segments as small video snippets.

Uses MediaPipe Holistic to track hand and pose landmarks, then calculates
motion energy to determine active vs idle periods.

Usage:
    # Basic: detect active signing and extract clips
    python sign_activity_detector.py input_cropped.mp4 active_clips/

    # Custom thresholds
    python sign_activity_detector.py input.mp4 output/ --threshold 0.02 --min-duration 1.0

    # Just analyze without extracting (preview mode)
    python sign_activity_detector.py input.mp4 output/ --analyze-only
"""

import cv2
import numpy as np
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except ImportError as e:
    print(f"Error: mediapipe is not installed or import failed: {e}")
    print("Install it with: pip install mediapipe")
    sys.exit(1)

# Try to import drawing utilities (only for visualization)
try:
    from mediapipe import solutions
    from mediapipe.framework.formats import landmark_pb2
    MP_DRAWING_AVAILABLE = True
except ImportError:
    MP_DRAWING_AVAILABLE = False


class SignActivityDetector:
    """Detect active signing vs idle periods using MediaPipe landmarks."""

    def __init__(self, motion_threshold=0.015, min_active_duration=1.0,
                 min_idle_duration=0.5, smoothing_window=5, visualize=False,
                 save_visualization=None, detect_horizontal_idle=True,
                 horizontal_y_threshold=0.15, horizontal_min_distance=0.15):
        """
        Args:
            motion_threshold: Minimum motion energy to consider as "active signing".
                              Lower = more sensitive (default: 0.015)
            min_active_duration: Minimum duration (seconds) for an active segment
            min_idle_duration: Minimum idle gap (seconds) to split segments
            smoothing_window: Number of frames for motion smoothing
            visualize: Show real-time visualization of landmark detection
            save_visualization: Path to save visualization video (None = don't save)
            detect_horizontal_idle: Enable horizontal hands idle detection (default: True)
            horizontal_y_threshold: Max Y difference between hands to be horizontal (default: 0.15)
            horizontal_min_distance: Min horizontal distance between hands (default: 0.15)
        """
        self.motion_threshold = motion_threshold
        self.min_active_duration = min_active_duration
        self.min_idle_duration = min_idle_duration
        self.smoothing_window = smoothing_window
        self.visualize = visualize
        self.save_visualization = save_visualization
        self.detect_horizontal_idle = detect_horizontal_idle
        self.horizontal_y_threshold = horizontal_y_threshold
        self.horizontal_min_distance = horizontal_min_distance
        self._last_rest_debug = {}  # Debug info for visualization

        # Initialize MediaPipe tasks for new API (0.10+)
        # Download models if not present
        self._setup_mediapipe_models()
        
        # Drawing utilities for visualization
        if self.visualize:
            if not MP_DRAWING_AVAILABLE:
                print("Warning: MediaPipe drawing utilities not available.")
                print("Visualization will use simple landmark plotting.")
            else:
                self.mp_drawing = solutions.drawing_utils
                self.mp_drawing_styles = solutions.drawing_styles
        
    def _setup_mediapipe_models(self):
        """Setup MediaPipe model files for pose and hand detection."""
        # For MediaPipe 0.10+, we need to download model files
        # Models will be auto-downloaded on first use
        self.pose_landmarker = None
        self.hand_landmarker = None
        self.models_ready = False

    def _download_model_if_needed(self, model_name, url):
        """Download MediaPipe model file if not present."""
        model_dir = os.path.expanduser("~/.mediapipe/models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, model_name)
        
        if not os.path.exists(model_path):
            print(f"    Downloading {model_name}...")
            import urllib.request
            try:
                urllib.request.urlretrieve(url, model_path)
                print(f"    ✓ Downloaded {model_name}")
            except Exception as e:
                print(f"    ✗ Failed to download {model_name}: {e}")
                return None
        
        return model_path
    
    def _create_pose_detector(self):
        """Create MediaPipe Pose detector using tasks API."""
        from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
        from mediapipe.tasks.python import BaseOptions
        
        # Download pose model if needed
        model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
        model_path = self._download_model_if_needed("pose_landmarker_lite.task", model_url)
        
        if not model_path:
            raise RuntimeError("Failed to download pose detection model")
        
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        return PoseLandmarker.create_from_options(options)
    
    def _create_hand_detector(self):
        """Create MediaPipe Hand detector using tasks API."""
        from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
        from mediapipe.tasks.python import BaseOptions
        
        # Download hand model if needed
        model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
        model_path = self._download_model_if_needed("hand_landmarker.task", model_url)
        
        if not model_path:
            raise RuntimeError("Failed to download hand detection model")
        
        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        return HandLandmarker.create_from_options(options)

    def _extract_landmarks_from_frame(self, frame, timestamp_ms, pose_detector, hand_detector):
        """Extract hand and upper body landmarks using new MediaPipe tasks API."""
        points = []
        
        # Convert frame to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        # Detect hands
        hand_results = hand_detector.detect_for_video(mp_image, timestamp_ms)
        
        # Left hand (21 landmarks × 3 coords = 63 values)
        left_hand_found = False
        if hand_results.hand_landmarks:
            for hand_idx, handedness in enumerate(hand_results.handedness):
                if handedness[0].category_name == 'Left':
                    for lm in hand_results.hand_landmarks[hand_idx]:
                        points.extend([lm.x, lm.y, lm.z])
                    left_hand_found = True
                    break
        if not left_hand_found:
            points.extend([0.0] * 63)

        # Right hand (21 landmarks × 3 coords = 63 values)
        right_hand_found = False
        if hand_results.hand_landmarks:
            for hand_idx, handedness in enumerate(hand_results.handedness):
                if handedness[0].category_name == 'Right':
                    for lm in hand_results.hand_landmarks[hand_idx]:
                        points.extend([lm.x, lm.y, lm.z])
                    right_hand_found = True
                    break
        if not right_hand_found:
            points.extend([0.0] * 63)

        # Detect pose
        pose_results = pose_detector.detect_for_video(mp_image, timestamp_ms)
        
        # Upper body (6 key points: shoulders, elbows, wrists)
        if pose_results.pose_landmarks:
            body_indices = [11, 12, 13, 14, 15, 16]
            landmarks = pose_results.pose_landmarks[0]
            for idx in body_indices:
                lm = landmarks[idx]
                points.extend([lm.x, lm.y, lm.z])
        else:
            points.extend([0.0] * 18)
        
        # Check if hands were detected
        has_hands = left_hand_found or right_hand_found

        return np.array(points), has_hands
    
    def _extract_landmarks_from_results(self, pose_results, hand_results):
        """Extract landmarks from already-processed MediaPipe results."""
        points = []
        
        # Left hand (21 landmarks × 3 coords = 63 values)
        left_hand_found = False
        if hand_results.hand_landmarks:
            for hand_idx, handedness in enumerate(hand_results.handedness):
                if handedness[0].category_name == 'Left':
                    for lm in hand_results.hand_landmarks[hand_idx]:
                        points.extend([lm.x, lm.y, lm.z])
                    left_hand_found = True
                    break
        if not left_hand_found:
            points.extend([0.0] * 63)

        # Right hand (21 landmarks × 3 coords = 63 values)
        right_hand_found = False
        if hand_results.hand_landmarks:
            for hand_idx, handedness in enumerate(hand_results.handedness):
                if handedness[0].category_name == 'Right':
                    for lm in hand_results.hand_landmarks[hand_idx]:
                        points.extend([lm.x, lm.y, lm.z])
                    right_hand_found = True
                    break
        if not right_hand_found:
            points.extend([0.0] * 63)

        # Upper body (6 key points: shoulders, elbows, wrists)
        if pose_results.pose_landmarks:
            body_indices = [11, 12, 13, 14, 15, 16]
            landmarks = pose_results.pose_landmarks[0]
            for idx in body_indices:
                lm = landmarks[idx]
                points.extend([lm.x, lm.y, lm.z])
        else:
            points.extend([0.0] * 18)
        
        # Check if hands were detected
        has_hands = left_hand_found or right_hand_found
        
        return np.array(points), has_hands
    
    def _is_horizontal_idle_position(self, pose_results, hand_results):
        """
        Detect if hands are in horizontal rest/idle position.
        Uses POSE landmarks (elbows + wrists) which are always available.
        Checks if forearms (elbow to wrist) are horizontal to the bottom of frame.
        
        Works for both:
        - Hands apart (resting at sides)
        - Hands clasped together (common rest position)
        """
        if not self.detect_horizontal_idle:
            return False
        
        # Only need pose landmarks (always has elbows + wrists)
        if not pose_results.pose_landmarks:
            return False
        
        pose_landmarks = pose_results.pose_landmarks[0]
        
        # MediaPipe pose landmark indices:
        # 13 = left elbow, 14 = right elbow
        # 15 = left wrist, 16 = right wrist
        left_elbow = pose_landmarks[13]
        right_elbow = pose_landmarks[14]
        left_wrist = pose_landmarks[15]
        right_wrist = pose_landmarks[16]
        
        # Condition 1: Both forearms are horizontal
        # Horizontal means elbow.y ≈ wrist.y (parallel to bottom of frame)
        left_forearm_y_diff = abs(left_elbow.y - left_wrist.y)
        right_forearm_y_diff = abs(right_elbow.y - right_wrist.y)
        left_is_horizontal = left_forearm_y_diff < self.horizontal_y_threshold
        right_is_horizontal = right_forearm_y_diff < self.horizontal_y_threshold
        
        # Condition 2: Wrists are in lower portion of frame (not near face)
        # Y increases downward, so > 0.4 means in lower 60% of frame
        left_in_lower = left_wrist.y > 0.4
        right_in_lower = right_wrist.y > 0.4
        
        # Rest = Both forearms horizontal + hands in lower portion
        # No "separated" requirement - clasped hands are also resting!
        is_resting = (left_is_horizontal and right_is_horizontal and 
                     left_in_lower and right_in_lower)
        
        # Store debug info for visualization
        self._last_rest_debug = {
            'left_horizontal': left_is_horizontal,
            'right_horizontal': right_is_horizontal,
            'in_lower': left_in_lower and right_in_lower,
            'left_forearm_diff': left_forearm_y_diff,
            'right_forearm_diff': right_forearm_y_diff,
            'left_wrist_y': left_wrist.y,
            'right_wrist_y': right_wrist.y,
        }
        
        return is_resting
    
    def _draw_landmarks_on_frame(self, frame, pose_results, hand_results, motion_energy, 
                                 is_active, smoothed_energies, frame_idx, is_horizontal_idle=False):
        """Draw MediaPipe landmarks and motion information on frame for visualization."""
        # Create a copy to draw on
        vis_frame = frame.copy()
        h, w = vis_frame.shape[:2]
        
        # Draw landmarks using simple circles and lines
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            for lm in pose_results.pose_landmarks[0]:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(vis_frame, (cx, cy), 3, (0, 255, 0), -1)
        
        # Draw hand landmarks
        if hand_results.hand_landmarks:
            for hand_landmarks in hand_results.hand_landmarks:
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(vis_frame, (cx, cy), 3, (255, 255, 0), -1)
                
                # Draw hand connections
                # Simplified connections for fingers
                connections = [
                    # Thumb
                    (0, 1), (1, 2), (2, 3), (3, 4),
                    # Index
                    (0, 5), (5, 6), (6, 7), (7, 8),
                    # Middle
                    (0, 9), (9, 10), (10, 11), (11, 12),
                    # Ring
                    (0, 13), (13, 14), (14, 15), (15, 16),
                    # Pinky
                    (0, 17), (17, 18), (18, 19), (19, 20),
                    # Palm
                    (5, 9), (9, 13), (13, 17)
                ]
                for start_idx, end_idx in connections:
                    if start_idx < len(hand_landmarks) and end_idx < len(hand_landmarks):
                        start = hand_landmarks[start_idx]
                        end = hand_landmarks[end_idx]
                        pt1 = (int(start.x * w), int(start.y * h))
                        pt2 = (int(end.x * w), int(end.y * h))
                        cv2.line(vis_frame, pt1, pt2, (255, 200, 0), 2)
        
        # Draw motion energy graph
        graph_h = 100
        graph_w = w
        graph = np.zeros((graph_h, graph_w, 3), dtype=np.uint8)
        
        # Draw recent motion history (last 300 frames or available)
        history_len = min(300, len(smoothed_energies))
        if history_len > 1:
            end_idx = min(frame_idx + 1, len(smoothed_energies))
            start_idx = max(0, end_idx - history_len)
            recent_energies = smoothed_energies[start_idx:end_idx]
            
            # Normalize for display
            max_energy = max(max(recent_energies), self.motion_threshold * 2)
            
            # Draw threshold line
            threshold_y = int(graph_h - (self.motion_threshold / max_energy) * graph_h)
            cv2.line(graph, (0, threshold_y), (graph_w, threshold_y), (0, 255, 255), 1)
            
            # Draw motion energy curve
            for i in range(1, len(recent_energies)):
                x1 = int((i - 1) / history_len * graph_w)
                x2 = int(i / history_len * graph_w)
                y1 = int(graph_h - (recent_energies[i-1] / max_energy) * graph_h)
                y2 = int(graph_h - (recent_energies[i] / max_energy) * graph_h)
                
                # Color based on activity
                color = (0, 255, 0) if recent_energies[i] > self.motion_threshold else (100, 100, 100)
                cv2.line(graph, (x1, y1), (x2, y2), color, 2)
        
        # Add info overlay with better layout
        info_height = 180  # Increased height for more labels
        overlay = np.zeros((info_height, w, 3), dtype=np.uint8)
        
        # Row 1: Status (left) and Resting (right)
        # Status - differentiate between horizontal idle and motion idle
        if is_horizontal_idle:
            status = "IDLE (Horizontal)"
            status_color = (0, 165, 255)  # Orange for horizontal idle
        elif is_active:
            status = "ACTIVE"
            status_color = (0, 255, 0)  # Green for active
        else:
            status = "IDLE (Low Motion)"
            status_color = (100, 100, 100)  # Gray for low motion idle
        cv2.putText(overlay, f"Status: {status}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
        
        # Row 2: Motion and Hands
        cv2.putText(overlay, f"Motion: {motion_energy:.4f}", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        hands_info = "Hands: YES" if hand_results.hand_landmarks else "Hands: NO"
        hands_color = (0, 255, 0) if hand_results.hand_landmarks else (0, 0, 255)
        right_x = max(10, w // 2 + 5)
        cv2.putText(overlay, hands_info, (right_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hands_color, 1)
        
        # Row 3: Threshold
        cv2.putText(overlay, f"Threshold: {self.motion_threshold:.4f}", (10, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Row 4: Frame info (left) and Rest status (right)
        cv2.putText(overlay, f"Frame: {frame_idx}", (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        if self.detect_horizontal_idle:
            resting_info = "Rest: YES" if is_horizontal_idle else "Rest: NO"
            resting_color = (0, 165, 255) if is_horizontal_idle else (150, 150, 150)
            right_x = max(10, w // 2 + 5)
            cv2.putText(overlay, resting_info, (right_x, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, resting_color, 1)
        
        # Row 5: Detailed status explanation with debug info
        if is_horizontal_idle:
            detail = "Forearms horizontal, hands lowered"
            detail_color = (0, 165, 255)
        elif is_active:
            detail = "Active signing motion detected"
            detail_color = (0, 255, 0)
        else:
            detail = "Motion below threshold"
            detail_color = (150, 150, 150)
        cv2.putText(overlay, detail, (10, 125),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, detail_color, 1)
        
        # Row 6: Debug info for horizontal detection (if enabled and Rest: NO)
        if self.detect_horizontal_idle and not is_horizontal_idle and hasattr(self, '_last_rest_debug') and self._last_rest_debug:
            debug = self._last_rest_debug
            issues = []
            if not debug.get('left_horizontal'): 
                issues.append(f"L-arm:{debug.get('left_forearm_diff', 0):.2f}")
            if not debug.get('right_horizontal'): 
                issues.append(f"R-arm:{debug.get('right_forearm_diff', 0):.2f}")
            if not debug.get('in_lower'): 
                issues.append(f"High(L:{debug.get('left_wrist_y', 0):.2f},R:{debug.get('right_wrist_y', 0):.2f})")
            
            if issues:
                debug_text = f"Not rest: {', '.join(issues)}"
                cv2.putText(overlay, debug_text, (10, 148),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 100, 100), 1)
        elif self.detect_horizontal_idle and not is_horizontal_idle and not pose_results.pose_landmarks:
            cv2.putText(overlay, "Not rest: No pose detected", (10, 148),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 100, 100), 1)
        
        # Instructions at bottom
        cv2.putText(overlay, "Press 'q' to quit, 'p' to pause", (10, 155),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        # Combine all elements
        combined = np.vstack([overlay, vis_frame, graph])
        
        return combined

    def analyze_video(self, video_path):
        """
        Analyze video to detect active signing periods.

        Returns:
            dict with 'fps', 'total_frames', 'motion_energy' (per-frame),
            'active_segments' (list of (start_sec, end_sec))
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video '{video_path}'")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(f"Analyzing video: {video_path}")
        print(f"  FPS: {fps:.1f}, Frames: {total_frames}, Duration: {duration:.1f}s")
        print(f"  Motion threshold: {self.motion_threshold}")
        print(f"  Min active duration: {self.min_active_duration}s")
        print()

        # Initialize MediaPipe detectors
        try:
            print("  Initializing MediaPipe detectors...")
            pose_detector = self._create_pose_detector()
            hand_detector = self._create_hand_detector()
            print("  MediaPipe detectors ready!")
        except Exception as e:
            print(f"Error initializing MediaPipe: {e}")
            print("Note: MediaPipe 0.10+ requires model files to be downloaded on first use.")
            cap.release()
            return None

        prev_landmarks = None
        motion_energies = []
        hand_detected = []
        frame_count = 0
        paused = False
        
        # Create window for visualization if enabled
        if self.visualize:
            window_name = "Sign Language Activity Detection (Press 'q' to quit, 'p' to pause)"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 900)
        
        # Setup video writer for saving visualization
        vis_writer = None
        temp_vis_path = None
        if self.save_visualization:
            # Get first frame to determine output dimensions
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, first_frame = cap.read()
            if ret:
                h, w = first_frame.shape[:2]
                # Output dimensions: info(180) + frame(h) + graph(100)
                out_h = 180 + h + 100
                out_w = w
                
                # Use avi temporarily for better compatibility with OpenCV
                temp_vis_path = self.save_visualization.replace('.mp4', '_temp.avi')
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                vis_writer = cv2.VideoWriter(temp_vis_path, fourcc, fps, (out_w, out_h))
                print(f"  Saving visualization to: {self.save_visualization}")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start

        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert BGR to RGB for MediaPipe
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate timestamp in milliseconds
                timestamp_ms = int((frame_count / fps) * 1000)

                # Get MediaPipe results
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                hand_results = hand_detector.detect_for_video(mp_image, timestamp_ms)
                pose_results = pose_detector.detect_for_video(mp_image, timestamp_ms)

                # Extract landmarks from results
                try:
                    landmarks, has_hands = self._extract_landmarks_from_results(
                        pose_results, hand_results
                    )
                except Exception as e:
                    if frame_count == 0:
                        print(f"  Warning: MediaPipe processing error: {e}")
                        print("  Continuing with zero landmarks...")
                    landmarks = np.zeros(144)  # 63 + 63 + 18
                    has_hands = False

                hand_detected.append(has_hands)

                # Calculate motion energy (difference between consecutive frames)
                if prev_landmarks is not None:
                    # Only compute motion for non-zero landmarks (detected parts)
                    mask = (landmarks != 0) & (prev_landmarks != 0)
                    if mask.any():
                        diff = np.abs(landmarks[mask] - prev_landmarks[mask])
                        energy = np.mean(diff)
                    else:
                        energy = 0.0
                    motion_energies.append(energy)
                else:
                    motion_energies.append(0.0)

                # Calculate smoothed energy for current frame
                if len(motion_energies) >= self.smoothing_window:
                    recent = motion_energies[-self.smoothing_window:]
                    smoothed_energy = np.mean(recent)
                else:
                    smoothed_energy = motion_energies[-1] if motion_energies else 0.0
                
                # Check for horizontal idle position (additional idle condition)
                # Pass both pose and hand results to check forearm angles
                is_horizontal_idle = self._is_horizontal_idle_position(pose_results, hand_results)
                
                # Activity determination: active if motion threshold met AND not in horizontal idle
                is_active = smoothed_energy > self.motion_threshold and not is_horizontal_idle

                # Visualization
                if self.visualize or self.save_visualization:
                    # For visualization, use all energies computed so far
                    smoothed_all = np.array(motion_energies)
                    if len(smoothed_all) > self.smoothing_window:
                        kernel = np.ones(self.smoothing_window) / self.smoothing_window
                        smoothed_all = np.convolve(smoothed_all, kernel, mode='same')
                    
                    vis_frame = self._draw_landmarks_on_frame(
                        frame, pose_results, hand_results, 
                        motion_energies[-1], is_active,
                        smoothed_all.tolist() if isinstance(smoothed_all, np.ndarray) else smoothed_all,
                        frame_count, is_horizontal_idle
                    )
                    
                    # Show visualization window
                    if self.visualize:
                        cv2.imshow(window_name, vis_frame)
                    
                    # Write to video file
                    if self.save_visualization and vis_writer is not None:
                        vis_writer.write(vis_frame)

                prev_landmarks = landmarks.copy()
                frame_count += 1

                if frame_count % 100 == 0 and not self.visualize:
                    progress = (frame_count / total_frames) * 100
                    save_status = " (saving visualization)" if self.save_visualization else ""
                    print(f"  Analyzing: {frame_count}/{total_frames} ({progress:.1f}%){save_status}")
            
            # Handle keyboard input
            if self.visualize:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n  Visualization stopped by user")
                    break
                elif key == ord('p'):
                    paused = not paused
                    status_msg = "PAUSED" if paused else "RESUMED"
                    print(f"  {status_msg}")
            elif self.save_visualization:
                # Still check for early exit even when not showing visualization
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n  Processing stopped by user")
                    break
            else:
                # Non-visualization mode, no delay
                pass

        cap.release()
        
        # Close video writer if used
        if vis_writer is not None:
            vis_writer.release()
            print(f"  Visualization frames saved")
            
            # Convert AVI to MP4 with proper codec and add audio
            if self.save_visualization and temp_vis_path:
                print(f"  Converting to MP4 and adding audio...")
                
                try:
                    import subprocess
                    subprocess.run([
                        'ffmpeg', '-y', '-loglevel', 'warning',
                        '-i', temp_vis_path,
                        '-i', video_path,
                        '-c:v', 'libx264',      # H.264 codec for video
                        '-preset', 'medium',     # Encoding speed
                        '-crf', '23',            # Quality
                        '-c:a', 'aac',           # AAC audio
                        '-b:a', '128k',          # Audio bitrate
                        '-map', '0:v:0',         # Video from temp file
                        '-map', '1:a:0?',        # Audio from original (if exists)
                        '-shortest',             # Match shortest stream
                        self.save_visualization
                    ], check=True, timeout=120)
                    os.remove(temp_vis_path)
                    print(f"  ✓ Visualization saved: {self.save_visualization}")
                except Exception as e:
                    print(f"  Warning: Could not convert to MP4: {e}")
                    print(f"  Temporary file available at: {temp_vis_path}")
        
        # Close visualization window if it was created
        if self.visualize:
            cv2.destroyAllWindows()
        
        # Close detectors
        pose_detector.close()
        hand_detector.close()

        motion_energies = np.array(motion_energies)

        # Smooth motion energy
        if len(motion_energies) > self.smoothing_window:
            kernel = np.ones(self.smoothing_window) / self.smoothing_window
            smoothed = np.convolve(motion_energies, kernel, mode='same')
        else:
            smoothed = motion_energies

        # Detect active segments
        is_active = smoothed > self.motion_threshold
        active_segments = self._find_segments(is_active, fps)

        # Statistics
        active_time = sum(end - start for start, end in active_segments)
        idle_time = duration - active_time
        hands_detected_pct = (sum(hand_detected) / len(hand_detected) * 100
                              if hand_detected else 0)

        print(f"\n  Analysis complete!")
        print(f"  Hands detected in: {hands_detected_pct:.1f}% of frames")
        print(f"  Active signing: {active_time:.1f}s ({active_time/duration*100:.1f}%)")
        print(f"  Idle periods: {idle_time:.1f}s ({idle_time/duration*100:.1f}%)")
        print(f"  Active segments found: {len(active_segments)}")

        return {
            'fps': fps,
            'total_frames': total_frames,
            'duration': duration,
            'motion_energy': smoothed.tolist(),
            'raw_motion_energy': motion_energies.tolist(),
            'active_segments': active_segments,
            'active_time': active_time,
            'idle_time': idle_time,
            'hands_detected_pct': hands_detected_pct,
        }

    def _find_segments(self, is_active, fps):
        """Find contiguous active segments, merging short gaps."""
        segments = []
        in_segment = False
        start_frame = 0

        for i, active in enumerate(is_active):
            if active and not in_segment:
                start_frame = i
                in_segment = True
            elif not active and in_segment:
                end_frame = i
                segments.append((start_frame, end_frame))
                in_segment = False

        if in_segment:
            segments.append((start_frame, len(is_active)))

        # Merge segments with small idle gaps between them
        min_idle_frames = int(self.min_idle_duration * fps)
        merged = []
        for start, end in segments:
            if merged and (start - merged[-1][1]) < min_idle_frames:
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))

        # Filter out segments shorter than min_active_duration
        min_active_frames = int(self.min_active_duration * fps)
        filtered = [(s, e) for s, e in merged if (e - s) >= min_active_frames]

        # Convert to seconds
        return [(s / fps, e / fps) for s, e in filtered]

    def extract_active_clips(self, video_path, output_dir, analysis):
        """Extract only the active signing segments as separate clips."""
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        fps = analysis['fps']
        segments = analysis['active_segments']

        if not segments:
            print("No active segments found!")
            return []

        print(f"\nExtracting {len(segments)} active signing clips...")

        clip_paths = []

        for i, (start_sec, end_sec) in enumerate(segments):
            duration = end_sec - start_sec

            clip_name = f"active_{i+1:03d}_{start_sec:.1f}s-{end_sec:.1f}s.mp4"
            clip_path = os.path.join(output_dir, clip_name)
            
            # Use ffmpeg to extract clip directly with both video and audio
            try:
                import subprocess
                subprocess.run([
                    'ffmpeg', '-y', '-loglevel', 'warning',
                    '-i', video_path,
                    '-ss', str(start_sec),
                    '-t', str(duration),
                    '-c:v', 'libx264',      # Use h264 codec for video
                    '-preset', 'medium',     # Encoding speed
                    '-crf', '23',            # Quality (lower=better, 23=default)
                    '-c:a', 'aac',           # AAC audio codec
                    '-b:a', '128k',          # Audio bitrate
                    clip_path
                ], check=True, timeout=60)
                
                print(f"  [{i+1}/{len(segments)}] {clip_name} ({duration:.1f}s)")
                
            except subprocess.TimeoutExpired:
                print(f"  [{i+1}/{len(segments)}] ⚠ Timeout extracting {clip_name}")
                continue
            except Exception as e:
                print(f"  [{i+1}/{len(segments)}] ✗ Error extracting {clip_name}: {e}")
                continue

            clip_paths.append({
                'path': clip_path,
                'start': round(start_sec, 2),
                'end': round(end_sec, 2),
                'duration': round(duration, 2),
            })

        cap.release()

        # Save metadata
        metadata = {
            'source_video': video_path,
            'total_duration': analysis['duration'],
            'active_time': analysis['active_time'],
            'idle_time': analysis['idle_time'],
            'hands_detected_pct': analysis['hands_detected_pct'],
            'motion_threshold': self.motion_threshold,
            'min_active_duration': self.min_active_duration,
            'clips': clip_paths,
        }

        metadata_path = os.path.join(output_dir, 'activity_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"\n  Metadata saved: {metadata_path}")
        print(f"  Total active clips: {len(clip_paths)}")
        total_active = sum(c['duration'] for c in clip_paths)
        print(f"  Total active duration: {total_active:.1f}s "
              f"(removed {analysis['idle_time']:.1f}s of idle time)")

        return clip_paths


def main():
    parser = argparse.ArgumentParser(
        description="Detect active signing vs idle periods using MediaPipe"
    )
    parser.add_argument("input", help="Input video (ideally the cropped signer video)")
    parser.add_argument("output", help="Output directory for active clips")
    parser.add_argument("--threshold", type=float, default=0.015,
                        help="Motion threshold (lower=more sensitive, default: 0.015)")
    parser.add_argument("--min-duration", type=float, default=1.0,
                        help="Minimum active segment duration in seconds (default: 1.0)")
    parser.add_argument("--min-idle", type=float, default=0.5,
                        help="Minimum idle gap to split segments in seconds (default: 0.5)")
    parser.add_argument("--smoothing", type=int, default=5,
                        help="Smoothing window size in frames (default: 5)")
    parser.add_argument("--analyze-only", action="store_true",
                        help="Only analyze, don't extract clips")
    parser.add_argument("--visualize", action="store_true",
                        help="Show real-time visualization of landmark detection (Press 'q' to quit, 'p' to pause)")
    parser.add_argument("--save-visualization", type=str, default=None,
                        help="Save visualization video to file (e.g., visualization.mp4)")
    parser.add_argument("--no-horizontal-idle", action="store_true",
                        help="Disable horizontal hands idle detection (default: enabled)")
    parser.add_argument("--horizontal-y-threshold", type=float, default=0.15,
                        help="Max Y difference for horizontal hands detection (default: 0.15)")
    parser.add_argument("--horizontal-min-distance", type=float, default=0.15,
                        help="Min X distance between hands for horizontal detection (default: 0.15)")

    args = parser.parse_args()

    detector = SignActivityDetector(
        motion_threshold=args.threshold,
        min_active_duration=args.min_duration,
        min_idle_duration=args.min_idle,
        smoothing_window=args.smoothing,
        visualize=args.visualize,
        save_visualization=args.save_visualization,
        detect_horizontal_idle=not args.no_horizontal_idle,
        horizontal_y_threshold=args.horizontal_y_threshold,
        horizontal_min_distance=args.horizontal_min_distance
    )

    # Analyze the video
    analysis = detector.analyze_video(args.input)

    if analysis is None:
        sys.exit(1)

    # Print segment details
    if analysis['active_segments']:
        print(f"\nActive signing segments:")
        for i, (start, end) in enumerate(analysis['active_segments']):
            print(f"  {i+1}. {start:.1f}s - {end:.1f}s ({end-start:.1f}s)")

    if args.analyze_only:
        print("\n(Analyze-only mode — no clips extracted)")
        # Save analysis
        os.makedirs(args.output, exist_ok=True)
        analysis_path = os.path.join(args.output, 'motion_analysis.json')
        # Remove large arrays for JSON
        save_data = {k: v for k, v in analysis.items()
                     if k not in ('motion_energy', 'raw_motion_energy')}
        with open(analysis_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"Analysis saved: {analysis_path}")
    else:
        # Extract active clips
        detector.extract_active_clips(args.input, args.output, analysis)

    print("\nDone!")


if __name__ == "__main__":
    main()
