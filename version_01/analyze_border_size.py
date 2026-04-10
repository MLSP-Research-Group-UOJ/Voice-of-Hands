#!/usr/bin/env python3
"""
Analyze the actual border size in the Parliament video
"""

import cv2
import numpy as np

video_path = "videos/Parliament_Live_01-12-2025.mp4"

print("="*60)
print("Analyzing Border Size in Parliament Video")
print("="*60)

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Could not open video")
    exit(1)

# Read a frame from middle of video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)

ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Could not read frame")
    exit(1)

height, width = frame.shape[:2]
print(f"\nVideo dimensions: {width}×{height}")

# Convert to HSV for better border detection
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Detect light colors (white, light gray, light green borders)
lower_light = np.array([0, 0, 180])
upper_light = np.array([180, 80, 255])

mask = cv2.inRange(hsv, lower_light, upper_light)

# Clean up mask
kernel = np.ones((3, 3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

# Find all contours
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"\nFound {len(contours)} light-colored regions")

# Create visualization
vis_frame = frame.copy()

# Analyze each interpreter window with border
interpreter_windows = []

for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area < 5000:  # Too small
        continue
    
    x, y, w, h = cv2.boundingRect(cnt)
    
    # Check aspect ratio (interpreter windows are roughly portrait/square)
    aspect = h / (w + 1e-6)
    if not (0.7 < aspect < 2.5):
        continue
    
    # Check if it's a border (has darker interior)
    margin = 5
    if x + margin < width and y + margin < height and \
       x + w - margin > 0 and y + h - margin > 0:
        
        # Sample the border region (outer edges)
        top_border = mask[y:y+15, x:x+w]
        bottom_border = mask[y+h-15:y+h, x:x+w]
        left_border = mask[y:y+h, x:x+15]
        right_border = mask[y:y+h, x+w-15:x+w]
        
        # Check if borders are bright
        border_brightness = (
            np.mean(top_border) + np.mean(bottom_border) + 
            np.mean(left_border) + np.mean(right_border)
        ) / 4
        
        # Sample interior (should be darker - the interpreter)
        int_margin = int(w * 0.2)
        interior = mask[y+int_margin:y+h-int_margin, x+int_margin:x+w-int_margin]
        interior_brightness = np.mean(interior) if interior.size > 0 else 255
        
        # This is likely a bordered window if border is bright and interior is dark
        if border_brightness > 150 and interior_brightness < 100:
            # Estimate border thickness by finding where brightness drops
            # Analyze left edge
            left_edge = mask[y:y+h, x:x+50]
            border_thickness_left = 0
            for col in range(left_edge.shape[1]):
                if np.mean(left_edge[:, col]) > 150:
                    border_thickness_left += 1
                else:
                    break
            
            # Analyze top edge
            top_edge = mask[y:y+50, x:x+w]
            border_thickness_top = 0
            for row in range(top_edge.shape[0]):
                if np.mean(top_edge[row, :]) > 150:
                    border_thickness_top += 1
                else:
                    break
            
            border_thickness = (border_thickness_left + border_thickness_top) // 2
            
            # Calculate interior region (without border)
            interior_x = x + border_thickness
            interior_y = y + border_thickness
            interior_w = w - (2 * border_thickness)
            interior_h = h - (2 * border_thickness)
            
            interpreter_windows.append({
                'outer_bbox': (x, y, w, h),
                'interior_bbox': (interior_x, interior_y, interior_w, interior_h),
                'border_thickness': border_thickness,
                'border_brightness': border_brightness,
                'interior_brightness': interior_brightness
            })
            
            # Draw on visualization
            # Outer border (full region with border) - RED
            cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(vis_frame, f"Full: {w}x{h}", (x, y-25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Interior region (without border) - GREEN
            cv2.rectangle(vis_frame, (interior_x, interior_y), 
                         (interior_x+interior_w, interior_y+interior_h), 
                         (0, 255, 0), 2)
            cv2.putText(vis_frame, f"Interior: {interior_w}x{interior_h}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(vis_frame, f"Border: ~{border_thickness}px", 
                       (x, y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

print(f"\nFound {len(interpreter_windows)} interpreter windows with borders:")
print("="*60)

for i, window in enumerate(interpreter_windows, 1):
    outer = window['outer_bbox']
    interior = window['interior_bbox']
    thickness = window['border_thickness']
    
    print(f"\nWindow {i}:")
    print(f"  Full region (with border): {outer[2]}×{outer[3]} at ({outer[0]}, {outer[1]})")
    print(f"  Interior region (no border): {interior[2]}×{interior[3]} at ({interior[0]}, {interior[1]})")
    print(f"  Border thickness: ~{thickness} pixels on each side")
    print(f"  Border takes: {thickness*2}×{thickness*2} pixels total")

# Save visualization
output_path = "border_size_analysis.jpg"
cv2.imwrite(output_path, vis_frame)
print(f"\n{'='*60}")
print(f"✓ Visualization saved to: {output_path}")
print(f"  RED boxes: Full region including border")
print(f"  GREEN boxes: Interior region (interpreter only)")
print("="*60)
