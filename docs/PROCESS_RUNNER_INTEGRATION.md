# ProcessRunner Integration Guide

This guide shows how to incrementally migrate from `shell=True` subprocess calls to the safer ProcessRunner approach.

## Overview

The codebase now supports **both** old and new approaches:
- **Old**: `subprocess.Popen(cmd, shell=True)` - still works, backward compatible
- **New**: `ProcessRunner.run_ffmpeg(args)` - safer, no shell injection risk

## Quick Start: Using ProcessRunner

### 1. Create a ProcessRunner

```python
from pathlib import Path
from modules.process_runner import SubprocessRunner

# Option A: Use system ffmpeg
runner = SubprocessRunner(
    ffmpeg_path=Path("/usr/bin/ffmpeg"),
    cwd=Path.cwd()  # Optional default working directory
)

# Option B: Use detected ffmpeg from config
if config.ffmpeg.installed and config.ffmpeg.path:
    runner = SubprocessRunner(
        ffmpeg_path=config.ffmpeg.path,
        cwd=config.main_paths.cwd
    )
else:
    runner = None  # Will fall back to old approach
```

### 2. Pass ProcessRunner to RenderThread

```python
# In mainWindow.py or main.py:

# Old way (still works):
thread = ThreadClassRender(config)

# New way (safer):
thread = ThreadClassRender(config, runner=runner)
```

### 3. Use Arg-Building Methods

```python
from modules.FFmpegConstructor import FFmpegConstructor

constructor = FFmpegConstructor(config)

# Old way: returns a string
cmd_string = constructor.build_soft_command(
    raw_path='input.mkv',
    sound_path='audio.wav',
    output_path='output.mkv',
    max_bitrate='9M',
    max_buffer='18M'
)
# Execute with shell=True (risky)
subprocess.Popen(cmd_string, shell=True)

# New way: returns a list
args_list = constructor.build_soft_args(
    raw_path='input.mkv',
    sound_path='audio.wav',
    output_path='output.mkv',
    max_bitrate='9M',
    max_buffer='18M'
)
# Execute safely without shell=True
runner.run_ffmpeg(args_list)
```

## Integration Example

Here's a complete example of integrating ProcessRunner into main.py:

```python
# main.py

from pathlib import Path
from configs.config import Config, PCInfo, Paths
from modules.process_runner import SubprocessRunner
from windows.mainWindow import MainWindow

def main():
    pc_info = PCInfo()
    cwd = get_cwd()  # Your existing cwd detection
    config = Config(Paths(cwd), pc_info)

    # Create ProcessRunner if ffmpeg is available
    runner = None
    if config.ffmpeg.installed and config.ffmpeg.path:
        runner = SubprocessRunner(
            ffmpeg_path=config.ffmpeg.path,
            cwd=config.main_paths.cwd
        )
        config.log('App System', 'main', f'ProcessRunner initialized: {runner}')

    # Pass runner to MainWindow (which passes it to threads)
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(config, runner=runner)  # Modified to accept runner
    mainWindow.show()

    sys.exit(app.exec_())
```

## Benefits of Incremental Migration

### Phase 1: Infrastructure (✅ Complete)
- ProcessRunner created
- Arg-building methods added
- Tests passing
- **Zero breaking changes**

### Phase 2: Optional Integration (Current)
- Pass ProcessRunner to threads optionally
- Old code continues working
- New code can use safer approach
- **Gradual migration**

### Phase 3: Full Migration (Future)
- All subprocess calls use ProcessRunner
- Remove shell=True completely
- Remove os.chdir() calls
- **Security hardened**

## Testing with ProcessRunner

```python
# tests/test_integration.py

from tests.mocks.mock_process_runner import MockProcessRunner

def test_render_with_process_runner(mock_config):
    """Test that RenderThread works with ProcessRunner."""
    mock_runner = MockProcessRunner()

    # Set up mock output
    mock_runner.set_ffprobe_output(0, "Duration: 00:24:00...")

    # Create thread with runner
    thread = ThreadClassRender(mock_config, runner=mock_runner)

    # Run analysis
    thread.ffmpeg_analysis()

    # Verify ffprobe was called
    assert len(mock_runner.ffprobe_calls) == 1
```

## Safe Process Killing

```python
# Old way (platform-specific, kills ALL ffmpeg):
if is_windows():
    subprocess.run('taskkill /f /im ffmpeg.exe', shell=True)
else:
    subprocess.run('kill $(pgrep ffmpeg)', shell=True)

# New way (portable, kills only our process):
runner.kill_ffmpeg()  # Works on all platforms, safe
```

## Migration Checklist

- [ ] Create ProcessRunner in main.py
- [ ] Pass runner to MainWindow
- [ ] Update MainWindow to pass runner to threads
- [ ] Update proc_kill() to use runner.kill_ffmpeg()
- [ ] Test on all platforms
- [ ] Gradually replace subprocess.Popen calls
- [ ] Remove shell=True completely
- [ ] Remove os.chdir() calls
- [ ] Update documentation

## Troubleshooting

**Q: My code still uses shell=True, is that OK?**
A: Yes! The old approach still works. ProcessRunner is optional for now.

**Q: Do I need to update all code at once?**
A: No! That's the point of incremental migration. Update gradually.

**Q: What if ProcessRunner is None?**
A: The code falls back to the old subprocess.Popen approach automatically.

**Q: How do I know if ProcessRunner is being used?**
A: Check the logs - if ProcessRunner is initialized, it will log the creation.

## See Also

- `modules/process_runner.py` - ProcessRunner implementation
- `tests/mocks/mock_process_runner.py` - Mock for testing
- `models/protocols.py` - ProcessRunner protocol definition
