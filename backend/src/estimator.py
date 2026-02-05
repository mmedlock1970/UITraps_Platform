"""
Cost and Time Estimation for UI Traps Analyzer

Provides estimates before analysis runs so users know what to expect.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisEstimate:
    """Estimation results for an analysis job."""

    # What was uploaded
    input_type: str  # 'single_image', 'multi_image', 'video'
    file_count: int
    total_size_mb: float

    # For video: estimated frames to analyze
    estimated_frames: Optional[int] = None
    video_duration_seconds: Optional[float] = None

    # Time estimates (in seconds)
    time_min_seconds: int = 0
    time_max_seconds: int = 0

    # Cost estimates (in credits or dollars)
    cost_min_credits: float = 0.0
    cost_max_credits: float = 0.0
    cost_min_dollars: float = 0.0
    cost_max_dollars: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            'input_type': self.input_type,
            'file_count': self.file_count,
            'total_size_mb': round(self.total_size_mb, 2),
            'estimated_frames': self.estimated_frames,
            'video_duration_seconds': self.video_duration_seconds,
            'time_estimate': {
                'min_seconds': self.time_min_seconds,
                'max_seconds': self.time_max_seconds,
                'min_formatted': format_time(self.time_min_seconds),
                'max_formatted': format_time(self.time_max_seconds),
            },
            'cost_estimate': {
                'min_credits': self.cost_min_credits,
                'max_credits': self.cost_max_credits,
                'min_dollars': round(self.cost_min_dollars, 2),
                'max_dollars': round(self.cost_max_dollars, 2),
            }
        }


# Estimation constants (adjust based on actual measurements)
class EstimationConstants:
    # Time per image analysis (seconds)
    TIME_PER_IMAGE_MIN = 30
    TIME_PER_IMAGE_MAX = 60

    # Time for video frame extraction (seconds)
    VIDEO_EXTRACTION_TIME = 10

    # Cost per image (in credits - 1 credit = 1 analysis unit)
    CREDITS_PER_IMAGE = 1

    # Cost per credit in dollars (based on Claude API pricing)
    # ~$0.015 input + $0.075 output per 1K tokens, image ~1000 tokens
    DOLLARS_PER_CREDIT_MIN = 0.10
    DOLLARS_PER_CREDIT_MAX = 0.30

    # Maximum files allowed
    MAX_IMAGES = 10
    MAX_VIDEO_FRAMES = 20


def format_time(seconds: int) -> str:
    """Format seconds as human-readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        if secs == 0:
            return f"{mins} minute{'s' if mins != 1 else ''}"
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


def estimate_single_image(file_size_bytes: int) -> AnalysisEstimate:
    """
    Estimate for a single image analysis.

    Args:
        file_size_bytes: Size of the image file

    Returns:
        AnalysisEstimate with time and cost predictions
    """
    return AnalysisEstimate(
        input_type='single_image',
        file_count=1,
        total_size_mb=file_size_bytes / (1024 * 1024),
        time_min_seconds=EstimationConstants.TIME_PER_IMAGE_MIN,
        time_max_seconds=EstimationConstants.TIME_PER_IMAGE_MAX,
        cost_min_credits=EstimationConstants.CREDITS_PER_IMAGE,
        cost_max_credits=EstimationConstants.CREDITS_PER_IMAGE,
        cost_min_dollars=EstimationConstants.DOLLARS_PER_CREDIT_MIN,
        cost_max_dollars=EstimationConstants.DOLLARS_PER_CREDIT_MAX,
    )


def estimate_multi_image(file_sizes_bytes: List[int]) -> AnalysisEstimate:
    """
    Estimate for multiple image analysis.

    Args:
        file_sizes_bytes: List of file sizes

    Returns:
        AnalysisEstimate with time and cost predictions
    """
    count = len(file_sizes_bytes)

    if count > EstimationConstants.MAX_IMAGES:
        raise ValueError(
            f"Maximum {EstimationConstants.MAX_IMAGES} images allowed. "
            f"You uploaded {count}."
        )

    total_size = sum(file_sizes_bytes)

    return AnalysisEstimate(
        input_type='multi_image',
        file_count=count,
        total_size_mb=total_size / (1024 * 1024),
        time_min_seconds=count * EstimationConstants.TIME_PER_IMAGE_MIN,
        time_max_seconds=count * EstimationConstants.TIME_PER_IMAGE_MAX,
        cost_min_credits=count * EstimationConstants.CREDITS_PER_IMAGE,
        cost_max_credits=count * EstimationConstants.CREDITS_PER_IMAGE,
        cost_min_dollars=count * EstimationConstants.DOLLARS_PER_CREDIT_MIN,
        cost_max_dollars=count * EstimationConstants.DOLLARS_PER_CREDIT_MAX,
    )


def estimate_video(
    file_size_bytes: int,
    duration_seconds: float,
    estimated_frames: int
) -> AnalysisEstimate:
    """
    Estimate for video analysis.

    Args:
        file_size_bytes: Size of video file
        duration_seconds: Video duration
        estimated_frames: Estimated frames to extract

    Returns:
        AnalysisEstimate with time and cost predictions
    """
    # Clamp frames to maximum
    frames = min(estimated_frames, EstimationConstants.MAX_VIDEO_FRAMES)

    # Time = extraction time + per-frame analysis time
    time_min = (
        EstimationConstants.VIDEO_EXTRACTION_TIME +
        frames * EstimationConstants.TIME_PER_IMAGE_MIN
    )
    time_max = (
        EstimationConstants.VIDEO_EXTRACTION_TIME +
        frames * EstimationConstants.TIME_PER_IMAGE_MAX
    )

    return AnalysisEstimate(
        input_type='video',
        file_count=1,
        total_size_mb=file_size_bytes / (1024 * 1024),
        estimated_frames=frames,
        video_duration_seconds=duration_seconds,
        time_min_seconds=time_min,
        time_max_seconds=time_max,
        cost_min_credits=frames * EstimationConstants.CREDITS_PER_IMAGE,
        cost_max_credits=frames * EstimationConstants.CREDITS_PER_IMAGE,
        cost_min_dollars=frames * EstimationConstants.DOLLARS_PER_CREDIT_MIN,
        cost_max_dollars=frames * EstimationConstants.DOLLARS_PER_CREDIT_MAX,
    )


def detect_input_type(filenames: List[str]) -> str:
    """
    Detect the type of input based on file extensions.

    Args:
        filenames: List of uploaded filenames

    Returns:
        'single_image', 'multi_image', or 'video'
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    video_extensions = {'.mp4', '.mov', '.webm', '.avi', '.mkv'}

    has_images = False
    has_videos = False

    for filename in filenames:
        ext = Path(filename).suffix.lower()
        if ext in image_extensions:
            has_images = True
        elif ext in video_extensions:
            has_videos = True

    # Video takes precedence (can't mix)
    if has_videos:
        if has_images:
            raise ValueError("Cannot mix images and videos. Upload one type.")
        return 'video'

    if len(filenames) == 1:
        return 'single_image'

    return 'multi_image'
