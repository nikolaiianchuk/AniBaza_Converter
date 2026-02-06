"""Encoding parameters and defaults for video rendering."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodingParams:
    """Calculated encoding parameters for a specific encode job.

    These are computed based on input video characteristics and user settings.
    """

    avg_bitrate: str  # e.g., "6M"
    max_bitrate: str  # e.g., "9M"
    buffer_size: str  # e.g., "18M"
    crf: int  # Constant Rate Factor for software encoding
    cq: int  # Constant Quality for NVENC
    qmin: int  # Minimum quantizer
    qmax: int  # Maximum quantizer


class EncodingDefaults:
    """Hardcoded encoding constants and defaults.

    These should eventually be configurable but are currently
    scattered throughout the codebase.
    """

    # Audio encoding
    AUDIO_BITRATE = "320K"
    AUDIO_SAMPLE_RATE = 48000
    AUDIO_CODEC = "aac"

    # Video encoding
    VIDEO_BITRATE = "3500k"  # Default average bitrate
    MAX_BITRATE_CAP = 6  # Maximum bitrate in Mbps

    # Frame rate (23.976 fps = 24000/1001)
    FRAME_RATE_NUM = 24000
    FRAME_RATE_DEN = 1001

    # CRF values by resolution
    CRF_1080P = 18
    CRF_720P = 20
    CRF_POTATO = 23

    # CQ offsets from CRF for NVENC
    CQ_OFFSET = 1  # CQ = CRF + 1

    # Quantizer ranges
    QMIN_OFFSET = 2  # qmin = cq - 2
    QMAX_OFFSET = 4  # qmax = cq + 4
