"""Integration tests for queue functionality with MainWindow."""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from models.enums import BuildState, JobStatus, LogoState, NvencState
from models.job import VideoPresets


class TestAddToQueueIntegration:
    """Test on_add_to_queue_clicked integration with UI and queue."""

    def test_add_to_queue_validates_and_creates_job(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked validates inputs, creates RenderJob, adds to queue."""
        from windows.mainWindow import MainWindow

        window = MainWindow(mock_config)

        # Set up valid paths in UI
        raw_path = tmp_path / "raw.mkv"
        audio_path = tmp_path / "audio.mka"
        sub_path = tmp_path / "sub.ass"

        # Create files so validation passes
        raw_path.touch()
        audio_path.touch()
        sub_path.touch()

        # Set paths in UI
        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = str(audio_path)
        window._ui_paths['sub'] = str(sub_path)

        # Set episode name
        window.config.build_settings.episode_name = "Episode_01"

        # Set build settings
        window.config.build_settings.build_state = BuildState.SOFT_AND_HARD
        window.config.build_settings.nvenc_state = NvencState.NVENC_BOTH
        window.config.build_settings.logo_state = LogoState.LOGO_BOTH

        # Ensure queue is empty
        assert len(window.job_queue.get_all_jobs()) == 0

        # Call add to queue
        window.on_add_to_queue_clicked()

        # Job should be added to queue
        jobs = window.job_queue.get_all_jobs()
        assert len(jobs) == 1

        # Verify job properties
        queued_job = jobs[0]
        assert queued_job.status == JobStatus.WAITING
        assert queued_job.job.episode_name == "Episode_01"
        assert queued_job.job.build_state == BuildState.SOFT_AND_HARD
        assert queued_job.job.nvenc_state == NvencState.NVENC_BOTH
        assert queued_job.job.logo_state == LogoState.LOGO_BOTH
        assert queued_job.job.paths.raw == raw_path
        assert queued_job.job.paths.audio == audio_path
        assert queued_job.job.paths.sub == sub_path
        assert queued_job.job.potato_mode == mock_config.potato_PC

        # Verify video settings (compare by attributes since VideoSettings may not be frozen)
        assert queued_job.job.video_settings.video_tune == VideoPresets.SOFTSUB.video_tune
        assert queued_job.job.video_settings.video_profile == VideoPresets.SOFTSUB.video_profile
        assert queued_job.job.video_settings.profile_level == VideoPresets.SOFTSUB.profile_level
        assert queued_job.job.video_settings.pixel_format == VideoPresets.SOFTSUB.pixel_format

    def test_add_to_queue_clears_ui_after_success(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked clears UI fields after successful add."""
        from windows.mainWindow import MainWindow

        window = MainWindow(mock_config)

        # Set up valid paths
        raw_path = tmp_path / "raw.mkv"
        audio_path = tmp_path / "audio.mka"
        sub_path = tmp_path / "sub.ass"

        raw_path.touch()
        audio_path.touch()
        sub_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = str(audio_path)
        window._ui_paths['sub'] = str(sub_path)
        window.config.build_settings.episode_name = "Episode_01"

        # Mock UI elements
        window.ui.raw_path_editline = MagicMock()
        window.ui.audio_path_editline = MagicMock()
        window.ui.subtitle_path_editline = MagicMock()

        # Call add to queue
        window.on_add_to_queue_clicked()

        # UI should be cleared
        window.ui.raw_path_editline.clear.assert_called_once()
        window.ui.audio_path_editline.clear.assert_called_once()
        window.ui.subtitle_path_editline.clear.assert_called_once()

        # Internal paths should be cleared
        assert window._ui_paths['raw'] == ''
        assert window._ui_paths['audio'] == ''
        assert window._ui_paths['sub'] == ''


class TestAddToQueueValidation:
    """Test validation in on_add_to_queue_clicked."""

    def test_add_to_queue_fails_with_missing_raw_path(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked shows error when raw path is missing."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Set invalid path (file doesn't exist)
        window._ui_paths['raw'] = str(tmp_path / "nonexistent.mkv")
        window._ui_paths['audio'] = ''
        window._ui_paths['sub'] = ''
        window.config.build_settings.episode_name = "Episode_01"

        # Call add to queue
        window.on_add_to_queue_clicked()

        # Should show error via display_error
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        error_message = args[0]
        assert "Raw video not found" in error_message or "не найден" in error_message.lower()

        # Job should NOT be added
        assert len(window.job_queue.get_all_jobs()) == 0

    def test_add_to_queue_fails_with_invalid_episode_name(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked shows error when episode name is invalid."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Set up valid paths
        raw_path = tmp_path / "raw.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = ''
        window._ui_paths['sub'] = ''

        # Invalid episode name (contains invalid characters)
        window.config.build_settings.episode_name = "Episode/01"

        # Mock display_error to verify error is shown (coding_error now uses display_error)
        window.display_error = Mock()

        window.on_add_to_queue_clicked()

        # Should show error message via display_error
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "Некорректное имя серии" in args[0]  # Error message about invalid name

        # Job should NOT be added
        assert len(window.job_queue.get_all_jobs()) == 0

    def test_add_to_queue_with_optional_paths(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked works with only raw path (no audio/sub)."""
        from windows.mainWindow import MainWindow

        window = MainWindow(mock_config)

        # Only raw path, no audio/sub
        raw_path = tmp_path / "raw.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = ''
        window._ui_paths['sub'] = ''
        window.config.build_settings.episode_name = "Episode_01"
        window.config.build_settings.build_state = BuildState.HARD_ONLY

        # Mock UI elements
        window.ui.raw_path_editline = MagicMock()
        window.ui.audio_path_editline = MagicMock()
        window.ui.subtitle_path_editline = MagicMock()

        # Call add to queue
        window.on_add_to_queue_clicked()

        # Job should be added
        jobs = window.job_queue.get_all_jobs()
        assert len(jobs) == 1

        # Verify optional paths are None
        queued_job = jobs[0]
        assert queued_job.job.paths.raw == raw_path
        assert queued_job.job.paths.audio is None
        assert queued_job.job.paths.sub is None

    def test_add_to_queue_refreshes_display(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_clicked refreshes queue widget display."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Mock refresh_queue_display
        window.refresh_queue_display = Mock()

        # Set up valid paths
        raw_path = tmp_path / "raw.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = ''
        window._ui_paths['sub'] = ''
        window.config.build_settings.episode_name = "Episode_01"

        # Mock UI elements
        window.ui.raw_path_editline = MagicMock()
        window.ui.audio_path_editline = MagicMock()
        window.ui.subtitle_path_editline = MagicMock()

        # Call add to queue
        window.on_add_to_queue_clicked()

        # Should refresh display
        window.refresh_queue_display.assert_called_once()


class TestStartButtonSmartBehavior:
    """Test start button smart behavior - queue processing vs immediate render."""

    def test_start_button_starts_queue_when_jobs_exist(self, qapp, mock_config, tmp_path):
        """on_start_button_clicked starts queue processor when jobs are waiting."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Add jobs to queue
        from models.job import RenderJob
        from models.render_paths import RenderPaths
        from models.enums import BuildState, NvencState, LogoState
        from models.encoding import EncodingParams

        raw_path = tmp_path / "raw.mkv"
        softsub_dir = tmp_path / 'softsub'
        hardsub_dir = tmp_path / 'hardsub'
        raw_path.touch()
        softsub_dir.mkdir(exist_ok=True)
        hardsub_dir.mkdir(exist_ok=True)

        paths = RenderPaths.from_ui_state(
            raw_path=str(raw_path),
            audio_path='',
            sub_path='',
            episode_name='Episode_01',
            softsub_dir=softsub_dir,
            hardsub_dir=hardsub_dir,
        )

        encoding_params = EncodingParams(
            avg_bitrate="6M",
            max_bitrate="9M",
            buffer_size="18M",
            crf=18,
            cq=19,
            qmin=17,
            qmax=23
        )

        job = RenderJob(
            paths=paths,
            episode_name='Episode_01',
            build_state=BuildState.HARD_ONLY,
            nvenc_state=NvencState.NVENC_BOTH,
            logo_state=LogoState.LOGO_BOTH,
            encoding_params=encoding_params,
            video_settings=mock_config.build_settings.softsub_settings,
            potato_mode=False
        )

        window.job_queue.add(job)

        # Mock queue processor start and isRunning
        window.queue_processor.start = Mock()
        window.queue_processor.isRunning = Mock(return_value=False)

        # Call on_add_to_queue_and_start (new unified button)
        window.on_add_to_queue_and_start()

        # Queue processor should be started
        window.queue_processor.start.assert_called_once()

    def test_start_button_does_nothing_when_no_jobs(self, qapp, mock_config, tmp_path):
        """on_add_to_queue_and_start does nothing when queue is empty and UI is empty."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Ensure queue is empty
        assert len(window.job_queue.get_all_jobs()) == 0

        # Mock on_add_to_queue_clicked to fail (simulating invalid UI state)
        window.on_add_to_queue_clicked = Mock(return_value=False)

        # Mock queue processor start
        window.queue_processor.start = Mock()
        window.queue_processor.isRunning = Mock(return_value=False)

        # Call on_add_to_queue_and_start with empty UI
        window.on_add_to_queue_and_start()

        # Queue processor should NOT be started (no jobs to process)
        window.queue_processor.start.assert_not_called()


class TestStopButtonBehavior:
    """Test stop button behavior - cancel queue vs kill immediate render."""

    def test_stop_button_cancels_queue_when_running(self, qapp, mock_config, tmp_path):
        """Stop button should cancel queue processor when running."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Add job to queue
        from models.job import RenderJob
        from models.render_paths import RenderPaths
        from models.enums import BuildState, NvencState, LogoState
        from models.encoding import EncodingParams

        raw_path = tmp_path / "raw.mkv"
        softsub_dir = tmp_path / 'softsub'
        hardsub_dir = tmp_path / 'hardsub'
        raw_path.touch()
        softsub_dir.mkdir(exist_ok=True)
        hardsub_dir.mkdir(exist_ok=True)

        paths = RenderPaths.from_ui_state(
            raw_path=str(raw_path),
            audio_path='',
            sub_path='',
            episode_name='Episode_01',
            softsub_dir=softsub_dir,
            hardsub_dir=hardsub_dir,
        )

        encoding_params = EncodingParams(
            avg_bitrate="6M",
            max_bitrate="9M",
            buffer_size="18M",
            crf=18,
            cq=19,
            qmin=17,
            qmax=23
        )

        job = RenderJob(
            paths=paths,
            episode_name='Episode_01',
            build_state=BuildState.HARD_ONLY,
            nvenc_state=NvencState.NVENC_BOTH,
            logo_state=LogoState.LOGO_BOTH,
            encoding_params=encoding_params,
            video_settings=mock_config.build_settings.softsub_settings,
            potato_mode=False
        )

        window.job_queue.add(job)

        # Mock queue processor methods
        window.queue_processor.isRunning = Mock(return_value=True)
        window.queue_processor.cancel_current_job = Mock()
        window.queue_processor.wait = Mock()

        # Call stop button handler
        window.on_stop_button_clicked()

        # Should cancel current job and wait for thread to finish
        window.queue_processor.cancel_current_job.assert_called_once()
        window.queue_processor.wait.assert_called_once()

    def test_stop_button_kills_immediate_render_when_queue_not_running(self, qapp, mock_config):
        """Stop button should call proc_kill when queue processor not running."""
        from windows.mainWindow import MainWindow
        from unittest.mock import Mock

        window = MainWindow(mock_config)

        # Mock queue processor as not running
        window.queue_processor.isRunning = Mock(return_value=False)

        # Mock proc_kill
        window.proc_kill = Mock()

        # Call stop button handler
        window.on_stop_button_clicked()

        # Should call proc_kill for immediate render
        window.proc_kill.assert_called_once()
