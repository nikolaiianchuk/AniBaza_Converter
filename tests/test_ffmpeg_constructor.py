"""Tests for modules/FFmpegConstructor.py - testing CURRENT codebase."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from modules.FFmpegConstructor import FFmpegConstructor


class TestFFmpegConstructor:
    """Test FFmpegConstructor command building."""

    @pytest.fixture
    def constructor(self, mock_config):
        """Create FFmpegConstructor with mock config."""
        return FFmpegConstructor(mock_config)

    @pytest.fixture
    def test_files(self, tmp_path):
        """Create test video/audio/sub files."""
        raw = tmp_path / "test.mkv"
        audio = tmp_path / "test.wav"
        sub = tmp_path / "test.ass"
        output = tmp_path / "output.mkv"
        logo = tmp_path / "logo.ass"

        # Create dummy files
        for file in [raw, audio, sub, logo]:
            file.write_text("")

        # Update logo path in config
        return {
            'raw': str(raw),
            'audio': str(audio),
            'sub': str(sub),
            'output': str(output),
            'logo': str(logo)
        }

    def test_build_soft_command_basic(self, constructor, test_files, mock_config):
        """Softsub command contains expected components."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_soft_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=test_files['sub'],
                output_path=test_files['output'],
                nvenc=False,
                include_logo=True
            )

        assert 'ffmpeg' in cmd
        assert '-y' in cmd
        assert '-i' in cmd
        assert test_files['raw'] in cmd
        assert test_files['audio'] in cmd
        assert 'libx264' in cmd
        assert test_files['output'] in cmd

    def test_build_soft_command_nvenc(self, constructor, test_files, mock_config):
        """Softsub with nvenc uses h264_nvenc codec."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_soft_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=None,
                output_path=test_files['output'],
                nvenc=True
            )

        assert 'h264_nvenc' in cmd
        assert 'libx264' not in cmd

    def test_build_soft_command_no_logo(self, constructor, test_files, mock_config):
        """Softsub without logo omits subtitle filter."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_soft_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=None,
                output_path=test_files['output'],
                nvenc=False,
                include_logo=False
            )

        assert 'subtitles=' not in cmd or 'subtitles' not in cmd.lower()

    def test_build_soft_command_no_sub(self, constructor, test_files, mock_config):
        """Softsub without subtitle omits subtitle input/map."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_soft_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=None,
                output_path=test_files['output'],
                nvenc=False
            )

        # Count -i flags (should be 2: video and audio only)
        i_count = cmd.count('-i')
        assert i_count == 2

    def test_build_soft_command_potato(self, constructor, test_files, mock_config):
        """Potato mode omits -tune flag."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_soft_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=None,
                output_path=test_files['output'],
                nvenc=False,
                potato_mode=True
            )

        # In potato mode, tune should not be present
        assert '-tune' not in cmd

    def test_build_hard_command_2burning(self, constructor, test_files, mock_config):
        """Hardsub with logo AND sub uses 2burning filter."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_hard_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=test_files['sub'],
                output_path=test_files['output'],
                nvenc=False,
                include_logo=True
            )

        # Should have two subtitles filters
        assert cmd.count('subtitles=') == 2

    def test_build_hard_command_1burning_logo(self, constructor, test_files, mock_config):
        """Hardsub with logo only uses 1burning."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_hard_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=None,
                output_path=test_files['output'],
                nvenc=False,
                include_logo=True
            )

        assert cmd.count('subtitles=') == 1

    def test_build_hard_command_1burning_sub(self, constructor, test_files, mock_config):
        """Hardsub with sub only uses 1burning."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_hard_command(
                raw_path=test_files['raw'],
                sound_path=test_files['audio'],
                sub_path=test_files['sub'],
                output_path=test_files['output'],
                nvenc=False,
                include_logo=False
            )

        assert cmd.count('subtitles=') == 1

    def test_build_hard_command_no_audio(self, constructor, test_files, mock_config):
        """Hardsub without audio omits audio inputs."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        with patch('os.chdir'):
            cmd = constructor.build_hard_command(
                raw_path=test_files['raw'],
                sound_path='',
                sub_path=test_files['sub'],
                output_path=test_files['output'],
                nvenc=False,
                include_logo=False
            )

        # Should only have one -i (for video)
        assert cmd.count('-i') == 1
        # Should not have audio codec
        assert '-c:a' not in cmd

    def test_sub_escaper(self, constructor, test_files, mock_config, tmp_path):
        """sub_escaper copies file and escapes path."""
        mock_config.main_paths.temp = tmp_path / "tmp"
        mock_config.main_paths.temp.mkdir(exist_ok=True)

        # Create a subtitle file with brackets
        sub_with_brackets = tmp_path / "[Test] subtitle.ass"
        sub_with_brackets.write_text("test content")

        constructor.sub_escaper(str(sub_with_brackets))

        # Check that sub dict is populated
        assert constructor.sub['exists'] is True
        assert constructor.sub['name'] == "[Test] subtitle.ass"
        assert constructor.sub['sanitized_name'] == "Test subtitle.ass"
        assert constructor.sub['temp_path'] != ''
        assert constructor.sub['escaped_path'] != ''

        # Check temp file was created
        temp_file = Path(constructor.sub['temp_path'])
        assert temp_file.exists()
        assert temp_file.read_text() == "test content"

    def test_logo_escaper(self, constructor, mock_config, tmp_path):
        """logo_escaper converts backslashes and escapes colons."""
        logo_path = tmp_path / "logo.ass"
        mock_config.main_paths.logo = logo_path

        constructor.logo_escaper()

        # On non-Windows, should not have backslashes
        assert '\\\\' not in constructor.escaped_logo_path or sys.platform == 'win32'

    def test_remove_temp_sub(self, constructor, test_files, mock_config, tmp_path):
        """remove_temp_sub deletes temp file and resets dict."""
        mock_config.main_paths.temp = tmp_path / "tmp"
        mock_config.main_paths.temp.mkdir(exist_ok=True)

        sub_file = tmp_path / "test.ass"
        sub_file.write_text("test")

        # Setup sub
        constructor.sub_escaper(str(sub_file))
        temp_path = constructor.sub['temp_path']

        assert Path(temp_path).exists()

        # Remove
        constructor.remove_temp_sub()

        assert not Path(temp_path).exists()
        assert constructor.sub['exists'] is False
        assert constructor.sub['name'] == ''
        assert constructor.sub['temp_path'] == ''


class TestFFmpegConstructorArgs:
    """Test new arg-building methods (no shell=True needed)."""

    @pytest.fixture
    def constructor(self, mock_config):
        """Create FFmpegConstructor with mock config."""
        return FFmpegConstructor(mock_config)

    @pytest.fixture
    def test_files(self, tmp_path):
        """Create test video/audio/sub files."""
        raw = tmp_path / "test.mkv"
        audio = tmp_path / "test.wav"
        sub = tmp_path / "test.ass"
        output = tmp_path / "output.mkv"
        logo = tmp_path / "logo.ass"

        for file in [raw, audio, sub, logo]:
            file.write_text("")

        return {
            'raw': str(raw),
            'audio': str(audio),
            'sub': str(sub),
            'output': str(output),
            'logo': str(logo)
        }

    def test_build_soft_args_returns_list(self, constructor, test_files, mock_config):
        """build_soft_args returns a list, not a string."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        args = constructor.build_soft_args(
            raw_path=test_files['raw'],
            sound_path=test_files['audio'],
            sub_path=None,
            output_path=test_files['output'],
            max_bitrate='9M',
            max_buffer='18M'
        )

        assert isinstance(args, list)
        assert all(isinstance(arg, str) for arg in args)

    def test_build_soft_args_no_shell_needed(self, constructor, test_files, mock_config):
        """Args can be passed directly to Popen (no shell=True)."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        args = constructor.build_soft_args(
            raw_path=test_files['raw'],
            sound_path=test_files['audio'],
            output_path=test_files['output'],
            max_bitrate='9M',
            max_buffer='18M'
        )

        # Should contain -y flag
        assert '-y' in args
        # Should contain input files
        assert '-i' in args
        assert test_files['raw'] in args
        assert test_files['audio'] in args
        # Should contain output
        assert test_files['output'] in args

    def test_build_soft_args_with_nvenc(self, constructor, test_files, mock_config):
        """build_soft_args uses correct codec for nvenc."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        args = constructor.build_soft_args(
            raw_path=test_files['raw'],
            sound_path=test_files['audio'],
            output_path=test_files['output'],
            nvenc=True,
            cq='19',
            cqmin='17',
            cqmax='23',
            max_bitrate='9M',
            max_buffer='18M'
        )

        # Should use h264_nvenc codec
        assert 'h264_nvenc' in args
        # Should use CQ instead of CRF
        assert '-cq' in args

    def test_build_hard_args_returns_list(self, constructor, test_files, mock_config):
        """build_hard_args returns a list."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        args = constructor.build_hard_args(
            raw_path=test_files['raw'],
            sound_path=test_files['audio'],
            sub_path=test_files['sub'],
            output_path=test_files['output'],
            max_bitrate='9M',
            max_buffer='18M'
        )

        assert isinstance(args, list)
        assert '-y' in args
        assert test_files['output'] in args

    def test_build_hard_args_uses_hevc(self, constructor, test_files, mock_config):
        """build_hard_args uses hevc codec."""
        mock_config.main_paths.logo = Path(test_files['logo'])

        args = constructor.build_hard_args(
            raw_path=test_files['raw'],
            sound_path=test_files['audio'],
            output_path=test_files['output'],
            nvenc=False,
            max_bitrate='9M',
            max_buffer='18M'
        )

        # Should use hevc codec (not h264)
        assert 'hevc' in args
        assert 'h264' not in ' '.join(args)
