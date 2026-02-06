"""Protocols for dependency injection and testing.

Protocols define structural interfaces without requiring inheritance.
"""

from pathlib import Path
from typing import Iterable, Protocol


class ProcessHandle(Protocol):
    """Interface for a running subprocess (ffmpeg/ffprobe)."""

    @property
    def stdout(self) -> Iterable[str]:
        """Stdout stream from the process."""
        ...

    def communicate(self) -> tuple[str, str]:
        """Wait for process and return (stdout, stderr)."""
        ...

    def wait(self) -> int:
        """Wait for process to complete and return exit code."""
        ...

    def terminate(self) -> None:
        """Terminate the process."""
        ...


class ProcessRunner(Protocol):
    """Interface for running ffmpeg/ffprobe subprocesses.

    This abstraction allows us to:
    - Eliminate shell=True security risk
    - Eliminate os.chdir() race conditions
    - Use portable process termination
    - Inject mocks for testing
    """

    def run_ffmpeg(self, args: list[str], cwd: Path | None = None) -> ProcessHandle:
        """Run ffmpeg with given arguments.

        Args:
            args: Command-line arguments (without 'ffmpeg' prefix)
            cwd: Working directory (optional)

        Returns:
            ProcessHandle for the running process
        """
        ...

    def run_ffprobe(self, args: list[str], cwd: Path | None = None) -> ProcessHandle:
        """Run ffprobe with given arguments.

        Args:
            args: Command-line arguments (without 'ffprobe' prefix)
            cwd: Working directory (optional)

        Returns:
            ProcessHandle for the running process
        """
        ...

    def kill_ffmpeg(self) -> None:
        """Terminate the currently running ffmpeg process (if any).

        This is safer than platform-specific process killing as it only
        terminates the process we started, not all ffmpeg processes.
        """
        ...
