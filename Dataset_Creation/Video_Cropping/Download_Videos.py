import os
import re
from yt_dlp import YoutubeDL

# Folder to save videos
DOWNLOAD_DIR = "videos"
URLS_FILE = "urls.txt"

# Create download folder
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def safe_name(name: str, max_len: int = 120) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:max_len]

def read_urls(path):
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls

def download_video(url):
    ydl_opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    urls = read_urls(URLS_FILE)

    print(f"Found {len(urls)} URLs")

    for i, url in enumerate(urls, start=1):
        print(f"Downloading {i}/{len(urls)}")
        download_video(url)

    print("All videos downloaded ✅")

if __name__ == "__main__":
    main()