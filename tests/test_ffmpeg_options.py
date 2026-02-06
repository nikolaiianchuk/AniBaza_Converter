"""Tests for models/ffmpeg_options.py."""

from pathlib import Path
import pytest

from models.encoding import EncodingParams
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping,
    _escape_path_for_filter
)
from models.job import VideoSettings, VideoPresets
from models.render_paths import RenderPaths


class TestCodecOptions:
    """Test CodecOptions dataclass."""

    def test_codec_options_construction(self):
        """CodecOptions constructs with required fields."""
        codecs = CodecOptions(video_codec='libx264')

        assert codecs.video_codec == 'libx264'
        assert codecs.audio_codec == 'aac'  # Default
        assert codecs.subtitle_codec == 'copy'  # Default

    def test_codec_options_custom_values(self):
        """CodecOptions accepts custom codec values."""
        codecs = CodecOptions(
            video_codec='hevc_nvenc',
            audio_codec='opus',
            subtitle_codec='ass'
        )

        assert codecs.video_codec == 'hevc_nvenc'
        assert codecs.audio_codec == 'opus'
        assert codecs.subtitle_codec == 'ass'

    def test_codec_options_immutable(self):
        """CodecOptions is immutable (frozen dataclass)."""
        codecs = CodecOptions(video_codec='hevc')

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            codecs.video_codec = 'libx264'


class TestStreamMapping:
    """Test StreamMapping dataclass."""

    def test_stream_mapping_defaults(self):
        """StreamMapping has sensible defaults."""
        mapping = StreamMapping()

        assert mapping.video_input_index == 0
        assert mapping.audio_input_index == 1
        assert mapping.subtitle_input_index == 2

    def test_stream_mapping_custom(self):
        """StreamMapping accepts custom indices."""
        mapping = StreamMapping(
            video_input_index=0,
            audio_input_index=None,  # No audio
            subtitle_input_index=1
        )

        assert mapping.video_input_index == 0
        assert mapping.audio_input_index is None
        assert mapping.subtitle_input_index == 1


class TestFilterOptions:
    """Test FilterOptions dataclass."""

    def test_filter_options_no_filters(self):
        """FilterOptions with no paths returns None filter string."""
        filters = FilterOptions()

        assert filters.to_filter_string() is None

    def test_filter_options_logo_only(self, tmp_path):
        """FilterOptions with logo only builds correct filter."""
        logo = tmp_path / "logo.ass"
        filters = FilterOptions(logo_path=logo)

        filter_str = filters.to_filter_string()

        assert filter_str is not None
        assert "subtitles=" in filter_str
        assert "logo.ass" in filter_str

    def test_filter_options_subtitle_only(self, tmp_path):
        """FilterOptions with subtitle only builds correct filter."""
        sub = tmp_path / "sub.ass"
        filters = FilterOptions(subtitle_path=sub)

        filter_str = filters.to_filter_string()

        assert filter_str is not None
        assert "subtitles=" in filter_str
        assert "sub.ass" in filter_str

    def test_filter_options_both(self, tmp_path):
        """FilterOptions with logo and subtitle builds combined filter."""
        logo = tmp_path / "logo.ass"
        sub = tmp_path / "sub.ass"
        filters = FilterOptions(logo_path=logo, subtitle_path=sub)

        filter_str = filters.to_filter_string()

        assert filter_str is not None
        assert filter_str.count("subtitles=") == 2
        assert ", " in filter_str  # Comma-separated

    def test_filter_options_immutable(self, tmp_path):
        """FilterOptions is immutable."""
        logo = tmp_path / "logo.ass"
        filters = FilterOptions(logo_path=logo)

        with pytest.raises(Exception):
            filters.logo_path = tmp_path / "different.ass"


class TestPathEscaping:
    """Test _escape_path_for_filter function."""

    def test_escape_unix_path(self):
        """Unix paths convert backslashes to forward slashes."""
        path = Path("/home/user/video.mkv")
        escaped = _escape_path_for_filter(path)

        assert escaped == "/home/user/video.mkv"

    def test_escape_windows_path_no_drive(self, tmp_path):
        """Relative Windows paths work correctly."""
        path = tmp_path / "subdir" / "file.ass"
        escaped = _escape_path_for_filter(path)

        # Should have forward slashes
        assert "\\" not in escaped
        assert "/" in escaped


class TestFFmpegOptions:
    """Test FFmpegOptions dataclass."""

    def test_ffmpeg_options_complete(self, mock_render_paths):
        """FFmpegOptions constructs with all required fields."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            use_nvenc=False
        )

        assert options.paths == mock_render_paths
        assert options.codecs.video_codec == 'libx264'
        assert options.encoding.crf == 18
        assert options.video == VideoPresets.SOFTSUB
        assert options.preset == 'faster'  # Default

    def test_ffmpeg_options_custom_preset(self, mock_render_paths):
        """FFmpegOptions accepts custom preset."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(),
            preset='ultrafast'
        )

        assert options.preset == 'ultrafast'

    def test_ffmpeg_options_nvenc_flags(self, mock_render_paths):
        """FFmpegOptions has correct NVENC flags."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='h264_nvenc'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            use_nvenc=True
        )

        assert options.use_nvenc is True
        assert options.codecs.video_codec == 'h264_nvenc'

    def test_ffmpeg_options_audio_subtitle_flags(self, mock_render_paths):
        """FFmpegOptions has correct audio/subtitle inclusion flags."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(),
            include_audio=False,
            include_subtitles=False
        )

        assert options.include_audio is False
        assert options.include_subtitles is False

    def test_ffmpeg_options_immutable(self, mock_render_paths):
        """FFmpegOptions is immutable."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions()
        )

        with pytest.raises(Exception):
            options.use_nvenc = True
