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
