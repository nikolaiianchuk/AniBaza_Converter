"""Factory for creating FFmpegOptions from high-level config.

Handles the complexity of converting RenderJob settings → FFmpegOptions.
Isolates path preparation and option assembly logic.
"""

import shutil
from pathlib import Path
from typing import Optional

from configs.config import Config
from models.encoding import EncodingParams
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping
)
from models.job import VideoSettings
from models.render_paths import RenderPaths


class FFmpegOptionsFactory:
    """Factory for creating FFmpegOptions from render job settings."""

    def __init__(self, config: Config, temp_dir: Path):
        """Initialize factory.

        Args:
            config: Application configuration (for logo path)
            temp_dir: Temporary directory for subtitle preprocessing
        """
        self.config = config
        self.temp_dir = temp_dir

    def create_softsub_options(
        self,
        paths: RenderPaths,
        video_settings: VideoSettings,
        encoding_params: EncodingParams,
        use_nvenc: bool,
        include_logo: bool,
        preset: str
    ) -> FFmpegOptions:
        """Create options for softsub encoding.

        Softsub keeps subtitles as a separate stream (not burned in).
        Logo can optionally be burned into video.

        Args:
            paths: Validated input/output paths
            video_settings: Video encoding settings (profile, pixel format, tune)
            encoding_params: Rate control parameters (CRF, bitrate, etc)
            use_nvenc: Whether to use NVENC hardware encoding
            include_logo: Whether to burn logo into video
            preset: FFmpeg preset (faster, fast, medium, etc)

        Returns:
            Complete FFmpegOptions ready for build_ffmpeg_args()
        """
        # Prepare logo path (only if burning)
        logo_path = self.config.main_paths.logo if include_logo else None

        return FFmpegOptions(
            paths=paths,
            codecs=CodecOptions(
                video_codec='h264_nvenc' if use_nvenc else 'libx264',
                audio_codec='aac',
                subtitle_codec='copy'
            ),
            encoding=encoding_params,
            video=video_settings,
            filters=FilterOptions(
                logo_path=logo_path,
                subtitle_path=None  # Softsub keeps subs as stream, not burned
            ),
            streams=StreamMapping(
                video_input_index=0,
                audio_input_index=1 if paths.audio else None,
                subtitle_input_index=2 if paths.sub else None
            ),
            preset=preset,
            use_nvenc=use_nvenc,
            include_audio=True,
            include_subtitles=bool(paths.sub)
        )

    def create_hardsub_options(
        self,
        paths: RenderPaths,
        video_settings: VideoSettings,
        encoding_params: EncodingParams,
        use_nvenc: bool,
        include_logo: bool,
        preset: str
    ) -> FFmpegOptions:
        """Create options for hardsub encoding.

        Hardsub burns subtitles directly into video (no subtitle stream).
        Logo can also be burned in.

        Args:
            paths: Validated input/output paths
            video_settings: Video encoding settings
            encoding_params: Rate control parameters
            use_nvenc: Whether to use NVENC hardware encoding
            include_logo: Whether to burn logo into video
            preset: FFmpeg preset

        Returns:
            Complete FFmpegOptions ready for build_ffmpeg_args()
        """
        # Prepare paths for burning
        logo_path = self.config.main_paths.logo if include_logo else None
        sub_path = self._prepare_subtitle(paths.sub) if paths.sub else None

        return FFmpegOptions(
            paths=paths,
            codecs=CodecOptions(
                video_codec='hevc_nvenc' if use_nvenc else 'hevc',
                audio_codec='aac'
            ),
            encoding=encoding_params,
            video=video_settings,
            filters=FilterOptions(
                logo_path=logo_path,
                subtitle_path=sub_path  # Hardsub burns subs into video
            ),
            streams=StreamMapping(
                video_input_index=0,
                audio_input_index=1 if paths.audio else None,
                subtitle_input_index=None  # No subtitle stream in hardsub
            ),
            preset=preset,
            use_nvenc=use_nvenc,
            include_audio=bool(paths.audio),
            include_subtitles=False  # Burned in, not as separate stream
        )

    def _prepare_subtitle(self, sub_path: Optional[Path]) -> Optional[Path]:
        """Prepare subtitle file for burning.

        FFmpeg filter syntax has issues with brackets in filenames.
        If the subtitle filename contains [ or ], copy it to temp with sanitized name.

        Args:
            sub_path: Original subtitle path

        Returns:
            Path safe for FFmpeg filter string (may be temp copy)
        """
        if not sub_path or not sub_path.exists():
            return None

        name = sub_path.name

        # Check if name has problematic characters for FFmpeg filters
        if '[' in name or ']' in name:
            # Copy to temp with sanitized name
            sanitized_name = name.replace('[', '').replace(']', '')
            temp_path = self.temp_dir / sanitized_name

            # Ensure temp directory exists
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copyfile(sub_path, temp_path)
            self.config.log('FFmpegOptionsFactory', '_prepare_subtitle',
                          f"Copied subtitle with brackets to temp: {sanitized_name}")

            return temp_path

        return sub_path
