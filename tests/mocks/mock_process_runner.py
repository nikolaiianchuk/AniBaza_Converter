"""Mock ProcessRunner for testing without real ffmpeg/ffprobe calls."""

from pathlib import Path
from typing import Optional

from models.protocols import ProcessHandle, ProcessRunner


class MockProcess:
    """Mock process handle that returns canned stdout."""

    def __init__(self, stdout_content: str = "", stderr_content: str = ""):
        """Initialize mock process.

        Args:
            stdout_content: Simulated stdout output
            stderr_content: Simulated stderr output
        """
        self._stdout_lines = stdout_content.splitlines(keepends=True) if stdout_content else []
        self._stderr = stderr_content
        self.returncode = 0

    @property
    def stdout(self):
        """Return stdout as iterable of lines."""
        return iter(self._stdout_lines)

    def communicate(self) -> tuple[str, str]:
        """Return (stdout, stderr) as strings."""
        return (''.join(self._stdout_lines), self._stderr)

    def wait(self) -> int:
        """Return exit code."""
        return self.returncode

    def terminate(self) -> None:
        """Mock terminate - no-op."""
        pass


class MockProcessRunner(ProcessRunner):
    """Mock ProcessRunner for testing.

    Records all ffmpeg/ffprobe calls and returns canned outputs.
    """

    def __init__(self):
        """Initialize mock runner."""
        self.ffmpeg_calls: list[list[str]] = []
        self.ffprobe_calls: list[list[str]] = []
        self.ffmpeg_outputs: dict[int, str] = {}  # call_index → stdout
        self.ffprobe_outputs: dict[int, str] = {}  # call_index → stdout
        self._kill_called = False

    def run_ffmpeg(self, args: list[str], cwd: Optional[Path] = None) -> ProcessHandle:
        """Record ffmpeg call and return mock process.

        Args:
            args: FFmpeg arguments
            cwd: Working directory (recorded but not used)

        Returns:
            MockProcess with canned output
        """
        self.ffmpeg_calls.append(args)
        call_index = len(self.ffmpeg_calls) - 1
        stdout = self.ffmpeg_outputs.get(call_index, "")
        return MockProcess(stdout)

    def run_ffprobe(self, args: list[str], cwd: Optional[Path] = None) -> ProcessHandle:
        """Record ffprobe call and return mock process.

        Args:
            args: FFprobe arguments
            cwd: Working directory (recorded but not used)

        Returns:
            MockProcess with canned output
        """
        self.ffprobe_calls.append(args)
        call_index = len(self.ffprobe_calls) - 1
        stdout = self.ffprobe_outputs.get(call_index, "")
        return MockProcess(stdout)

    def kill_ffmpeg(self) -> None:
        """Record kill call."""
        self._kill_called = True

    def set_ffmpeg_output(self, call_index: int, output: str) -> None:
        """Set canned output for a specific ffmpeg call.

        Args:
            call_index: Which call to mock (0-indexed)
            output: Stdout to return
        """
        self.ffmpeg_outputs[call_index] = output

    def set_ffprobe_output(self, call_index: int, output: str) -> None:
        """Set canned output for a specific ffprobe call.

        Args:
            call_index: Which call to mock (0-indexed)
            output: Stdout to return
        """
        self.ffprobe_outputs[call_index] = output
