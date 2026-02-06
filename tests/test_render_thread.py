"""Tests for threads/RenderThread.py - testing CURRENT codebase."""

from unittest.mock import MagicMock, patch

import pytest

from threads.RenderThread import ThreadClassRender


class MockProcess:
    """Mock subprocess.Popen process."""

    def __init__(self, stdout_lines: list[str]):
        self.stdout = iter(stdout_lines)


class TestRenderThread:
    """Test ThreadClassRender."""

    @pytest.fixture
    def render_thread(self, mock_config):
        """Create render thread with mock config."""
        # Disable sys.excepthook override in __init__
        with patch('sys.excepthook'):
            thread = ThreadClassRender(mock_config)
        return thread

    def test_ffmpeg_analysis_decoding_1080p(self, render_thread):
        """FFprobe output for 1080p is parsed correctly."""
        ffprobe_output = [
            "Input #0, matroska,webm, from 'test.mkv':\n",
            "  Duration: 00:24:02.05, start: 0.000000, bitrate: 5000 kb/s\n",
            "    Stream #0:0: Video: h264 (High), yuv420p(tv), 1920x1080, 23.98 fps\n",
        ]

        mock_proc = MockProcess(ffprobe_output)
        render_thread.ffmpeg_analysis_decoding(mock_proc)

        # Check duration parsing
        expected_duration = 24 * 60 + 2.05  # 1442.05 seconds
        assert abs(render_thread.config.total_duration_sec - expected_duration) < 0.1

        # Check frame count (duration * 24000/1001)
        expected_frames = expected_duration * 24000 / 1001.0
        assert abs(render_thread.config.total_frames - expected_frames) < 1

        # Check resolution
        assert render_thread.config.video_res == "1080p"

    def test_ffmpeg_analysis_decoding_720p(self, render_thread):
        """FFprobe output for 720p is parsed correctly."""
        ffprobe_output = [
            "Input #0, matroska,webm, from 'test.mkv':\n",
            "  Duration: 00:12:30.00, start: 0.000000, bitrate: 3000 kb/s\n",
            "    Stream #0:0: Video: h264 (Main), yuv420p(tv), 1280x720, 23.98 fps\n",
        ]

        mock_proc = MockProcess(ffprobe_output)
        render_thread.ffmpeg_analysis_decoding(mock_proc)

        assert render_thread.config.video_res == "720p"

    def test_ffmpeg_analysis_decoding_pixel_formats(self, render_thread):
        """Different pixel formats are detected."""
        # Test yuv420p
        ffprobe_output = [
            "Duration: 00:01:00.00\n",
            "Stream #0:0: Video: h264 (High), yuv420p(tv), 1920x1080\n",
        ]
        mock_proc = MockProcess(ffprobe_output)
        render_thread.ffmpeg_analysis_decoding(mock_proc)
        assert render_thread.config.build_settings.softsub_settings.pixel_format == 'yuv420p'

        # Test yuv420p10le
        render_thread.config.build_settings.softsub_settings.pixel_format = 'yuv420p10le'
        render_thread.config.build_settings.hardsub_settings.pixel_format = 'yuv420p10le'
        ffprobe_output2 = [
            "Duration: 00:01:00.00\n",
            "Stream #0:0: Video: hevc (Main 10), yuv420p10le(tv), 1920x1080\n",
        ]
        mock_proc2 = MockProcess(ffprobe_output2)
        render_thread.ffmpeg_analysis_decoding(mock_proc2)
        assert render_thread.config.build_settings.softsub_settings.pixel_format == 'yuv420p'

    def test_ffmpeg_analysis_decoding_profiles(self, render_thread):
        """Video profiles are parsed and set correctly."""
        test_cases = [
            ("(Main)", "main", "main"),  # Fixed: hardsub should be 'main' for Main profile
            ("(Main 10)", "high10", "main10"),
            ("(High)", "high", "main10"),
            ("(High 10)", "high10", "main10"),
        ]

        for profile_str, expected_soft, expected_hard in test_cases:
            ffprobe_output = [
                "Duration: 00:01:00.00\n",
                f"Stream #0:0: Video: h264 {profile_str}, yuv420p, 1920x1080\n",
            ]
            mock_proc = MockProcess(ffprobe_output)

            # Reset nvenc state for test
            render_thread.config.build_settings.nvenc_state = 2  # No nvenc for softsub

            render_thread.ffmpeg_analysis_decoding(mock_proc)

            assert render_thread.config.build_settings.softsub_settings.video_profile == expected_soft
            assert render_thread.config.build_settings.hardsub_settings.video_profile == expected_hard

    def test_ffmpeg_analysis_decoding_potato_overrides(self, render_thread):
        """Potato mode forces yuv420p and main profile."""
        render_thread.config.potato_PC = True

        ffprobe_output = [
            "Duration: 00:01:00.00\n",
            "Stream #0:0: Video: hevc (Main 10), yuv420p10le, 1920x1080\n",
        ]
        mock_proc = MockProcess(ffprobe_output)
        render_thread.ffmpeg_analysis_decoding(mock_proc)

        assert render_thread.config.build_settings.softsub_settings.pixel_format == 'yuv420p'
        assert render_thread.config.build_settings.hardsub_settings.pixel_format == 'yuv420p'
        assert render_thread.config.build_settings.softsub_settings.video_profile == 'main'
        assert render_thread.config.build_settings.hardsub_settings.video_profile == 'main'

    def test_calculate_encoding_params_1080p(self, render_thread):
        """Encoding params for 1080p use CRF 18."""
        render_thread.config.total_duration_sec = 1442  # Set duration to avoid division by zero
        params = render_thread.calculate_encoding_params(2.0, "1080p")

        assert params['crf'] == '18'
        assert params['cq'] == '19'
        assert params['qmin'] == '17'
        assert params['qmax'] == '23'

    def test_calculate_encoding_params_720p(self, render_thread):
        """Encoding params for 720p use CRF 20."""
        render_thread.config.total_duration_sec = 1442  # Set duration
        params = render_thread.calculate_encoding_params(2.0, "720p")

        assert params['crf'] == '20'
        assert params['cq'] == '21'

    def test_calculate_encoding_params_potato(self, render_thread):
        """Potato mode halves bitrate and sets CRF 23."""
        render_thread.config.potato_PC = True
        render_thread.config.total_duration_sec = 1000  # Set duration

        params = render_thread.calculate_encoding_params(2.0, "1080p")

        # Check potato CRF
        assert params['crf'] == '23'
        assert params['cq'] == '21'

        # Check bitrate is halved (roughly)
        avg_bitrate = int(params['avg_bitrate'].rstrip('M'))
        assert avg_bitrate <= 3  # Should be less than or equal to 3M due to halving and capping

    def test_calculate_encoding_params_cap(self, render_thread):
        """Average bitrate is capped at 6M."""
        # Set very short duration to get high bitrate
        render_thread.config.total_duration_sec = 100

        params = render_thread.calculate_encoding_params(10.0, "1080p")

        avg_bitrate = int(params['avg_bitrate'].rstrip('M'))
        assert avg_bitrate == 6  # Capped at 6M

    def test_softsub_runs_for_state_0_and_1(self, render_thread, mock_config):
        """Softsub encoding runs for build_state 0 and 1."""
        mock_config.rendering_paths = {
            'raw': '/test/raw.mkv',
            'audio': '/test/audio.wav',
            'sub': None,
            'softsub': '/test/output.mkv',
            'hardsub': '/test/output.mp4'
        }

        with patch('subprocess.Popen') as mock_popen, \
             patch('os.chdir'):
            mock_proc = MagicMock()
            mock_proc.stdout = []
            mock_popen.return_value = mock_proc

            # Test state 0
            mock_config.build_settings.build_state = 0
            render_thread.softsub()
            assert mock_popen.called

            # Reset and test state 1
            mock_popen.reset_mock()
            mock_config.build_settings.build_state = 1
            render_thread.softsub()
            assert mock_popen.called

    def test_hardsub_runs_for_state_0_and_2(self, render_thread, mock_config):
        """Hardsub encoding runs for build_state 0 and 2."""
        mock_config.rendering_paths = {
            'raw': '/test/raw.mkv',
            'audio': '/test/audio.wav',
            'sub': None,
            'softsub': '/test/output.mkv',
            'hardsub': '/test/output.mp4'
        }

        with patch('subprocess.Popen') as mock_popen, \
             patch('os.chdir'):
            mock_proc = MagicMock()
            mock_proc.stdout = []
            mock_popen.return_value = mock_proc

            # Test state 0
            mock_config.build_settings.build_state = 0
            render_thread.hardsub()
            assert mock_popen.called

            # Reset and test state 2
            mock_popen.reset_mock()
            mock_config.build_settings.build_state = 2
            render_thread.hardsub()
            assert mock_popen.called

    def test_hardsubbering_runs_for_state_3(self, render_thread, mock_config):
        """Hardsubbering (for hardsubbers) runs only for state 3."""
        mock_config.rendering_paths = {
            'raw': '/test/raw.mkv',
            'audio': None,
            'sub': '/test/sub.ass',
            'softsub': None,
            'hardsub': '/test/output.mp4'
        }

        with patch('subprocess.Popen') as mock_popen, \
             patch('os.chdir'):
            mock_proc = MagicMock()
            mock_proc.stdout = []
            mock_popen.return_value = mock_proc

            # Test state 3
            mock_config.build_settings.build_state = 3
            render_thread.hardsubbering()
            assert mock_popen.called

            # Test state 2 (should not run)
            mock_popen.reset_mock()
            mock_config.build_settings.build_state = 2
            render_thread.hardsubbering()
            assert not mock_popen.called

    def test_raw_repairing_runs_for_state_4(self, render_thread, mock_config):
        """Raw repairing runs only for state 4."""
        mock_config.rendering_paths = {
            'raw': '/test/raw.mkv',
            'softsub': '/test/output.mkv',
        }

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_proc.stdout = []
            mock_popen.return_value = mock_proc

            # Test state 4
            mock_config.build_settings.build_state = 4
            render_thread.raw_repairing()
            assert mock_popen.called

            # Test state 0 (should not run)
            mock_popen.reset_mock()
            mock_config.build_settings.build_state = 0
            render_thread.raw_repairing()
            assert not mock_popen.called

    def test_frame_update_parses_progress(self, render_thread, mock_config):
        """frame_update parses frame and fps from ffmpeg output."""
        mock_config.total_frames = 1000

        ffmpeg_output = [
            "frame=  100 fps= 25 q=-1.0 size=    1024kB time=00:00:04.00 bitrate=2097.2kbits/s speed=1.0x\n",
            "frame=  200 fps= 26 q=-1.0 size=    2048kB time=00:00:08.00 bitrate=2097.2kbits/s speed=1.04x\n",
        ]

        mock_proc = MockProcess(ffmpeg_output)

        with patch.object(render_thread, 'frame_upd') as mock_frame_signal, \
             patch.object(render_thread, 'elapsed_time_upd') as mock_time_signal:
            render_thread.frame_update(mock_proc)

            # Check signals were emitted
            assert mock_frame_signal.emit.call_count == 2
            assert mock_time_signal.emit.call_count == 2

            # Check first frame emission
            first_call = mock_frame_signal.emit.call_args_list[0]
            assert first_call[0][0] == '100'
