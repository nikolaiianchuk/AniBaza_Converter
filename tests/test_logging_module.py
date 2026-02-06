"""Tests for modules/LoggingModule.py - testing CURRENT codebase."""

from datetime import datetime
from pathlib import Path

import pytest

from modules.LoggingModule import LoggingModule


class TestLoggingModule:
    """Test LoggingModule functionality."""

    def test_start_logging_creates_file(self, tmp_path):
        """start_logging creates log file."""
        logger = LoggingModule()
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        logger.start_logging(True, logs_dir, 10)

        assert logger.log_flag is True
        assert logger.log_file is not None
        assert logger.log_filename is not None

        # Check file was created
        log_path = Path(logger.log_filename)
        assert log_path.exists()

        logger.stop_logging()

    def test_write_to_log_format(self, tmp_path):
        """write_to_log includes timestamp, module, function, message."""
        logger = LoggingModule()
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        logger.start_logging(True, logs_dir, 10)
        logger.write_to_log("TestModule", "test_function", "Test message")
        logger.stop_logging()

        log_path = Path(logger.log_filename)
        content = log_path.read_text()

        assert "[TestModule]" in content
        assert "[test_function]" in content
        assert "Test message" in content
        # Check timestamp format
        assert datetime.now().strftime("%Y-%m-%d") in content

    def test_log_rotation(self, tmp_path):
        """Old logs deleted when exceeding max_logs."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        # Create 12 old log files
        for i in range(12):
            old_log = logs_dir / f"mainlog_2024-01-{i+1:02d}_00-00-00.txt"
            old_log.write_text(f"Old log {i}")

        logger = LoggingModule()
        logger.start_logging(True, logs_dir, 10)
        logger.stop_logging()

        # Check that rotation happened: should have kept last 10 old files + 1 new file = 11 total
        # The rotation deletes oldest files before creating the new one
        remaining_logs = list(logs_dir.glob("*.txt"))
        assert len(remaining_logs) == 11  # 10 most recent old files + 1 new file

    def test_logging_disabled(self, tmp_path):
        """No file created when logging disabled."""
        logger = LoggingModule()
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        logger.start_logging(False, logs_dir, 10)

        assert logger.log_flag is False
        assert logger.log_file is None

        # Try to write (should be no-op)
        logger.write_to_log("Test", "test", "message")

        # No log files should exist
        log_files = list(logs_dir.glob("*.txt"))
        assert len(log_files) == 0

    def test_correct_path_usage(self, tmp_path):
        """Verifies that log_filename uses the provided logs_dir parameter."""
        logger = LoggingModule()
        logs_dir = tmp_path / "custom_logs"
        logs_dir.mkdir()

        logger.start_logging(True, logs_dir, 10)

        # FIXED: log_filename should use the provided logs_dir
        assert str(logs_dir) in logger.log_filename
        assert logger.log_filename.startswith(str(logs_dir))

        logger.stop_logging()

    def test_remove_empty_lines_from_log(self, tmp_path):
        """remove_empty_lines_from_log filters out empty lines."""
        log_file = tmp_path / "test.log"
        log_file.write_text("Line 1\n\nLine 2\n\n\nLine 3\n")

        logger = LoggingModule()
        logger.remove_empty_lines_from_log(str(log_file))

        content = log_file.read_text()
        lines = content.split('\n')

        # Should have 3 non-empty lines
        non_empty = [line for line in lines if line.strip()]
        assert len(non_empty) == 3
