# Lib import
import math
import os
import shutil
import re
import subprocess
import sys
import traceback
import config
import loggingModule

from PyQt5 import QtCore
from PyQt5.QtCore import QThread

# Coding class with thread
class ThreadClassSoft(QThread):
    # Signals
    frame_upd = QtCore.pyqtSignal(object)
    time_upd = QtCore.pyqtSignal(object)
    state_upd = QtCore.pyqtSignal(object)

    # Thread init
    def __init__(self):
        super(ThreadClassSoft, self).__init__()
        sys.excepthook = self.handle_exception
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        loggingModule.write_to_log(f"Handled exception: {error_message}")

    # Frame updater
    def frame_update(self, proc):
        for line in proc.stdout:
            loggingModule.write_to_log(line)
            frame_match = re.search(r'frame=\s*(\d+)\s+fps=\s*(\d+)', line)

            if frame_match:
                remaining_frames = config.total_frames - int(frame_match.group(1))
                fps = float(frame_match.group(2))
                remaining_time = remaining_frames / (fps if math.ceil(fps) != 0 else 1)
                rem_hrs = int(remaining_time // 3600)
                rem_minutes = int((remaining_time % 3600) // 60)
                rem_sec = remaining_time % 60
                
                self.frame_upd.emit(frame_match.group(1))
                self.state_update(f"{config.current_state} Оставшееся время: {rem_hrs}ч {rem_minutes}м {rem_sec:.2f}с")
                
    # State updater
    def state_update(self, state):
        self.state_upd.emit(state)
        
    def cmd_prettyfier(self, cmd):
        cmd_list = cmd.split('-')
        prettified_cmd = '\n' + cmd_list[0] + '\n' + ''.join(f'-{line}\n' for line in cmd_list[1:-1])
        last_part = cmd_list[-1].split(' ')
        prettified_cmd += '-' + last_part[0] + ' ' + last_part[1] + '\n' + last_part[2]
        return prettified_cmd

    # Softsubbing
    def softsub(self):
        loggingModule.write_to_log("Starting softsubbing...")
        if config.build_state in [0, 1]:
            cmd = config.init_cmd + \
                config.override_output_cmd + \
                config.video_input_cmd + \
                config.audio_input_cmd + \
                config.subtitle_input_cmd + \
                config.video_stream_cmd + \
                config.audio_stream_cmd + \
                (config.subtitle_stream_cmd if config.sub else '') + \
                config.video_title_metadata_cmd + \
                config.video_lang_metadata_cmd + \
                config.audio_title_metadata_cmd + \
                config.audio_lang_metadata_cmd + \
                (config.subtitle_title_metadata_cmd if config.sub else '') + \
                (config.subtitle_lang_metadata_cmd if config.sub else '') + \
                config.soft_burning_cmd + \
                config.video_codec_cmd.get('copy' if not config.logo else 'h264' + config.nvenc)   + \
                "-crf 18 -maxrate 8M -bufsize 32M -preset faster -tune animation -profile:v high10 -level:v 5.0 -pix_fmt yuv420p10le " + \
                config.audio_codec_cmd + \
                config.audio_bitrate_cmd + \
                config.audio_samplerate_cmd + \
                (config.subtitle_codec_cmd if config.sub else '') + \
                config.softsub_output_cmd
                #config.video_pixel_format_cmd + \
            
            loggingModule.write_to_log(f"Generated command: {cmd}")
            config.current_state = "Собираю софтсаб..."
            self.state_update(config.current_state)
            process = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                encoding='utf-8',
                                )
            self.frame_update(process)

    # Hardsubbing special
    def hardsubbering(self):
        loggingModule.write_to_log("Starting special hardsubbing...")
        if config.build_state == 3:
            cmd = config.init_cmd + \
                config.override_output_cmd + \
                config.video_input_cmd + \
                config.hard_burning_cmd + \
                config.video_codec_cmd.get(config.codec) + \
                config.video_bitrate_cmd + \
                config.video_pixel_format_cmd + \
                config.hardsub_output_cmd
            
            loggingModule.write_to_log(f"Generated command: {cmd}")
            config.current_state = "Собираю хардсаб для хардсабберов..."
            self.state_update(config.current_state)
            process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8'
                                )
            self.frame_update(process)

    # Hardsubbing
    def hardsub(self):
        loggingModule.write_to_log("Starting hardsubbing...")
        if config.build_state in [0, 2]:
            cmd = config.init_cmd + \
                config.override_output_cmd + \
                config.video_input_cmd + \
                config.audio_input_cmd + \
                config.video_stream_cmd + \
                config.audio_stream_cmd + \
                config.hard_burning_cmd + \
                config.audio_codec_cmd + \
                config.audio_bitrate_cmd + \
                config.audio_samplerate_cmd + \
                config.video_codec_cmd.get(config.codec) + \
                config.video_bitrate_cmd + \
                config.video_pixel_format_cmd + \
                config.hardsub_output_cmd

            loggingModule.write_to_log(f"Generated command: {cmd}")
            config.current_state = "Собираю хардсаб..."
            self.state_update(config.current_state)
            process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8'
                                )
            self.frame_update(process)

    def ffmpeg_analysis(self):
        loggingModule.write_to_log("Starting ffmpeg analysis...")
        cmd = 'ffprobe "' + config.raw_path +'"'
        loggingModule.write_to_log(f"Generated command: {cmd}")
        process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                shell=True,
                                encoding='utf-8'
                                )
        self.ffmpeg_analysis_decoding(process)
        
    def ffmpeg_analysis_decoding(self, proc):
        for line in proc.stdout:
            loggingModule.write_to_log(line)
            duration_match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', line)
            codec_match = re.search(r'Stream #Video:\s*(.*)', line)
            
            if duration_match:
                hrs, minutes, sec = map(float, duration_match.groups())
                duration = hrs * 3600 + minutes * 60 + sec
                config.total_frames = duration * 24000 / 1001.0
                self.time_upd.emit(config.total_frames)
            

    # Coding commands
    def run(self):
        try:
            loggingModule.write_to_log("Running ffmpeg thread...")
            temp = f'{chr(92)}:{chr(92)}{chr(92)}' 
            os.chdir(config.main_dir)
            if config.sub:
                sub_name = os.path.basename(config.sub_path)
                sanitized_name = str(sub_name).replace('[', '').replace(']', '')
                temp_dir = os.path.join(config.main_dir, 'tmp')
                
                os.makedirs(temp_dir, exist_ok=True)
                temp_sub_path = os.path.join(temp_dir, sanitized_name)
                shutil.copyfile(config.sub_path, temp_sub_path)
                
                config.subtitle_burning_cmd = f'{str(temp_sub_path).replace(chr(92), "/").replace(":/", temp)}'
            
            config.logo_burning_cmd = f'{str(config.logo_file).replace(chr(92), "/").replace(":/", temp)}'
            config.soft_burning_cmd = f'-vf "subtitles=\'{config.logo_burning_cmd}\'" ' if config.logo else ''
            burning_separator = '\', ' if config.sub and config.logo else ''
            config.hard_burning_cmd = ('-vf "' if config.sub or config.logo else '') + \
                                (f'subtitles=\'{config.logo_burning_cmd}' if config.logo else '') + \
                                burning_separator + \
                                (f'subtitles=\'{config.subtitle_burning_cmd}' if config.sub else '') + \
                                ('\'" ' if config.sub or config.logo else '')
            
            self.ffmpeg_analysis()
            self.softsub()
            self.hardsub()
            self.hardsubbering()     
            if (config.sub):
                os.remove(temp_sub_path)

        except Exception as e:
            loggingModule.write_to_log(f"Error occurred: {e}")
            input()
