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
