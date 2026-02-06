"""Tests for modules/process_runner.py and mocks/mock_process_runner.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.process_runner import SubprocessRunner
from tests.mocks.mock_process_runner import MockProcess, MockProcessRunner


class TestMockProcess:
    """Test MockProcess helper."""

    def test_mock_process_stdout(self):
        """MockProcess returns stdout lines."""
        output = "line 1\nline 2\nline 3\n"
        proc = MockProcess(output)

        lines = list(proc.stdout)
        assert len(lines) == 3
        assert lines[0] == "line 1\n"
        assert lines[2] == "line 3\n"

    def test_mock_process_communicate(self):
        """MockProcess.communicate() returns (stdout, stderr)."""
        proc = MockProcess("stdout content", "stderr content")

        stdout, stderr = proc.communicate()
        assert stdout == "stdout content"
        assert stderr == "stderr content"

    def test_mock_process_wait(self):
        """MockProcess.wait() returns exit code."""
        proc = MockProcess()
        assert proc.wait() == 0


class TestMockProcessRunner:
    """Test MockProcessRunner."""

    def test_records_ffmpeg_calls(self):
        """MockProcessRunner records all ffmpeg calls."""
        runner = MockProcessRunner()

        runner.run_ffmpeg(['-y', '-i', 'input.mkv', 'output.mp4'])
        runner.run_ffmpeg(['-version'])

        assert len(runner.ffmpeg_calls) == 2
        assert runner.ffmpeg_calls[0] == ['-y', '-i', 'input.mkv', 'output.mp4']
        assert runner.ffmpeg_calls[1] == ['-version']

    def test_records_ffprobe_calls(self):
        """MockProcessRunner records all ffprobe calls."""
        runner = MockProcessRunner()

        runner.run_ffprobe(['-i', 'video.mkv'])

        assert len(runner.ffprobe_calls) == 1
        assert runner.ffprobe_calls[0] == ['-i', 'video.mkv']

    def test_returns_canned_output(self):
        """MockProcessRunner returns configured output."""
        runner = MockProcessRunner()
        runner.set_ffmpeg_output(0, "ffmpeg version 7.1\n")

        proc = runner.run_ffmpeg(['-version'])
        stdout, _ = proc.communicate()

        assert stdout == "ffmpeg version 7.1\n"

    def test_kill_tracked(self):
        """MockProcessRunner tracks kill calls."""
        runner = MockProcessRunner()

        assert runner._kill_called is False
        runner.kill_ffmpeg()
        assert runner._kill_called is True


class TestSubprocessRunner:
    """Test SubprocessRunner."""

    def test_run_ffmpeg_builds_command(self):
        """SubprocessRunner builds correct ffmpeg command."""
        runner = SubprocessRunner(Path("/usr/bin/ffmpeg"))

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_popen.return_value = mock_proc

            runner.run_ffmpeg(['-y', '-i', 'input.mkv', 'output.mp4'])

            # Verify Popen was called with correct arguments
            call_args = mock_popen.call_args
            cmd = call_args[0][0]
            assert cmd[0] == '/usr/bin/ffmpeg'
            assert cmd[1:] == ['-y', '-i', 'input.mkv', 'output.mp4']

    def test_run_ffmpeg_no_shell(self):
        """SubprocessRunner does not use shell=True."""
        runner = SubprocessRunner(Path("/usr/bin/ffmpeg"))

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_popen.return_value = mock_proc

            runner.run_ffmpeg(['-version'])

            # Verify shell=True was NOT used
            call_kwargs = mock_popen.call_args[1]
            assert 'shell' not in call_kwargs or call_kwargs.get('shell') is False

    def test_run_ffmpeg_uses_cwd(self):
        """SubprocessRunner uses provided cwd parameter."""
        runner = SubprocessRunner(Path("/usr/bin/ffmpeg"), cwd=Path("/default"))

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_popen.return_value = mock_proc

            runner.run_ffmpeg(['-version'], cwd=Path("/custom"))

            # Verify cwd was passed to Popen
            call_kwargs = mock_popen.call_args[1]
            assert call_kwargs['cwd'] == '/custom'

    def test_run_ffprobe_builds_command(self):
        """SubprocessRunner builds correct ffprobe command."""
        runner = SubprocessRunner(
            Path("/usr/bin/ffmpeg"),
            ffprobe_path=Path("/usr/bin/ffprobe")
        )

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_popen.return_value = mock_proc

            runner.run_ffprobe(['-i', 'video.mkv'])

            # Verify command starts with ffprobe path
            call_args = mock_popen.call_args
            cmd = call_args[0][0]
            assert cmd[0] == '/usr/bin/ffprobe'
            assert cmd[1:] == ['-i', 'video.mkv']

    def test_kill_ffmpeg_terminates_process(self):
        """kill_ffmpeg terminates the active process."""
        runner = SubprocessRunner(Path("/usr/bin/ffmpeg"))

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_proc.wait.return_value = 0
            mock_popen.return_value = mock_proc

            # Start a process
            runner.run_ffmpeg(['-version'])

            # Kill it
            runner.kill_ffmpeg()

            # Verify terminate and wait were called
            mock_proc.terminate.assert_called_once()
            mock_proc.wait.assert_called()

    def test_kill_ffmpeg_force_kills_on_timeout(self):
        """kill_ffmpeg force kills if terminate times out."""
        runner = SubprocessRunner(Path("/usr/bin/ffmpeg"))

        with patch('subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            # First wait times out, second succeeds
            import subprocess
            mock_proc.wait.side_effect = [subprocess.TimeoutExpired('cmd', 5), 0]
            mock_popen.return_value = mock_proc

            # Start a process
            runner.run_ffmpeg(['-version'])

            # Kill it
            runner.kill_ffmpeg()

            # Verify kill was called after timeout
            mock_proc.terminate.assert_called_once()
            mock_proc.kill.assert_called_once()
