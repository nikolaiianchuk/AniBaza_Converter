"""Video metadata parsing from ffprobe output.

Pure functions for parsing ffmpeg/ffprobe output into structured data.
No side effects, easy to test, reusable.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VideoInfo:
    """Parsed video metadata from ffprobe output.

    All fields have sensible defaults if parsing fails.
    Immutable to prevent accidental modification.
    """

    duration_seconds: float = 0.0
    total_frames: float = 0.0
    resolution: str = "unknown"
    pixel_format: str = "yuv420p"
    video_profile: str = "main"


def parse_ffprobe_output(lines: list[str]) -> VideoInfo:
    """Parse video info from ffprobe output lines.

    Pure function: same input always produces same output.

    Args:
        lines: Output lines from ffprobe

    Returns:
        VideoInfo with parsed metadata
    """
    duration_sec: Optional[float] = None
    resolution: Optional[str] = None
    pixel_format: Optional[str] = None
    video_profile: Optional[str] = None

    for line in lines:
        # Parse each field independently (first match wins)
        if duration_sec is None:
            duration_sec = _parse_duration(line)

        if resolution is None:
            resolution = _parse_resolution(line)

        # Only check codec lines for format/profile
        if 'Video:' in line:
            if pixel_format is None:
                pixel_format = _parse_pixel_format(line)
            if video_profile is None:
                video_profile = _parse_video_profile(line)

    # Calculate frames from duration (23.976 fps = 24000/1001)
    total_frames = (duration_sec * 24000 / 1001.0) if duration_sec else 0.0

    return VideoInfo(
        duration_seconds=duration_sec or 0.0,
        total_frames=total_frames,
        resolution=resolution or "unknown",
        pixel_format=pixel_format or "yuv420p",
        video_profile=video_profile or "main"
    )


def _parse_duration(line: str) -> Optional[float]:
    """Parse duration from ffprobe line.

    Example: "Duration: 00:24:02.05, start: 0.000000"

    Args:
        line: Single line from ffprobe output

    Returns:
        Duration in seconds, or None if not found
    """
    match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', line)
    if match:
        hrs, minutes, sec = map(float, match.groups())
        return hrs * 3600 + minutes * 60 + sec
    return None


def _parse_resolution(line: str) -> Optional[str]:
    """Parse resolution from ffprobe line.

    Example: "1920x1080" -> "1080p"
              "3840x2160" -> "2160p"
              "7680x4320" -> "4.21875K"

    Args:
        line: Single line from ffprobe output

    Returns:
        Resolution string like "1080p" or "4K", or None if not found
    """
    match = re.search(r'(\d{3,4})x(\d{3,4})', line)
    if match:
        _, height = match.groups()
        height_int = int(height)
        if height_int < 4096:
            return f"{height}p"
        else:
            return f"{height_int/1024}K"
    return None


def _parse_pixel_format(codec_line: str) -> Optional[str]:
    """Parse pixel format from codec info line.

    Handles various delimiters after format name: comma, space, parenthesis.
    Checks in priority order: p010le > yuv420p10le > yuv420p

    Example: "Video: hevc (Main 10), yuv420p10le(tv, bt2020nc/bt2020/smpte2084)"

    Args:
        codec_line: Line containing video codec info

    Returns:
        Pixel format string, or None if not found
    """
    # Check in priority order (most specific first)
    for fmt in ['p010le', 'yuv420p10le', 'yuv420p']:
        # Match format followed by delimiter (comma, space, or paren)
        if re.search(rf'\b{fmt}[,\s(]', codec_line):
            return fmt
    return None


def _parse_video_profile(codec_line: str) -> Optional[str]:
    """Parse video profile from codec info line.

    Maps ffmpeg profile markers to profile names.

    Example: "Video: h264 (High 10)" -> "high10"

    Args:
        codec_line: Line containing video codec info

    Returns:
        Profile name, or None if not found
    """
    profile_map = {
        '(Main)': 'main',
        '(Main 10)': 'main10',
        '(High)': 'high',
        '(High 10)': 'high10'
    }

    for marker, profile in profile_map.items():
        if marker in codec_line:
            return profile

    return None
