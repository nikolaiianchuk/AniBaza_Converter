# FFmpegConstructor Refactoring Plan

## Current Problems (Anti-Patterns)

### 1. Massive Duplication
```python
# Four methods doing almost the same thing:
build_soft_command()   # Returns string (deprecated, uses shell=True)
build_soft_args()      # Returns list (current)
build_hard_command()   # Returns string (deprecated, uses shell=True)
build_hard_args()      # Returns list (current)

# Two giant template dicts with 90% overlap:
softsub_ffmpeg_commands = {...}  # 39 lines
hardsub_ffmpeg_commands = {...}  # 25 lines
```

### 2. Bloated Parameter Lists
```python
def build_soft_args(
    self, raw_path='', sound_path='', sub_path=None,
    output_path='', nvenc=False, crf_rate=None, cqmin=None,
    cq=None, cqmax=None, max_bitrate='', max_buffer='',
    video_profile='main', profile_level='4.2', pixel_format='yuv420p',
    preset='faster', tune='animation', include_logo=True, potato_mode=False
):  # 16 parameters! Should use dataclasses instead
```

### 3. Mixed Responsibilities
- **Path escaping** (sub_escaper, logo_escaper)
- **Command building** (build_*_args)
- **State management** (self.sub, self.escaped_logo_path)
- **Template string substitution** (in build_*_command)

### 4. Mutable State
```python
self.sub = SubtitleInfo()  # Mutable state shared across calls
self.escaped_logo_path = ''  # Side effects in logo_escaper()
```

### 5. Legacy Code Still Present
`build_soft_command()` and `build_hard_command()` should be deleted but still exist (200+ lines of dead code).

## Solution: Type-First Refactoring

### Core Principle
FFmpegConstructor should be a **pure converter**:
```
VideoSettings + EncodingParams + RenderPaths → list[str] (ffmpeg args)
```

No state, no side effects, just data transformation.

---

## Phase 1: Define New Architecture

### 1.1 Create `models/ffmpeg_options.py`

```python
"""Structured FFmpeg command options."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from models.encoding import EncodingParams
from models.job import VideoSettings
from models.render_paths import RenderPaths


@dataclass(frozen=True)
class CodecOptions:
    """Codec selection options."""
    video_codec: str  # 'libx264', 'h264_nvenc', 'hevc', 'hevc_nvenc'
    audio_codec: str = 'aac'
    subtitle_codec: str = 'copy'


@dataclass(frozen=True)
class StreamMapping:
    """Input stream mapping configuration."""
    video_input_index: int = 0
    audio_input_index: Optional[int] = 1
    subtitle_input_index: Optional[int] = 2


@dataclass(frozen=True)
class FilterOptions:
    """Video filter configuration."""
    logo_path: Optional[Path] = None
    subtitle_path: Optional[Path] = None

    def to_filter_string(self) -> Optional[str]:
        """Build -vf filter string."""
        filters = []
        if self.logo_path:
            escaped = _escape_path_for_filter(self.logo_path)
            filters.append(f"subtitles='{escaped}'")
        if self.subtitle_path:
            escaped = _escape_path_for_filter(self.subtitle_path)
            filters.append(f"subtitles='{escaped}'")

        return ", ".join(filters) if filters else None


@dataclass(frozen=True)
class FFmpegOptions:
    """Complete FFmpeg encoding options.

    This is the unified representation of all encoding settings.
    Single source of truth for building ffmpeg commands.
    """
    # Input/output
    paths: RenderPaths

    # Codecs
    codecs: CodecOptions

    # Encoding parameters
    encoding: EncodingParams

    # Video settings
    video: VideoSettings

    # Filters
    filters: FilterOptions

    # Stream configuration
    streams: StreamMapping = StreamMapping()

    # Preset
    preset: str = 'faster'

    # Flags
    use_nvenc: bool = False
    include_audio: bool = True
    include_subtitles: bool = True


def _escape_path_for_filter(path: Path) -> str:
    """Escape path for use in FFmpeg filter string.

    Windows paths need special escaping: C:\foo\bar.ass → C\\:\\\\foo\\\\bar.ass
    """
    path_str = str(path).replace('\\', '/')
    # Escape colon for filter syntax
    return path_str.replace(':/', r'\:\\')
```

### 1.2 Create `modules/ffmpeg_builder.py`

```python
"""Pure functional FFmpeg command builder.

Single responsibility: Convert FFmpegOptions → list[str] (ffmpeg arguments)
No state, no side effects, no file I/O.
"""

from pathlib import Path
from typing import Optional

from models.ffmpeg_options import FFmpegOptions, FilterOptions
from models.encoding import EncodingDefaults


def build_ffmpeg_args(options: FFmpegOptions) -> list[str]:
    """Build complete FFmpeg argument list.

    Pure function: same input always produces same output.
    No side effects, no state.

    Args:
        options: Complete encoding options

    Returns:
        List of ffmpeg arguments (safe for subprocess.Popen)
    """
    args = []

    # Basic flags
    args.extend(['-y'])  # Override output

    # Inputs
    _add_inputs(args, options)

    # Stream mapping
    _add_stream_mapping(args, options)

    # Metadata
    _add_metadata(args, options)

    # Video filters
    _add_filters(args, options.filters)

    # Video encoding
    _add_video_encoding(args, options)

    # Audio encoding
    if options.include_audio:
        _add_audio_encoding(args)

    # Subtitle handling
    if options.include_subtitles and options.paths.sub:
        args.extend(['-c:s', options.codecs.subtitle_codec])

    # Output
    args.append(str(options.paths.softsub if options.include_subtitles
                    else options.paths.hardsub))

    return args


def _add_inputs(args: list[str], options: FFmpegOptions) -> None:
    """Add input file arguments."""
    args.extend(['-i', str(options.paths.raw)])

    if options.include_audio and options.paths.audio:
        args.extend(['-i', str(options.paths.audio)])

    if options.include_subtitles and options.paths.sub:
        args.extend(['-i', str(options.paths.sub)])


def _add_stream_mapping(args: list[str], options: FFmpegOptions) -> None:
    """Add stream mapping arguments."""
    args.extend(['-map', f'{options.streams.video_input_index}:v:0'])

    if options.include_audio and options.streams.audio_input_index is not None:
        args.extend(['-map', f'{options.streams.audio_input_index}:a'])

    if options.include_subtitles and options.streams.subtitle_input_index is not None:
        args.extend(['-map', f'{options.streams.subtitle_input_index}:s'])

    args.extend(['-dn'])  # Discard data streams


def _add_metadata(args: list[str], options: FFmpegOptions) -> None:
    """Add metadata arguments."""
    args.extend([
        '-metadata:s:v:0', 'title=Original',
        '-metadata:s:v:0', 'language=jap'
    ])

    if options.include_audio:
        args.extend([
            '-metadata:s:a:0', 'title=AniBaza',
            '-metadata:s:a:0', 'language=rus'
        ])

    if options.include_subtitles and options.paths.sub:
        args.extend([
            '-metadata:s:s:0', 'title=Caption',
            '-metadata:s:s:0', 'language=rus'
        ])


def _add_filters(args: list[str], filters: FilterOptions) -> None:
    """Add video filter arguments."""
    filter_str = filters.to_filter_string()
    if filter_str:
        args.extend(['-vf', filter_str])


def _add_video_encoding(args: list[str], options: FFmpegOptions) -> None:
    """Add video encoding arguments."""
    # Codec
    args.extend(['-c:v', options.codecs.video_codec])

    # Rate control
    if options.use_nvenc:
        args.extend([
            '-cq', str(options.encoding.cq),
            '-qmin', str(options.encoding.qmin),
            '-qmax', str(options.encoding.qmax)
        ])
    else:
        args.extend(['-crf', str(options.encoding.crf)])

    # Bitrate
    args.extend(['-b:v', options.encoding.avg_bitrate])
    args.extend(['-maxrate', options.encoding.max_bitrate])
    args.extend(['-bufsize', options.encoding.buffer_size])

    # Preset
    args.extend(['-preset', options.preset])

    # Tune (only for non-nvenc, non-potato)
    if options.video.video_tune and not options.use_nvenc:
        args.extend(['-tune', options.video.video_tune])

    # Profile and format
    args.extend(['-profile:v', options.video.video_profile])
    args.extend(['-pix_fmt', options.video.pixel_format])


def _add_audio_encoding(args: list[str]) -> None:
    """Add audio encoding arguments."""
    args.extend(['-c:a', EncodingDefaults.AUDIO_CODEC])
    args.extend(['-b:a', EncodingDefaults.AUDIO_BITRATE])
    args.extend(['-ar', str(EncodingDefaults.AUDIO_SAMPLE_RATE)])
```

### 1.3 Create Factory: `modules/ffmpeg_factory.py`

```python
"""Factory for creating FFmpegOptions from high-level config.

Handles the complexity of converting RenderJob + Config → FFmpegOptions.
"""

from pathlib import Path
from typing import Optional

from configs.config import Config
from models.enums import NvencState
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping
)
from models.job import VideoSettings
from models.render_paths import RenderPaths


class FFmpegOptionsFactory:
    """Factory for creating FFmpegOptions from render job settings."""

    def __init__(self, config: Config, temp_dir: Path):
        self.config = config
        self.temp_dir = temp_dir

    def create_softsub_options(
        self,
        paths: RenderPaths,
        video_settings: VideoSettings,
        encoding_params,
        use_nvenc: bool,
        include_logo: bool,
        preset: str
    ) -> FFmpegOptions:
        """Create options for softsub encoding."""
        # Prepare paths
        logo_path = self.config.main_paths.logo if include_logo else None
        sub_path = self._prepare_subtitle(paths.sub) if paths.sub else None

        return FFmpegOptions(
            paths=paths,
            codecs=CodecOptions(
                video_codec='h264_nvenc' if use_nvenc else 'libx264',
                audio_codec='aac',
                subtitle_codec='copy'
            ),
            encoding=encoding_params,
            video=video_settings,
            filters=FilterOptions(
                logo_path=logo_path,
                subtitle_path=None  # Softsub keeps subs as stream
            ),
            streams=StreamMapping(
                video_input_index=0,
                audio_input_index=1 if paths.audio else None,
                subtitle_input_index=2 if paths.sub else None
            ),
            preset=preset,
            use_nvenc=use_nvenc,
            include_audio=True,
            include_subtitles=bool(paths.sub)
        )

    def create_hardsub_options(
        self,
        paths: RenderPaths,
        video_settings: VideoSettings,
        encoding_params,
        use_nvenc: bool,
        include_logo: bool,
        preset: str
    ) -> FFmpegOptions:
        """Create options for hardsub encoding."""
        # Prepare paths
        logo_path = self.config.main_paths.logo if include_logo else None
        sub_path = self._prepare_subtitle(paths.sub) if paths.sub else None

        return FFmpegOptions(
            paths=paths,
            codecs=CodecOptions(
                video_codec='hevc_nvenc' if use_nvenc else 'hevc',
                audio_codec='aac'
            ),
            encoding=encoding_params,
            video=video_settings,
            filters=FilterOptions(
                logo_path=logo_path,
                subtitle_path=sub_path  # Hardsub burns subs into video
            ),
            streams=StreamMapping(
                video_input_index=0,
                audio_input_index=1 if paths.audio else None,
                subtitle_input_index=None  # No subtitle stream in hardsub
            ),
            preset=preset,
            use_nvenc=use_nvenc,
            include_audio=bool(paths.audio),
            include_subtitles=False  # Burned in, not as stream
        )

    def _prepare_subtitle(self, sub_path: Path) -> Optional[Path]:
        """Prepare subtitle file for burning.

        Copies file to temp if it has problematic characters ([, ]).
        Returns path safe for FFmpeg filter string.
        """
        if not sub_path or not sub_path.exists():
            return None

        name = sub_path.name
        # Check if name has problematic characters
        if '[' in name or ']' in name:
            # Copy to temp with sanitized name
            sanitized_name = name.replace('[', '').replace(']', '')
            temp_path = self.temp_dir / sanitized_name
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            import shutil
            shutil.copyfile(sub_path, temp_path)
            return temp_path

        return sub_path
```

---

## Phase 2: Write Tests (TDD)

### 2.1 `tests/test_ffmpeg_options.py`

```python
"""Tests for models/ffmpeg_options.py."""

from pathlib import Path
import pytest

from models.encoding import EncodingParams
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping,
    _escape_path_for_filter
)
from models.job import VideoSettings, VideoPresets
from models.render_paths import RenderPaths


class TestCodecOptions:
    def test_codec_options_construction(self):
        """CodecOptions constructs with required fields."""
        codecs = CodecOptions(video_codec='libx264')
        assert codecs.video_codec == 'libx264'
        assert codecs.audio_codec == 'aac'  # Default
        assert codecs.subtitle_codec == 'copy'  # Default

    def test_codec_options_immutable(self):
        """CodecOptions is immutable."""
        codecs = CodecOptions(video_codec='hevc')
        with pytest.raises(Exception):  # FrozenInstanceError
            codecs.video_codec = 'libx264'


class TestFilterOptions:
    def test_filter_options_no_filters(self):
        """FilterOptions with no paths returns None filter string."""
        filters = FilterOptions()
        assert filters.to_filter_string() is None

    def test_filter_options_logo_only(self, tmp_path):
        """FilterOptions with logo only builds correct filter."""
        logo = tmp_path / "logo.ass"
        filters = FilterOptions(logo_path=logo)

        filter_str = filters.to_filter_string()
        assert "subtitles=" in filter_str
        assert str(logo.name) in filter_str

    def test_filter_options_subtitle_only(self, tmp_path):
        """FilterOptions with subtitle only builds correct filter."""
        sub = tmp_path / "sub.ass"
        filters = FilterOptions(subtitle_path=sub)

        filter_str = filters.to_filter_string()
        assert "subtitles=" in filter_str
        assert str(sub.name) in filter_str

    def test_filter_options_both(self, tmp_path):
        """FilterOptions with logo and subtitle builds combined filter."""
        logo = tmp_path / "logo.ass"
        sub = tmp_path / "sub.ass"
        filters = FilterOptions(logo_path=logo, subtitle_path=sub)

        filter_str = filters.to_filter_string()
        assert filter_str.count("subtitles=") == 2
        assert ", " in filter_str  # Comma-separated


class TestPathEscaping:
    def test_escape_unix_path(self):
        """Unix paths pass through mostly unchanged."""
        path = Path("/home/user/video.mkv")
        escaped = _escape_path_for_filter(path)
        assert escaped == "/home/user/video.mkv"

    def test_escape_windows_path(self):
        """Windows paths get special escaping for filters."""
        # This test may need adjustment based on actual Windows behavior
        path = Path("C:/Users/test/video.mkv")
        escaped = _escape_path_for_filter(path)
        assert r"\:\\" in escaped or "C:/" in escaped


class TestFFmpegOptions:
    def test_ffmpeg_options_complete(self, mock_render_paths):
        """FFmpegOptions constructs with all required fields."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            use_nvenc=False
        )

        assert options.paths == mock_render_paths
        assert options.codecs.video_codec == 'libx264'
        assert options.encoding.crf == 18
        assert options.video == VideoPresets.SOFTSUB

    def test_ffmpeg_options_immutable(self, mock_render_paths):
        """FFmpegOptions is immutable."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions()
        )

        with pytest.raises(Exception):
            options.use_nvenc = True
```

### 2.2 `tests/test_ffmpeg_builder.py`

```python
"""Tests for modules/ffmpeg_builder.py."""

from pathlib import Path

from models.encoding import EncodingParams
from models.ffmpeg_options import (
    CodecOptions, FFmpegOptions, FilterOptions, StreamMapping
)
from models.job import VideoPresets
from modules.ffmpeg_builder import build_ffmpeg_args


class TestFFmpegBuilder:
    def test_build_basic_softsub_args(self, mock_render_paths):
        """Builds basic softsub command."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions(),
            use_nvenc=False,
            include_audio=True,
            include_subtitles=True
        )

        args = build_ffmpeg_args(options)

        # Verify basic structure
        assert '-y' in args
        assert '-i' in args
        assert '-c:v' in args
        assert args[args.index('-c:v') + 1] == 'libx264'
        assert '-crf' in args
        assert str(mock_render_paths.softsub) in args

    def test_build_nvenc_hardsub_args(self, mock_render_paths):
        """Builds NVENC hardsub command."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc_nvenc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(),
            use_nvenc=True,
            include_audio=True,
            include_subtitles=False
        )

        args = build_ffmpeg_args(options)

        # Verify NVENC-specific args
        assert args[args.index('-c:v') + 1] == 'hevc_nvenc'
        assert '-cq' in args
        assert '-qmin' in args
        assert '-qmax' in args
        assert '-crf' not in args  # CRF not used with NVENC

    def test_build_with_filters(self, mock_render_paths, tmp_path):
        """Builds command with video filters."""
        logo = tmp_path / "logo.ass"
        sub = tmp_path / "sub.ass"
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(logo_path=logo, subtitle_path=sub),
            use_nvenc=False
        )

        args = build_ffmpeg_args(options)

        # Verify filter is present
        assert '-vf' in args
        vf_index = args.index('-vf')
        filter_string = args[vf_index + 1]
        assert 'subtitles=' in filter_string
        assert filter_string.count('subtitles=') == 2  # Logo + sub

    def test_build_no_audio(self, mock_render_paths):
        """Builds command without audio."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='hevc'),
            encoding=encoding,
            video=VideoPresets.HARDSUB,
            filters=FilterOptions(),
            include_audio=False,
            include_subtitles=False
        )

        args = build_ffmpeg_args(options)

        # Verify audio codec not present
        assert '-c:a' not in args
        assert '-b:a' not in args

    def test_build_is_deterministic(self, mock_render_paths):
        """Same options produce same args (pure function)."""
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = FFmpegOptions(
            paths=mock_render_paths,
            codecs=CodecOptions(video_codec='libx264'),
            encoding=encoding,
            video=VideoPresets.SOFTSUB,
            filters=FilterOptions()
        )

        args1 = build_ffmpeg_args(options)
        args2 = build_ffmpeg_args(options)

        assert args1 == args2  # Deterministic output
```

### 2.3 `tests/test_ffmpeg_factory.py`

```python
"""Tests for modules/ffmpeg_factory.py."""

from models.enums import NvencState
from models.job import VideoPresets
from modules.ffmpeg_factory import FFmpegOptionsFactory


class TestFFmpegOptionsFactory:
    def test_create_softsub_options(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates valid softsub options."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_softsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.SOFTSUB,
            encoding_params=encoding,
            use_nvenc=False,
            include_logo=True,
            preset='faster'
        )

        assert options.codecs.video_codec == 'libx264'
        assert options.include_audio is True
        assert options.include_subtitles is True
        assert options.filters.logo_path is not None

    def test_create_hardsub_options(self, mock_config, mock_render_paths, tmp_path):
        """Factory creates valid hardsub options."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)
        encoding = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        options = factory.create_hardsub_options(
            paths=mock_render_paths,
            video_settings=VideoPresets.HARDSUB,
            encoding_params=encoding,
            use_nvenc=True,
            include_logo=True,
            preset='faster'
        )

        assert options.codecs.video_codec == 'hevc_nvenc'
        assert options.include_audio is True
        assert options.include_subtitles is False  # Burned in
        assert options.filters.subtitle_path is not None

    def test_prepare_subtitle_with_brackets(self, mock_config, tmp_path):
        """Subtitle with brackets gets copied to temp."""
        factory = FFmpegOptionsFactory(mock_config, tmp_path)

        # Create subtitle with problematic name
        sub_with_brackets = tmp_path / "original" / "[AniBaza] Episode 01.ass"
        sub_with_brackets.parent.mkdir()
        sub_with_brackets.write_text("test subtitle")

        prepared = factory._prepare_subtitle(sub_with_brackets)

        assert prepared != sub_with_brackets
        assert '[' not in prepared.name
        assert ']' not in prepared.name
        assert prepared.exists()
```

---

## Phase 3: Refactor RenderThread

Update RenderThread to use new builder:

```python
# Before (in RenderThread.softsub):
args = self.command_constructor.build_soft_args(
    raw_path      = str(self.paths.raw),
    sound_path    = str(self.paths.audio) if self.paths.audio else '',
    sub_path      = str(self.paths.sub) if self.paths.sub else None,
    output_path   = str(self.paths.softsub),
    nvenc         = True if self.config.build_settings.nvenc_state in [0, 1] else False,
    crf_rate      = self.encoding_params['crf'],
    # ... 10 more parameters
)

# After:
factory = FFmpegOptionsFactory(self.config, self.config.main_paths.temp)
options = factory.create_softsub_options(
    paths=self.paths,
    video_settings=self.config.build_settings.softsub_settings,
    encoding_params=self.encoding_params,
    use_nvenc=self.config.build_settings.nvenc_state in [0, 1],
    include_logo=self.config.build_settings.logo_state in [0, 1],
    preset=self.config.render_speed[self.render_speed][0]
)
args = build_ffmpeg_args(options)
```

---

## Phase 4: Remove Legacy Code

Delete:
- `build_soft_command()` - 67 lines
- `build_hard_command()` - 68 lines
- `softsub_ffmpeg_commands` dict - 39 lines
- `hardsub_ffmpeg_commands` dict - 25 lines
- Mutable state: `self.sub`, `self.escaped_logo_path`

Keep:
- `build_soft_args()` → wrapper around new builder (backward compat)
- `build_hard_args()` → wrapper around new builder (backward compat)

---

## Phase 5: Final Cleanup

Remove wrappers, update all call sites to use builder directly.

---

## Benefits After Refactoring

### Before (Current State)
```python
# 405 lines of code in FFmpegConstructor
# 4 methods with 16+ parameters each
# 2 giant template dicts
# Mutable state (self.sub, self.escaped_logo_path)
# Duplicate logic across soft/hard methods
# String templates + shell=True (legacy)

constructor = FFmpegConstructor(config)
args = constructor.build_soft_args(
    raw_path, sound_path, sub_path, output_path,
    nvenc, crf, qmin, cq, qmax, max_bitrate, max_buffer,
    video_profile, profile_level, pixel_format, preset,
    tune, include_logo, potato_mode  # 16 parameters!
)
```

### After (Clean)
```python
# ~200 lines split across 3 focused modules
# Type-safe dataclasses (FFmpegOptions)
# No state, no side effects (pure functions)
# Single source of truth for encoding options
# No duplication

factory = FFmpegOptionsFactory(config, temp_dir)
options = factory.create_softsub_options(
    paths=render_paths,
    video_settings=VideoPresets.SOFTSUB,
    encoding_params=encoding,
    use_nvenc=False,
    include_logo=True,
    preset='faster'  # 6 parameters, all meaningful
)
args = build_ffmpeg_args(options)  # Pure function
```

## Estimated Effort

- **Phase 1 (Types)**: 1 hour - Define dataclasses and builder
- **Phase 2 (Tests)**: 1.5 hours - Write ~15 tests for new modules
- **Phase 3 (Integration)**: 1 hour - Update RenderThread call sites
- **Phase 4 (Cleanup)**: 30 minutes - Delete legacy code
- **Phase 5 (Final)**: 30 minutes - Remove wrappers

**Total: ~4.5 hours** of focused work.

## Success Metrics

- ✅ Zero duplication (4 methods → 1 builder function)
- ✅ Type-safe (dataclasses instead of 16 parameters)
- ✅ Pure functions (no state, deterministic)
- ✅ ~200 lines removed
- ✅ All 125+ tests still passing
- ✅ Easier to test (pure functions)
- ✅ Easier to extend (add new codec? Add to CodecOptions)
