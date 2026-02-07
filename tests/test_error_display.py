"""Tests for error display functionality in MainWindow."""

from unittest.mock import Mock, patch
import pytest

from models.enums import ErrorSeverity
from windows.mainWindow import MainWindow


class TestDisplayError:
    """Test display_error method."""

    def test_display_error_sets_label_text(self, qapp, mock_config):
        """display_error sets app_state_label text."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        window.display_error("Test error message", ErrorSeverity.ERROR)

        window.ui.app_state_label.setText.assert_called_once_with("Test error message")

    def test_display_error_sets_error_property(self, qapp, mock_config):
        """display_error sets errorLevel property for ERROR severity."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        window.display_error("Test error", ErrorSeverity.ERROR)

        window.ui.app_state_label.setProperty.assert_called_with("errorLevel", "error")

    def test_display_error_sets_warning_property(self, qapp, mock_config):
        """display_error sets errorLevel property for WARNING severity."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        window.display_error("Test warning", ErrorSeverity.WARNING)

        window.ui.app_state_label.setProperty.assert_called_with("errorLevel", "warning")

    def test_display_error_sets_info_property(self, qapp, mock_config):
        """display_error sets errorLevel property for INFO severity."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        window.display_error("Test info", ErrorSeverity.INFO)

        window.ui.app_state_label.setProperty.assert_called_with("errorLevel", "info")

    def test_display_error_refreshes_styling(self, qapp, mock_config):
        """display_error calls unpolish/polish to refresh widget styling."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()
        mock_style = Mock()
        window.ui.app_state_label.style.return_value = mock_style

        window.display_error("Test", ErrorSeverity.ERROR)

        mock_style.unpolish.assert_called_once()
        mock_style.polish.assert_called_once()


class TestCodingErrorRefactored:
    """Test coding_error uses display_error instead of MessageBox."""

    def test_coding_error_no_messagebox(self, qapp, mock_config):
        """coding_error does NOT create QMessageBox."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        with patch('windows.mainWindow.QMessageBox') as mock_msgbox:
            # Mock exec_ to prevent blocking
            mock_instance = Mock()
            mock_msgbox.return_value = mock_instance
            mock_instance.exec_.return_value = 0

            window.coding_error('softsub')

            # QMessageBox should NOT be instantiated
            mock_msgbox.assert_not_called()

    def test_coding_error_calls_display_error(self, qapp, mock_config):
        """coding_error calls display_error with error message."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        with patch('windows.mainWindow.QMessageBox') as mock_msgbox:
            # Mock exec_ to prevent blocking (for current implementation)
            mock_instance = Mock()
            mock_msgbox.return_value = mock_instance
            mock_instance.exec_.return_value = 0

            window.coding_error('softsub')

            # After refactor: should call display_error with softsub error message
            window.display_error.assert_called_once()
            args = window.display_error.call_args[0]
            assert "Софтсабы" in args[0]  # Error message contains "Софтсабы"
            assert args[1] == ErrorSeverity.ERROR

    def test_coding_error_all_types_work(self, qapp, mock_config):
        """coding_error handles all 10 error types."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        error_types = ['softsub', 'hardsub', 'name', 'raw', 'audio',
                       'subtitle', 'logo', 'logs_folder', 'stop', 'hardsub_folder']

        with patch('windows.mainWindow.QMessageBox') as mock_msgbox:
            # Mock exec_ to prevent blocking (for current implementation)
            mock_instance = Mock()
            mock_msgbox.return_value = mock_instance
            mock_instance.exec_.return_value = 0

            for error_type in error_types:
                window.display_error.reset_mock()
                window.coding_error(error_type)
                window.display_error.assert_called_once()


class TestValidateBeforeRender:
    """Test _validate_before_render uses display_error."""

    def test_validate_no_messagebox_on_error(self, qapp, mock_config, tmp_path):
        """_validate_before_render does NOT show QMessageBox on validation failure."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Invalid path
        window._ui_paths['raw'] = str(tmp_path / "nonexistent.mkv")

        with patch('PyQt5.QtWidgets.QMessageBox.critical') as mock_critical:
            result = window._validate_before_render()

            # Should NOT call QMessageBox.critical
            mock_critical.assert_not_called()

    def test_validate_calls_display_error_on_failure(self, qapp, mock_config, tmp_path):
        """_validate_before_render calls display_error on validation failure."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Invalid path
        window._ui_paths['raw'] = str(tmp_path / "nonexistent.mkv")

        result = window._validate_before_render()

        # Should call display_error with ERROR severity
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "not found" in args[0].lower() or "не найден" in args[0].lower()
        assert args[1] == ErrorSeverity.ERROR
        assert result is False


class TestJobFailedHandler:
    """Test on_job_failed shows errors to user."""

    def test_on_job_failed_shows_error(self, qapp, mock_config):
        """on_job_failed calls display_error with job details."""
        window = MainWindow(mock_config)
        window.display_error = Mock()
        window.refresh_queue_display = Mock()

        # Simulate job failure
        job_id = "test-job-123"
        error_message = "FFmpeg encoding failed"

        window.on_job_failed(job_id, error_message)

        # Should call display_error with ERROR severity
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "Ошибка обработки" in args[0]
        assert error_message in args[0]
        assert args[1] == ErrorSeverity.ERROR

    def test_on_job_failed_refreshes_display(self, qapp, mock_config):
        """on_job_failed refreshes queue display."""
        window = MainWindow(mock_config)
        window.display_error = Mock()
        window.refresh_queue_display = Mock()

        window.on_job_failed("job-123", "Error message")

        # Should refresh queue display
        window.refresh_queue_display.assert_called_once()


class TestDisplayErrorDefaults:
    """Test display_error default parameters and edge cases."""

    def test_display_error_defaults_to_info_severity(self, qapp, mock_config):
        """display_error uses INFO severity by default."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        # Call without severity parameter
        window.display_error("Test message")

        # Should use INFO severity (default)
        window.ui.app_state_label.setProperty.assert_called_with("errorLevel", "info")

    def test_display_error_handles_empty_message(self, qapp, mock_config):
        """display_error handles empty message string."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        window.display_error("", ErrorSeverity.ERROR)

        # Should still set text even if empty
        window.ui.app_state_label.setText.assert_called_once_with("")
        window.ui.app_state_label.setProperty.assert_called_with("errorLevel", "error")

    def test_display_error_handles_multiline_message(self, qapp, mock_config):
        """display_error handles multiline error messages."""
        window = MainWindow(mock_config)
        window.ui.app_state_label = Mock()

        multiline_message = "Error on line 1\nError on line 2\nError on line 3"
        window.display_error(multiline_message, ErrorSeverity.ERROR)

        window.ui.app_state_label.setText.assert_called_once_with(multiline_message)


class TestCodingErrorSpecificTypes:
    """Test coding_error behavior for specific error types."""

    def test_coding_error_stop_uses_warning_severity(self, qapp, mock_config):
        """coding_error uses WARNING severity for 'stop' error type."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        window.coding_error('stop')

        # 'stop' should use WARNING, not ERROR
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert args[1] == ErrorSeverity.WARNING
        assert "Рендер окончен" in args[0]

    def test_coding_error_hardsub_folder_creates_directory(self, qapp, mock_config, tmp_path):
        """coding_error creates directory for 'hardsub_folder' error type."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Set hardsub path to non-existent directory
        hardsub_path = tmp_path / "test_hardsub"
        window.config.main_paths.hardsub = hardsub_path

        assert not hardsub_path.exists()

        window.coding_error('hardsub_folder')

        # Directory should be created
        assert hardsub_path.exists()

        # Should show INFO message, not ERROR
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert args[1] == ErrorSeverity.INFO
        assert "создана" in args[0].lower()

    def test_coding_error_unknown_type_shows_error(self, qapp, mock_config):
        """coding_error handles unknown error types gracefully."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        window.coding_error('unknown_error_type')

        # Should call display_error with unknown type message
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "Unknown error type" in args[0]
        assert args[1] == ErrorSeverity.ERROR


class TestValidateBeforeRenderEdgeCases:
    """Test _validate_before_render edge cases and multiple validation failures."""

    def test_validate_passes_with_valid_raw_path(self, qapp, mock_config, tmp_path):
        """_validate_before_render passes with valid raw path."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Create valid file
        raw_path = tmp_path / "valid.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window.config.build_settings.episode_name = "Valid_Episode_01"

        result = window._validate_before_render()

        # Should pass validation
        assert result is True
        window.display_error.assert_not_called()

    def test_validate_fails_with_invalid_audio_path(self, qapp, mock_config, tmp_path):
        """_validate_before_render fails with invalid audio path."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Valid raw, invalid audio
        raw_path = tmp_path / "raw.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = str(tmp_path / "nonexistent_audio.mka")
        window.config.build_settings.episode_name = "Test_Episode"

        result = window._validate_before_render()

        # Should fail on audio validation
        assert result is False
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "audio" in args[0].lower() or "аудио" in args[0].lower()

    def test_validate_fails_with_invalid_subtitle_path(self, qapp, mock_config, tmp_path):
        """_validate_before_render fails with invalid subtitle path."""
        window = MainWindow(mock_config)
        window.display_error = Mock()

        # Valid raw, invalid subtitle
        raw_path = tmp_path / "raw.mkv"
        raw_path.touch()

        window._ui_paths['raw'] = str(raw_path)
        window._ui_paths['audio'] = ''
        window._ui_paths['sub'] = str(tmp_path / "nonexistent_sub.ass")
        window.config.build_settings.episode_name = "Test_Episode"

        result = window._validate_before_render()

        # Should fail on subtitle validation
        assert result is False
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "subtitle" in args[0].lower() or "субтитр" in args[0].lower()


class TestJobFailedHandlerWithQueue:
    """Test on_job_failed with actual job queue integration."""

    def test_on_job_failed_with_valid_job_id(self, qapp, mock_config, mock_render_paths):
        """on_job_failed retrieves episode name from actual job in queue."""
        from models.job import RenderJob
        from models.enums import BuildState, NvencState, LogoState
        from models.encoding import EncodingParams
        from models.job import VideoPresets

        window = MainWindow(mock_config)
        window.display_error = Mock()
        window.refresh_queue_display = Mock()

        # Create and add a real job to the queue
        encoding_params = EncodingParams(
            avg_bitrate="6M", max_bitrate="9M", buffer_size="18M",
            crf=18, cq=19, qmin=17, qmax=23
        )

        job = RenderJob(
            paths=mock_render_paths,
            episode_name="Test_Episode_42",
            build_state=BuildState.HARD_ONLY,
            nvenc_state=NvencState.NVENC_BOTH,
            logo_state=LogoState.LOGO_BOTH,
            encoding_params=encoding_params,
            video_settings=VideoPresets.SOFTSUB,
            potato_mode=False
        )

        job_id = window.job_queue.add(job)

        # Simulate job failure
        window.on_job_failed(job_id, "FFmpeg crashed unexpectedly")

        # Should show error with actual episode name
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "Test_Episode_42" in args[0]
        assert "FFmpeg crashed unexpectedly" in args[0]
        assert args[1] == ErrorSeverity.ERROR

    def test_on_job_failed_with_invalid_job_id(self, qapp, mock_config):
        """on_job_failed handles invalid job ID gracefully."""
        window = MainWindow(mock_config)
        window.display_error = Mock()
        window.refresh_queue_display = Mock()

        # Use non-existent job ID
        window.on_job_failed("non-existent-job-id", "Some error")

        # Should still display error with "Unknown" episode name
        window.display_error.assert_called_once()
        args = window.display_error.call_args[0]
        assert "Unknown" in args[0]
        assert "Some error" in args[0]
