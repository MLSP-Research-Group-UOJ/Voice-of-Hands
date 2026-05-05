#!/usr/bin/env python3
"""
Script to spatially crop a video to show only a specific area (e.g., sign language interpreter).

Usage:
    # Interactive mode - select area with mouse
    python crop_video_spatial.py input.mp4 output.mp4
    
    # With predefined coordinates
    python crop_video_spatial.py input.mp4 output.mp4 --coords 240 205 1580 700
"""

import cv2
import sys
import argparse
import numpy as np


class VideoAreaSelector:
    """Interactive area selector for video cropping."""
    
    def __init__(self, video_path):
        self.video_path = video_path
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.frame = None
        self.display_frame = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for area selection."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)
            
    def select_area(self):
        """Open video and allow user to select crop area."""
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            print(f"Error: Cannot open video '{self.video_path}'")
            return None
        
        # Read first frame
        ret, self.frame = cap.read()
        cap.release()
        
        if not ret:
            print("Error: Cannot read video frame")
            return None
        
        # Create window and set mouse callback
        window_name = "Select Sign Language Area (Draw rectangle, press SPACE to confirm, ESC to cancel)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        print("\n=== INSTRUCTIONS ===")
        print("1. Click and drag to draw a rectangle around the sign language area")
        print("2. Press SPACE to confirm selection")
        print("3. Press ESC to cancel")
        print("4. Press R to reset selection")
        print("==================\n")
        
        while True:
            # Copy frame for display
            self.display_frame = self.frame.copy()
            
            # Draw rectangle if points are set
            if self.start_point and self.end_point:
                cv2.rectangle(
                    self.display_frame,
                    self.start_point,
                    self.end_point,
                    (0, 255, 0),
                    2
                )
                
                # Show coordinates
                x1, y1 = self.start_point
                x2, y2 = self.end_point
                cv2.putText(
                    self.display_frame,
                    f"Area: ({min(x1,x2)}, {min(y1,y2)}) to ({max(x1,x2)}, {max(y1,y2)})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
            
            cv2.imshow(window_name, self.display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # SPACE - confirm
            if key == ord(' '):
                if self.start_point and self.end_point:
                    break
            # ESC - cancel
            elif key == 27:
                cv2.destroyAllWindows()
                return None
            # R - reset
            elif key == ord('r') or key == ord('R'):
                self.start_point = None
                self.end_point = None
        
        cv2.destroyAllWindows()
        
        # Return normalized coordinates (x1, y1, x2, y2)
        x1 = min(self.start_point[0], self.end_point[0])
        y1 = min(self.start_point[1], self.end_point[1])
        x2 = max(self.start_point[0], self.end_point[0])
        y2 = max(self.start_point[1], self.end_point[1])
        
        return (x1, y1, x2, y2)


def crop_video_spatial(input_path, output_path, coords):
    """
    Crop video to specified spatial coordinates.
    
    Args:
        input_path: Input video path
        output_path: Output video path
        coords: Tuple of (x1, y1, x2, y2) crop coordinates
    """
    x1, y1, x2, y2 = coords
    
    print(f"\nCropping video:")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Crop area: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"  Output size: {x2-x1}x{y2-y1}")
    
    # Open input video
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        print(f"Error: Cannot open video '{input_path}'")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate crop dimensions
    crop_width = x2 - x1
    crop_height = y2 - y1
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (crop_width, crop_height))
    
    if not out.isOpened():
        print("Error: Cannot create output video")
        cap.release()
        return False
    
    # Process frames
    frame_count = 0
    print("\nProcessing frames...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Crop frame
        cropped = frame[y1:y2, x1:x2]
        out.write(cropped)
        
        frame_count += 1
        
        # Progress indicator
        if frame_count % 100 == 0:
            progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            print(f"  Processed {frame_count}/{total_frames} frames ({progress:.1f}%)")
    
    # Cleanup
    cap.release()
    out.release()
    
    print(f"\n✓ Video cropped successfully!")
    print(f"  Output: {output_path}")
    print(f"  Total frames: {frame_count}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Spatially crop a video to show only a specific area"
    )
    parser.add_argument("input", help="Input video path")
    parser.add_argument("output", help="Output video path")
    parser.add_argument(
        "--coords",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Crop coordinates: x1 y1 x2 y2 (e.g., 240 205 1580 700)"
    )
    
    args = parser.parse_args()
    
    # Get crop coordinates
    if args.coords:
        coords = tuple(args.coords)
        print(f"Using provided coordinates: {coords}")
    else:
        print("No coordinates provided. Opening interactive selector...")
        selector = VideoAreaSelector(args.input)
        coords = selector.select_area()
        
        if coords is None:
            print("Selection cancelled.")
            return
        
        print(f"Selected coordinates: {coords}")
    
    # Crop the video
    success = crop_video_spatial(args.input, args.output, coords)
    
    if success:
        print("\nDone!")
    else:
        print("\nFailed to crop video.")
        sys.exit(1)


if __name__ == "__main__":
    main()
