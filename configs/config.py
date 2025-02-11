import pathlib

from pathlib import Path
from modules.LoggingModule import LoggingModule
# Main paths 
main_paths = {
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
logging_module = LoggingModule()
command_constructor = None
updater_thread = None
download_thread = None

# PC info
computer = None
PC_info = {
    'System' : '',
    'OS'     : '',
    'CPU'    : '',
    'GPU'    : '',
}

# Application info
app_info = {
    'title'          : '',
    'version_number' : '',
    'version_name'   : '',
    'author'         : '',
    'update_link'    : 'https://raw.githubusercontent.com/Miki-san/AniBaza_Converter/master/latest_version.json'
}

# Special settings
dev_settings = {
    'dev_mode' : True,
    'logging'  : {
        'state'    : True,
        'max_logs' : 10
    }
}

# Rendering paths
rendering_paths = {
    'raw'     : '',
    'audio'   : '',
    'sub'     : '',
    'softsub' : '',
    'hardsub' : ''
}

# Working variables
build_states = {
    'Софт и хард'      : 0, 
    'Только софт'      : 1, 
    'Только хард'      : 2, 
    'Для хардсабберов' : 3,
    'Починить равку'   : 4
}

update_search = True
total_duration_sec = 0
total_frames = 0
current_state = ''
video_res = ''

# Build settings
build_settings = {
    'episode_name'     : '',
    'build_state'      : 0,
    'logo'             : True,
    'softsub_settings' : {
        'video_profile' : 'high10',
        'profile_level' : '5.0',
        'pixel_format'  : 'yuv420p10le'
    },
    'hardsub_settings' : {
        'nvenc'         : False,
        'hevc'          : False,
        'video_tune'    : 'animation',
        'video_profile' : 'main10',
        'profile_level' : '5.0',
        'pixel_format'  : 'yuv420p10le'
    }
}
