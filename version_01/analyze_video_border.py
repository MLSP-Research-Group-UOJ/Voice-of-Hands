#!/usr/bin/env python3
"""
Analyze the video to understand the border structure
"""
import cv2
import numpy as np

video_path = "Parliament_Live_01-12-2025.mp4"
cap = cv2.VideoCapture(video_path)

# Read a frame from middle of video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
ret, frame = cap.read()

if not ret:
    print("Failed to read frame")
    exit(1)

h, w = frame.shape[:2]
print(f"Video resolution: {w}×{h}")
print()

# Convert to HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Sample edges to understand border color
print("Analyzing border colors...")
print()

# Top edge
top_strip = frame[:20, :]
top_avg = np.mean(top_strip, axis=(0, 1))
print(f"Top edge - BGR: {top_avg}")
print(f"Top edge - RGB: ({top_avg[2]:.0f}, {top_avg[1]:.0f}, {top_avg[0]:.0f})")

# Bottom edge
bottom_strip = frame[h-20:, :]
bottom_avg = np.mean(bottom_strip, axis=(0, 1))
print(f"Bottom edge - BGR: {bottom_avg}")
print(f"Bottom edge - RGB: ({bottom_avg[2]:.0f}, {bottom_avg[1]:.0f}, {bottom_avg[0]:.0f})")

# Left edge
left_strip = frame[:, :20]
left_avg = np.mean(left_strip, axis=(0, 1))
print(f"Left edge - BGR: {left_avg}")
print(f"Left edge - RGB: ({left_avg[2]:.0f}, {left_avg[1]:.0f}, {left_avg[0]:.0f})")

# Right edge
right_strip = frame[:, w-20:]
right_avg = np.mean(right_strip, axis=(0, 1))
print(f"Right edge - BGR: {right_avg}")
print(f"Right edge - RGB: ({right_avg[2]:.0f}, {right_avg[1]:.0f}, {right_avg[0]:.0f})")
print()

# Look for Picture-in-Picture regions (potential SLI box)
# Search bottom-right corner (most common PiP location)
print("Analyzing potential PiP regions...")
print()

# Check bottom-right quadrant
br_x = w // 2
br_y = h // 2
br_quadrant = frame[br_y:, br_x:]

# Convert to grayscale
gray = cv2.cvtColor(br_quadrant, cv2.COLOR_BGR2GRAY)

# Find edges
edges = cv2.Canny(gray, 50, 150)

# Find contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find rectangular contours
print("Found rectangles in bottom-right quadrant:")
for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
    area = cv2.contourArea(cnt)
    if area < 1000:  # Too small
        continue
        
    x, y, cw, ch = cv2.boundingRect(cnt)
    
    # Convert to full frame coordinates
    abs_x = br_x + x
    abs_y = br_y + y
    
    # Check aspect ratio (sign language interpreters are usually square or portrait)
    aspect = cw / ch if ch > 0 else 0
    
    print(f"  Region: ({abs_x}, {abs_y}) to ({abs_x+cw}, {abs_y+ch})")
    print(f"  Size: {cw}×{ch}, Aspect: {aspect:.2f}, Area: {area:.0f}")
    
    # Check border thickness
    # Sample around the perimeter
    border_samples = []
    
    # Top border
    if y > 5:
        border_top = frame[br_y+y-5:br_y+y, br_x+x:br_x+x+cw]
        if border_top.size > 0:
            border_samples.append(np.mean(border_top))
    
    # Bottom border
    if y+ch < br_quadrant.shape[0] - 5:
        border_bottom = frame[br_y+y+ch:br_y+y+ch+5, br_x+x:br_x+x+cw]
        if border_bottom.size > 0:
            border_samples.append(np.mean(border_bottom))
    
    # Left border
    if x > 5:
        border_left = frame[br_y+y:br_y+y+ch, br_x+x-5:br_x+x]
        if border_left.size > 0:
            border_samples.append(np.mean(border_left))
    
    # Right border
    if x+cw < br_quadrant.shape[1] - 5:
        border_right = frame[br_y+y:br_y+y+ch, br_x+x+cw:br_x+x+cw+5]
        if border_right.size > 0:
            border_samples.append(np.mean(border_right))
    
    if border_samples:
        print(f"  Border brightness: {np.mean(border_samples):.1f}/255")
    print()

# Save annotated frame
output = frame.copy()

# Draw grid lines to show quadrants
cv2.line(output, (w//2, 0), (w//2, h), (0, 255, 0), 1)
cv2.line(output, (0, h//2), (w, h//2), (0, 255, 0), 1)

# Highlight bottom-right quadrant
cv2.rectangle(output, (br_x, br_y), (w, h), (0, 255, 255), 2)

# Draw detected contours
for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
    area = cv2.contourArea(cnt)
    if area < 1000:
        continue
    x, y, cw, ch = cv2.boundingRect(cnt)
    abs_x = br_x + x
    abs_y = br_y + y
    cv2.rectangle(output, (abs_x, abs_y), (abs_x+cw, abs_y+ch), (0, 0, 255), 2)

cv2.imwrite("analyze_video_border.jpg", output)
print("Saved analysis to: analyze_video_border.jpg")

cap.release()
