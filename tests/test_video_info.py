"""Tests for models/video_info.py - video metadata parsing."""

import pytest

from models.video_info import (
    VideoInfo, parse_ffprobe_output,
    _parse_duration, _parse_resolution, _parse_pixel_format, _parse_video_profile
)


class TestParseDuration:
    """Test duration parsing from ffprobe output."""

    def test_parse_duration_standard(self):
        """Parse standard duration format."""
        line = "Duration: 00:24:02.05, start: 0.000000, bitrate: 5000 kb/s"
        duration = _parse_duration(line)

        assert duration == pytest.approx(24 * 60 + 2.05)  # 1442.05 seconds

    def test_parse_duration_with_hours(self):
        """Parse duration with hours."""
        line = "Duration: 01:30:45.50, start: 0.000000"
        duration = _parse_duration(line)

        assert duration == pytest.approx(1 * 3600 + 30 * 60 + 45.5)

    def test_parse_duration_no_match(self):
        """Return None when no duration found."""
        line = "Stream #0:0: Video: h264"
        duration = _parse_duration(line)

        assert duration is None


class TestParseResolution:
    """Test resolution parsing from ffprobe output."""

    def test_parse_resolution_1080p(self):
        """Parse 1920x1080 as 1080p."""
        line = "Stream #0:0: Video: h264, yuv420p, 1920x1080, 23.98 fps"
        resolution = _parse_resolution(line)

        assert resolution == "1080p"

    def test_parse_resolution_720p(self):
        """Parse 1280x720 as 720p."""
        line = "1280x720, 30 fps"
        resolution = _parse_resolution(line)

        assert resolution == "720p"

    def test_parse_resolution_4k(self):
        """Parse 3840x2160 as 2160p."""
        line = "3840x2160, 60 fps"
        resolution = _parse_resolution(line)

        assert resolution == "2160p"

    def test_parse_resolution_8k(self):
        """Parse 7680x4320 as K format."""
        line = "7680x4320, 24 fps"
        resolution = _parse_resolution(line)

        # 4320 / 1024 = 4.21875
        assert "4." in resolution
        assert "K" in resolution

    def test_parse_resolution_no_match(self):
        """Return None when no resolution found."""
        line = "Duration: 00:24:02.05"
        resolution = _parse_resolution(line)

        assert resolution is None


class TestParsePixelFormat:
    """Test pixel format parsing from codec line."""

    def test_parse_pixel_format_yuv420p_comma(self):
        """Parse yuv420p followed by comma."""
        line = "Video: h264 (High), yuv420p, 1920x1080"
        fmt = _parse_pixel_format(line)

        assert fmt == "yuv420p"

    def test_parse_pixel_format_yuv420p_paren(self):
        """Parse yuv420p followed by parenthesis."""
        line = "Video: h264, yuv420p(tv, bt709)"
        fmt = _parse_pixel_format(line)

        assert fmt == "yuv420p"

    def test_parse_pixel_format_yuv420p_space(self):
        """Parse yuv420p followed by space."""
        line = "Video: h264, yuv420p 1920x1080"
        fmt = _parse_pixel_format(line)

        assert fmt == "yuv420p"

    def test_parse_pixel_format_yuv420p10le(self):
        """Parse yuv420p10le (10-bit)."""
        line = "Video: hevc (Main 10), yuv420p10le(tv, bt2020nc)"
        fmt = _parse_pixel_format(line)

        assert fmt == "yuv420p10le"

    def test_parse_pixel_format_p010le(self):
        """Parse p010le (10-bit alternative)."""
        line = "Video: hevc, p010le(tv), 1920x1080"
        fmt = _parse_pixel_format(line)

        assert fmt == "p010le"

    def test_parse_pixel_format_priority(self):
        """p010le has higher priority than yuv420p."""
        # If both present, should return p010le
        line = "Video: hevc, p010le, yuv420p"
        fmt = _parse_pixel_format(line)

        assert fmt == "p010le"

    def test_parse_pixel_format_no_match(self):
        """Return None when no format found."""
        line = "Audio: aac, 48000 Hz, stereo"
        fmt = _parse_pixel_format(line)

        assert fmt is None


class TestParseVideoProfile:
    """Test video profile parsing from codec line."""

    def test_parse_video_profile_main(self):
        """Parse Main profile."""
        line = "Video: h264 (Main), yuv420p, 1920x1080"
        profile = _parse_video_profile(line)

        assert profile == "main"

    def test_parse_video_profile_main10(self):
        """Parse Main 10 profile."""
        line = "Video: hevc (Main 10), yuv420p10le"
        profile = _parse_video_profile(line)

        assert profile == "main10"

    def test_parse_video_profile_high(self):
        """Parse High profile."""
        line = "Video: h264 (High), yuv420p"
        profile = _parse_video_profile(line)

        assert profile == "high"

    def test_parse_video_profile_high10(self):
        """Parse High 10 profile."""
        line = "Video: h264 (High 10), yuv420p10le"
        profile = _parse_video_profile(line)

        assert profile == "high10"

    def test_parse_video_profile_no_match(self):
        """Return None when no profile found."""
        line = "Video: h264, yuv420p, 1920x1080"
        profile = _parse_video_profile(line)

        assert profile is None


class TestParseFfprobeOutput:
    """Test complete ffprobe output parsing."""

    def test_parse_complete_output_1080p(self):
        """Parse complete 1080p video info."""
        lines = [
            "ffprobe version 7.1",
            "Input #0, matroska,webm, from 'video.mkv':",
            "  Duration: 00:24:02.05, start: 0.000000, bitrate: 5000 kb/s",
            "  Stream #0:0: Video: h264 (High), yuv420p, 1920x1080, 23.98 fps"
        ]

        info = parse_ffprobe_output(lines)

        assert info.duration_seconds == pytest.approx(1442.05)
        assert info.total_frames == pytest.approx(1442.05 * 24000 / 1001.0)
        assert info.resolution == "1080p"
        assert info.pixel_format == "yuv420p"
        assert info.video_profile == "high"

    def test_parse_complete_output_720p_main10(self):
        """Parse 720p video with Main 10 profile."""
        lines = [
            "Duration: 00:12:30.00, start: 0.000000",
            "Stream #0:0: Video: hevc (Main 10), yuv420p10le(tv), 1280x720"
        ]

        info = parse_ffprobe_output(lines)

        assert info.duration_seconds == pytest.approx(12 * 60 + 30)
        assert info.resolution == "720p"
        assert info.pixel_format == "yuv420p10le"
        assert info.video_profile == "main10"

    def test_parse_output_with_p010le(self):
        """Parse video with p010le pixel format."""
        lines = [
            "Duration: 00:05:00.00",
            "Stream #0:0: Video: hevc (Main 10), p010le(tv), 3840x2160"
        ]

        info = parse_ffprobe_output(lines)

        assert info.resolution == "2160p"
        assert info.pixel_format == "p010le"

    def test_parse_empty_output(self):
        """Return defaults for empty output."""
        info = parse_ffprobe_output([])

        assert info.duration_seconds == 0.0
        assert info.total_frames == 0.0
        assert info.resolution == "unknown"
        assert info.pixel_format == "yuv420p"
        assert info.video_profile == "main"

    def test_parse_partial_output(self):
        """Handle missing fields gracefully."""
        lines = [
            "Duration: 00:10:00.00",
            # No video stream info
        ]

        info = parse_ffprobe_output(lines)

        assert info.duration_seconds == pytest.approx(600.0)
        assert info.resolution == "unknown"  # Default
        assert info.pixel_format == "yuv420p"  # Default
        assert info.video_profile == "main"  # Default

    def test_videoinfo_immutable(self):
        """VideoInfo is immutable (frozen dataclass)."""
        info = VideoInfo(duration_seconds=100.0)

        with pytest.raises(Exception):  # FrozenInstanceError
            info.duration_seconds = 200.0


class TestVideoInfoDefaults:
    """Test VideoInfo default values."""

    def test_videoinfo_defaults(self):
        """VideoInfo has sensible defaults."""
        info = VideoInfo()

        assert info.duration_seconds == 0.0
        assert info.total_frames == 0.0
        assert info.resolution == "unknown"
        assert info.pixel_format == "yuv420p"
        assert info.video_profile == "main"

    def test_videoinfo_partial_init(self):
        """VideoInfo can be partially initialized."""
        info = VideoInfo(duration_seconds=100.0, resolution="720p")

        assert info.duration_seconds == 100.0
        assert info.resolution == "720p"
        assert info.pixel_format == "yuv420p"  # Default
