# Lib import
import math
import re
import subprocess
import sys
import traceback
from typing import Optional

from modules.FFmpegConstructor import FFmpegConstructor
from models.protocols import ProcessRunner
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
    def __init__(self, config, runner: Optional[ProcessRunner] = None):
        """Initialize render thread.

        Args:
            config: Application configuration
            runner: Optional ProcessRunner for safe subprocess execution.
                    If not provided, falls back to old shell=True approach.
        """
        super(ThreadClassRender, self).__init__()
        self.config = config
        self.runner = runner  # New: Optional ProcessRunner for safe execution
        sys.excepthook = self.handle_exception
        self.config.command_constructor = FFmpegConstructor(self.config)
        self.render_speed = -1 if self.config.potato_PC else 1
        self.encoding_params = {
            "avg_bitrate": "6M",
            "max_bitrate": "9M",
            "buffer_size": "18M",
            "crf": "18",
            "cq": "18",
            "qmin": "17",
            "qmax": "25"
        }
        
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
                remaining_frames = self.config.total_frames - int(frame_match.group(1))
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
            cmd = self.config.command_constructor.build_soft_command(
                raw_path      = self.config.rendering_paths['raw'],
                sound_path    = self.config.rendering_paths['audio'],
                sub_path      = self.config.rendering_paths['sub'],
                output_path   = self.config.rendering_paths['softsub'],
                nvenc         = True if self.config.build_settings.nvenc_state in [0, 1] else False,
                crf_rate      = self.encoding_params['crf'],
                cqmin         = self.encoding_params['qmin'], 
                cq            = self.encoding_params['cq'], 
                cqmax         = self.encoding_params['qmax'],
                max_bitrate   = self.encoding_params['max_bitrate'],
                max_buffer    = self.encoding_params['buffer_size'],
                preset        = self.config.render_speed[self.render_speed][0] if self.config.build_settings.nvenc_state in [2, 3] else self.config.render_speed[self.render_speed][1], 
                tune          = self.config.build_settings.softsub_settings.video_tune if self.config.build_settings.nvenc_state in [2, 3] else 'hq',
                video_profile = self.config.build_settings.softsub_settings.video_profile,
                profile_level = self.config.build_settings.softsub_settings.profile_level,
                pixel_format  = self.config.build_settings.softsub_settings.pixel_format,
                include_logo  = True if self.config.build_settings.logo_state in [0, 1] else False,
                potato_mode   = self.config.potato_PC
            )
            self.config.log('RenderThread', 'softsub', f"Generated command: {cmd}")
            self.config.current_state = "Собираю софтсаб..."
            self.state_update(self.config.current_state)
            process = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                encoding='utf-8',
                                errors='replace'
                                )
            self.frame_update(process)

    # Hardsubbing
    def hardsub(self):
        self.config.log('RenderThread', 'hardsub', "Starting hardsubbing...")
        if self.config.build_settings.build_state in [0, 2]:
            cmd = self.config.command_constructor.build_hard_command(
                raw_path      = self.config.rendering_paths['raw'], 
                sound_path    = self.config.rendering_paths['audio'], 
                sub_path      = self.config.rendering_paths['sub'], 
                output_path   = self.config.rendering_paths['hardsub'], 
                nvenc         = True if self.config.build_settings.nvenc_state in [0, 2] else False,
                crf_rate      = self.encoding_params['crf'], 
                cqmin         = self.encoding_params['qmin'], 
                cq            = self.encoding_params['cq'], 
                cqmax         = self.encoding_params['qmax'], 
                max_bitrate   = self.encoding_params['max_bitrate'],
                max_buffer    = self.encoding_params['buffer_size'],
                preset        = self.config.render_speed[self.render_speed][0] if self.config.build_settings.nvenc_state in [1, 3] else self.config.render_speed[self.render_speed][1], 
                tune          = self.config.build_settings.hardsub_settings.video_tune if self.config.build_settings.nvenc_state in [1, 3] else 'hq',
                video_profile = self.config.build_settings.hardsub_settings.video_profile, 
                profile_level = self.config.build_settings.hardsub_settings.profile_level if '10' in self.config.build_settings.hardsub_settings.video_profile else '4.2', 
                pixel_format  = self.config.build_settings.hardsub_settings.pixel_format, 
                include_logo  = True if self.config.build_settings.logo_state in [0, 2] else False,
                potato_mode   = self.config.potato_PC
            )
            self.config.log('RenderThread', 'hardsub', f"Generated command: {cmd}")
            self.config.current_state = "Собираю хардсаб..."
            self.state_update(self.config.current_state)
            process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8',
                                errors='replace'
                                )
            self.frame_update(process)

    # Hardsubbing special
    def hardsubbering(self):
        self.config.log('RenderThread', 'hardsubbering', "Starting special hardsubbing...")
        if self.config.build_settings.build_state == 3:
            cmd = self.config.command_constructor.build_hard_command(
                raw_path      = self.config.rendering_paths['raw'],  
                sub_path      = self.config.rendering_paths['sub'], 
                output_path   = self.config.rendering_paths['hardsub'], 
                nvenc         = True if self.config.build_settings.nvenc_state in [0, 2] else False, 
                crf_rate      = self.encoding_params['crf'], 
                cqmin         = self.encoding_params['qmin'], 
                cq            = self.encoding_params['cq'], 
                cqmax         = self.encoding_params['qmax'], 
                max_bitrate   = self.encoding_params['max_bitrate'],
                max_buffer    = self.encoding_params['buffer_size'],
                preset        = 'faster' if self.config.build_settings.nvenc_state in [1, 3] else 'p4', 
                tune          = self.config.build_settings.hardsub_settings.video_tune if self.config.build_settings.nvenc_state in [1, 3] else 'hq',
                video_profile = self.config.build_settings.hardsub_settings.video_profile, 
                profile_level = self.config.build_settings.hardsub_settings.profile_level if '10' in self.config.build_settings.hardsub_settings.video_profile else '4.2', 
                pixel_format  = self.config.build_settings.hardsub_settings.pixel_format, 
                include_logo  = True if self.config.build_settings.logo_state in [0, 2] else False,
            )
            self.config.log('RenderThread', 'hardsubbering', f"Generated command: {cmd}")
            self.config.current_state = "Собираю хардсаб для хардсабберов..."
            self.state_update(self.config.current_state)
            process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8',
                                errors='replace'
                                )
            self.frame_update(process)
            
    def raw_repairing(self):
        self.config.log('RenderThread', 'raw_repairing', "Starting raw repairing...")
        if self.config.build_settings.build_state == 4:
            cmd = "ffmpeg -y -i {RAW} -c:v libx264 -c:a copy -c:s copy {OUTPUT}".format(
                RAW    = self.config.rendering_paths['raw'],
                OUTPUT = self.config.rendering_paths['softsub']
            )
            self.config.log('RenderThread', 'raw_repairing', f"Generated command: {cmd}")
            self.config.current_state = "Востанавливаю равку..."
            self.state_update(self.config.current_state)
            process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8',
                                errors='replace'
                                )
            self.frame_update(process)

    def ffmpeg_analysis(self):
        self.config.log('RenderThread', 'ffmpeg_analysis', "Starting ffmpeg analysis...")
        cmd = 'ffprobe "' + self.config.rendering_paths['raw'] +'"'
        self.config.log('RenderThread', 'ffmpeg_analysis', f"Generated command: {cmd}")
        process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8',
                                errors='replace'
                                )
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
        avg_bitrate = (file_size_gb * 1024 * 8) / self.config.total_duration_sec
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
                self.config.video_res = f"{height}p" if int(height) < 4096 else f"{int(height)/1024}K"
                self.config.log('RenderThread', 'ffmpeg_analysis_decoding', f"Video resolution: {self.config.video_res}")
            
            if duration_match:
                hrs, minutes, sec = map(float, duration_match.groups())
                self.config.total_duration_sec =  hrs * 3600 + minutes * 60 + sec
                self.config.total_frames = self.config.total_duration_sec * 24000 / 1001.0
                self.time_upd.emit(self.config.total_frames)
            
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

    def _run_process_safe(self, args: list[str]) -> subprocess.Popen:
        """Run ffmpeg using ProcessRunner if available, else fall back to old method.

        This enables incremental migration - new code uses safe ProcessRunner,
        old code continues working with shell=True.

        Args:
            args: FFmpeg arguments as a list

        Returns:
            Process handle for frame_update()
        """
        if self.runner:
            # New safe approach: no shell=True, no os.chdir()
            return self.runner.run_ffmpeg(args)
        else:
            # Old approach: shell=True (kept for backward compatibility)
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

    # Coding commands
    def run(self):
        try:
            self.config.log('RenderThread', 'run', "Running ffmpeg thread...")
            self.ffmpeg_analysis()
            self.encoding_params = self.calculate_encoding_params(2, self.config.video_res)
            self.softsub()
            self.hardsub()
            self.hardsubbering()
            self.raw_repairing()
            self.config.command_constructor.remove_temp_sub()

        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
