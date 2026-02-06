"""Tests for modules/ConfigModule.py - testing CURRENT codebase."""

from pathlib import Path

import pytest

import modules.ConfigModule as ConfigModule


class TestConfigModule:
    """Test ConfigModule load/save functionality."""

    def test_load_configs_populates_settings(self, mock_config, tmp_path):
        """load_configs reads all settings from INI file."""
        # Create config file
        config_content = """[dev settings]
enableDevMode = False
enableLogging = True

[log settings]
max_logs = 20

[main settings]
logo_state = 1
nvenc_state = 2
build_state = 1
update_search = False
potato_PC = True
"""
        mock_config.main_paths.config.write_text(config_content)

        ConfigModule.load_configs(mock_config)

        # Phase 4: dataclass attributes
        assert mock_config.dev_settings.dev_mode is False
        assert mock_config.dev_settings.logging_enabled is True
        assert mock_config.dev_settings.max_logs == 20
        assert mock_config.build_settings.logo_state == 1
        assert mock_config.build_settings.nvenc_state == 2
        assert mock_config.build_settings.build_state == 1
        assert mock_config.update_search is False
        assert mock_config.potato_PC is True

    def test_load_configs_app_info(self, mock_config, tmp_path):
        """load_configs reads app info from version file."""
        version_content = """[app data]
title = Test App
version = 1.2.3
versionname = TestVersion
author = Test Author
update_url = https://example.com/update.json
"""
        mock_config.main_paths.version.write_text(version_content)

        ConfigModule.load_configs(mock_config)

        # Phase 4: dataclass attributes
        assert mock_config.app_info.title == 'Test App'
        assert mock_config.app_info.version_number == '1.2.3'
        assert mock_config.app_info.version_name == 'TestVersion'
        assert mock_config.app_info.author == 'Test Author'
        assert mock_config.app_info.update_link == 'https://example.com/update.json'

    def test_save_config_writes_values(self, mock_config, tmp_path):
        """save_config persists values to INI file."""
        # Create initial config file
        config_content = """[dev settings]
enableDevMode = True
enableLogging = True

[log settings]
max_logs = 10

[main settings]
logo_state = 0
nvenc_state = 0
build_state = 0
update_search = True
potato_PC = False
"""
        mock_config.main_paths.config.write_text(config_content)

        # Modify values (Phase 4: dataclass attributes)
        from configs.config import BuildSettings
        from models.enums import BuildState, LogoState, NvencState
        mock_config.build_settings = BuildSettings(
            episode_name='',
            logo_state=LogoState(2),
            nvenc_state=NvencState(1),
            build_state=BuildState(3)
        )
        mock_config.update_search = False
        mock_config.potato_PC = True

        # Save
        ConfigModule.save_config(mock_config)

        # Reload and verify
        ConfigModule.load_configs(mock_config)
        assert mock_config.build_settings.logo_state == 2
        assert mock_config.build_settings.nvenc_state == 1
        assert mock_config.build_settings.build_state == 3
        assert mock_config.update_search is False
        assert mock_config.potato_PC is True

    def test_get_config_value_types(self, mock_config, tmp_path):
        """get_config_value handles bool, int, str conversions."""
        config_content = """[test]
bool_val = True
int_val = 42
str_val = test string
"""
        config_file = tmp_path / "test.ini"
        config_file.write_text(config_content)

        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_file)

        # Test bool
        bool_val = ConfigModule.get_config_value(mock_config, parser, 'test', 'bool_val', bool)
        assert bool_val is True
        assert isinstance(bool_val, bool)

        # Test int
        int_val = ConfigModule.get_config_value(mock_config, parser, 'test', 'int_val', int)
        assert int_val == 42
        assert isinstance(int_val, int)

        # Test str
        str_val = ConfigModule.get_config_value(mock_config, parser, 'test', 'str_val', str)
        assert str_val == 'test string'
        assert isinstance(str_val, str)

    def test_missing_config_file(self, mock_config, tmp_path):
        """Missing config file returns None from load_parser."""
        nonexistent = tmp_path / "nonexistent.ini"
        parser = ConfigModule.load_parser(mock_config, nonexistent)
        assert parser is None
