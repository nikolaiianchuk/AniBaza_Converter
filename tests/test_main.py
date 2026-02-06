"""Tests for main.py - testing CURRENT codebase."""

import os
from pathlib import Path

import pytest


def test_restore_config_creates(mock_config, tmp_path):
    """restore_config creates default config.ini when missing."""
    from main import restore_config

    # Ensure config file doesn't exist
    if mock_config.main_paths.config.exists():
        mock_config.main_paths.config.unlink()

    restore_config(mock_config)

    # Check file was created
    assert mock_config.main_paths.config.exists()

    # Check content has expected sections
    content = mock_config.main_paths.config.read_text()
    assert '[dev settings]' in content
    assert '[log settings]' in content
    assert '[main settings]' in content


def test_restore_config_noop(mock_config, tmp_path):
    """restore_config does nothing when file exists."""
    from main import restore_config

    # Create config file
    original_content = "[test]\nvalue = 123"
    mock_config.main_paths.config.write_text(original_content)

    restore_config(mock_config)

    # File should not be modified
    assert mock_config.main_paths.config.read_text() == original_content
