# Lib import
import math
import re
import subprocess
import sys
import traceback
from typing import Optional

from modules.GlobalExceptionHandler import get_global_handler
from modules.ffmpeg_factory import FFmpegOptionsFactory
from modules.ffmpeg_builder import build_ffmpeg_args
from models.encoding import EncodingParams
from models.enums import BuildState, NvencState, LogoState
from models.protocols import ProcessRunner
from models.render_paths import RenderPaths
from models.video_info import VideoInfo, parse_ffprobe_output
from PyQt5 import QtCore
from PyQt5.QtCore import QThread

# Coding class with thread
class ThreadClassRender(QThread):
    # Signals
    frame_upd        = QtCore.pyqtSignal(object)
    time_upd         = QtCore.pyqtSignal(object)
    state_upd        = QtCore.pyqtSignal(object)
    elapsed_time_upd = QtCore.pyqtSignal(object)

    # Thread init
    def __init__(self, config, runner: Optional[ProcessRunner] = None, paths: RenderPaths = None):
        """Initialize render thread.

        Args:
            config: Application configuration
            runner: Optional ProcessRunner for safe subprocess execution.
            paths: RenderPaths with validated file paths (required).
        """
        super(ThreadClassRender, self).__init__()
        self.config = config
        self.runner = runner
        self.paths = paths
        get_global_handler().register_callback(self.handle_exception)

        # Factory for creating FFmpegOptions
        self.ffmpeg_factory = FFmpegOptionsFactory(config, config.main_paths.temp)

        self.render_speed = -1 if self.config.potato_PC else 1
        self.total_duration_sec = 0
        self.total_frames = 0
        self.video_res = ''
        self._cancelled = False  # Flag to stop entire job

        # Convert to EncodingParams dataclass
        self.encoding_params = EncodingParams(
            avg_bitrate="6M",
            max_bitrate="9M",
            buffer_size="18M",
            crf=18,
            cq=19,
            qmin=17,
            qmax=23
        )
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.config.log('RenderThread', 'handle_exception', f"Handled exception: {error_message}")

    # Frame updater
    def frame_update(self, proc):
        for line in proc.stdout:
            self.config.log('RenderThread', 'frame_update', line)
            frame_match = re.search(r'frame=\s*(\d+)\s+fps=\s*(\d+)', line)

            if frame_match:
                remaining_frames = self.total_frames - int(frame_match.group(1))
                fps = float(frame_match.group(2))
                remaining_time = remaining_frames / (fps if math.ceil(fps) != 0 else 1)
                rem_hrs = int(remaining_time // 3600)
                rem_minutes = int((remaining_time % 3600) // 60)
                rem_sec = remaining_time % 60
                
                self.frame_upd.emit(frame_match.group(1))
                self.elapsed_time_update(f"Оставшееся время: {rem_hrs}ч {rem_minutes}м {rem_sec:.2f}с")
                
    # State updater
    def state_update(self, state):
        self.state_upd.emit(state)
        
    def elapsed_time_update(self, time):
        self.elapsed_time_upd.emit(time)
        
    def cmd_prettyfier(self, cmd):
        cmd_list = cmd.split('-')
        prettified_cmd = '\n' + cmd_list[0] + '\n' + ''.join(f'-{line}\n' for line in cmd_list[1:-1])
        last_part = cmd_list[-1].split(' ')
        prettified_cmd += '-' + last_part[0] + ' ' + last_part[1] + '\n' + last_part[2]
        return prettified_cmd

    # Softsubbing
    def softsub(self):
        self.config.log('RenderThread', 'softsub', "Starting softsubbing...")
        # Only run if build_state includes softsub
        if self.config.build_settings.build_state in [BuildState.SOFT_AND_HARD, BuildState.SOFT_ONLY]:
            # Create options using factory
            use_nvenc = self.config.build_settings.nvenc_state in [NvencState.NVENC_BOTH, NvencState.NVENC_SOFT_ONLY]
            include_logo = self.config.build_settings.logo_state in [LogoState.LOGO_BOTH, LogoState.LOGO_SOFT_ONLY]
            preset = (self.config.render_speed[self.render_speed][0]
                     if self.config.build_settings.nvenc_state in [NvencState.NVENC_HARD_ONLY, NvencState.NVENC_NONE]
                     else self.config.render_speed[self.render_speed][1])

            options = self.ffmpeg_factory.create_softsub_options(
                paths=self.paths,
                video_settings=self.config.build_settings.softsub_settings,
                encoding_params=self.encoding_params,
                use_nvenc=use_nvenc,
                include_logo=include_logo,
                preset=preset
            )

            # Build args from options
            args = build_ffmpeg_args(options)
            self.config.log('RenderThread', 'softsub', f"Generated args: {' '.join(args)}")
            self._run_encode(args, "Собираю софтсаб...")

    # Hardsubbing
    def hardsub(self):
        self.config.log('RenderThread', 'hardsub', "Starting hardsubbing...")
        # Only run if build_state includes hardsub
        if self.config.build_settings.build_state in [BuildState.SOFT_AND_HARD, BuildState.HARD_ONLY]:
            # Create options using factory
            use_nvenc = self.config.build_settings.nvenc_state in [NvencState.NVENC_BOTH, NvencState.NVENC_HARD_ONLY]
            include_logo = self.config.build_settings.logo_state in [LogoState.LOGO_BOTH, LogoState.LOGO_HARD_ONLY]
            preset = (self.config.render_speed[self.render_speed][0]
                     if self.config.build_settings.nvenc_state in [NvencState.NVENC_SOFT_ONLY, NvencState.NVENC_NONE]
                     else self.config.render_speed[self.render_speed][1])

            options = self.ffmpeg_factory.create_hardsub_options(
                paths=self.paths,
                video_settings=self.config.build_settings.hardsub_settings,
                encoding_params=self.encoding_params,
                use_nvenc=use_nvenc,
                include_logo=include_logo,
                preset=preset
            )

            # Build args from options
            args = build_ffmpeg_args(options)
            self.config.log('RenderThread', 'hardsub', f"Generated args: {' '.join(args)}")
            self._run_encode(args, "Собираю хардсаб...")

    # Hardsubbing special
    def hardsubbering(self):
        self.config.log('RenderThread', 'hardsubbering', "Starting special hardsubbing...")
        # Special mode for hardsubbers (no audio/softsub)
        if self.config.build_settings.build_state == BuildState.FOR_HARDSUBBERS:
            # Create options using factory (no audio for hardsubbers)
            use_nvenc = self.config.build_settings.nvenc_state in [NvencState.NVENC_BOTH, NvencState.NVENC_HARD_ONLY]
            include_logo = self.config.build_settings.logo_state in [LogoState.LOGO_BOTH, LogoState.LOGO_HARD_ONLY]
            preset = 'faster' if self.config.build_settings.nvenc_state in [NvencState.NVENC_SOFT_ONLY, NvencState.NVENC_NONE] else 'p4'

            options = self.ffmpeg_factory.create_hardsub_options(
                paths=self.paths,
                video_settings=self.config.build_settings.hardsub_settings,
                encoding_params=self.encoding_params,
                use_nvenc=use_nvenc,
                include_logo=include_logo,
                preset=preset
            )

            # Build args from options
            args = build_ffmpeg_args(options)
            self.config.log('RenderThread', 'hardsubbering', f"Generated args: {' '.join(args)}")
            self._run_encode(args, "Собираю хардсаб для хардсабберов...")
            
    def raw_repairing(self):
        self.config.log('RenderThread', 'raw_repairing', "Starting raw repairing...")
        # Repair mode: fix broken raw video
        if self.config.build_settings.build_state == BuildState.RAW_REPAIR:
            args = [
                '-y',
                '-i', str(self.paths.raw),
                '-c:v', 'libx264',
                '-c:a', 'copy',
                '-c:s', 'copy',
                str(self.paths.softsub)
            ]
            self.config.log('RenderThread', 'raw_repairing', f"Generated args: {args}")
            self._run_encode(args, "Востанавливаю равку...")

    def ffmpeg_analysis(self):
        self.config.log('RenderThread', 'ffmpeg_analysis', "Starting ffmpeg analysis...")
        args = [str(self.paths.raw)]
        self.config.log('RenderThread', 'ffmpeg_analysis', f"Generated args: {args}")
        process = self._run_process_safe(args, is_ffprobe=True)
        self.ffmpeg_analysis_decoding(process)
    
    def calculate_encoding_params(self, file_size_gb, resolution) -> EncodingParams:
        """Calculate encoding parameters based on file size and resolution.

        Args:
            file_size_gb: Input file size in GB
            resolution: Video resolution (e.g., "1080p", "720p")

        Returns:
            EncodingParams dataclass with calculated values
        """
        avg_bitrate = (file_size_gb * 1024 * 8) / self.total_duration_sec
        avg_bitrate = avg_bitrate if avg_bitrate < 6 else 6

        if self.config.potato_PC:
            avg_bitrate /= 2

        max_bitrate = avg_bitrate * 1.5
        buffer_size = max_bitrate * 2

        if resolution in ["1080p", "4K"]:
            crf = 18
            cq = 19
        elif resolution == "720p":
            crf = 20
            cq = 21
        else:
            crf = 23
            cq = 23

        if self.config.potato_PC:
            crf = 23
            cq = 21

        qmin = cq - 2
        qmax = cq + 4

        params = EncodingParams(
            avg_bitrate=f"{int(avg_bitrate)}M",
            max_bitrate=f"{int(max_bitrate)}M",
            buffer_size=f"{int(buffer_size)}M",
            crf=crf,
            cq=cq,
            qmin=qmin,
            qmax=qmax
        )

        self.config.log('RenderThread', 'calculate_encoding_params',
                       f"EncodingParams: {params}")
        return params
    
    def ffmpeg_analysis_decoding(self, proc):
        """Parse video metadata from ffprobe output and apply to config.

        Wraps pure parsing function with logging and state application.
        """
        # Collect all output lines for parsing
        lines = []
        for line in proc.stdout:
            self.config.log('RenderThread', 'ffmpeg_analysis_decoding', line)
            lines.append(line)

        # Parse using pure function
        info = parse_ffprobe_output(lines)

        # Log parsed results
        self.config.log('RenderThread', 'ffmpeg_analysis_decoding',
                       f"Parsed: {info.resolution}, {info.pixel_format}, {info.video_profile}")

        # Apply parsed info to state
        self._apply_video_info(info)

    def _apply_video_info(self, info: VideoInfo):
        """Apply parsed video info to config settings.

        Separate from parsing for cleaner separation of concerns.
        Handles potato mode overrides and format/profile mapping for codec compatibility.
        """
        # Set runtime state
        self.total_duration_sec = info.duration_seconds
        self.total_frames = info.total_frames
        self.video_res = info.resolution
        self.time_upd.emit(info.total_frames)

        # Potato mode: force compatible settings
        if self.config.potato_PC:
            soft_pixel_fmt = 'yuv420p'
            hard_pixel_fmt = 'yuv420p'
            soft_profile = 'main'
            hard_profile = 'main'
            self.config.log('RenderThread', '_apply_video_info',
                          "Potato mode: forcing yuv420p and main profile")
        else:
            # Map parsed formats to output formats based on codec compatibility
            soft_pixel_fmt, hard_pixel_fmt = self._map_pixel_formats(info.pixel_format)
            soft_profile, hard_profile = self._map_profiles(info.video_profile)

        # Apply to build settings
        self.config.build_settings.softsub_settings.pixel_format = soft_pixel_fmt
        self.config.build_settings.hardsub_settings.pixel_format = hard_pixel_fmt
        self.config.build_settings.softsub_settings.video_profile = soft_profile
        self.config.build_settings.hardsub_settings.video_profile = hard_profile

        self.config.log('RenderThread', '_apply_video_info',
                       f"Applied settings: soft({soft_pixel_fmt}, {soft_profile}), "
                       f"hard({hard_pixel_fmt}, {hard_profile})")

    def _map_pixel_formats(self, parsed_format: str) -> tuple[str, str]:
        """Map parsed pixel format to softsub and hardsub formats.

        Handles codec compatibility - 10-bit formats need conversion for softsub.

        Args:
            parsed_format: Pixel format from video metadata

        Returns:
            Tuple of (softsub_format, hardsub_format)
        """
        if parsed_format in ['yuv420p10le', 'p010le']:
            # 10-bit formats: softsub uses 8-bit, hardsub preserves 10-bit
            softsub_fmt = 'yuv420p'
            # Hardsub format depends on nvenc usage
            if self.config.build_settings.nvenc_state in [NvencState.NVENC_SOFT_ONLY, NvencState.NVENC_NONE]:
                hardsub_fmt = 'yuv420p10le'
            else:
                hardsub_fmt = 'p010le'
            return softsub_fmt, hardsub_fmt
        else:
            # 8-bit: use as-is for both
            return parsed_format, parsed_format

    def _map_profiles(self, parsed_profile: str) -> tuple[str, str]:
        """Map parsed video profile to softsub and hardsub profiles.

        Different codecs need different profile mappings for compatibility.

        Args:
            parsed_profile: Video profile from metadata

        Returns:
            Tuple of (softsub_profile, hardsub_profile)
        """
        # Profile mapping based on parsed profile and nvenc usage
        profile_map = {
            'main': ('main', 'main'),
            'main10': (
                'high10' if self.config.build_settings.nvenc_state in [NvencState.NVENC_HARD_ONLY, NvencState.NVENC_NONE] else 'high',
                'main10'
            ),
            'high': ('high', 'main10'),
            'high10': (
                'high10' if self.config.build_settings.nvenc_state in [NvencState.NVENC_HARD_ONLY, NvencState.NVENC_NONE] else 'high',
                'main10'
            )
        }

        return profile_map.get(parsed_profile, (parsed_profile, parsed_profile))

    def _run_process_safe(self, args: list[str], is_ffprobe: bool = False) -> subprocess.Popen:
        """Run ffmpeg/ffprobe using ProcessRunner if available, else fall back to old method.

        This enables incremental migration - new code uses safe ProcessRunner,
        old code continues working with shell=True.

        Args:
            args: FFmpeg/ffprobe arguments as a list
            is_ffprobe: If True, run ffprobe instead of ffmpeg

        Returns:
            Process handle for frame_update() or ffmpeg_analysis_decoding()
        """
        if self.runner:
            # New safe approach: no shell=True, no os.chdir()
            if is_ffprobe:
                return self.runner.run_ffprobe(args)
            else:
                return self.runner.run_ffmpeg(args)
        else:
            # Old approach: shell=True (kept for backward compatibility)
            if is_ffprobe:
                cmd = f'ffprobe "{args[0]}"'
            else:
                cmd = ' '.join(args)
            return subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

    def _run_encode(self, args: list[str], state_label: str) -> None:
        """Phase 5.7: Consolidated encode execution helper.

        Encapsulates the common pattern of:
        1. Update UI state
        2. Run ffmpeg process
        3. Monitor progress

        Args:
            args: FFmpeg arguments as a list
            state_label: Status message to display (e.g., "Собираю софтсаб...")
        """
        self.state_update(state_label)
        process = self._run_process_safe(args)
        self.frame_update(process)

    def _cleanup_temp_files(self):
        """Clean up temporary subtitle files created by FFmpegOptionsFactory."""
        import shutil
        temp_dir = self.config.main_paths.temp
        if temp_dir.exists():
            # Remove all files in temp directory (factory creates subtitle copies here)
            for temp_file in temp_dir.glob('*'):
                if temp_file.is_file():
                    try:
                        temp_file.unlink()
                        self.config.log('RenderThread', '_cleanup_temp_files',
                                      f"Removed temp file: {temp_file.name}")
                    except Exception as e:
                        self.config.log('RenderThread', '_cleanup_temp_files',
                                      f"Failed to remove {temp_file.name}: {e}")

    # Coding commands
    def stop(self):
        """Stop the entire render job (all encoding steps)."""
        self._cancelled = True
        if self.runner:
            self.runner.kill_ffmpeg()
        self.config.log('RenderThread', 'stop', "Render job cancelled")

    def run(self):
        try:
            self.config.log('RenderThread', 'run', "Running ffmpeg thread...")
            self.ffmpeg_analysis()
            if self._cancelled:
                return

            self.encoding_params = self.calculate_encoding_params(2, self.video_res)
            if self._cancelled:
                return

            self.softsub()
            if self._cancelled:
                return

            self.hardsub()
            if self._cancelled:
                return

            self.hardsubbering()
            if self._cancelled:
                return

            self.raw_repairing()
            if self._cancelled:
                return

            self._cleanup_temp_files()

        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
