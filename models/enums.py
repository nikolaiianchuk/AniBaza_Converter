"""Enums for build states and configuration options.

Using IntEnum to maintain backward compatibility with existing
integer-based currentIndex() values and `in [0, 1]` checks.
"""

from enum import IntEnum


class BuildState(IntEnum):
    """Video build state - which outputs to generate."""

    SOFT_AND_HARD = 0  # Both softsub and hardsub
    SOFT_ONLY = 1  # Only softsub
    HARD_ONLY = 2  # Only hardsub
    FOR_HARDSUBBERS = 3  # Special hardsub mode (no audio/softsub)
    RAW_REPAIR = 4  # Repair raw video


class NvencState(IntEnum):
    """NVENC hardware encoding state."""

    NVENC_BOTH = 0  # Use NVENC for both softsub and hardsub
    NVENC_SOFT_ONLY = 1  # Use NVENC only for softsub
    NVENC_HARD_ONLY = 2  # Use NVENC only for hardsub
    NVENC_NONE = 3  # No NVENC (software encoding)


class LogoState(IntEnum):
    """Logo burn-in state."""

    LOGO_BOTH = 0  # Burn logo into both softsub and hardsub
    LOGO_SOFT_ONLY = 1  # Burn logo only into softsub
    LOGO_HARD_ONLY = 2  # Burn logo only into hardsub
