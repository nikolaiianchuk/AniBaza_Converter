"""Tests for stylesheet loading in MainWindow."""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from windows.mainWindow import MainWindow


class TestStylesheetLoading:
    """Test stylesheet loading functionality."""

    def test_stylesheet_file_exists(self):
        """resources/styles.qss file exists."""
        qss_path = Path("resources/styles.qss")
        assert qss_path.exists(), "Stylesheet file not found"

    def test_load_stylesheet_method_exists(self, qapp, mock_config):
        """MainWindow has _load_stylesheet method."""
        window = MainWindow(mock_config)
        assert hasattr(window, '_load_stylesheet')

    def test_load_stylesheet_reads_file(self, qapp, mock_config, tmp_path):
        """_load_stylesheet reads and applies stylesheet content."""
        window = MainWindow(mock_config)

        # Create temporary stylesheet
        test_qss = tmp_path / "resources" / "styles.qss"
        test_qss.parent.mkdir(parents=True)
        test_qss.write_text("QLabel { color: red; }")

        # Mock config path
        window.config.main_paths.cwd = tmp_path

        # Mock setStyleSheet to capture content
        window.setStyleSheet = Mock()

        # Load stylesheet from test path
        window._load_stylesheet()

        # Should read and apply stylesheet
        window.setStyleSheet.assert_called_once()
        applied_content = window.setStyleSheet.call_args[0][0]
        assert "QLabel" in applied_content
        assert "color: red" in applied_content

    def test_stylesheet_applied_to_window(self, qapp, mock_config):
        """MainWindow has non-empty stylesheet after initialization."""
        window = MainWindow(mock_config)

        # Window should have stylesheet applied
        stylesheet = window.styleSheet()
        assert stylesheet != "", "Stylesheet not applied to window"
        assert "job_queue_list" in stylesheet or "app_state_label" in stylesheet


class TestAppStateLabelObjectName:
    """Test app_state_label has object name for QSS."""

    def test_app_state_label_has_object_name(self, qapp, mock_config):
        """app_state_label has object name set."""
        window = MainWindow(mock_config)

        assert window.ui.app_state_label.objectName() == "app_state_label"
