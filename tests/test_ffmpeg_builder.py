"""Tests for modules/ffmpeg_builder.py."""

from pathlib import Path

from models.encoding import EncodingParams, EncodingDefaults
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping
)
from models.job import VideoPresets
from modules.ffmpeg_builder import build_ffmpeg_args


class TestFFmpegBuilder:
    """Test build_ffmpeg_args pure function."""

    def test_build_basic_softsub_args(self, mock_render_paths):
        """Builds basic softsub command with all required elements."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            use_nvenc=False,
            include_audio=True,
            include_subtitles=True
        )

        args = build_ffmpeg_args(options)

        # Verify basic structure
        assert '-y' in args
        assert '-i' in args
        assert '-c:v' in args
        assert args[args.index('-c:v') + 1] == 'libx264'
        assert '-crf' in args
        assert str(mock_render_paths.softsub) in args

    def test_build_nvenc_hardsub_args(self, mock_render_paths):
        """Builds NVENC hardsub command with CQ instead of CRF."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc_nvenc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(),
            use_nvenc=True,
            include_audio=True,
            include_subtitles=False
        )

        args = build_ffmpeg_args(options)

        # Verify NVENC-specific args
        assert args[args.index('-c:v') + 1] == 'hevc_nvenc'
        assert '-cq' in args
        assert '-qmin' in args
        assert '-qmax' in args
        assert '-crf' not in args  # CRF not used with NVENC
        assert str(mock_render_paths.hardsub) in args

    def test_build_with_logo_filter(self, mock_render_paths, tmp_path):
        """Builds command with logo burning filter."""
        logo = tmp_path / "logo.ass"
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(logo_path=logo),
            use_nvenc=False
        )

        args = build_ffmpeg_args(options)

        # Verify filter is present
        assert '-vf' in args
        vf_index = args.index('-vf')
        filter_string = args[vf_index + 1]
        assert 'subtitles=' in filter_string
        assert 'logo.ass' in filter_string

    def test_build_with_both_filters(self, mock_render_paths, tmp_path):
        """Builds command with both logo and subtitle burning."""
        logo = tmp_path / "logo.ass"
        sub = tmp_path / "sub.ass"
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(logo_path=logo, subtitle_path=sub),
            use_nvenc=False,
            include_subtitles=False
        )

        args = build_ffmpeg_args(options)

        # Verify filter is present with both
        assert '-vf' in args
        vf_index = args.index('-vf')
        filter_string = args[vf_index + 1]
        assert filter_string.count('subtitles=') == 2  # Logo + sub

    def test_build_no_audio(self, mock_render_paths):
        """Builds command without audio stream."""
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

        args = build_ffmpeg_args(options)

        # Verify audio codec not present
        assert '-c:a' not in args
        assert '-b:a' not in args

    def test_build_with_audio(self, mock_render_paths):
        """Builds command with audio using defaults."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            include_audio=True
        )

        args = build_ffmpeg_args(options)

        # Verify audio codec and settings
        assert '-c:a' in args
        assert args[args.index('-c:a') + 1] == EncodingDefaults.AUDIO_CODEC
        assert '-b:a' in args
        assert args[args.index('-b:a') + 1] == EncodingDefaults.AUDIO_BITRATE
        assert '-ar' in args
        assert args[args.index('-ar') + 1] == str(EncodingDefaults.AUDIO_SAMPLE_RATE)

    def test_build_with_subtitle_codec(self, mock_render_paths):
        """Builds command with subtitle stream codec."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        # Mock paths with subtitle
        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264', subtitle_codec='copy'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            include_subtitles=True
        )

        args = build_ffmpeg_args(options)

        # Verify subtitle codec
        assert '-c:s' in args
        assert args[args.index('-c:s') + 1] == 'copy'

    def test_build_video_profile_and_format(self, mock_render_paths):
        """Builds command with video profile and pixel format."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions()
        )

        args = build_ffmpeg_args(options)

        # Verify profile and format
        assert '-profile:v' in args
        assert args[args.index('-profile:v') + 1] == VideoPresets.SOFTSUB.video_profile
        assert '-pix_fmt' in args
        assert args[args.index('-pix_fmt') + 1] == VideoPresets.SOFTSUB.pixel_format

    def test_build_with_tune(self, mock_render_paths):
        """Builds command with tune parameter (non-NVENC)."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,  # Has tune='animation'
            filters=FilterOptions(),
            use_nvenc=False
        )

        args = build_ffmpeg_args(options)

        # Verify tune is present
        assert '-tune' in args
        assert args[args.index('-tune') + 1] == 'animation'

    def test_build_nvenc_skips_tune(self, mock_render_paths):
        """Builds NVENC command without tune parameter."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='h264_nvenc'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,  # Has tune, but should be skipped
            filters=FilterOptions(),
            use_nvenc=True
        )

        args = build_ffmpeg_args(options)

        # Verify tune is NOT present
        assert '-tune' not in args

    def test_build_potato_no_tune(self, mock_render_paths):
        """Builds potato preset command without tune."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.POTATO,  # tune is empty string
            filters=FilterOptions(),
            use_nvenc=False
        )

        args = build_ffmpeg_args(options)

        # Verify tune is NOT present (empty string)
        assert '-tune' not in args

    def test_build_is_deterministic(self, mock_render_paths):
        """Same options produce same args (pure function)."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions()
        )

        args1 = build_ffmpeg_args(options)
        args2 = build_ffmpeg_args(options)

        assert args1 == args2  # Deterministic output

    def test_build_stream_mapping(self, mock_render_paths):
        """Builds command with correct stream mapping."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            streams=StreamMapping(
                video_input_index=0,
                audio_input_index=1,
                subtitle_input_index=2
            ),
            include_audio=True,
            include_subtitles=True
        )

        args = build_ffmpeg_args(options)

        # Verify stream mappings
        assert '-map' in args
        map_indices = [i for i, arg in enumerate(args) if arg == '-map']
        assert len(map_indices) >= 2  # At least video and audio

        # Check video mapping
        assert '0:v:0' in args

    def test_build_metadata(self, mock_render_paths):
        """Builds command with stream metadata."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            include_audio=True,
            include_subtitles=True
        )

        args = build_ffmpeg_args(options)

        # Verify metadata is present
        assert '-metadata:s:v:0' in args
        assert 'title=Original' in args
        assert 'language=jap' in args
        assert 'title=AniBaza' in args
        assert 'language=rus' in args
