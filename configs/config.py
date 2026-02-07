import os
import platform
import re
import subprocess
import sys

from dataclasses import dataclass, field
from pathlib import Path
from modules.LoggingModule import LoggingModule
from shutil import which
from typing import Optional

from models.enums import BuildState, LogoState, NvencState


@dataclass
class Paths:
    appdata: Path
    cwd: Path
    config_dir: Path
    config: Path
    version: Path
    logs: Path
    temp: Path
    softsub: Path
    hardsub: Path
    logo: Path

    def __init__(self, cwd: str):
        self.appdata = Path(os.getenv("APPDATA") or "")
        self.cwd = Path(cwd)
        self.config_dir = Path(cwd, "configs")
        self.config = Path(self.config_dir, "config.ini")
        self.version = Path(self.config_dir, "current_version.ini")
        self.logs = Path(cwd, "logs")
        self.temp = Path(cwd, "tmp")
        self.softsub = Path("")
        self.hardsub = Path(cwd, "HARDSUB")
        self.logo = Path(cwd, "logo/AniBaza_Logo16x9.ass")
        self.create_missing_folders()

    def create_missing_folders(self):
        for dir in [self.config_dir, self.logs, self.temp, self.hardsub]:
            if not os.path.exists(dir):
                os.mkdir(dir)


@dataclass()
class PCInfo:
    Platform: str = sys.platform
    OSName: str = ""
    OSVersion: str = ""
    CPU: str = ""
    RAM: str = ""
    GPU: str = ""

    def __post_init__(self):
        if self.is_windows():
            self._init_win32()
        else:
            self._init_default()

    def _init_win32(self):
        import wmi

        hardware = wmi.WMI()
        os_info = hardware.Win32_OperatingSystem()[0]
        proc_info = hardware.Win32_Processor()[0]
        gpu_info = hardware.Win32_VideoController()[0]

        os_name = os_info.Name.encode("utf-8").split(b"|")[0].decode("utf-8")
        os_version = " ".join([os_info.Version, os_info.BuildNumber])
        system_ram = int(float(os_info.TotalVisibleMemorySize) // (1024 * 1024)) + 1  # KB to GB

        self.OSName = os_name
        self.OSVersion = os_version
        self.CPU = proc_info.Name
        self.RAM = str(system_ram)
        self.GPU = gpu_info.Name

    def _init_default(self):
        self.OSName = platform.system()
        self.OSVersion = platform.platform()
        self.CPU = platform.processor()

    def is_windows(self) -> bool:
        return self.Platform == "win32"


@dataclass
class FFMpegConfig:
    installed: bool
    path: Optional[Path]
    version: Optional[str]
    nvenc: bool

    def __init__(self):
        self.installed = False
        self.path = None
        self.version = None
        self.nvenc = False

        path = which("ffmpeg")
        if not path:
            path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
        self.installed = os.path.exists(path)

        if not self.installed:
            return

        self.path = Path(path)
        self.__parse_ffmpeg_output()

    def __parse_ffmpeg_output(self):
        process = subprocess.Popen(
            [str(self.path), "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )
        stdout, _ = process.communicate()
        match = re.search(r"ffmpeg\s+version\s+([a-zA-Z0-9]+\.[0-9]+(?:\.[0-9]+)?)", stdout)
        if match:
            self.version = match.group(1)

        # validate nvenc availability
        process = subprocess.Popen(
            [
                str(self.path),
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=black:s=1080x1080",
                "-vframes",
                "1",
                "-an",
                "-c:v",
                "hevc_nvenc",
                "-f",
                "null",
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )
        _, stderr = process.communicate()
        self.nvenc = not stderr


@dataclass
class AppInfo:
    """Application metadata and versioning information."""

    title: str = ""
    version_number: str = ""
    version_name: str = ""
    author: str = ""
    update_link: str = "https://raw.githubusercontent.com/Miki-san/AniBaza_Converter/master/latest_version.json"


@dataclass
class DevSettings:
    """Development and debugging settings."""

    dev_mode: bool = True
    logging_enabled: bool = True
    max_logs: int = 10


@dataclass
class VideoSettings:
    """Video encoding settings — the actual tunable parameters."""

    video_tune: str = "animation"
    video_profile: str = "high10"
    profile_level: str = "4.1"
    pixel_format: str = "yuv420p10le"


class VideoPresets:
    """Named presets for different encoding scenarios."""

    SOFTSUB = VideoSettings(
        video_tune="animation",
        video_profile="high10",
        profile_level="4.1",
        pixel_format="yuv420p10le",
    )
    HARDSUB = VideoSettings(
        video_tune="animation",
        video_profile="main10",
        profile_level="4.1",
        pixel_format="yuv420p10le",
    )
    POTATO = VideoSettings(
        video_tune="",  # tune is skipped in potato mode
        video_profile="main",
        profile_level="4.1",
        pixel_format="yuv420p",
    )


@dataclass
class BuildSettings:
    """Build configuration for video rendering."""

    episode_name: str = ""
    build_state: BuildState = BuildState.SOFT_AND_HARD
    logo_state: LogoState = LogoState.LOGO_BOTH
    nvenc_state: NvencState = NvencState.NVENC_BOTH
    softsub_settings: VideoSettings = field(default_factory=lambda: VideoPresets.SOFTSUB)
    hardsub_settings: VideoSettings = field(default_factory=lambda: VideoPresets.HARDSUB)


class Config:
    def __init__(self, paths: Paths, pc_info: PCInfo):
        # Main paths
        self.main_paths: Paths = paths
        self.pc_info: PCInfo = pc_info
        self.ffmpeg: FFMpegConfig = FFMpegConfig()

        # Main objects
        self.logging_module = LoggingModule()
        self.updater_thread = None
        self.download_thread = None
        self.ffmpeg_thread = None

        self.app_info = AppInfo()
        self.dev_settings = DevSettings()
        self.build_settings = BuildSettings()

        # Working variables
        self.build_states = {
            "Софт и хард": 0,
            "Только софт": 1,
            "Только хард": 2,
            "Для хардсабберов": 3,
            "Починить равку": 4,
        }

        self.render_speed = {
            -1: ("ultrafast", "p1"),
            0: ("superfast", "p2"),
            1: ("veryfast", "p3"),
            2: ("faster", "p4"),
            3: ("fast", "p5"),
        }

        self.update_search = True
        self.potato_PC = False

        # Rendering paths - backward compatibility with old UI code
        self.rendering_paths = {
            'raw': '',
            'audio': '',
            'sub': '',
            'softsub': '',
            'hardsub': ''
        }

    def start_log(self):
        self.logging_module.start_logging(
            self.dev_settings.logging_enabled, self.main_paths.logs, self.dev_settings.max_logs
        )

    def log(self, module, function, message):
        # Упрощённый метод для логирования.
        self.logging_module.write_to_log(module, function, message)

    def stop_log(self):
        self.logging_module.stop_logging()
