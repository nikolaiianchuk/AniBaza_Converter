"""Render job data model - fully describes a single video encode operation."""

from dataclasses import dataclass, field
from pathlib import Path

from models.encoding import EncodingParams
from models.enums import BuildState, LogoState, NvencState
from models.render_paths import RenderPaths


@dataclass(frozen=True)
class VideoSettings:
    """Base video encoding settings - the actual tunable parameters.

    These are the real settings that control video quality and encoding.
    Softsub, hardsub, and potato are just named presets for these values.
    """

    video_tune: str = "animation"  # libx264 tune preset
    video_profile: str = "high10"  # H.264 profile
    profile_level: str = "4.1"  # H.264 level
    pixel_format: str = "yuv420p10le"  # Pixel format (color depth)


class VideoPresets:
    """Named presets for video settings.

    Softsub, hardsub, and potato are presets - named VideoSettings with
    different defaults. The encoding methods resolve the correct preset
    per encode step.
    """

    SOFTSUB = VideoSettings(
        video_tune="animation",
        video_profile="high10",
        profile_level="4.1",
        pixel_format="yuv420p10le",
    )

    HARDSUB = VideoSettings(
        video_tune="animation",
        video_profile="main10",
        profile_level="4.1",
        pixel_format="yuv420p10le",
    )

    POTATO = VideoSettings(
        video_tune="",  # No tune in potato mode
        video_profile="main",
        profile_level="4.1",
        pixel_format="yuv420p",
    )


@dataclass
class RenderJob:
    """Complete description of a render job.

    This contains all information needed to execute a video encode,
    eliminating the need to pass around the giant Config object.
    """

    # File paths (input and output)
    paths: RenderPaths

    # Metadata
    episode_name: str

    # Build configuration
    build_state: BuildState
    nvenc_state: NvencState
    logo_state: LogoState

    # Encoding parameters (calculated from analysis)
    encoding_params: EncodingParams

    # Video settings for this specific encode
    video_settings: VideoSettings

    # Flags
    potato_mode: bool = False

    # Runtime state (mutable fields)
    total_duration_sec: float = field(default=0.0, init=False)
    total_frames: float = field(default=0.0, init=False)
    video_res: str = field(default="", init=False)
