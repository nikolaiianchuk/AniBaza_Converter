import pathlib

from pathlib import Path

appTitle = ''
appVersion = ''
appVersionName = ''
appAuthor = ''

hardsub_dir = Path(pathlib.Path.cwd(), 'HARDSUB')
logs_dir = Path(pathlib.Path.cwd(), 'logs')
logo_file = Path(pathlib.Path.cwd(), 'logo/AniBaza_Logo16x9.ass')
main_dir = Path(pathlib.Path.cwd())
build_states = {'Софт и хард' : 0, 'Только софт' : 1, 'Только хард' : 2, 'Для хардсабберов' : 3}
build_state = 0
configSettings = None
enableDevMode = True
enableLogging = True
log_file = None
log_filename = None
log_flag = False
max_logs = 10
total_frames = 0
current_state = ''

#other ffmpeg commands
init_cmd = 'ffmpeg '
override_output_cmd = '-y '
output_title_metadata_cmd = ''
nvencFlag = False
hevcFlag = False
nvenc = ''
hevc = 'h264'
codec = 'h264'
sub = True
logo = True
softsub_output_cmd = ''
hardsub_output_cmd = ''
episode_line = ''
soft_path = ''

#video ffmpeg commands
video_bitrate_cmd = ''
video_input_cmd = ''
video_stream_cmd = '-map 0:v '
video_title_metadata_cmd = '-metadata:s:v:0 title="Original" '
video_lang_metadata_cmd = '-metadata:s:v:0 language=jap '
video_codec_cmd = {'copy' : '-c:v copy ', 'h264_nvenc' : '-c:v h264_nvenc ', 'h264' : '-c:v libx264 ', 'h265' : '-c:v libx265 ', 'h265_nvenc' : '-c:v hevc_nvenc '}
video_pixel_format_cmd = '-pix_fmt yuv420p '
video_bitrate = '1000'
raw_path = ''

#audio ffmpeg commands
audio_input_cmd = ''
audio_stream_cmd = '-map 1:a '
audio_title_metadata_cmd = '-metadata:s:a:0 title="AniBaza" '
audio_lang_metadata_cmd = '-metadata:s:a:0 language=rus '
audio_codec_cmd = '-c:a aac '
audio_bitrate_cmd = '-b:a 320K '
audio_samplerate_cmd = '-ar 48000 '
sound_path = ''

#subtitle ffmpeg commands
subtitle_input_cmd = ''
subtitle_stream_cmd = '-map 2:s '
subtitle_lang_metadata_cmd = '-metadata:s:s:0 language=rus '
subtitle_title_metadata_cmd = '-metadata:s:s:0 title="Caption" '
subtitle_codec_cmd = '-c:s copy '
subtitle_burning_cmd = ''
sub_name = ''
sub_path = ''
logo_burning_cmd = ''
soft_burning_cmd = ''
hard_burning_cmd = ''