"""
Video Processing for UI Traps Analyzer

Uses FFmpeg to extract frames from video files for analysis.
Implements scene detection to only extract frames when UI changes.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import json


class VideoProcessor:
    """
    Processes video files to extract frames for UI analysis.

    Uses FFmpeg with scene detection to extract only frames
    where the UI visually changes, avoiding redundant analysis.
    """

    # Supported video formats
    SUPPORTED_FORMATS = {'.mp4', '.mov', '.webm', '.avi', '.mkv'}

    # Scene detection threshold (0.0-1.0, lower = more sensitive)
    DEFAULT_SCENE_THRESHOLD = 0.3

    # Maximum frames to extract (cost control)
    MAX_FRAMES = 20

    # Minimum frames to ensure coverage
    MIN_FRAMES = 3

    def __init__(self, ffmpeg_path: str = None, require_ffmpeg: bool = False):
        """
        Initialize the video processor.

        Args:
            ffmpeg_path: Path to ffmpeg binary. If None, uses system ffmpeg.
            require_ffmpeg: If True, raises error when FFmpeg not found.
                           If False, sets ffmpeg_available = False.
        """
        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        self.ffmpeg_available = self.ffmpeg_path is not None and self.ffprobe_path is not None

        if require_ffmpeg and not self.ffmpeg_available:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg:\n"
                "  Windows: choco install ffmpeg\n"
                "  Mac: brew install ffmpeg\n"
                "  Linux: apt install ffmpeg"
            )

    def _find_ffmpeg(self) -> Optional[str]:
        """Find ffmpeg in system PATH. Returns None if not found."""
        return shutil.which('ffmpeg')

    def _find_ffprobe(self) -> Optional[str]:
        """Find ffprobe in system PATH. Returns None if not found."""
        return shutil.which('ffprobe')

    def _require_ffmpeg(self):
        """Raise error if FFmpeg is not available."""
        if not self.ffmpeg_available:
            raise RuntimeError(
                "FFmpeg not available. Please install FFmpeg:\n"
                "  Windows: choco install ffmpeg\n"
                "  Mac: brew install ffmpeg\n"
                "  Linux: apt install ffmpeg"
            )

    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata (duration, resolution, fps).

        Args:
            video_path: Path to video file

        Returns:
            Dict with duration, width, height, fps
        """
        self._require_ffmpeg()
        cmd = [
            self.ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ValueError(f"Failed to read video: {result.stderr}")

        data = json.loads(result.stdout)

        # Find video stream
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if not video_stream:
            raise ValueError("No video stream found in file")

        # Parse frame rate (could be "30/1" or "29.97")
        fps_str = video_stream.get('r_frame_rate', '30/1')
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den) if float(den) > 0 else 30.0
        else:
            fps = float(fps_str)

        return {
            'duration': float(data.get('format', {}).get('duration', 0)),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'fps': fps,
            'codec': video_stream.get('codec_name', 'unknown'),
            'file_size': int(data.get('format', {}).get('size', 0))
        }

    def estimate_frames(self, video_path: str, scene_threshold: float = None) -> int:
        """
        Estimate how many frames will be extracted.

        This is a rough estimate based on video duration.
        Actual frame count depends on scene changes.

        Args:
            video_path: Path to video file
            scene_threshold: Scene detection sensitivity

        Returns:
            Estimated frame count
        """
        info = self.get_video_info(video_path)
        duration = info['duration']

        # Rough heuristic: expect 1 scene change per 3-5 seconds on average
        # This varies greatly based on content
        estimated = int(duration / 4) + 1

        # Clamp to min/max
        return max(self.MIN_FRAMES, min(self.MAX_FRAMES, estimated))

    def extract_frames(
        self,
        video_path: str,
        output_dir: str = None,
        scene_threshold: float = None,
        max_frames: int = None
    ) -> List[Tuple[str, float]]:
        """
        Extract frames from video using scene detection.

        Args:
            video_path: Path to input video
            output_dir: Directory for output frames (temp if None)
            scene_threshold: Scene change sensitivity (0.0-1.0)
            max_frames: Maximum frames to extract

        Returns:
            List of (frame_path, timestamp) tuples
        """
        self._require_ffmpeg()
        scene_threshold = scene_threshold or self.DEFAULT_SCENE_THRESHOLD
        max_frames = max_frames or self.MAX_FRAMES

        # Validate input
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        if video_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {video_path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='uitraps_frames_')
        else:
            os.makedirs(output_dir, exist_ok=True)

        output_pattern = os.path.join(output_dir, 'frame_%04d.png')

        # FFmpeg command with scene detection
        # select='gt(scene,0.3)' extracts frames where scene change > threshold
        cmd = [
            self.ffmpeg_path,
            '-i', str(video_path),
            '-vf', f"select='gt(scene,{scene_threshold})',showinfo",
            '-vsync', 'vfr',
            '-frame_pts', '1',
            output_pattern,
            '-y'  # Overwrite
        ]

        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Collect extracted frames
        frames = []
        frame_files = sorted(Path(output_dir).glob('frame_*.png'))

        # If scene detection found too few frames, fall back to interval extraction
        if len(frame_files) < self.MIN_FRAMES:
            frames = self._extract_interval_frames(
                video_path, output_dir, self.MIN_FRAMES
            )
        else:
            # Parse timestamps from filenames or estimate
            info = self.get_video_info(str(video_path))
            duration = info['duration']

            for i, frame_path in enumerate(frame_files[:max_frames]):
                # Estimate timestamp based on frame position
                timestamp = (i / max(len(frame_files), 1)) * duration
                frames.append((str(frame_path), timestamp))

        return frames

    def _extract_interval_frames(
        self,
        video_path: Path,
        output_dir: str,
        num_frames: int
    ) -> List[Tuple[str, float]]:
        """
        Extract frames at regular intervals (fallback method).

        Used when scene detection doesn't find enough frames.
        """
        info = self.get_video_info(str(video_path))
        duration = info['duration']

        frames = []
        interval = duration / (num_frames + 1)

        for i in range(1, num_frames + 1):
            timestamp = i * interval
            output_path = os.path.join(output_dir, f'interval_{i:04d}.png')

            cmd = [
                self.ffmpeg_path,
                '-ss', str(timestamp),
                '-i', str(video_path),
                '-vframes', '1',
                '-q:v', '2',
                output_path,
                '-y'
            ]

            subprocess.run(cmd, capture_output=True, timeout=30)

            if os.path.exists(output_path):
                frames.append((output_path, timestamp))

        return frames

    def cleanup_frames(self, frame_paths: List[str]) -> None:
        """
        Clean up extracted frame files.

        Args:
            frame_paths: List of frame file paths to delete
        """
        for path in frame_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass

        # Also try to remove the parent temp directory if empty
        if frame_paths:
            parent_dir = os.path.dirname(frame_paths[0])
            if parent_dir and 'uitraps_frames_' in parent_dir:
                try:
                    os.rmdir(parent_dir)
                except Exception:
                    pass


def is_ffmpeg_available() -> bool:
    """Check if FFmpeg is available on the system."""
    return shutil.which('ffmpeg') is not None


def get_video_duration(video_path: str) -> float:
    """Quick helper to get video duration in seconds."""
    processor = VideoProcessor(require_ffmpeg=True)
    info = processor.get_video_info(video_path)
    return info['duration']
