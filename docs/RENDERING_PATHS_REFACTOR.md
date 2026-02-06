# Rendering Paths Refactoring Plan

## Goal

Move `rendering_paths` from Config god-object to RenderJob, giving each render job ownership of its file paths.

## Current Problems (Anti-Patterns)

1. **Scattered State**: Paths stored in Config but set by MainWindow and read by RenderThread
2. **Mutable Dict**: Using `dict[str, str]` loses type safety - typos in keys cause runtime errors
3. **Mixed Concerns**: Config holds both app configuration AND session-specific render paths
4. **Temporal Coupling**: Paths must be set before creating RenderThread, but nothing enforces this

## Solution: Type-First Refactoring

### Phase 1: Define New Types (Type-First Development)

**1.1 Create `models/render_paths.py`**

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class RenderPaths:
    """Immutable paths for a single render job."""
    # Input paths (from user)
    raw: Path
    audio: Optional[Path]
    sub: Optional[Path]

    # Output paths (computed)
    softsub: Path
    hardsub: Path

    @classmethod
    def from_ui_state(
        cls,
        raw_path: str,
        audio_path: str,
        sub_path: str,
        episode_name: str,
        softsub_dir: Path,
        hardsub_dir: Path
    ) -> 'RenderPaths':
        """Factory method: construct from MainWindow UI state."""
        return cls(
            raw=Path(raw_path),
            audio=Path(audio_path) if audio_path else None,
            sub=Path(sub_path) if sub_path else None,
            softsub=softsub_dir / f"{episode_name}.mkv",
            hardsub=hardsub_dir / f"{episode_name}.mp4",
        )

    def validate(self) -> list[str]:
        """Validate paths exist. Returns list of error messages."""
        errors = []
        if not self.raw.exists():
            errors.append(f"Raw video not found: {self.raw}")
        if self.audio and not self.audio.exists():
            errors.append(f"Audio file not found: {self.audio}")
        if self.sub and not self.sub.exists():
            errors.append(f"Subtitle file not found: {self.sub}")
        return errors
```

**Benefits:**
- ✅ Type-safe: `paths.raw` instead of `paths['raw']` (typos caught at type-check time)
- ✅ Immutable: `frozen=True` prevents accidental mutation
- ✅ Self-validating: `validate()` method encapsulates validation logic
- ✅ Clear ownership: Each RenderJob owns its paths

**1.2 Update `models/job.py`**

```python
from models.render_paths import RenderPaths

@dataclass
class RenderJob:
    """Complete specification for a render operation."""
    # ADD THIS:
    paths: RenderPaths

    # Existing fields:
    episode_name: str
    build_state: BuildState
    nvenc_state: NvencState
    logo_state: LogoState
    encoding_params: EncodingParams
    video_settings: VideoSettings
    potato_mode: bool

    @classmethod
    def from_config_and_paths(
        cls,
        config: Config,
        paths: RenderPaths
    ) -> 'RenderJob':
        """Factory: construct RenderJob from Config + validated paths."""
        # Calculate encoding params based on config + video analysis
        encoding_params = EncodingParams(...)  # existing logic

        return cls(
            paths=paths,
            episode_name=config.build_settings.episode_name,
            build_state=config.build_settings.build_state,
            nvenc_state=config.build_settings.nvenc_state,
            logo_state=config.build_settings.logo_state,
            encoding_params=encoding_params,
            video_settings=config.build_settings.video_settings,
            potato_mode=config.potato_PC,
        )
```

### Phase 2: Write Tests (TDD)

**2.1 `tests/test_render_paths.py`**

```python
def test_render_paths_construction():
    """RenderPaths constructs with all required fields."""
    paths = RenderPaths(
        raw=Path("/path/to/raw.mkv"),
        audio=Path("/path/to/audio.mka"),
        sub=Path("/path/to/sub.ass"),
        softsub=Path("/output/ep01.mkv"),
        hardsub=Path("/output/ep01.mp4"),
    )
    assert paths.raw == Path("/path/to/raw.mkv")
    assert paths.softsub == Path("/output/ep01.mkv")

def test_render_paths_from_ui_state(tmp_path):
    """Factory method creates RenderPaths from UI inputs."""
    paths = RenderPaths.from_ui_state(
        raw_path="/raw.mkv",
        audio_path="/audio.mka",
        sub_path="/sub.ass",
        episode_name="Episode 01",
        softsub_dir=tmp_path / "soft",
        hardsub_dir=tmp_path / "hard",
    )
    assert paths.softsub == tmp_path / "soft" / "Episode 01.mkv"
    assert paths.hardsub == tmp_path / "hard" / "Episode 01.mp4"

def test_render_paths_optional_audio_sub():
    """Audio and sub paths can be None."""
    paths = RenderPaths(
        raw=Path("/raw.mkv"),
        audio=None,
        sub=None,
        softsub=Path("/soft.mkv"),
        hardsub=Path("/hard.mp4"),
    )
    assert paths.audio is None
    assert paths.sub is None

def test_render_paths_validation_missing_raw(tmp_path):
    """Validation detects missing raw file."""
    paths = RenderPaths(
        raw=tmp_path / "missing.mkv",
        audio=None,
        sub=None,
        softsub=tmp_path / "soft.mkv",
        hardsub=tmp_path / "hard.mp4",
    )
    errors = paths.validate()
    assert len(errors) == 1
    assert "Raw video not found" in errors[0]

def test_render_paths_validation_all_exist(tmp_path):
    """Validation passes when all required files exist."""
    raw = tmp_path / "raw.mkv"
    audio = tmp_path / "audio.mka"
    raw.touch()
    audio.touch()

    paths = RenderPaths(
        raw=raw,
        audio=audio,
        sub=None,
        softsub=tmp_path / "soft.mkv",
        hardsub=tmp_path / "hard.mp4",
    )
    errors = paths.validate()
    assert len(errors) == 0

def test_render_paths_immutable():
    """RenderPaths is immutable (frozen dataclass)."""
    paths = RenderPaths(
        raw=Path("/raw.mkv"),
        audio=None,
        sub=None,
        softsub=Path("/soft.mkv"),
        hardsub=Path("/hard.mp4"),
    )
    with pytest.raises(FrozenInstanceError):
        paths.raw = Path("/different.mkv")
```

**2.2 Update `tests/test_render_thread.py`**

Add tests for RenderThread using RenderJob with paths:

```python
def test_render_thread_uses_job_paths(mock_config, mock_runner, tmp_path):
    """RenderThread reads paths from RenderJob, not Config."""
    raw = tmp_path / "raw.mkv"
    raw.touch()

    paths = RenderPaths(
        raw=raw,
        audio=tmp_path / "audio.mka",
        sub=tmp_path / "sub.ass",
        softsub=tmp_path / "soft.mkv",
        hardsub=tmp_path / "hard.mp4",
    )

    job = RenderJob(
        paths=paths,
        episode_name="Episode 01",
        build_state=BuildState.SOFT_AND_HARD,
        # ... other fields
    )

    render_thread = RenderThread(mock_config, mock_runner, job)
    render_thread.run()

    # Verify paths from job were used
    assert mock_runner.ffmpeg_calls[0]  # contains paths.raw
```

### Phase 3: Refactor MainWindow (UI Layer)

**3.1 Update `windows/mainWindow.py`**

```python
class MainWindow:
    def __init__(self, config, runner):
        super().__init__()
        self.config = config
        self.runner = runner
        # NEW: Store UI path state locally, not on config
        self._ui_paths = {
            'raw': '',
            'audio': '',
            'sub': '',
        }

    def update_render_paths(self):
        """Update UI display of output paths (no longer stored)."""
        episode = self.config.build_settings.episode_name
        softsub_path = self.config.main_paths.softsub / f"{episode}.mkv"
        hardsub_path = self.config.main_paths.hardsub / f"{episode}.mp4"

        # Just update UI display
        self.config.log('mainWindow', 'update_render_paths',
                       f"Softsub will be: {softsub_path}")
        self.config.log('mainWindow', 'update_render_paths',
                       f"Hardsub will be: {hardsub_path}")

    def universal_update(self, path, value):
        """Update settings using dot notation."""
        # For path updates, store locally
        if path.startswith('ui_paths.'):
            key = path.split('.')[1]
            self._ui_paths[key] = value
            return

        # Existing config updates...
        parts = path.split('.')
        # ... rest of implementation

    def _create_render_paths(self) -> RenderPaths:
        """Factory: create RenderPaths from current UI state."""
        return RenderPaths.from_ui_state(
            raw_path=self._ui_paths['raw'],
            audio_path=self._ui_paths['audio'],
            sub_path=self._ui_paths['sub'],
            episode_name=self.config.build_settings.episode_name,
            softsub_dir=self.config.main_paths.softsub,
            hardsub_dir=self.config.main_paths.hardsub,
        )

    def _validate_before_render(self) -> bool:
        """Validate paths before starting render."""
        try:
            paths = self._create_render_paths()
            errors = paths.validate()

            if errors:
                # Show errors to user
                error_msg = "\\n".join(errors)
                QtWidgets.QMessageBox.critical(self, "Validation Error", error_msg)
                return False

            return True
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return False

    def render(self):
        """Start render with validated paths."""
        if not self._validate_before_render():
            return

        # Create immutable paths and job
        paths = self._create_render_paths()
        job = RenderJob.from_config_and_paths(self.config, paths)

        # Start render thread with job
        self.threadMain = RenderThread(self.config, self.runner, job)
        self.threadMain.state_update.connect(self.state_update)
        self.threadMain.update.connect(self.update_frame)
        self.threadMain.finished.connect(self.finish)
        self.threadMain.start()

        self.config.log('mainWindow', 'render', f"Started render job: {job.episode_name}")
```

**Key improvements:**
- ✅ Validation happens ONCE before render starts (fail-fast)
- ✅ Paths are immutable after validation (no accidental changes mid-render)
- ✅ Clear separation: UI state → RenderPaths → RenderJob → RenderThread
- ✅ No temporal coupling: Can't start render without valid paths

### Phase 4: Refactor RenderThread (Execution Layer)

**4.1 Update `threads/RenderThread.py`**

```python
class RenderThread(QThread):
    def __init__(self, config: Config, runner: ProcessRunner, job: RenderJob):
        super().__init__()
        self.config = config
        self.runner = runner
        self.job = job  # NEW: Job owns paths
        self.command_constructor = FFmpegConstructor(config)
        # ... rest of init

    def softsub(self):
        """Build and run softsub encode."""
        args = self.command_constructor.build_soft_args(
            raw_path=str(self.job.paths.raw),          # From job
            sound_path=str(self.job.paths.audio) if self.job.paths.audio else '',
            sub_path=str(self.job.paths.sub) if self.job.paths.sub else None,
            output_path=str(self.job.paths.softsub),   # From job
            # ... other params
        )
        self._run_encode(args, "Софтсаб делается")

    def hardsub(self):
        """Build and run hardsub encode."""
        args = self.command_constructor.build_hard_args(
            raw_path=str(self.job.paths.raw),          # From job
            sound_path=str(self.job.paths.audio) if self.job.paths.audio else '',
            sub_path=str(self.job.paths.sub) if self.job.paths.sub else None,
            output_path=str(self.job.paths.hardsub),   # From job
            # ... other params
        )
        self._run_encode(args, "Хардсаб делается")

    def ffmpeg_analysis_decoding(self):
        """Analyze raw video to determine encoding params."""
        args = [str(self.job.paths.raw)]  # From job
        process = self.runner.run_ffprobe(args)
        # ... rest of analysis
```

### Phase 5: Remove from Config

**5.1 Update `configs/config.py`**

```python
class Config:
    def __init__(self, paths: Paths, pc_info: PCInfo):
        # ... other init

        # REMOVE THIS:
        # self.rendering_paths = { ... }
```

**5.2 Update `tests/conftest.py`**

```python
@pytest.fixture
def mock_config(tmp_path):
    """Mock Config without rendering_paths."""
    # ... other setup

    # REMOVE THIS:
    # config.rendering_paths = { ... }

    return config

@pytest.fixture
def mock_render_paths(tmp_path):
    """Fixture: mock RenderPaths for testing."""
    raw = tmp_path / "raw.mkv"
    raw.touch()

    return RenderPaths(
        raw=raw,
        audio=tmp_path / "audio.mka",
        sub=tmp_path / "sub.ass",
        softsub=tmp_path / "soft.mkv",
        hardsub=tmp_path / "hard.mp4",
    )
```

## Migration Checklist

### Phase 1: Types ✓
- [ ] Create `models/render_paths.py` with RenderPaths dataclass
- [ ] Add `paths: RenderPaths` to RenderJob
- [ ] Add factory methods: `RenderPaths.from_ui_state()`, `RenderJob.from_config_and_paths()`

### Phase 2: Tests ✓
- [ ] Write `tests/test_render_paths.py` (8 tests)
- [ ] Update `tests/test_render_thread.py` to use RenderJob with paths
- [ ] Add `mock_render_paths` fixture to conftest.py
- [ ] ALL TESTS GREEN before proceeding

### Phase 3: MainWindow ✓
- [ ] Add `self._ui_paths` dict to store UI state
- [ ] Update `update_render_paths()` to compute, not store
- [ ] Update `universal_update()` to handle ui_paths.*
- [ ] Add `_create_render_paths()` factory method
- [ ] Add `_validate_before_render()` with user feedback
- [ ] Update `render()` to create job with paths
- [ ] Update file dialog handlers (raw, audio, sub)
- [ ] Run tests - should still be green

### Phase 4: RenderThread ✓
- [ ] Update `__init__` to accept `job: RenderJob`
- [ ] Update `softsub()` to use `self.job.paths.*`
- [ ] Update `hardsub()` to use `self.job.paths.*`
- [ ] Update `hardsubbering()` to use `self.job.paths.*`
- [ ] Update `raw_repairing()` to use `self.job.paths.*`
- [ ] Update `ffmpeg_analysis_decoding()` to use `self.job.paths.raw`
- [ ] Run tests - should still be green

### Phase 5: Cleanup ✓
- [ ] Remove `self.rendering_paths` from Config.__init__
- [ ] Remove `config.rendering_paths` from conftest fixtures
- [ ] Update all test assertions
- [ ] Run full test suite - should still be green
- [ ] Manual smoke test: launch app, select files, start render

## Benefits After Refactoring

**Before (Current State):**
```python
# Anti-pattern: Mutable dict, typos not caught
config.rendering_paths['raw'] = '/path/to/file.mkv'
config.rendering_paths['raww']  # Typo! Returns None, crashes later

# Anti-pattern: Validation scattered
if not os.path.exists(config.rendering_paths['raw']):
    show_error()
if not os.path.exists(config.rendering_paths['audio']):
    show_error()
# ... repeated in multiple places

# Anti-pattern: Temporal coupling
render_thread = RenderThread(config, runner)  # Paths set earlier?
```

**After (Type-Safe):**
```python
# Type-safe: Typos caught at type-check time
paths.raw  # ✓ Checked by type checker
paths.raww  # ✗ Type error!

# Single validation point with clear errors
errors = paths.validate()
if errors:
    show_errors(errors)
    return

# Explicit construction - no temporal coupling
paths = RenderPaths.from_ui_state(...)
job = RenderJob.from_config_and_paths(config, paths)
render_thread = RenderThread(config, runner, job)  # All data present
```

## Estimated Effort

- **Phase 1 (Types)**: 30 minutes - straightforward dataclass definitions
- **Phase 2 (Tests)**: 1 hour - write 10-12 new tests, update existing tests
- **Phase 3 (MainWindow)**: 1.5 hours - refactor 21 usage sites, add validation UI
- **Phase 4 (RenderThread)**: 45 minutes - update 6 methods to use job.paths
- **Phase 5 (Cleanup)**: 30 minutes - remove old code, final test pass

**Total: ~4 hours** of focused work, done incrementally with tests green at each phase.

## Risk Mitigation

1. **Write tests first** - Phase 2 creates safety net before touching production code
2. **Incremental changes** - Each phase is independently testable
3. **Type safety** - Compile-time checks catch most errors
4. **Immutability** - Frozen dataclass prevents mutation bugs
5. **Clear validation** - Fail-fast with user-friendly errors

## Follow-Up Work (Optional)

After this refactoring succeeds:
- [ ] Consider moving `episode_name` from BuildSettings to RenderJob (it's job-specific)
- [ ] Extract path computation logic to `PathResolver` service
- [ ] Add `RenderJob.to_dict()` / `from_dict()` for persistence
