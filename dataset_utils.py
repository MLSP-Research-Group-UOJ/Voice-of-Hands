#!/usr/bin/env python3
"""
Dataset Utilities for Sign Language Interpreter Dataset
Provides tools for quality control, analysis, and organization.
"""

import os
import cv2
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class DatasetAnalyzer:
    """Analyze and manage SLI video dataset"""
    
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir
        self.clips_dir = os.path.join(dataset_dir, "clips")
        
    def get_dataset_statistics(self) -> Dict:
        """
        Get comprehensive statistics about the dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        print("Analyzing dataset...")
        
        if not os.path.exists(self.clips_dir):
            return {"error": "Clips directory not found"}
        
        clips = self._find_video_files(self.clips_dir)
        
        if not clips:
            return {"error": "No video clips found"}
        
        stats = {
            "total_clips": len(clips),
            "total_duration": 0,
            "resolutions": defaultdict(int),
            "fps_values": defaultdict(int),
            "file_sizes": [],
            "frame_counts": [],
            "clips": []
        }
        
        print(f"Analyzing {len(clips)} clips...")
        
        for i, clip_path in enumerate(clips, 1):
            try:
                cap = cv2.VideoCapture(clip_path)
                
                if not cap.isOpened():
                    continue
                
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                file_size = os.path.getsize(clip_path)
                
                stats["total_duration"] += duration
                stats["resolutions"][f"{width}x{height}"] += 1
                stats["fps_values"][int(fps)] += 1
                stats["file_sizes"].append(file_size)
                stats["frame_counts"].append(frame_count)
                
                stats["clips"].append({
                    "path": clip_path,
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "frames": frame_count,
                    "duration": duration,
                    "size_mb": file_size / (1024 * 1024)
                })
                
                cap.release()
                
                if i % 50 == 0:
                    print(f"  Processed {i}/{len(clips)}...")
                    
            except Exception as e:
                print(f"  Error processing {clip_path}: {e}")
                continue
        
        # Calculate summary statistics
        if stats["file_sizes"]:
            stats["avg_file_size_mb"] = np.mean(stats["file_sizes"]) / (1024 * 1024)
            stats["total_size_gb"] = sum(stats["file_sizes"]) / (1024 ** 3)
        
        if stats["frame_counts"]:
            stats["avg_frames"] = np.mean(stats["frame_counts"])
        
        stats["total_hours"] = stats["total_duration"] / 3600
        
        return stats
    
    def print_statistics(self, stats: Dict):
        """Print dataset statistics in a readable format"""
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        
        if "error" in stats:
            print(f"Error: {stats['error']}")
            return
        
        print(f"\n📊 General Information:")
        print(f"  Total clips: {stats['total_clips']}")
        print(f"  Total duration: {stats['total_hours']:.2f} hours ({stats['total_duration']:.1f} seconds)")
        print(f"  Total size: {stats['total_size_gb']:.2f} GB")
        print(f"  Average file size: {stats['avg_file_size_mb']:.2f} MB")
        print(f"  Average frames per clip: {stats['avg_frames']:.1f}")
        
        print(f"\n🎬 Resolutions:")
        for resolution, count in sorted(stats['resolutions'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_clips']) * 100
            print(f"  {resolution}: {count} clips ({percentage:.1f}%)")
        
        print(f"\n⚡ Frame Rates:")
        for fps, count in sorted(stats['fps_values'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_clips']) * 100
            print(f"  {fps} FPS: {count} clips ({percentage:.1f}%)")
        
        print("="*60 + "\n")
    
    def save_statistics(self, output_path: str):
        """Save statistics to JSON file"""
        stats = self.get_dataset_statistics()
        
        # Convert defaultdict to regular dict for JSON serialization
        if "resolutions" in stats:
            stats["resolutions"] = dict(stats["resolutions"])
        if "fps_values" in stats:
            stats["fps_values"] = dict(stats["fps_values"])
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Statistics saved to: {output_path}")
        return stats
    
    def find_duplicates(self) -> List[Tuple[str, str]]:
        """
        Find potential duplicate clips based on file size and frame count.
        
        Returns:
            List of tuples containing potential duplicate pairs
        """
        print("Searching for potential duplicates...")
        
        clips = self._find_video_files(self.clips_dir)
        clip_signatures = defaultdict(list)
        
        for clip_path in clips:
            try:
                cap = cv2.VideoCapture(clip_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                file_size = os.path.getsize(clip_path)
                cap.release()
                
                # Create signature (file_size, frame_count)
                signature = (file_size, frame_count)
                clip_signatures[signature].append(clip_path)
                
            except Exception as e:
                continue
        
        # Find signatures with multiple clips
        duplicates = []
        for signature, paths in clip_signatures.items():
            if len(paths) > 1:
                # Check if actual duplicates
                for i in range(len(paths)):
                    for j in range(i + 1, len(paths)):
                        duplicates.append((paths[i], paths[j]))
        
        print(f"Found {len(duplicates)} potential duplicate pairs")
        return duplicates
    
    def check_quality(self, min_resolution: Tuple[int, int] = (200, 200),
                     min_duration: float = 1.0,
                     max_duration: float = 30.0) -> Dict:
        """
        Check quality of clips and identify problematic ones.
        
        Args:
            min_resolution: Minimum (width, height) in pixels
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            
        Returns:
            Dictionary with quality report
        """
        print("Checking clip quality...")
        
        clips = self._find_video_files(self.clips_dir)
        
        report = {
            "total_clips": len(clips),
            "too_small": [],
            "too_short": [],
            "too_long": [],
            "corrupted": [],
            "low_motion": [],
            "good": []
        }
        
        for clip_path in clips:
            try:
                cap = cv2.VideoCapture(clip_path)
                
                if not cap.isOpened():
                    report["corrupted"].append(clip_path)
                    continue
                
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                
                # Check resolution
                if width < min_resolution[0] or height < min_resolution[1]:
                    report["too_small"].append(clip_path)
                    cap.release()
                    continue
                
                # Check duration
                if duration < min_duration:
                    report["too_short"].append(clip_path)
                    cap.release()
                    continue
                
                if duration > max_duration:
                    report["too_long"].append(clip_path)
                    cap.release()
                    continue
                
                # Check motion (sample 10 frames)
                motion_scores = []
                prev_frame = None
                
                for i in range(min(10, frame_count)):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_count // 10)
                    ret, frame = cap.read()
                    
                    if ret and prev_frame is not None:
                        diff = cv2.absdiff(frame, prev_frame)
                        motion = np.mean(diff)
                        motion_scores.append(motion)
                    
                    prev_frame = frame if ret else None
                
                avg_motion = np.mean(motion_scores) if motion_scores else 0
                
                if avg_motion < 1.0:  # Very low motion
                    report["low_motion"].append(clip_path)
                else:
                    report["good"].append(clip_path)
                
                cap.release()
                
            except Exception as e:
                report["corrupted"].append(clip_path)
                continue
        
        return report
    
    def print_quality_report(self, report: Dict):
        """Print quality report in readable format"""
        print("\n" + "="*60)
        print("QUALITY REPORT")
        print("="*60)
        
        total = report["total_clips"]
        good = len(report["good"])
        
        print(f"\n✅ Good clips: {good}/{total} ({good/total*100:.1f}%)")
        
        issues = [
            ("too_small", "⚠️  Too small resolution"),
            ("too_short", "⚠️  Too short duration"),
            ("too_long", "⚠️  Too long duration"),
            ("low_motion", "⚠️  Low motion (static)"),
            ("corrupted", "❌ Corrupted/unreadable")
        ]
        
        for key, label in issues:
            count = len(report[key])
            if count > 0:
                print(f"{label}: {count} clips")
                if count <= 5:  # Show paths for small numbers
                    for path in report[key]:
                        print(f"    - {os.path.basename(path)}")
        
        print("="*60 + "\n")
    
    def create_preview_grid(self, output_path: str, num_samples: int = 16):
        """
        Create a preview grid showing sample frames from the dataset.
        
        Args:
            output_path: Path to save preview image
            num_samples: Number of clips to sample
        """
        print(f"Creating preview grid with {num_samples} samples...")
        
        clips = self._find_video_files(self.clips_dir)
        
        if not clips:
            print("No clips found")
            return
        
        # Sample random clips
        import random
        sample_clips = random.sample(clips, min(num_samples, len(clips)))
        
        # Extract middle frame from each clip
        frames = []
        for clip_path in sample_clips:
            try:
                cap = cv2.VideoCapture(clip_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Get middle frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
                ret, frame = cap.read()
                
                if ret:
                    # Resize to standard size
                    frame = cv2.resize(frame, (320, 240))
                    frames.append(frame)
                
                cap.release()
            except Exception:
                continue
        
        if not frames:
            print("Could not extract frames")
            return
        
        # Create grid
        grid_size = int(np.ceil(np.sqrt(len(frames))))
        
        # Pad with black frames if needed
        while len(frames) < grid_size * grid_size:
            frames.append(np.zeros_like(frames[0]))
        
        # Arrange in grid
        rows = []
        for i in range(grid_size):
            row = np.hstack(frames[i*grid_size:(i+1)*grid_size])
            rows.append(row)
        
        grid = np.vstack(rows)
        
        cv2.imwrite(output_path, grid)
        print(f"Preview grid saved to: {output_path}")
    
    def _find_video_files(self, directory: str) -> List[str]:
        """Find all video files in directory"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        videos = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    videos.append(os.path.join(root, file))
        
        return videos


def main():
    """Example usage of dataset utilities"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage: python dataset_utils.py <dataset_dir> [command]

Commands:
  stats      - Print dataset statistics
  quality    - Check quality of clips
  duplicates - Find potential duplicates
  preview    - Create preview grid
  all        - Run all checks (default)

Example:
  python dataset_utils.py dataset/processed stats
        """)
        return
    
    dataset_dir = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    analyzer = DatasetAnalyzer(dataset_dir)
    
    if command in ["stats", "all"]:
        stats = analyzer.get_dataset_statistics()
        analyzer.print_statistics(stats)
        analyzer.save_statistics(os.path.join(dataset_dir, "statistics.json"))
    
    if command in ["quality", "all"]:
        report = analyzer.check_quality()
        analyzer.print_quality_report(report)
    
    if command in ["duplicates", "all"]:
        duplicates = analyzer.find_duplicates()
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} potential duplicates:")
            for dup1, dup2 in duplicates[:10]:  # Show first 10
                print(f"  {os.path.basename(dup1)}")
                print(f"  {os.path.basename(dup2)}")
                print()
    
    if command in ["preview", "all"]:
        analyzer.create_preview_grid(
            os.path.join(dataset_dir, "preview_grid.jpg"),
            num_samples=16
        )


if __name__ == "__main__":
    main()
