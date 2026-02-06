"""Structured FFmpeg command options.

Pure data structures for representing FFmpeg encoding options.
No logic, no side effects - just typed data.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from models.encoding import EncodingParams
from models.job import VideoSettings
from models.render_paths import RenderPaths


@dataclass(frozen=True)
class CodecOptions:
    """Codec selection options."""
    video_codec: str  # 'libx264', 'h264_nvenc', 'hevc', 'hevc_nvenc'
    audio_codec: str = 'aac'
    subtitle_codec: str = 'copy'


@dataclass(frozen=True)
class StreamMapping:
    """Input stream mapping configuration."""
    video_input_index: int = 0
    audio_input_index: Optional[int] = 1
    subtitle_input_index: Optional[int] = 2


@dataclass(frozen=True)
class FilterOptions:
    """Video filter configuration."""
    logo_path: Optional[Path] = None
    subtitle_path: Optional[Path] = None

    def to_filter_string(self) -> Optional[str]:
        """Build -vf filter string.

        Returns:
            Filter string for -vf argument, or None if no filters.
        """
        filters = []
        if self.logo_path:
            escaped = _escape_path_for_filter(self.logo_path)
            filters.append(f"subtitles='{escaped}'")
        if self.subtitle_path:
            escaped = _escape_path_for_filter(self.subtitle_path)
            filters.append(f"subtitles='{escaped}'")

        return ", ".join(filters) if filters else None


@dataclass(frozen=True)
class FFmpegOptions:
    """Complete FFmpeg encoding options.

    This is the unified representation of all encoding settings.
    Single source of truth for building ffmpeg commands.

    All fields are immutable - once created, options cannot change.
    """
    # Input/output
    paths: RenderPaths

    # Codecs
    codecs: CodecOptions

    # Encoding parameters
    encoding: EncodingParams

    # Video settings
    video: VideoSettings

    # Filters
    filters: FilterOptions

    # Stream configuration
    streams: StreamMapping = StreamMapping()

    # Preset
    preset: str = 'faster'

    # Flags
    use_nvenc: bool = False
    include_audio: bool = True
    include_subtitles: bool = True


def _escape_path_for_filter(path: Path) -> str:
    """Escape path for use in FFmpeg filter string.

    Windows paths need special escaping for FFmpeg filter syntax.
    Example: C:\\foo\\bar.ass → C/foo/bar.ass with colon escaping

    Args:
        path: Path to escape

    Returns:
        Escaped path string safe for FFmpeg filter
    """
    # Convert backslashes to forward slashes
    path_str = str(path).replace('\\', '/')
    # Escape colon for filter syntax (Windows drive letters)
    return path_str.replace(':/', r'\:\\')
