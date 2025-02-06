# Lib import
import math
import os
import shutil
import re
import subprocess
import sys
import traceback
import configs.config as config

from modules.FFmpegConstructor import FFmpegConstructor
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
    def __init__(self):
        super(ThreadClassRender, self).__init__()
        sys.excepthook = self.handle_exception
        config.command_constructor = FFmpegConstructor()
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        config.logging_module.write_to_log('RenderThread', f"Handled exception: {error_message}")

    # Frame updater
    def frame_update(self, proc):
        for line in proc.stdout:
            config.logging_module.write_to_log('RenderThread', line)
            frame_match = re.search(r'frame=\s*(\d+)\s+fps=\s*(\d+)', line)

            if frame_match:
                remaining_frames = config.total_frames - int(frame_match.group(1))
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
        config.logging_module.write_to_log('RenderThread', "Starting softsubbing...")
        if config.build_settings['build_state'] in [0, 1]:
            cmd = config.command_constructor.build_soft_command(
                raw_path      = config.rendering_paths['raw'],
                sound_path    = config.rendering_paths['audio'],
                sub_path      = config.rendering_paths['sub'],
                output_path   = config.rendering_paths['softsub'],
                video_profile = config.build_settings['softsub_settings']['video_profile'],
                profile_level = config.build_settings['softsub_settings']['profile_level'],
                pixel_format  = config.build_settings['softsub_settings']['pixel_format'],
                include_logo  = config.build_settings['logo']
            )
            config.logging_module.write_to_log('RenderThread', f"Generated command: {cmd}")
            config.current_state = "Собираю софтсаб..."
            self.state_update(config.current_state)
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
        config.logging_module.write_to_log('RenderThread', "Starting hardsubbing...")
        if config.build_settings['build_state'] in [0, 2]:
            cmd = config.command_constructor.build_hard_command(
                raw_path      = config.rendering_paths['raw'], 
                sound_path    = config.rendering_paths['audio'], 
                sub_path      = config.rendering_paths['sub'], 
                output_path   = config.rendering_paths['hardsub'], 
                nvenc         = config.build_settings['hardsub_settings']['nvenc'], 
                crf_rate      = '18', 
                cqmin         = '17', 
                cq            = '18', 
                cqmax         = '25', 
                preset        = 'faster' if not config.build_settings['hardsub_settings']['nvenc'] else 'p5', 
                tune          = config.build_settings['hardsub_settings']['video_tune'] if not config.build_settings['hardsub_settings']['nvenc'] else 'uhq',
                video_profile = config.build_settings['hardsub_settings']['video_profile'], 
                profile_level = config.build_settings['hardsub_settings']['profile_level'] if '10' in config.build_settings['hardsub_settings']['video_profile'] else '4.2', 
                pixel_format  = config.build_settings['hardsub_settings']['pixel_format'], 
                include_logo  = config.build_settings['logo']
            )
            config.logging_module.write_to_log('RenderThread', f"Generated command: {cmd}")
            config.current_state = "Собираю хардсаб..."
            self.state_update(config.current_state)
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
        config.logging_module.write_to_log('RenderThread', "Starting special hardsubbing...")
        if config.build_settings['build_state'] == 3:
            #cmd = f"{config.init_cmd}{config.override_output_cmd}{config.video_input_cmd}{config.hard_burning_cmd}{config.video_codec_cmd.get(config.codec)}-crf 18 {config.video_pixel_format_cmd}{config.hardsub_output_cmd}"
            cmd = ''
            config.logging_module.write_to_log('RenderThread', f"Generated command: {cmd}")
            config.current_state = "Собираю хардсаб для хардсабберов..."
            self.state_update(config.current_state)
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
        config.logging_module.write_to_log('RenderThread', "Starting ffmpeg analysis...")
        cmd = 'ffprobe "' + config.rendering_paths['raw'] +'"'
        config.logging_module.write_to_log('RenderThread', f"Generated command: {cmd}")
        process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8',
                                errors='replace'
                                )
        self.ffmpeg_analysis_decoding(process)
        
    def ffmpeg_analysis_decoding(self, proc):
        profiles = {
            '(Main)'    : ['main', 'main'], 
            '(Main 10)' : ['high10', 'main10'], 
            '(High)'    : ['high', 'main10'], 
            '(High 10)' : ['high10', 'main10']
        }
        
        for line in proc.stdout:
            config.logging_module.write_to_log('RenderThread', line)
            duration_match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', line)
            codec_match = re.search(r'Stream.*Video:\s*(.*)', line)
            
            if duration_match:
                hrs, minutes, sec = map(float, duration_match.groups())
                duration = hrs * 3600 + minutes * 60 + sec
                config.total_frames = duration * 24000 / 1001.0
                self.time_upd.emit(config.total_frames)
            
            if codec_match:
                for item in ['yuv420p,', 'yuv420p(', 'yuv420p ', 'yuv420p10le,', 'yuv420p10le(', 'yuv420p10le ', 'p010le,', 'p010le(', 'p010le ']:
                    if item in codec_match.group(0):
                        config.logging_module.write_to_log('RenderThread', f"found {item[:-1]}")
                        if item[:-1] == 'yuv420p':
                            config.build_settings['softsub_settings']['pixel_format'] = 'yuv420p'
                            config.build_settings['hardsub_settings']['pixel_format'] = 'yuv420p'
                        elif item[:-1] in ['yuv420p10le', 'p010le']:
                            config.build_settings['softsub_settings']['pixel_format'] = 'yuv420p10le'
                            config.build_settings['hardsub_settings']['pixel_format'] = 'yuv420p10le' if config.build_settings['hardsub_settings']['nvenc'] == False else 'p010le'
                    
                for item in ['(Main)', '(Main 10)', '(High)', '(High 10)']:
                    if item in codec_match.group(0):
                        config.logging_module.write_to_log('RenderThread', f"found {item[1:-1]}")
                        config.build_settings['softsub_settings']['video_profile'] = profiles[item][0]
                        config.build_settings['hardsub_settings']['video_profile'] = profiles[item][1]
                        config.logging_module.write_to_log('RenderThread', f"Settings set: {profiles[item]}")

    # Coding commands
    def run(self):
        try:
            config.logging_module.write_to_log('RenderThread', "Running ffmpeg thread...")
            self.ffmpeg_analysis()
            self.softsub()
            self.hardsub()
            #self.hardsubbering()     
            config.command_constructor.remove_temp_sub()

        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
