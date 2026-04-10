"""
Visual preview of border detection with different margins and output sizes.
Shows detected regions and cropped results.
"""

import cv2
import numpy as np
from sli_detector import SLIDetector

def create_preview(video_path, output_path="border_detection_preview.jpg", start_time=0, crop_adjust=0):
    """
    Create a visual preview showing border detection results with different settings.
    
    Args:
        video_path: Path to video file
        output_path: Path to save preview image
        start_time: Start time in seconds (default: 0)
        crop_adjust: Adjust crop size in pixels (default: 0)
    """
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return
    
    # Seek to start time
    if start_time > 0:
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        print(f"Starting from: {start_time/60:.1f} minutes ({start_time:.0f} seconds)")
    
    # Read frame at specified time
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Cannot read frame from video")
        return
    
    print(f"Video frame size: {frame.shape[1]}×{frame.shape[0]} pixels")
    
    # Test different border margins
    margins = [0.05, 0.10, 0.15, 0.20]
    margin_labels = ["5% margin (Largest crop)", "10% margin (Larger crop)", "15% margin (Default)", "20% margin (Tighter crop)"]
    
    # Create a large canvas for the preview
    preview_height = 300 * len(margins) + 100
    preview_width = 1800
    preview_canvas = np.ones((preview_height, preview_width, 3), dtype=np.uint8) * 255
    
    y_offset = 50
    
    for margin, label in zip(margins, margin_labels):
        # Detect with this margin
        detector = SLIDetector(video_path, border_margin=margin)
        result = detector._detect_border(sample_frames=50, start_time=start_time)
        
        if result is None:
            print(f"No detection for margin {margin}")
            continue
        
        x, y = result.x1, result.y1
        w, h = result.x2 - result.x1, result.y2 - result.y1
        
        # Apply crop adjustment
        if crop_adjust != 0:
            x = max(0, x - crop_adjust)
            y = max(0, y - crop_adjust)
            w = min(frame.shape[1] - x, w + 2 * crop_adjust)
            h = min(frame.shape[0] - y, h + 2 * crop_adjust)
        
        print(f"\nMargin {margin:.2f} ({label}):")
        print(f"  Detected region: ({x}, {y}) to ({x+w}, {y+h})")
        print(f"  Interior size: {w}×{h} pixels")
        if crop_adjust != 0:
            print(f"  (Adjusted by {crop_adjust:+d} pixels on each side)")
        print(f"  Confidence: {result.confidence:.2f}")
        
        # Draw on original frame
        frame_with_box = frame.copy()
        cv2.rectangle(frame_with_box, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # Add label
        if crop_adjust != 0:
            label_text = f"{label}: {w}×{h}px (adj:{crop_adjust:+d}px)"
        else:
            label_text = f"{label}: {w}×{h}px"
        cv2.putText(frame_with_box, label_text, (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Crop the detected region
        cropped_original = frame[y:y+h, x:x+w].copy()
        
        # Create resized versions
        cropped_128 = cv2.resize(cropped_original, (128, 128), interpolation=cv2.INTER_CUBIC)
        cropped_256 = cv2.resize(cropped_original, (256, 256), interpolation=cv2.INTER_CUBIC)
        
        # Scale down full frame for display
        display_scale = 0.3
        frame_display = cv2.resize(frame_with_box, None, fx=display_scale, fy=display_scale)
        
        # Add text labels for each version
        original_display = cv2.resize(cropped_original, (250, 250))
        cv2.putText(original_display, f"Original: {w}x{h}", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(original_display, f"Original: {w}x{h}", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        display_128 = cv2.resize(cropped_128, (250, 250))
        cv2.putText(display_128, "Resized: 128x128", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(display_128, "Resized: 128x128", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        display_256 = cv2.resize(cropped_256, (250, 250))
        cv2.putText(display_256, "Resized: 256x256", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(display_256, "Resized: 256x256", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Place on canvas
        x_pos = 50
        
        # Full frame with detection box
        fh, fw = frame_display.shape[:2]
        preview_canvas[y_offset:y_offset+fh, x_pos:x_pos+fw] = frame_display
        x_pos += fw + 30
        
        # Original crop
        preview_canvas[y_offset:y_offset+250, x_pos:x_pos+250] = original_display
        x_pos += 280
        
        # 128x128 resize
        preview_canvas[y_offset:y_offset+250, x_pos:x_pos+250] = display_128
        x_pos += 280
        
        # 256x256 resize
        preview_canvas[y_offset:y_offset+250, x_pos:x_pos+250] = display_256
        
        # Add margin label
        text_y = y_offset - 10
        cv2.putText(preview_canvas, label, (50, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        y_offset += 300
    
    # Add title
    title = "Border Detection Preview - Different Margins and Output Sizes"
    if start_time > 0:
        title += f" (at {start_time/60:.1f} min)"
    if crop_adjust != 0:
        title += f" [crop_adjust: {crop_adjust:+d}px]"
    cv2.putText(preview_canvas, title,
                (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    
    # Add column headers
    cv2.putText(preview_canvas, "Video Frame", (50, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(preview_canvas, "Original Size", (450, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(preview_canvas, "128x128 Output", (750, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(preview_canvas, "256x256 Output", (1050, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    
    # Save preview
    cv2.imwrite(output_path, preview_canvas)
    print(f"\n✅ Preview saved to: {output_path}")
    print(f"Preview image size: {preview_canvas.shape[1]}×{preview_canvas.shape[0]} pixels")
    
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preview_border_detection.py <video_path> [start_time_seconds] [crop_adjust_pixels]")
        print("\nExample:")
        print("  python preview_border_detection.py videos/Parliament_Live_01-12-2025.mp4")
        print("  python preview_border_detection.py videos/Parliament_Live_01-12-2025.mp4 480")
        print("  python preview_border_detection.py videos/Parliament_Live_01-12-2025.mp4 480 10")
        print("  (480 = start from 8 minutes, 10 = expand crop by 10 pixels)")
        sys.exit(1)
    
    video_path = sys.argv[1]
    start_time = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    crop_adjust = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    # Generate output filename with timestamp and crop adjust
    if start_time > 0 and crop_adjust != 0:
        output_path = f"border_detection_preview_{int(start_time/60)}min_adj{crop_adjust:+d}px.jpg"
    elif start_time > 0:
        output_path = f"border_detection_preview_{int(start_time/60)}min.jpg"
    elif crop_adjust != 0:
        output_path = f"border_detection_preview_adj{crop_adjust:+d}px.jpg"
    else:
        output_path = "border_detection_preview.jpg"
    
    create_preview(video_path, output_path, start_time, crop_adjust)
