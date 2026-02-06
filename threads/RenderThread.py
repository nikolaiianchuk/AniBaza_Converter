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
from models.protocols import ProcessRunner
from models.render_paths import RenderPaths
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
        if self.config.build_settings.build_state in [0, 1]:
            # Create options using factory
            use_nvenc = self.config.build_settings.nvenc_state in [0, 1]
            include_logo = self.config.build_settings.logo_state in [0, 1]
            preset = (self.config.render_speed[self.render_speed][0]
                     if self.config.build_settings.nvenc_state in [2, 3]
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
        if self.config.build_settings.build_state in [0, 2]:
            # Create options using factory
            use_nvenc = self.config.build_settings.nvenc_state in [0, 2]
            include_logo = self.config.build_settings.logo_state in [0, 2]
            preset = (self.config.render_speed[self.render_speed][0]
                     if self.config.build_settings.nvenc_state in [1, 3]
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
        if self.config.build_settings.build_state == 3:
            # Create options using factory (no audio for hardsubbers)
            use_nvenc = self.config.build_settings.nvenc_state in [0, 2]
            include_logo = self.config.build_settings.logo_state in [0, 2]
            preset = 'faster' if self.config.build_settings.nvenc_state in [1, 3] else 'p4'

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
        if self.config.build_settings.build_state == 4:
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
    
    def calculate_encoding_params(self, file_size_gb, resolution):
        output = {
            "avg_bitrate": "{AVG}M",
            "max_bitrate": "{MAX}M",
            "buffer_size": "{BUFFER}M",
            "crf": "{CRF}",
            "cq": "{CQ}",
            "qmin": "{QMIN}",
            "qmax": "{QMAX}"
        }
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
        
        output['avg_bitrate'] = output['avg_bitrate'].format(AVG=int(avg_bitrate))
        output['max_bitrate'] = output['max_bitrate'].format(MAX=int(max_bitrate))
        output['buffer_size'] = output['buffer_size'].format(BUFFER=int(buffer_size))
        output['crf'] = output['crf'].format(CRF=crf)
        output['cq'] = output['cq'].format(CQ=cq)
        output['qmin'] = output['qmin'].format(QMIN=qmin)
        output['qmax'] = output['qmax'].format(QMAX=qmax)
        
        self.config.log('RenderThread', 'calculate_encoding_params', f"EncodingParams: {output}")
        return output
    
    def ffmpeg_analysis_decoding(self, proc):
        profiles = {
            '(Main)'    : ['main', 'main', 'main'], 
            '(Main 10)' : ['high10', 'high', 'main10'], 
            '(High)'    : ['high', 'high', 'main10'], 
            '(High 10)' : ['high10', 'high', 'main10']
        }
        
        for line in proc.stdout:
            self.config.log('RenderThread', 'ffmpeg_analysis_decoding', line)
            duration_match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', line)
            codec_match = re.search(r'Stream.*Video:\s*(.*)', line)
            resolution_match = re.search(r'(\d{3,4})x(\d{3,4})', line)
            if resolution_match:
                _, height = resolution_match.groups()
                self.video_res = f"{height}p" if int(height) < 4096 else f"{int(height)/1024}K"
                self.config.log('RenderThread', 'ffmpeg_analysis_decoding', f"Video resolution: {self.video_res}")
            
            if duration_match:
                hrs, minutes, sec = map(float, duration_match.groups())
                self.total_duration_sec =  hrs * 3600 + minutes * 60 + sec
                self.total_frames = self.total_duration_sec * 24000 / 1001.0
                self.time_upd.emit(self.total_frames)
            
            if codec_match:
                for item in ['yuv420p,', 'yuv420p(', 'yuv420p ', 'yuv420p10le,', 'yuv420p10le(', 'yuv420p10le ', 'p010le,', 'p010le(', 'p010le ']:
                    if item in codec_match.group(0):
                        self.config.log('RenderThread', 'ffmpeg_analysis_decoding', f"found {item[:-1]}")
                        if item[:-1] == 'yuv420p':
                            self.config.build_settings.softsub_settings.pixel_format = 'yuv420p'
                            self.config.build_settings.hardsub_settings.pixel_format = 'yuv420p'
                        elif item[:-1] in ['yuv420p10le', 'p010le']:
                            self.config.build_settings.softsub_settings.pixel_format = 'yuv420p' #'yuv420p10le' if self.config.build_settings['softsub_settings']['nvenc'] == False else 'p010le'
                            self.config.build_settings.hardsub_settings.pixel_format = 'yuv420p10le' if self.config.build_settings.nvenc_state in [1, 3] else 'p010le'
                    
                for item in profiles.keys():
                    if item in codec_match.group(0):
                        self.config.log('RenderThread', 'ffmpeg_analysis_decoding', f"found {item[1:-1]}")
                        self.config.build_settings.softsub_settings.video_profile = profiles[item][0 if self.config.build_settings.nvenc_state in [2, 3] else 1]
                        self.config.build_settings.hardsub_settings.video_profile = profiles[item][2]
                        self.config.log('RenderThread', 'ffmpeg_analysis_decoding', f"Settings set: {profiles[item]}")
        
        if self.config.potato_PC:
            self.config.build_settings.softsub_settings.pixel_format = 'yuv420p'
            self.config.build_settings.hardsub_settings.pixel_format = 'yuv420p'
            self.config.build_settings.softsub_settings.video_profile = 'main'
            self.config.build_settings.hardsub_settings.video_profile = 'main'

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
    def run(self):
        try:
            self.config.log('RenderThread', 'run', "Running ffmpeg thread...")
            self.ffmpeg_analysis()
            self.encoding_params = self.calculate_encoding_params(2, self.video_res)
            self.softsub()
            self.hardsub()
            self.hardsubbering()
            self.raw_repairing()
            self._cleanup_temp_files()

        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
