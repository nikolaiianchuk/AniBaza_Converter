import pathlib
import wmi

from pathlib import Path
from modules.LoggingModule import LoggingModule

class Config:
    def __init__(self):
        # Main paths 
        self.main_paths = {
            'CWD'     : Path(pathlib.Path.cwd()),
            'config'  : Path(pathlib.Path.cwd(), 'configs/config.ini'),
            'version' : Path(pathlib.Path.cwd(), 'configs/current_version.ini'),
            'logs'    : Path(pathlib.Path.cwd(), 'logs'),
            'temp'    : Path(pathlib.Path.cwd(), 'tmp'),
            'softsub' : '',
            'hardsub' : Path(pathlib.Path.cwd(), 'HARDSUB'),
            'logo'    : Path(pathlib.Path.cwd(), 'logo/AniBaza_Logo16x9.ass')
        }

        # Main objects
        self.logging_module = LoggingModule()
        self.command_constructor = None
        self.updater_thread = None
        self.download_thread = None
        self.ffmpeg_thread = None

        # PC info
        self.computer = wmi.WMI()
        self.PC_info = {
            'OS Name'    : "",
            'OS Version' : "",
            'CPU'        : "",
            'RAM'        : "",
            'GPU'        : ""
        }

        # Application info
        self.app_info = {
            'title'          : '',
            'version_number' : '',
            'version_name'   : '',
            'author'         : '',
            'update_link'    : 'https://raw.githubusercontent.com/Miki-san/AniBaza_Converter/master/latest_version.json'
        }

        # Special settings
        self.dev_settings = {
            'dev_mode' : True,
            'logging'  : {
                'state'    : True,
                'max_logs' : 10
            }
        }

        # Rendering paths
        self.rendering_paths = {
            'raw'     : '',
            'audio'   : '',
            'sub'     : '',
            'softsub' : '',
            'hardsub' : ''
        }

        # Working variables
        self.build_states = {
            'Софт и хард'      : 0, 
            'Только софт'      : 1, 
            'Только хард'      : 2, 
            'Для хардсабберов' : 3,
            'Починить равку'   : 4
        }

        self.update_search = True
        self.total_duration_sec = 0
        self.total_frames = 0
        self.current_state = ''
        self.video_res = ''
        self.first_show = True

        # Build settings
        self.build_settings = {
            'episode_name'     : '',
            'build_state'      : 0,
            'logo'             : True,
            'softsub_settings' : {
                'nvenc'         : False,
                'video_tune'    : 'animation',
                'video_profile' : 'high10',
                'profile_level' : '4.1',
                'pixel_format'  : 'yuv420p10le'
            },
            'hardsub_settings' : {
                'nvenc'         : False,
                'video_tune'    : 'animation',
                'video_profile' : 'main10',
                'profile_level' : '4.1',
                'pixel_format'  : 'yuv420p10le'
            }
        }
    
    def start_log(self):
        self.logging_module.start_logging(
            self.dev_settings['logging']['state'], 
            self.main_paths['logs'], 
            self.dev_settings['logging']['max_logs']
        )
    
    def log(self, module, message):
        # Упрощённый метод для логирования.
        self.logging_module.write_to_log(module, message)
    
    def stop_log(self):
        self.logging_module.stop_logging()

