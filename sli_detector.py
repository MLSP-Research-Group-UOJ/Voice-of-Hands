"""
Sign Language Interpreter (SLI) Region Detector
Dataset Collection System - Focuses on detecting and extracting interpreter regions
surrounded by light-colored borders for precise cropping.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """Result of SLI region detection"""
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    method: str


class SLIDetector:
    """
    Multi-method detector for Sign Language Interpreter regions.
    Uses lightweight, non-training approaches.
    """
    
    def __init__(self, video_path: str, border_margin: float = 0.15):
        """
        Initialize SLI Detector.
        
        Args:
            video_path: Path to video file
            border_margin: How much border to exclude (0.0-0.5). Default 0.15 = 15% on each side.
                          Increase to exclude more border, decrease to include more area.
                          Example: 0.10 = 10% border, 0.20 = 20% border
        """
        self.video_path = video_path
        self.border_margin = border_margin
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video: {video_path}")
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def detect(self, method: str = "auto", sample_frames: int = 50, start_time: float = 0) -> DetectionResult:
        """
        Detect SLI region using specified method.
        
        Args:
            method: "auto", "border", "motion", "edge", "pose", or "hybrid"
            sample_frames: Number of frames to analyze
            start_time: Start detection from this time in seconds (default: 0)
            
        Returns:
            DetectionResult with bounding box and confidence
        """
        if method == "auto":
            # Auto mode: Try border detection first (most precise)
            return self._detect_auto(sample_frames, start_time)
        elif method == "border":
            return self._detect_border(sample_frames, start_time)
        elif method == "hybrid":
            return self._detect_hybrid(sample_frames, start_time)
        elif method == "motion":
            return self._detect_motion(sample_frames, start_time)
        elif method == "edge":
            return self._detect_edge(sample_frames, start_time)
        elif method == "pose":
            return self._detect_pose(sample_frames, start_time)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _detect_auto(self, sample_frames: int, start_time: float = 0) -> DetectionResult:
        """
        Auto detection: Try border detection first (most precise), then fallback.
        """
        print("  [Detector] Auto detection mode - trying border detection first...")
        
        # Try border detection (most precise for videos with colored borders)
        border_result = self._detect_border(sample_frames, start_time)
        
        # Lower threshold to 0.25 to prioritize border detection for interpreter videos
        if border_result.confidence > 0.25:
            print(f"  [Detector] Border detection succeeded (confidence: {border_result.confidence:.2f})")
            return border_result
        
        # Fallback to hybrid approach only if border confidence is very low
        print("  [Detector] Border detection uncertain, trying hybrid approach...")
        return self._detect_hybrid(sample_frames)
    
    def _detect_hybrid(self, sample_frames: int) -> DetectionResult:
        """
        Hybrid approach: Try motion first, fallback to edge detection.
        """
        print("  [Detector] Using hybrid detection (motion + edge fallback)...")
        
        # Try motion detection first
        motion_result = self._detect_motion(sample_frames)
        
        # If motion detection has high confidence, use it
        if motion_result.confidence > 0.6:
            print(f"  [Detector] Motion detection succeeded (confidence: {motion_result.confidence:.2f})")
            return motion_result
        
        # Fallback to edge detection
        print("  [Detector] Motion confidence low, falling back to edge detection...")
        edge_result = self._detect_edge(sample_frames)
        
        # Return whichever has higher confidence
        if edge_result.confidence > motion_result.confidence:
            return edge_result
        return motion_result
    
    def _detect_border(self, sample_frames: int, start_time: float = 0) -> DetectionResult:
        """
        Border-based detection: Detect light-colored static border around interpreter.
        This method precisely identifies the rectangular border and extracts the interior region.
        """
        print("  [Detector] Analyzing border patterns...")
        
        # Start from specified time
        start_frame = int(start_time * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Sample multiple frames to find consistent border
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // sample_frames)
        
        border_candidates = []
        frame_count = 0
        
        while frame_count < sample_frames:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Detect border in this frame
            border_box = self._find_border_in_frame(frame)
            if border_box is not None:
                border_candidates.append(border_box)
            
            frame_count += 1
            
            # Skip frames
            for _ in range(step - 1):
                ret = self.cap.grab()
                if not ret:
                    break
        
        if not border_candidates:
            print("  [Detector] No border detected")
            return self._fallback_detection("border")
        
        # Find most consistent border (median of all detections)
        boxes_array = np.array(border_candidates)
        median_box = np.median(boxes_array, axis=0).astype(int)
        
        # Calculate confidence based on consistency
        std_dev = np.std(boxes_array, axis=0)
        avg_std = np.mean(std_dev)
        confidence = max(0.3, min(0.95, 1.0 - (avg_std / 50.0)))
        
        print(f"  [Detector] Border detected with {len(border_candidates)} consistent frames")
        
        return DetectionResult(
            x1=median_box[0], y1=median_box[1],
            x2=median_box[2], y2=median_box[3],
            confidence=confidence,
            method="border"
        )
    
    def _find_border_in_frame(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Find light-colored border rectangle in a single frame.
        Looks for consistent colored rectangles in corner regions.
        """
        # Focus on corner regions where interpreter typically appears
        roi_list = self._get_corner_roi()
        
        best_box = None
        best_score = 0
        
        for corner_name, (rx1, ry1, rx2, ry2) in roi_list:
            roi = frame[ry1:ry2, rx1:rx2].copy()
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Detect light colors (white, light gray, beige, etc.)
            # These are common border colors in broadcast videos
            lower_light = np.array([0, 0, 180])      # Light colors (high value)
            upper_light = np.array([180, 80, 255])   # Allow some saturation
            
            mask = cv2.inRange(hsv, lower_light, upper_light)
            
            # Morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 1000:  # Too small
                    continue
                
                # Get bounding box
                bx, by, bw, bh = cv2.boundingRect(cnt)
                
                # Check aspect ratio (should be roughly portrait or square)
                aspect = bh / (bw + 1e-6)
                if not (0.7 < aspect < 2.5):
                    continue
                
                # Check if it's a border (has hole in middle)
                # The border should have a dark interior
                # Use configurable border margin
                interior_x1 = bx + int(bw * self.border_margin)
                interior_y1 = by + int(bh * self.border_margin)
                interior_x2 = bx + int(bw * (1.0 - self.border_margin))
                interior_y2 = by + int(bh * (1.0 - self.border_margin))
                
                if interior_x2 > interior_x1 and interior_y2 > interior_y1:
                    interior = mask[interior_y1:interior_y2, interior_x1:interior_x2]
                    if interior.size > 0:
                        interior_brightness = np.mean(interior)
                        
                        # Good border: bright edge, dark interior
                        if interior_brightness < 100:  # Dark interior
                            # Convert back to full frame coordinates
                            abs_x1 = rx1 + interior_x1
                            abs_y1 = ry1 + interior_y1
                            abs_x2 = rx1 + interior_x2
                            abs_y2 = ry1 + interior_y2
                            
                            # Score based on size and interior darkness
                            score = area * (1.0 - interior_brightness / 255.0)
                            
                            if score > best_score:
                                best_score = score
                                best_box = (abs_x1, abs_y1, abs_x2, abs_y2)
        
        return best_box
    
    def _detect_motion(self, sample_frames: int, start_time: float = 0) -> DetectionResult:
        """
        Method 1: Motion Heatmap using Optical Flow
        Identifies regions with consistent high-frequency motion (signing hands).
        """
        print("  [Detector] Analyzing motion patterns...")
        
        # Start from specified time
        start_frame = int(start_time * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Accumulate motion over frames
        motion_accumulator = np.zeros((self.height, self.width), dtype=np.float32)
        
        ret, prev_frame = self.cap.read()
        if not ret:
            return self._fallback_detection("motion")
        
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        frame_count = 0
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // sample_frames)
        
        while frame_count < sample_frames:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow (Farneback method - fast and reliable)
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray,
                None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0
            )
            
            # Calculate motion magnitude
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            motion_accumulator += magnitude
            
            prev_gray = gray
            frame_count += 1
            
            # Skip frames for efficiency
            for _ in range(step - 1):
                ret = self.cap.grab()
                if not ret:
                    break
        
        # Normalize motion heatmap
        motion_heatmap = motion_accumulator / (frame_count + 1e-6)
        
        # Focus on bottom corners (likely SLI locations)
        roi = self._get_corner_roi()
        
        # Find region with highest motion in corners
        best_box, confidence = self._find_motion_hotspot(motion_heatmap, roi)
        
        return DetectionResult(
            x1=best_box[0], y1=best_box[1],
            x2=best_box[2], y2=best_box[3],
            confidence=confidence,
            method="motion"
        )
    
    def _detect_edge(self, sample_frames: int, start_time: float = 0) -> DetectionResult:
        """
        Method 2: Screen Layout Analysis using Edge Detection
        Identifies rectangular overlays/boxes in the corners.
        """
        print("  [Detector] Analyzing screen layout and edges...")
        
        # Start from specified time
        start_frame = int(start_time * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Sample frames and accumulate edges
        edge_accumulator = np.zeros((self.height, self.width), dtype=np.float32)
        
        frame_count = 0
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // sample_frames)
        
        while frame_count < sample_frames:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_accumulator += edges.astype(np.float32)
            
            frame_count += 1
            
            # Skip frames
            for _ in range(step - 1):
                ret = self.cap.grab()
                if not ret:
                    break
        
        # Normalize
        edge_map = edge_accumulator / (frame_count + 1e-6)
        edge_map = (edge_map * 255 / edge_map.max()).astype(np.uint8)
        
        # Find rectangles in corner regions
        roi = self._get_corner_roi()
        best_box, confidence = self._find_rectangle_in_corners(edge_map, roi)
        
        return DetectionResult(
            x1=best_box[0], y1=best_box[1],
            x2=best_box[2], y2=best_box[3],
            confidence=confidence,
            method="edge"
        )
    
    def _detect_pose(self, sample_frames: int, start_time: float = 0) -> DetectionResult:
        """
        Method 3: Pose-Based Detection using MediaPipe
        Identifies small person in corner with visible hand/arm keypoints.
        """
        print("  [Detector] Analyzing human poses (requires MediaPipe)...")
        
        try:
            import mediapipe as mp
        except ImportError:
            print("  [Warning] MediaPipe not installed. Install with: pip install mediapipe")
            return self._fallback_detection("pose")
        
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Fastest model
            min_detection_confidence=0.5
        )
        
        # Start from specified time
        start_frame = int(start_time * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        candidates = []
        frame_count = 0
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // min(sample_frames, 30))  # Pose is slower
        
        while frame_count < min(sample_frames, 30):
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Convert to RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            
            if results.pose_landmarks:
                # Extract keypoints
                landmarks = results.pose_landmarks.landmark
                
                # Calculate bounding box from keypoints
                x_coords = [lm.x * self.width for lm in landmarks]
                y_coords = [lm.y * self.height for lm in landmarks]
                
                x1, x2 = int(min(x_coords)), int(max(x_coords))
                y1, y2 = int(min(y_coords)), int(max(y_coords))
                
                box_width = x2 - x1
                box_height = y2 - y1
                
                # Check if small person in corner
                is_small = box_height < self.height * 0.3
                in_corner = self._is_in_corner(x1, y1, x2, y2)
                
                # Check wrist visibility (sign language indicator)
                wrists_visible = (
                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility > 0.5 and
                    landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].visibility > 0.5
                )
                
                if is_small and in_corner and wrists_visible:
                    candidates.append((x1, y1, x2, y2))
            
            frame_count += 1
            
            for _ in range(step - 1):
                ret = self.cap.grab()
                if not ret:
                    break
        
        pose.close()
        
        if not candidates:
            return self._fallback_detection("pose")
        
        # Find most consistent box
        best_box = self._find_consistent_box(candidates)
        
        return DetectionResult(
            x1=best_box[0], y1=best_box[1],
            x2=best_box[2], y2=best_box[3],
            confidence=0.8 if len(candidates) > sample_frames * 0.3 else 0.5,
            method="pose"
        )
    
    def _get_corner_roi(self) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Define corner regions where SLI is typically located"""
        margin = 0.55  # Start searching from 55% of width/height
        
        return [
            ("bottom_right", (
                int(self.width * margin), int(self.height * margin),
                self.width, self.height
            )),
            ("bottom_left", (
                0, int(self.height * margin),
                int(self.width * (1 - margin)), self.height
            )),
            ("top_right", (
                int(self.width * margin), 0,
                self.width, int(self.height * (1 - margin))
            )),
            ("top_left", (
                0, 0,
                int(self.width * (1 - margin)), int(self.height * (1 - margin))
            )),
        ]
    
    def _find_motion_hotspot(self, motion_map: np.ndarray, corners: List) -> Tuple[Tuple[int, int, int, int], float]:
        """Find rectangular region with highest motion in corners"""
        best_score = 0
        best_box = None
        
        for corner_name, (x1, y1, x2, y2) in corners:
            # Extract corner region
            corner_motion = motion_map[y1:y2, x1:x2]
            
            # Apply threshold to find active regions
            threshold = np.percentile(corner_motion, 85)
            binary = (corner_motion > threshold).astype(np.uint8) * 255
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 500:  # Too small
                    continue
                
                # Get bounding box
                bx, by, bw, bh = cv2.boundingRect(cnt)
                
                # Convert to full image coordinates
                abs_x1 = x1 + bx
                abs_y1 = y1 + by
                abs_x2 = abs_x1 + bw
                abs_y2 = abs_y1 + bh
                
                # Calculate score (motion intensity * area)
                roi_motion = corner_motion[by:by+bh, bx:bx+bw]
                score = np.mean(roi_motion) * area
                
                if score > best_score:
                    best_score = score
                    best_box = (abs_x1, abs_y1, abs_x2, abs_y2)
        
        if best_box is None:
            # Fallback to most likely corner
            best_box = (
                int(self.width * 0.72), int(self.height * 0.62),
                int(self.width * 0.98), int(self.height * 0.95)
            )
            confidence = 0.3
        else:
            # Normalize confidence
            max_possible_score = np.max(motion_map) * (self.width * 0.3) * (self.height * 0.3)
            confidence = min(0.95, best_score / (max_possible_score + 1e-6))
        
        return best_box, confidence
    
    def _find_rectangle_in_corners(self, edge_map: np.ndarray, corners: List) -> Tuple[Tuple[int, int, int, int], float]:
        """Find rectangular overlays in corners using edge detection"""
        best_score = 0
        best_box = None
        
        for corner_name, (x1, y1, x2, y2) in corners:
            corner_edges = edge_map[y1:y2, x1:x2]
            
            # Find contours in edge map
            contours, _ = cv2.findContours(corner_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                
                # Look for rectangles (4 corners)
                if len(approx) >= 4:
                    area = cv2.contourArea(cnt)
                    if area < 1000:
                        continue
                    
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    
                    # Check aspect ratio (interpreter boxes are usually portrait or square)
                    aspect = bh / (bw + 1e-6)
                    if not (0.8 < aspect < 2.0):
                        continue
                    
                    # Convert to full coordinates
                    abs_x1 = x1 + bx
                    abs_y1 = y1 + by
                    abs_x2 = abs_x1 + bw
                    abs_y2 = abs_y1 + bh
                    
                    # Score based on edge density and size
                    roi_edges = corner_edges[by:by+bh, bx:bx+bw]
                    edge_density = np.mean(roi_edges)
                    score = edge_density * area
                    
                    if score > best_score:
                        best_score = score
                        best_box = (abs_x1, abs_y1, abs_x2, abs_y2)
        
        if best_box is None:
            best_box = (
                int(self.width * 0.72), int(self.height * 0.62),
                int(self.width * 0.98), int(self.height * 0.95)
            )
            confidence = 0.3
        else:
            max_possible = 255 * (self.width * 0.3) * (self.height * 0.3)
            confidence = min(0.9, best_score / (max_possible + 1e-6))
        
        return best_box, confidence
    
    def _is_in_corner(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if bounding box is in a corner region"""
        # Calculate center
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        
        # Check if in corner (outer 40% of each dimension)
        in_right = cx > self.width * 0.6
        in_left = cx < self.width * 0.4
        in_bottom = cy > self.height * 0.6
        in_top = cy < self.height * 0.4
        
        return (in_right or in_left) and (in_bottom or in_top)
    
    def _find_consistent_box(self, boxes: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Find median bounding box from multiple detections"""
        if not boxes:
            return (
                int(self.width * 0.72), int(self.height * 0.62),
                int(self.width * 0.98), int(self.height * 0.95)
            )
        
        boxes_array = np.array(boxes)
        median_box = np.median(boxes_array, axis=0).astype(int)
        return tuple(median_box)
    
    def _fallback_detection(self, method: str) -> DetectionResult:
        """Fallback to default bottom-right corner when detection fails"""
        print(f"  [Warning] {method} detection failed, using fallback position")
        return DetectionResult(
            x1=int(self.width * 0.72),
            y1=int(self.height * 0.62),
            x2=int(self.width * 0.98),
            y2=int(self.height * 0.95),
            confidence=0.3,
            method=f"{method}_fallback"
        )
    
    def visualize_detection(self, result: DetectionResult, output_path: str, num_frames: int = 5, 
                            save_individual_frames: bool = True, border_margin: float = 0.15, 
                            crop_adjust: int = 0, start_time: float = 0):
        """
        Create a visualization of the detection result on sample frames.
        Useful for debugging and validation.
        
        Args:
            result: Detection result with bounding box
            output_path: Path to save the preview grid image
            num_frames: Number of sample frames to visualize
            save_individual_frames: Also save individual detection frames
            border_margin: Border margin value used for detection
            crop_adjust: Crop adjustment value used
            start_time: Start time offset used
        """
        print(f"  [Visualizer] Creating detection preview...")
        
        # Start from specified start_time
        start_frame = int(start_time * self.fps) if start_time > 0 else 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        remaining_frames = total_frames - start_frame
        step = max(1, remaining_frames // num_frames)
        
        frames_with_boxes = []
        individual_frame_paths = []
        
        for i in range(num_frames):
            frame_pos = start_frame + (i * step)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Draw detection box
            cv2.rectangle(frame, (result.x1, result.y1), (result.x2, result.y2), (0, 255, 0), 3)
            
            # Add comprehensive label
            w, h = result.x2 - result.x1, result.y2 - result.y1
            label = f"{result.method.upper()} | Confidence: {result.confidence:.2f}"
            cv2.putText(frame, label, (result.x1, result.y1 - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add size info
            size_label = f"Size: {w}x{h}px"
            cv2.putText(frame, size_label, (result.x1, result.y1 - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Add parameters info in bottom left corner
            param_y = frame.shape[0] - 80
            cv2.putText(frame, f"Border Margin: {border_margin:.0%}", (10, param_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Crop Adjust: {crop_adjust:+d}px", (10, param_y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_pos}/{total_frames}", (10, param_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            frames_with_boxes.append(frame)
            
            # Save individual frame if requested
            if save_individual_frames:
                import os
                output_dir = os.path.dirname(output_path)
                base_name = os.path.splitext(os.path.basename(output_path))[0]
                frame_path = os.path.join(output_dir, f"{base_name}_frame{i+1:02d}.jpg")
                cv2.imwrite(frame_path, frame)
                individual_frame_paths.append(frame_path)
        
        # Create grid of frames
        if frames_with_boxes:
            # Resize for display
            display_width = 960
            scale = display_width / self.width
            display_height = int(self.height * scale)
            
            resized = [cv2.resize(f, (display_width, display_height)) for f in frames_with_boxes]
            
            # Stack horizontally or in grid
            if len(resized) <= 3:
                grid = np.hstack(resized)
            else:
                row1 = np.hstack(resized[:3])
                row2 = np.hstack(resized[3:] + [np.zeros_like(resized[0])] * (3 - len(resized[3:])))
                grid = np.vstack([row1, row2])
            
            cv2.imwrite(output_path, grid)
            print(f"  [Visualizer] Saved preview to: {output_path}")


    def crop_and_save_sli(self, result: DetectionResult, output_path: str, 
                          padding: int = 10, start_time: float = 0, 
                          duration: Optional[float] = None, 
                          apply_smoothing: bool = True,
                          target_size: Optional[tuple] = (256, 256),
                          crop_adjust: int = 0) -> bool:
        """
        Crop the detected SLI region and save as a new video file.
        
        Args:
            result: DetectionResult from detect() method
            output_path: Path to save cropped video
            padding: Additional pixels to add around detected box (default: 10)
                    Set to 0 for border detection to crop exactly to border
            start_time: Start time in seconds (default: 0 - from beginning)
            duration: Duration to extract in seconds (None = entire video)
            apply_smoothing: Apply temporal smoothing to stabilize bounding box
            target_size: Resize output to (width, height). Default: (256, 256) for DNN training
                        Set to None to keep original crop size
            crop_adjust: Adjust crop size in pixels. Positive = larger crop, negative = smaller crop
                        Example: +10 adds 10 pixels on each side, -5 removes 5 pixels from each side
            
        Returns:
            True if successful, False otherwise
        """
        print(f"  [Cropper] Extracting SLI region from video...")
        
        # For border detection, respect the detected boundaries exactly
        # For other methods, add padding for safety
        if result.method == "border" and padding > 0:
            print(f"  [Cropper] Border detection: using exact boundaries (padding=0)")
            padding = 0
        
        # Add padding to bounding box
        x1 = max(0, result.x1 - padding)
        y1 = max(0, result.y1 - padding)
        x2 = min(self.width, result.x2 + padding)
        y2 = min(self.height, result.y2 + padding)
        
        # Apply crop adjustment (independent of padding)
        if crop_adjust != 0:
            x1 = max(0, x1 - crop_adjust)
            y1 = max(0, y1 - crop_adjust)
            x2 = min(self.width, x2 + crop_adjust)
            y2 = min(self.height, y2 + crop_adjust)
            if crop_adjust > 0:
                print(f"  [Cropper] Expanding crop by {crop_adjust} pixels on each side")
            else:
                print(f"  [Cropper] Reducing crop by {abs(crop_adjust)} pixels on each side")
        
        crop_width = x2 - x1
        crop_height = y2 - y1
        
        # Make dimensions even (required by some codecs)
        if crop_width % 2 != 0:
            crop_width -= 1
            x2 = x1 + crop_width
        if crop_height % 2 != 0:
            crop_height -= 1
            y2 = y1 + crop_height
        
        # Determine output dimensions
        if target_size is not None:
            output_width, output_height = target_size
            print(f"  [Cropper] Crop region: ({x1}, {y1}) to ({x2}, {y2}) - {crop_width}x{crop_height}")
            print(f"  [Cropper] Resizing to: {output_width}x{output_height} for DNN training")
        else:
            output_width, output_height = crop_width, crop_height
            print(f"  [Cropper] Crop region: ({x1}, {y1}) to ({x2}, {y2}) - {crop_width}x{crop_height}")
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (output_width, output_height))
        
        if not out.isOpened():
            print(f"  [Error] Could not create output video: {output_path}")
            return False
        
        # Calculate frame range
        start_frame = int(start_time * self.fps)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if duration is not None:
            end_frame = min(start_frame + int(duration * self.fps), total_frames)
        else:
            end_frame = total_frames
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frames_processed = 0
        frames_to_process = end_frame - start_frame
        
        print(f"  [Cropper] Processing frames {start_frame} to {end_frame} ({frames_to_process} frames)...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret or self.cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
                break
            
            # Crop the frame
            cropped = frame[y1:y2, x1:x2]
            
            # Resize if target size specified
            if target_size is not None:
                cropped = cv2.resize(cropped, target_size, interpolation=cv2.INTER_CUBIC)
            
            # Write to output
            out.write(cropped)
            frames_processed += 1
            
            # Progress indicator
            if frames_processed % 100 == 0:
                progress = (frames_processed / frames_to_process) * 100
                print(f"  [Cropper] Progress: {progress:.1f}% ({frames_processed}/{frames_to_process})")
        
        out.release()
        print(f"  [Cropper] Successfully saved cropped video: {output_path}")
        print(f"  [Cropper] Total frames processed: {frames_processed}")
        
        # Add audio from original video using ffmpeg
        print(f"  [Cropper] Adding audio from original video...")
        temp_output = output_path.replace('.mp4', '_temp.mp4')
        import os
        os.rename(output_path, temp_output)
        
        # Build ffmpeg command to add audio
        import subprocess
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', temp_output,  # Video without audio
            '-i', self.video_path,  # Original video with audio
            '-ss', str(start_time),  # Start time for audio
            '-map', '0:v',  # Take video from first input
            '-map', '1:a',  # Take audio from second input
            '-c:v', 'copy',  # Copy video codec
            '-c:a', 'aac',  # Encode audio as AAC
            '-shortest',  # Match shortest stream
            output_path
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                os.remove(temp_output)
                print(f"  [Cropper] Audio added successfully")
            else:
                # If ffmpeg fails, keep video without audio
                os.rename(temp_output, output_path)
                print(f"  [Cropper] Warning: Could not add audio (ffmpeg may not be installed)")
                print(f"  [Cropper] Video saved without audio")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If ffmpeg not available, keep video without audio
            if os.path.exists(temp_output):
                os.rename(temp_output, output_path)
            print(f"  [Cropper] Warning: ffmpeg not available, video saved without audio")
        
        return True
    
    def extract_sli_clips(self, result: DetectionResult, output_dir: str,
                          clip_duration: float = 5.0, overlap: float = 0.5,
                          min_motion_threshold: float = 0.1, padding: int = 10,
                          target_size: Optional[tuple] = (256, 256),
                          start_time: float = 0,
                          crop_adjust: int = 0) -> List[str]:
        """
        Extract multiple short clips of the SLI region for dataset creation.
        Automatically segments the video into clips with active signing.
        
        Args:
            result: DetectionResult from detect() method
            output_dir: Directory to save clips
            clip_duration: Duration of each clip in seconds
            overlap: Overlap between consecutive clips (0-1)
            min_motion_threshold: Minimum motion to include clip (filters static frames)
            padding: Additional pixels around detected box
            target_size: Resize clips to (width, height). Default: (256, 256) for DNN training
                        Set to None to keep original crop size
            start_time: Start extracting clips from this time in seconds (default: 0)
            crop_adjust: Adjust crop size in pixels. Positive = larger, negative = smaller
            
        Returns:
            List of paths to saved clips
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"  [Clipper] Extracting {clip_duration}s clips with {overlap*100}% overlap...")
        
        # For border detection, respect exact boundaries
        if result.method == "border" and padding > 0:
            print(f"  [Clipper] Border detection: using exact boundaries (padding=0)")
            padding = 0
        
        # Setup crop region
        x1 = max(0, result.x1 - padding)
        y1 = max(0, result.y1 - padding)
        x2 = min(self.width, result.x2 + padding)
        y2 = min(self.height, result.y2 + padding)
        
        # Apply crop adjustment
        if crop_adjust != 0:
            x1 = max(0, x1 - crop_adjust)
            y1 = max(0, y1 - crop_adjust)
            x2 = min(self.width, x2 + crop_adjust)
            y2 = min(self.height, y2 + crop_adjust)
        
        crop_width = x2 - x1
        crop_height = y2 - y1
        
        # Make dimensions even
        if crop_width % 2 != 0:
            crop_width -= 1
            x2 = x1 + crop_width
        if crop_height % 2 != 0:
            crop_height -= 1
            y2 = y1 + crop_height
        
        # Determine output dimensions
        if target_size is not None:
            output_width, output_height = target_size
            print(f"  [Clipper] Output size: {output_width}x{output_height} (resized for DNN)")
        else:
            output_width, output_height = crop_width, crop_height
        
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / self.fps
        
        frames_per_clip = int(clip_duration * self.fps)
        step_frames = int(frames_per_clip * (1 - overlap))
        
        saved_clips = []
        clip_index = 0
        
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        
        # Start from specified time
        start_frame_offset = int(start_time * self.fps)
        
        for start_frame in range(start_frame_offset, total_frames - frames_per_clip, step_frames):
            clip_name = f"{base_name}_clip_{clip_index:04d}.mp4"
            clip_path = os.path.join(output_dir, clip_name)
            
            # Setup writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(clip_path, fourcc, self.fps, (output_width, output_height))
            
            if not out.isOpened():
                print(f"  [Warning] Could not create clip: {clip_path}")
                continue
            
            # Extract clip
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            motion_scores = []
            prev_crop = None
            frames_written = 0
            
            for _ in range(frames_per_clip):
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                cropped = frame[y1:y2, x1:x2]
                
                # Resize if target size specified
                if target_size is not None:
                    cropped_resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_CUBIC)
                else:
                    cropped_resized = cropped
                
                # Calculate motion for filtering (use original size for motion detection)
                if prev_crop is not None:
                    diff = cv2.absdiff(cropped, prev_crop)
                    motion = np.mean(diff)
                    motion_scores.append(motion)
                
                out.write(cropped_resized)
                frames_written += 1
                prev_crop = cropped.copy()
            
            out.release()
            
            # Check if clip has sufficient motion
            if motion_scores:
                avg_motion = np.mean(motion_scores)
                
                if avg_motion > min_motion_threshold:
                    saved_clips.append(clip_path)
                    clip_index += 1
                    
                    if clip_index % 10 == 0:
                        print(f"  [Clipper] Saved {clip_index} clips...")
                else:
                    # Remove static clip
                    os.remove(clip_path)
            else:
                os.remove(clip_path)
        
        print(f"  [Clipper] Successfully extracted {len(saved_clips)} clips to: {output_dir}")
        return saved_clips


def detect_sli_region(video_path: str, method: str = "auto", sample_frames: int = 50) -> DetectionResult:
    """
    Convenience function to detect SLI region in a video.
    
    Args:
        video_path: Path to video file
        method: "auto" (default), "motion", "edge", "pose", or "hybrid"
        sample_frames: Number of frames to analyze
        
    Returns:
        DetectionResult with bounding box coordinates and confidence
    """
    detector = SLIDetector(video_path)
    result = detector.detect(method=method, sample_frames=sample_frames)
    return result


def process_video_for_dataset(video_path: str, output_dir: str, 
                               detection_method: str = "auto",
                               clip_duration: float = 5.0,
                               min_confidence: float = 0.5,
                               save_full_video: bool = False,
                               create_preview: bool = True,
                               output_size: str = "original",
                               border_margin: float = 0.15,
                               start_time: float = 0,
                               crop_adjust: int = 0) -> dict:
    """
    Complete pipeline to process a video and extract SLI clips for dataset creation.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save results
        detection_method: SLI detection method ("auto", "motion", "edge", "pose", "hybrid")
        clip_duration: Duration of each clip in seconds
        min_confidence: Minimum detection confidence to proceed
        save_full_video: Also save full cropped video (in addition to clips)
        create_preview: Create visualization of detection
        output_size: Output resolution - "original" (keep detected size, e.g. 124×124),
                    "128" (resize to 128×128), "256" (resize to 256×256)
        border_margin: Border exclusion margin (0.0-0.5). Default 0.15 = 15% on each side.
                      Increase to crop more tightly, decrease to include more area.
        start_time: Start processing from this time in seconds (e.g., 480 = 8 minutes)
        crop_adjust: Adjust crop size in pixels. Positive = expand crop, negative = shrink crop
                    Example: 10 adds 10 pixels on each side, -5 removes 5 pixels from each side
        
    Returns:
        Dictionary with results including paths to saved files
    """
    import os
    
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(video_path)}")
    print(f"{'='*60}\n")
    
    # 1. Detect SLI region
    print("[Step 1/4] Detecting SLI region...")
    if start_time > 0:
        print(f"  Starting from: {start_time/60:.1f} minutes ({start_time:.0f} seconds)")
    detector = SLIDetector(video_path, border_margin=border_margin)
    result = detector.detect(method=detection_method, sample_frames=50, start_time=start_time)
    
    print(f"\n  Detection Result:")
    print(f"    Method: {result.method}")
    print(f"    Confidence: {result.confidence:.2f}")
    print(f"    Bounding Box: ({result.x1}, {result.y1}) -> ({result.x2}, {result.y2})")
    print(f"    Size: {result.x2 - result.x1}x{result.y2 - result.y1}")
    
    if result.confidence < min_confidence:
        print(f"\n  [Warning] Low confidence ({result.confidence:.2f} < {min_confidence})")
        print(f"  Proceeding anyway, but results may be inaccurate.\n")
    
    # Create output directory structure
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    clips_dir = os.path.join(output_dir, "clips")
    previews_dir = os.path.join(output_dir, "previews")
    full_videos_dir = os.path.join(output_dir, "full_cropped")
    
    results = {
        "video_path": video_path,
        "detection": {
            "bbox": (result.x1, result.y1, result.x2, result.y2),
            "confidence": result.confidence,
            "method": result.method
        },
        "clips": [],
        "full_video": None,
        "preview": None
    }
    
    # 2. Create preview (optional)
    if create_preview:
        print("\n[Step 2/4] Creating detection preview with sample frames...")
        os.makedirs(previews_dir, exist_ok=True)
        preview_path = os.path.join(previews_dir, f"{base_name}_detection.jpg")
        detector.visualize_detection(result, preview_path, num_frames=5, 
                                    save_individual_frames=True,
                                    border_margin=border_margin,
                                    crop_adjust=crop_adjust,
                                    start_time=start_time)
        results["preview"] = preview_path
        print(f"  [Visualizer] Preview grid saved: {preview_path}")
        print(f"  [Visualizer] Individual frames saved in: {previews_dir}")
    else:
        print("\n[Step 2/4] Skipping preview creation...")
    
    # 3. Extract clips
    print("\n[Step 3/4] Extracting SLI clips...")
    # Determine target size based on user preference
    if output_size == "original":
        target_size = None
        print(f"  Output size: Original detected size ({result.x2-result.x1}×{result.y2-result.y1})")
    elif output_size == "128":
        target_size = (128, 128)
        print(f"  Output size: 128×128 (resized from {result.x2-result.x1}×{result.y2-result.y1})")
    elif output_size == "256":
        target_size = (256, 256)
        print(f"  Output size: 256×256 (resized from {result.x2-result.x1}×{result.y2-result.y1})")
    else:
        target_size = None
        print(f"  Output size: Original (unknown size option: {output_size})")
    
    clips = detector.extract_sli_clips(
        result, 
        clips_dir,
        clip_duration=clip_duration,
        overlap=0.3,
        min_motion_threshold=1.0,
        target_size=target_size,
        start_time=start_time,
        crop_adjust=crop_adjust
    )
    results["clips"] = clips
    
    # 4. Save full cropped video (optional)
    if save_full_video:
        print("\n[Step 4/4] Saving full cropped video...")
        os.makedirs(full_videos_dir, exist_ok=True)
        full_video_path = os.path.join(full_videos_dir, f"{base_name}_sli_cropped.mp4")
        # Use padding=0 for border detection to crop exactly to border
        # Use padding=10 for other methods for safety margin
        padding = 0 if result.method == "border" else 10
        # Use same target size as clips
        success = detector.crop_and_save_sli(
            result, full_video_path, 
            padding=padding,
            target_size=target_size,
            crop_adjust=crop_adjust
        )
        if success:
            results["full_video"] = full_video_path
    else:
        print("\n[Step 4/4] Skipping full video save...")
    
    print(f"\n{'='*60}")
    print(f"Processing Complete!")
    print(f"  Clips extracted: {len(clips)}")
    print(f"  Output directory: {output_dir}")
    print(f"{'='*60}\n")
    
    return results


def batch_process_videos(video_paths: List[str], output_base_dir: str,
                         detection_method: str = "auto",
                         clip_duration: float = 5.0,
                         save_full_videos: bool = False) -> List[dict]:
    """
    Process multiple videos in batch for dataset creation.
    
    Args:
        video_paths: List of paths to video files
        output_base_dir: Base directory for all outputs
        detection_method: SLI detection method
        clip_duration: Duration of each clip in seconds
        save_full_videos: Save full cropped videos in addition to clips
        
    Returns:
        List of result dictionaries for each video
    """
    import os
    
    print(f"\n{'#'*60}")
    print(f"BATCH PROCESSING: {len(video_paths)} videos")
    print(f"{'#'*60}\n")
    
    all_results = []
    successful = 0
    failed = 0
    
    for i, video_path in enumerate(video_paths, 1):
        print(f"\n>>> Processing video {i}/{len(video_paths)}")
        
        try:
            # Create subdirectory for each video
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            video_output_dir = os.path.join(output_base_dir, video_name)
            
            result = process_video_for_dataset(
                video_path,
                video_output_dir,
                detection_method=detection_method,
                clip_duration=clip_duration,
                save_full_video=save_full_videos,
                create_preview=True
            )
            
            all_results.append(result)
            successful += 1
            
        except Exception as e:
            print(f"\n  [ERROR] Failed to process {video_path}")
            print(f"  {str(e)}\n")
            failed += 1
            continue
    
    # Summary
    print(f"\n{'#'*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"  Total videos: {len(video_paths)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total clips extracted: {sum(len(r['clips']) for r in all_results)}")
    print(f"{'#'*60}\n")
    
    return all_results
