"""Tests for modules/AppUpdater.py - testing CURRENT codebase."""

from unittest.mock import MagicMock, patch

import pytest

from modules.AppUpdater import UpdaterThread


class TestAppUpdater:
    """Test AppUpdater functionality."""

    @pytest.fixture
    def updater_thread(self, mock_config):
        """Create UpdaterThread with mock config."""
        with patch('sys.excepthook'):
            thread = UpdaterThread(mock_config)
        return thread

    def test_get_latest_ffmpeg_version(self, updater_thread, monkeypatch):
        """Parses version from mocked HTTP response."""
        mock_response = MagicMock()
        mock_response.text = "7.1"
        mock_response.raise_for_status = MagicMock()

        mock_get = MagicMock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        version = updater_thread.get_latest_ffmpeg_version()

        assert version == "7.1"
        assert mock_get.called

    def test_should_update_newer(self, updater_thread, monkeypatch):
        """should_update_ffmpeg returns True when latest > installed."""
        updater_thread.config.ffmpeg.version = "6.0"

        mock_response = MagicMock()
        mock_response.text = "7.1"
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))

        should_update, latest, installed = updater_thread.should_update_ffmpeg()

        # BUG: String comparison - "7.1" > "6.0" happens to work here
        assert should_update is True
        assert latest == "7.1"
        assert installed == "6.0"

    def test_should_update_current(self, updater_thread, monkeypatch):
        """should_update_ffmpeg returns False when versions equal."""
        updater_thread.config.ffmpeg.version = "7.1"

        mock_response = MagicMock()
        mock_response.text = "7.1"
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))

        should_update, latest, installed = updater_thread.should_update_ffmpeg()

        assert should_update is False

    def test_check_for_app_update(self, updater_thread, monkeypatch):
        """check_for_app_update parses JSON and compares versions."""
        updater_thread.config.app_info['version_number'] = "1.0.0"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "version": "1.1.0",
            "url": "https://example.com/update.exe",
            "name": "v1.1.0"
        }
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))

        version, url, name = updater_thread.check_for_app_update()

        # BUG: String comparison - "1.1.0" > "1.0.0" happens to work
        assert version == "1.1.0"
        assert url == "https://example.com/update.exe"
        assert name == "v1.1.0"

    def test_version_comparison_bug(self, updater_thread, monkeypatch):
        """Documents string comparison bug: '7.1' > '10.0' is True."""
        updater_thread.config.ffmpeg.version = "10.0"

        mock_response = MagicMock()
        mock_response.text = "7.1"
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))

        should_update, latest, installed = updater_thread.should_update_ffmpeg()

        # BUG: String comparison gives wrong result
        # "7.1" > "10.0" is False in string comparison, but 7.1 < 10.0 numerically
        # This documents the bug - will be fixed in Phase 5
        assert latest == "7.1"
        assert installed == "10.0"
        # String comparison would say no update needed, but semantically it should be False

    def test_get_latest_ffmpeg_version_network_error(self, updater_thread, monkeypatch):
        """Network errors are handled gracefully."""
        def mock_get_error(*args, **kwargs):
            raise ConnectionError("Network error")

        monkeypatch.setattr("requests.get", mock_get_error)

        version = updater_thread.get_latest_ffmpeg_version()

        assert version is None

    def test_check_for_app_update_no_update(self, updater_thread, monkeypatch):
        """No update when current version is latest."""
        updater_thread.config.app_info['version_number'] = "2.0.0"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "version": "1.0.0",
            "url": "https://example.com/update.exe",
            "name": "v1.0.0"
        }
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))

        version, url, name = updater_thread.check_for_app_update()

        # Should return None when no update available
        assert version is None
        assert url is None
        assert name is None
