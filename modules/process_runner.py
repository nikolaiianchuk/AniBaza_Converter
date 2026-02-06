"""Process runner for ffmpeg/ffprobe - eliminates shell=True and os.chdir() risks.

This abstraction provides:
- No shell injection vulnerabilities (no shell=True)
- No race conditions (no os.chdir())
- Portable process killing (process.terminate() instead of platform-specific commands)
- Testable via dependency injection
"""

import subprocess
from pathlib import Path
from typing import Optional

from models.protocols import ProcessHandle, ProcessRunner


class SubprocessRunner(ProcessRunner):
    """Concrete implementation of ProcessRunner using subprocess.Popen.

    Key improvements over direct subprocess usage:
    - Commands are lists, not strings (no shell=True)
    - Working directory is per-process (no os.chdir())
    - Tracks active process for safe termination
    """

    def __init__(self, ffmpeg_path: Path, ffprobe_path: Optional[Path] = None, cwd: Optional[Path] = None):
        """Initialize process runner.

        Args:
            ffmpeg_path: Path to ffmpeg executable
            ffprobe_path: Path to ffprobe executable (defaults to same dir as ffmpeg)
            cwd: Default working directory for processes (optional)
        """
        self._ffmpeg = ffmpeg_path
        self._ffprobe = ffprobe_path or (ffmpeg_path.parent / "ffprobe")
        self._cwd = cwd
        self._active: Optional[subprocess.Popen] = None

    def run_ffmpeg(self, args: list[str], cwd: Optional[Path] = None) -> ProcessHandle:
        """Run ffmpeg with given arguments.

        Args:
            args: Command-line arguments (without 'ffmpeg' prefix)
            cwd: Working directory (uses default if not specified)

        Returns:
            Running process handle

        Example:
            runner.run_ffmpeg(['-y', '-i', 'input.mkv', 'output.mp4'])
        """
        cmd = [str(self._ffmpeg)] + args
        self._active = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(cwd or self._cwd) if (cwd or self._cwd) else None,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        return self._active

    def run_ffprobe(self, args: list[str], cwd: Optional[Path] = None) -> ProcessHandle:
        """Run ffprobe with given arguments.

        Args:
            args: Command-line arguments (without 'ffprobe' prefix)
            cwd: Working directory (uses default if not specified)

        Returns:
            Running process handle

        Example:
            runner.run_ffprobe(['-i', 'video.mkv'])
        """
        cmd = [str(self._ffprobe)] + args
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(cwd or self._cwd) if (cwd or self._cwd) else None,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        return process

    def kill_ffmpeg(self) -> None:
        """Terminate the currently running ffmpeg process (if any).

        This is safer than platform-specific process killing:
        - Only terminates the process WE started
        - Works cross-platform (no taskkill/pgrep)
        - Waits for clean shutdown
        """
        if self._active:
            try:
                self._active.terminate()
                self._active.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if terminate didn't work
                self._active.kill()
                self._active.wait()
            finally:
                self._active = None
