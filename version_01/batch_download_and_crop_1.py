import os
import re
import sys
import cv2
from yt_dlp import YoutubeDL
from sli_detector import detect_sli_region, SLIDetector

# =========================
# CONFIG (edit these only)
# =========================

URLS_FILE = "urls.txt"

DOWNLOAD_DIR = "videos"
CROPPED_DIR = "cropped"
PREVIEW_DIR = "detection_previews"  # For visualization of detected regions

# Detection method:
# - "auto" or "hybrid": Try motion first, fallback to edge (RECOMMENDED)
# - "motion": Motion heatmap (best for active signing)
# - "edge": Screen layout analysis (best for bordered overlays)
# - "pose": MediaPipe pose detection (requires mediapipe, most accurate but slower)
# - "manual": Use fixed coordinates below
DETECTION_METHOD = "auto"

# Number of frames to sample for detection (more = slower but more accurate)
SAMPLE_FRAMES = 50  # 30-100 recommended

# Manual ROI (only used if DETECTION_METHOD = "manual")
ROI_X1 = 0.72  # start x (72% from left)
ROI_Y1 = 0.62  # start y (62% from top)
ROI_X2 = 0.98  # end x (98% = right edge)
ROI_Y2 = 0.95  # end y (95% = bottom edge)

# Minimum confidence threshold for auto-detection (0.0-1.0)
# If detection confidence is below this, will ask for manual review
MIN_CONFIDENCE = 0.5

# If your videos are long, you can optionally limit seconds for quick testing:
# Set to None to crop full video.
MAX_SECONDS = None  # e.g., 30 for first 30 seconds, or None for full

# Create detection preview images for verification
CREATE_PREVIEW = True

# =========================
# Helpers
# =========================

def ensure_dirs():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(CROPPED_DIR, exist_ok=True)
    os.makedirs(PREVIEW_DIR, exist_ok=True)

def read_urls(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Create it and paste links (one per line).")

    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls

def safe_name(name: str, max_len: int = 120) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)  # Windows-safe filename
    name = re.sub(r"\s+", " ", name).strip()
    return name[:max_len]

def download_video(url: str) -> str:
    """
    Downloads best video up to 1080p + best audio, merges to mp4 when possible.
    Returns the downloaded file path.
    """
    ydl_opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Sometimes yt-dlp returns a "requested_downloads" list with final filepath
        if "requested_downloads" in info and info["requested_downloads"]:
            return info["requested_downloads"][0]["filepath"]

        # Fallback: build path from title/id/ext (may not always match merge)
        title = safe_name(info.get("title", "video"))
        vid = info.get("id", "id")
        ext = info.get("ext", "mp4")
        candidate = os.path.join(DOWNLOAD_DIR, f"{title} [{vid}].{ext}")
        if os.path.exists(candidate):
            return candidate

        # If merge happened, ext might be mp4
        candidate_mp4 = os.path.join(DOWNLOAD_DIR, f"{title} [{vid}].mp4")
        if os.path.exists(candidate_mp4):
            return candidate_mp4

        raise RuntimeError("Download completed but could not locate output file.")

def crop_video(input_path: str, output_path: str):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x1 = int(width * ROI_X1)
    y1 = int(height * ROI_Y1)
    x2 = int(width * ROI_X2)
    y2 = int(height * ROI_Y2)

    # safety clamp
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(x1 + 1, min(x2, width))
    y2 = max(y1 + 1, min(y2, height))

    roi_w = x2 - x1
    roi_h = y2 - y1

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps if fps > 0 else 25, (roi_w, roi_h))

    max_frames = None
    if MAX_SECONDS is not None and fps and fps > 0:
        max_frames = int(MAX_SECONDS * fps)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        crop = frame[y1:y2, x1:x2]
        out.write(crop)

        frame_count += 1
        if frame_count % 200 == 0:
            print(f"    Cropping... frames: {frame_count}")

        if max_frames is not None and frame_count >= max_frames:
            print(f"    Stopped early at {MAX_SECONDS}s (MAX_SECONDS).")
            break

    cap.release()
    out.release()

def main():
    ensure_dirs()
    urls = read_urls(URLS_FILE)

    if not urls:
        print("No URLs found in urls.txt")
        sys.exit(0)

    print(f"Found {len(urls)} URLs.")
    print("ROI config:",
          f"x: {ROI_X1:.2f}→{ROI_X2:.2f}, y: {ROI_Y1:.2f}→{ROI_Y2:.2f}")

    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")

        try:
            video_path = download_video(url)
            print("  Downloaded:", video_path)

            base = os.path.splitext(os.path.basename(video_path))[0]
            out_path = os.path.join(CROPPED_DIR, base + "_signer.mp4")

            if os.path.exists(out_path):
                print("  Cropped already exists, skipping:", out_path)
                continue

            crop_video(video_path, out_path)
            print("  Saved cropped:", out_path)

        except Exception as e:
            print("  ERROR:", e)
            # continue to next URL instead of stopping everything

    print("\nDONE ✅")

if __name__ == "__main__":
    main()