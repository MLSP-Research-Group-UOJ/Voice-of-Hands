#!/usr/bin/env python3
"""
Enhanced Clip Extraction with Timestamp Metadata
Tracks precise timestamps for audio-sign language alignment research
"""

import os
import cv2
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class TimestampedClipExtractor:
    """
    Extracts video clips with precise timestamp tracking for multimodal alignment
    """
    
    def __init__(self, video_path: str, output_base_dir: str):
        """
        Initialize extractor
        
        Args:
            video_path: Path to original broadcast video
            output_base_dir: Base directory for output (will create subdirectories)
        """
        self.video_path = video_path
        self.output_base_dir = output_base_dir
        self.video_name = Path(video_path).stem
        
        # Create output structure
        self.video_clips_dir = os.path.join(output_base_dir, "video_clips")
        self.audio_clips_dir = os.path.join(output_base_dir, "audio_clips")
        self.transcriptions_dir = os.path.join(output_base_dir, "transcriptions")
        
        for dir_path in [self.video_clips_dir, self.audio_clips_dir, self.transcriptions_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Get video properties
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video Info:")
        print(f"  Duration: {self.duration:.1f}s ({self.duration/60:.1f} minutes)")
        print(f"  FPS: {self.fps}")
        print(f"  Resolution: {self.width}x{self.height}")
        print(f"  Total Frames: {self.total_frames}")
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def extract_clips_with_metadata(self, 
                                     crop_region: Dict[str, int],
                                     clip_duration: float = 5.0,
                                     start_time: float = 0.0,
                                     end_time: Optional[float] = None,
                                     overlap: float = 0.0,
                                     output_size: tuple = (256, 256),
                                     extract_audio: bool = True,
                                     min_motion_threshold: float = 5.0) -> Dict:
        """
        Extract video clips with comprehensive timestamp metadata
        
        Args:
            crop_region: Dict with keys 'x1', 'y1', 'x2', 'y2'
            clip_duration: Duration of each clip in seconds
            start_time: Start extracting from this time (seconds)
            end_time: Stop at this time (None = end of video)
            overlap: Overlap between clips (0.0-0.9)
            output_size: Output resolution (width, height)
            extract_audio: Whether to extract audio segments
            min_motion_threshold: Minimum motion to keep clip
        
        Returns:
            Dictionary with dataset metadata
        """
        if end_time is None:
            end_time = self.duration
        
        frames_per_clip = int(clip_duration * self.fps)
        step_frames = int(frames_per_clip * (1 - overlap))
        
        start_frame = int(start_time * self.fps)
        end_frame = int(end_time * self.fps)
        
        x1, y1 = crop_region['x1'], crop_region['y1']
        x2, y2 = crop_region['x2'], crop_region['y2']
        
        print(f"\nExtracting clips:")
        print(f"  Crop region: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"  Clip duration: {clip_duration}s")
        print(f"  Time range: {start_time:.1f}s to {end_time:.1f}s")
        print(f"  Overlap: {overlap*100:.0f}%")
        
        metadata = {
            "dataset_info": {
                "original_video": self.video_path,
                "video_name": self.video_name,
                "video_duration": self.duration,
                "fps": self.fps,
                "resolution": f"{self.width}x{self.height}",
                "created_date": datetime.now().isoformat(),
                "clip_duration": clip_duration,
                "overlap": overlap,
                "output_size": f"{output_size[0]}x{output_size[1]}"
            },
            "clips": []
        }
        
        clip_index = 0
        successful_clips = 0
        
        for frame_idx in range(start_frame, end_frame - frames_per_clip, step_frames):
            clip_start_time = frame_idx / self.fps
            clip_end_time = (frame_idx + frames_per_clip) / self.fps
            
            # Generate filenames
            clip_id = f"{clip_index:04d}"
            video_filename = f"{self.video_name}_clip_{clip_id}.mp4"
            audio_filename = f"{self.video_name}_clip_{clip_id}.wav"
            text_filename = f"{self.video_name}_clip_{clip_id}.txt"
            
            video_path = os.path.join(self.video_clips_dir, video_filename)
            audio_path = os.path.join(self.audio_clips_dir, audio_filename)
            
            # Extract video clip
            motion_score = self._extract_video_clip(
                frame_idx, frames_per_clip, 
                (x1, y1, x2, y2), output_size, video_path
            )
            
            # Check motion threshold
            if motion_score < min_motion_threshold:
                if os.path.exists(video_path):
                    os.remove(video_path)
                clip_index += 1
                continue
            
            # Extract audio clip
            if extract_audio:
                self._extract_audio_clip(clip_start_time, clip_duration, audio_path)
            
            # Create metadata entry
            clip_metadata = {
                "clip_id": clip_id,
                "filename": video_filename,
                "audio_filename": audio_filename if extract_audio else None,
                "text_filename": text_filename,
                "timestamp": {
                    "start_seconds": round(clip_start_time, 3),
                    "end_seconds": round(clip_end_time, 3),
                    "start_frame": frame_idx,
                    "end_frame": frame_idx + frames_per_clip,
                    "duration": clip_duration
                },
                "crop_region": {
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "width": x2 - x1, "height": y2 - y1
                },
                "output_resolution": f"{output_size[0]}x{output_size[1]}",
                "motion_score": round(motion_score, 2),
                "quality_passed": True,
                "transcription": None,  # To be filled by ASR
                "transcription_confidence": None
            }
            
            metadata["clips"].append(clip_metadata)
            successful_clips += 1
            clip_index += 1
            
            if successful_clips % 50 == 0:
                print(f"  Processed {successful_clips} clips...")
        
        # Save metadata
        metadata_path = os.path.join(self.output_base_dir, "alignment_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Extraction complete!")
        print(f"  Total clips: {successful_clips}")
        print(f"  Metadata saved: {metadata_path}")
        
        return metadata
    
    def _extract_video_clip(self, start_frame: int, num_frames: int, 
                           crop_region: tuple, output_size: tuple, 
                           output_path: str) -> float:
        """Extract and save a single video clip, return motion score"""
        x1, y1, x2, y2 = crop_region
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, output_size)
        
        if not out.isOpened():
            print(f"Warning: Could not create {output_path}")
            return 0.0
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        motion_scores = []
        prev_crop = None
        
        for _ in range(num_frames):
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Crop
            cropped = frame[y1:y2, x1:x2]
            
            # Calculate motion
            if prev_crop is not None:
                diff = cv2.absdiff(cropped, prev_crop)
                motion = float(cv2.mean(diff)[0])
                motion_scores.append(motion)
            
            # Resize and save
            resized = cv2.resize(cropped, output_size, interpolation=cv2.INTER_CUBIC)
            out.write(resized)
            prev_crop = cropped.copy()
        
        out.release()
        
        avg_motion = sum(motion_scores) / len(motion_scores) if motion_scores else 0.0
        return avg_motion
    
    def _extract_audio_clip(self, start_time: float, duration: float, output_path: str):
        """Extract audio clip using ffmpeg"""
        try:
            subprocess.run([
                'ffmpeg', '-y', '-loglevel', 'error',
                '-i', self.video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate (good for ASR)
                '-ac', '1',  # Mono
                output_path
            ], check=True, timeout=30)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Audio extraction failed for {output_path}")
        except Exception as e:
            print(f"Error extracting audio: {e}")
    
    def transcribe_audio_clips(self, metadata_path: str, model_name: str = "base", 
                              language: str = None) -> Dict:
        """
        Transcribe all audio clips using Whisper
        
        Args:
            metadata_path: Path to alignment_metadata.json
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (e.g., 'si' for Sinhala, 'en' for English, 
                     'ta' for Tamil). If None, auto-detects language.
        
        Returns:
            Updated metadata with transcriptions
        """
        try:
            import whisper
        except ImportError:
            print("❌ Whisper not installed. Install with: pip install openai-whisper")
            return {}
        
        print(f"\nLoading Whisper model '{model_name}'...")
        model = whisper.load_model(model_name)
        
        if language:
            print(f"Language: {language} (forced)")
        else:
            print("Language: Auto-detect (recommended for mixed languages)")
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"Transcribing {len(metadata['clips'])} clips...")
        
        for i, clip in enumerate(metadata['clips']):
            audio_file = os.path.join(self.audio_clips_dir, clip['audio_filename'])
            
            if not os.path.exists(audio_file):
                print(f"  Warning: Audio file not found: {audio_file}")
                continue
            
            # Transcribe (with language parameter or auto-detect)
            if language:
                result = model.transcribe(audio_file, language=language, word_timestamps=True)
            else:
                # Auto-detect language (recommended for mixed-language content)
                result = model.transcribe(audio_file, word_timestamps=True)
            
            # Update metadata
            clip['transcription'] = result['text'].strip()
            clip['transcription_language'] = result.get('language', 'unknown')
            
            # Calculate average confidence from segments
            if 'segments' in result and result['segments']:
                confidences = []
                word_details = []
                
                for segment in result['segments']:
                    # Segment-level confidence
                    if 'no_speech_prob' in segment:
                        confidences.append(1.0 - segment['no_speech_prob'])
                    
                    # Word-level details
                    if 'words' in segment:
                        for word in segment['words']:
                            word_details.append({
                                'word': word.get('word', '').strip(),
                                'start': round(word.get('start', 0), 3),
                                'end': round(word.get('end', 0), 3),
                                'probability': round(word.get('probability', 0), 3)
                            })
                
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                clip['transcription_confidence'] = round(avg_conf, 3)
                clip['word_timestamps'] = word_details
            
            # Save transcription to text file
            text_file = os.path.join(self.transcriptions_dir, clip['text_filename'])
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(clip['transcription'])
            
            if (i + 1) % 10 == 0:
                print(f"  Transcribed {i + 1}/{len(metadata['clips'])} clips...")
        
        # Save updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Transcription complete!")
        print(f"  Updated metadata: {metadata_path}")
        
        return metadata


def extract_from_existing_clips(clips_dir: str, original_video: str, 
                                output_dir: str, fps: float = 30.0,
                                clip_duration: float = 5.0):
    """
    Retroactively extract audio and create metadata for existing clips
    
    Args:
        clips_dir: Directory with existing video clips
        original_video: Path to original broadcast video
        output_dir: Output directory for audio and metadata
        fps: FPS of videos
        clip_duration: Duration of each clip
    """
    print("Extracting timestamps from existing clips...")
    
    audio_dir = os.path.join(output_dir, "audio_clips")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Get sorted list of clips
    clip_files = sorted([f for f in os.listdir(clips_dir) if f.endswith('.mp4')])
    
    metadata = {
        "dataset_info": {
            "original_video": original_video,
            "created_date": datetime.now().isoformat(),
            "clip_duration": clip_duration,
            "fps": fps
        },
        "clips": []
    }
    
    for i, clip_file in enumerate(clip_files):
        # Calculate timestamp based on clip index
        start_time = i * clip_duration
        end_time = start_time + clip_duration
        
        clip_id = f"{i:04d}"
        audio_filename = clip_file.replace('.mp4', '.wav')
        
        # Extract audio
        audio_path = os.path.join(audio_dir, audio_filename)
        try:
            subprocess.run([
                'ffmpeg', '-y', '-loglevel', 'error',
                '-i', original_video,
                '-ss', str(start_time),
                '-t', str(clip_duration),
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                audio_path
            ], check=True, timeout=30)
        except:
            print(f"  Warning: Could not extract audio for {clip_file}")
            audio_filename = None
        
        # Add to metadata
        metadata["clips"].append({
            "clip_id": clip_id,
            "filename": clip_file,
            "audio_filename": audio_filename,
            "timestamp": {
                "start_seconds": round(start_time, 3),
                "end_seconds": round(end_time, 3),
                "duration": clip_duration
            }
        })
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(clip_files)} clips...")
    
    # Save metadata
    metadata_path = os.path.join(output_dir, "alignment_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Extraction complete!")
    print(f"  Audio segments: {audio_dir}")
    print(f"  Metadata: {metadata_path}")


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python timestamp_extractor.py <video_path> <output_dir>")
        print("\nExample:")
        print("  python timestamp_extractor.py videos/news.mp4 multimodal_output")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Example crop region (you'll get this from your detector)
    crop_region = {
        'x1': 1065, 'y1': 452,
        'x2': 1265, 'y2': 652
    }
    
    extractor = TimestampedClipExtractor(video_path, output_dir)
    metadata = extractor.extract_clips_with_metadata(
        crop_region=crop_region,
        clip_duration=5.0,
        start_time=480.0,  # Start at 8 minutes
        extract_audio=True
    )
    
    print("\nTo transcribe audio, run:")
    print(f"  metadata = extractor.transcribe_audio_clips('{output_dir}/alignment_metadata.json')")
