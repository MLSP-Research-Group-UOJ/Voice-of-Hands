import os
import cv2

# =========================
# CONFIG
# =========================

INPUT_DIR = "videos"
OUTPUT_DIR = "cropped"

# Fixed crop coordinates (pixels)
X1 = 240
Y1 = 205
X2 = 1580
Y2 = 700

MAX_SECONDS = None

# =========================

os.makedirs(OUTPUT_DIR, exist_ok=True)

videos = [f for f in os.listdir(INPUT_DIR) if f.endswith((".mp4", ".mkv", ".webm"))]

print(f"Found {len(videos)} videos")

for video in videos:

    input_path = os.path.join(INPUT_DIR, video)
    output_path = os.path.join(OUTPUT_DIR, video.replace(".mp4", "_signer.mp4"))

    print("Processing:", video)

    cap = cv2.VideoCapture(input_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    # ROI width and height
    roi_w = X2 - X1
    roi_h = Y2 - Y1

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps if fps > 0 else 25, (roi_w, roi_h))

    frame_count = 0
    max_frames = None

    if MAX_SECONDS and fps:
        max_frames = int(MAX_SECONDS * fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        crop = frame[Y1:Y2, X1:X2]
        out.write(crop)

        frame_count += 1

        if frame_count % 200 == 0:
            print("frames:", frame_count)

        if max_frames and frame_count >= max_frames:
            break

    cap.release()
    out.release()

    print("Saved:", output_path)

print("DONE")