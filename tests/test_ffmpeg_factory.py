"""Tests for modules/ffmpeg_factory.py."""

from pathlib import Path

from models.encoding import EncodingParams
from models.job import VideoPresets
from modules.ffmpeg_factory import FFmpegOptionsFactory


class TestFFmpegOptionsFactory:
    """Test FFmpegOptionsFactory."""

    def test_create_softsub_options(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates valid softsub options."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_softsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.SOFTSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=True,
            preset='faster'
        )

        assert options.codecs.video_codec == 'libx264'
        assert options.include_audio is True
        assert options.include_subtitles is True
        assert options.filters.logo_path is not None
        assert options.filters.subtitle_path is None  # Not burned in softsub
        assert options.preset == 'faster'

    def test_create_softsub_options_nvenc(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates softsub options with NVENC."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_softsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.SOFTSUB,
            encoding_params=encoding,
            use_nvenc=True,
            include_logo=False,
            preset='p4'
        )

        assert options.codecs.video_codec == 'h264_nvenc'
        assert options.use_nvenc is True
        assert options.filters.logo_path is None

    def test_create_hardsub_options(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates valid hardsub options."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_hardsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.HARDSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=True,
            preset='faster'
        )

        assert options.codecs.video_codec == 'hevc'
        assert options.include_audio is True
        assert options.include_subtitles is False  # Burned in
        assert options.filters.logo_path is not None
        assert options.filters.subtitle_path is not None  # Burned in hardsub

    def test_create_hardsub_options_nvenc(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates hardsub options with NVENC."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_hardsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.HARDSUB,
            encoding_params=encoding,
            use_nvenc=True,
            include_logo=False,
            preset='p7'
        )

        assert options.codecs.video_codec == 'hevc_nvenc'
        assert options.use_nvenc is True
        assert options.preset == 'p7'

    def test_create_hardsub_options_no_audio(self, mock_config, tmp_path):
        """Factory creates hardsub options without audio."""
        from models.render_paths import RenderPaths

        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        # Create paths without audio
        raw = tmp_path / "raw.mkv"
        raw.touch()
        paths_no_audio = RenderPaths(
            raw=raw,
            audio=None,  # No audio
            sub=tmp_path / "sub.ass",
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4"
        )

        options = factory.create_hardsub_options(
            paths=paths_no_audio,
            video_settings=VideoPresets.HARDSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=False,
            preset='faster'
        )

        assert options.include_audio is False
        assert options.streams.audio_input_index is None

    def test_prepare_subtitle_no_brackets(self, mock_config, tmp_path):
        """Subtitle without brackets returns original path."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)

        # Create subtitle with clean name
        sub_clean = tmp_path / "Episode_01.ass"
        sub_clean.write_text("test subtitle")

        prepared = factory._prepare_subtitle(sub_clean)

        assert prepared == sub_clean  # Same path returned

    def test_prepare_subtitle_with_brackets(self, mock_config, tmp_path):
        """Subtitle with brackets gets copied to temp."""
        # Use a different temp dir for the factory
        factory_temp = tmp_path / "factory_temp"
        factory = FFmpegOptionsFactory(mock_config, factory_temp)

        # Create subtitle with problematic name
        original_dir = tmp_path / "original"
        original_dir.mkdir()
        sub_with_brackets = original_dir / "[AniBaza] Episode 01.ass"
        sub_with_brackets.write_text("test subtitle")

        prepared = factory._prepare_subtitle(sub_with_brackets)

        # Should be different path
        assert prepared != sub_with_brackets
        # Should not have brackets
        assert '[' not in prepared.name
        assert ']' not in prepared.name
        # Should exist
        assert prepared.exists()
        # Should be in factory temp dir
        assert prepared.parent == factory_temp

    def test_prepare_subtitle_none(self, mock_config, tmp_path):
        """Prepare subtitle with None returns None."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)

        prepared = factory._prepare_subtitle(None)

        assert prepared is None

    def test_prepare_subtitle_nonexistent(self, mock_config, tmp_path):
        """Prepare subtitle with nonexistent path returns None."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)

        nonexistent = tmp_path / "doesnt_exist.ass"

        prepared = factory._prepare_subtitle(nonexistent)

        assert prepared is None

    def test_prepare_subtitle_creates_temp_dir(self, mock_config, tmp_path):
        """Prepare subtitle creates temp directory if needed."""
        # Use temp dir that doesn't exist yet
        factory_temp = tmp_path / "new_temp_dir"
        factory = FFmpegOptionsFactory(mock_config, factory_temp)

        # Create subtitle with brackets
        original_dir = tmp_path / "original"
        original_dir.mkdir()
        sub_with_brackets = original_dir / "[Test] file.ass"
        sub_with_brackets.write_text("test")

        prepared = factory._prepare_subtitle(sub_with_brackets)

        # Temp dir should have been created
        assert factory_temp.exists()
        assert factory_temp.is_dir()
        assert prepared.parent == factory_temp

    def test_softsub_stream_mapping(self, mock_config, mock_render_paths, tmp_path):
        """Softsub options have correct stream mapping."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_softsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.SOFTSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=True,
            preset='faster'
        )

        # Softsub keeps subtitle as stream
        assert options.streams.video_input_index == 0
        assert options.streams.audio_input_index == 1
        assert options.streams.subtitle_input_index == 2

    def test_hardsub_stream_mapping(self, mock_config, mock_render_paths, tmp_path):
        """Hardsub options have correct stream mapping (no subtitle stream)."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_hardsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.HARDSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=True,
            preset='faster'
        )

        # Hardsub burns subtitle, no stream
        assert options.streams.video_input_index == 0
        assert options.streams.audio_input_index == 1
        assert options.streams.subtitle_input_index is None
