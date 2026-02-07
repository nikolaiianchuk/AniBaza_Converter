"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path
from typing import Generator

import pytest
from PyQt5.QtWidgets import QApplication

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.config import (
    AppInfo,
    BuildSettings,
    Config,
    DevSettings,
    FFMpegConfig,
    PCInfo,
    Paths,
)
from models.enums import BuildState, LogoState, NvencState
from models.render_paths import RenderPaths


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't call app.quit() - causes issues with pytest-qt


@pytest.fixture
def mock_ffmpeg_config() -> FFMpegConfig:
    """Create FFMpegConfig without subprocess calls."""
    config = object.__new__(FFMpegConfig)
    config.installed = True
    config.path = Path("/usr/bin/ffmpeg")
    config.version = "7.1"
    config.nvenc = False
    return config


@pytest.fixture
def mock_pc_info() -> PCInfo:
    """Create PCInfo for non-Windows testing."""
    info = object.__new__(PCInfo)
    info.Platform = "darwin"
    info.OSName = "Darwin"
    info.OSVersion = "23.0.0"
    info.CPU = "Apple M1"
    info.RAM = "16"
    info.GPU = "Apple M1"
    return info


@pytest.fixture
def mock_paths(tmp_path: Path) -> Paths:
    """Create Paths using tmp_path, without creating directories."""
    paths = object.__new__(Paths)
    paths.appdata = tmp_path / "appdata"
    paths.cwd = project_root  # Use real project root for resources
    paths.config_dir = tmp_path / "configs"
    paths.config = paths.config_dir / "config.ini"
    paths.version = paths.config_dir / "current_version.ini"
    paths.logs = tmp_path / "logs"
    paths.temp = tmp_path / "tmp"
    paths.softsub = Path("")
    paths.hardsub = tmp_path / "HARDSUB"
    paths.logo = tmp_path / "logo" / "AniBaza_Logo16x9.ass"

    # Create directories
    for dir_path in [paths.config_dir, paths.logs, paths.temp, paths.hardsub]:
        dir_path.mkdir(parents=True, exist_ok=True)

    return paths


@pytest.fixture
def mock_config(tmp_path: Path, mock_paths: Paths, mock_pc_info: PCInfo, mock_ffmpeg_config: FFMpegConfig) -> Config:
    """Create fully populated Config without subprocess calls."""
    config = object.__new__(Config)

    # Main paths
    config.main_paths = mock_paths
    config.pc_info = mock_pc_info
    config.ffmpeg = mock_ffmpeg_config

    # Main objects
    from modules.LoggingModule import LoggingModule
    config.logging_module = LoggingModule()
    # Phase 4.2: Thread references moved to their owners
    config.updater_thread = None
    config.download_thread = None
    config.ffmpeg_thread = None

    # Application info (Phase 4: now dataclass)
    config.app_info = AppInfo(
        title='AniBaza Converter',
        version_number='1.0.0',
        version_name='Test',
        author='Test Author',
        update_link='https://raw.githubusercontent.com/Miki-san/AniBaza_Converter/master/latest_version.json'
    )

    # Special settings (Phase 4: now dataclass)
    config.dev_settings = DevSettings(
        dev_mode=True,
        logging_enabled=True,
        max_logs=10
    )

    # Working variables
    config.build_states = {
        'Софт и хард': 0,
        'Только софт': 1,
        'Только хард': 2,
        'Для хардсабберов': 3,
        'Починить равку': 4
    }

    config.render_speed = {
        -1: ('ultrafast', 'p1'),
        0: ('superfast', 'p2'),
        1: ('veryfast', 'p3'),
        2: ('faster', 'p4'),
        3: ('fast', 'p5')
    }

    config.update_search = True
    # Phase 4.3: Runtime state moved to proper owners (RenderThread, MainWindow)
    config.potato_PC = False

    # Build settings (Phase 4: now dataclass)
    config.build_settings = BuildSettings(
        episode_name='Test_Episode_01',  # Valid name to prevent MessageBox in tests
        build_state=BuildState.SOFT_AND_HARD,
        logo_state=LogoState.LOGO_BOTH,
        nvenc_state=NvencState.NVENC_BOTH
    )

    return config


@pytest.fixture
def mock_render_paths(tmp_path):
    """Fixture: mock RenderPaths for testing."""
    raw = tmp_path / "raw.mkv"
    audio = tmp_path / "audio.mka"
    sub = tmp_path / "sub.ass"

    # Create files so validation passes
    raw.touch()
    audio.touch()
    sub.touch()

    return RenderPaths(
        raw=raw,
        audio=audio,
        sub=sub,
        softsub=tmp_path / "soft.mkv",
        hardsub=tmp_path / "hard.mp4",
    )
