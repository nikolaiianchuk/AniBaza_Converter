import os
import shutil

from pathlib import Path
from models.encoding import SubtitleInfo, EncodingDefaults

class FFmpegConstructor:
    def __init__(self, config):
        self.config = config
        self.softsub_ffmpeg_commands = {
            'init'                 : 'ffmpeg',
            'override output'      : '-y',
            'video input'          : '-i "{RAW_PATH_INPUT}"',
            'audio input'          : '-i "{SOUND_PATH_INPUT}"',
            'subtitle input'       : '-i "{SUB_PATH_INPUT}"',
            'video map'            : '-map 0:v:0',
            'audio map'            : '-map 1:a',
            'subtitle map'         : '-map 2:s',
            'garbage deleter'      : '-dn',
            'video metadata'       : '-metadata:s:v:0 title="Original" -metadata:s:v:0 language=jap',
            'audio metadata'       : '-metadata:s:a:0 title="AniBaza" -metadata:s:a:0 language=rus',
            'subtitle metadata'    : '-metadata:s:s:0 title="Caption" -metadata:s:s:0 language=rus',
            'logo burning'         : '-vf "subtitles=\'{ESCAPED_LOGO_PATH}\'"',
            'video codec'          : '-c:v {CODEC}',
            'video bitrate'        : '-b:v {BITRATE}',
            'video CRF'            : '-crf {CRF_RATE}',
            'video CQ'             : '-cq {CQ} -qmin {QMIN} -qmax {QMAX}',
            'video max bitrate'    : '-maxrate {MAX}',
            'video max bufsize'    : '-bufsize {BUFFER}',
            'render preset'        : '-preset {RENDER_PRESET}',
            'video tune'           : '-tune {TUNE}',
            'video profile'        : '-profile:v {VIDEO_PROFILE}',
            'profile level'        : '-level:v {PROFILE_LEVEL}',
            'video pixel format'   : '-pix_fmt {PIXEL_FORMAT}',
            'audio codec'          : '-c:a aac',
            'audio bitrate'        : '-b:a 320K',
            'audio discretization' : '-ar 48000',
            'subtitle codec'       : '-c:s copy',
            'video output'         : '"{OUTPUT_FILE_PATH}"'
        }
        self.hardsub_ffmpeg_commands = {
            'init'                 : 'ffmpeg',
            'override output'      : '-y',
            'video input'          : '-i "{RAW_PATH_INPUT}"',
            'audio input'          : '-i "{SOUND_PATH_INPUT}"',
            'video map'            : '-map 0:v:0',
            'audio map'            : '-map 1:a',
            'garbage deleter'      : '-dn',
            '1burning'             : '-vf "subtitles=\'{LOGO_OR_SUB_PATH}\'"',
            '2burning'             : '-vf "subtitles=\'{ESCAPED_LOGO_PATH}\', subtitles=\'{ESCAPED_SUB_PATH}\'"',
            'video codec'          : '-c:v hevc{NVENC}',
            'video bitrate'        : '-b:v {BITRATE}',
            'video CRF'            : '-crf {CRF_RATE}',
            'video CQ'             : '-cq {CQ} -qmin {QMIN} -qmax {QMAX}',
            'video max bitrate'    : '-maxrate {MAX}',
            'video max bufsize'    : '-bufsize {BUFFER}',
            'render preset'        : '-preset {RENDER_PRESET}',
            'video tune'           : '-tune {TUNE}',
            'video profile'        : '-profile:v {VIDEO_PROFILE}',
            'profile level'        : '-level:v {PROFILE_LEVEL}',
            'video pixel format'   : '-pix_fmt {PIXEL_FORMAT}',
            'audio codec'          : '-c:a aac',
            'audio bitrate'        : '-b:a 320K',
            'audio discretization' : '-ar 48000',
            'video output'         : '"{OUTPUT_FILE_PATH}"'
        }
        self.sub = SubtitleInfo()

        # Path separator for Windows paths in ffmpeg filters
        # Use raw string instead of chr(92) obfuscation
        self.separator = r'\:\\'
        self.escaped_logo_path = ''

    def sub_escaper(self, path):
        name = os.path.basename(path)
        sanitized_name = str(name).replace('[', '').replace(']', '')
        os.makedirs(self.config.main_paths.temp, exist_ok=True)
        temp_path = os.path.join(self.config.main_paths.temp, sanitized_name)
        shutil.copyfile(path, temp_path)
        escaped_path = f"{str(temp_path).replace(chr(92), '/').replace(':/', self.separator)}"

        self.sub = SubtitleInfo(
            name=name,
            sanitized_name=sanitized_name,
            path=path,
            temp_path=temp_path,
            escaped_path=escaped_path,
            exists=True
        )

    def logo_escaper(self):
        self.escaped_logo_path = f"{str(self.config.main_paths.logo).replace(chr(92), '/').replace(':/', self.separator)}"

    def build_soft_args(self, raw_path='', sound_path='', sub_path=None,
                        output_path='', nvenc=False, crf_rate=None, cqmin=None,
                        cq=None, cqmax=None, max_bitrate='', max_buffer='', video_profile='main',
                        profile_level='4.2', pixel_format='yuv420p', preset='faster', tune='animation',
                        include_logo=True, potato_mode=False):
        """Build ffmpeg arguments as a list (no shell=True needed).

        This is the new, safer way to build commands. Returns a list of arguments
        that can be passed directly to subprocess.Popen without shell=True.

        Args are the same as build_soft_command(), but returns list instead of string.
        """
        if crf_rate is None:
            crf_rate = str(EncodingDefaults.CRF_1080P)
        if cq is None:
            cq = str(EncodingDefaults.CRF_1080P + EncodingDefaults.CQ_OFFSET)
        if cqmin is None:
            cqmin = str(int(cq) - EncodingDefaults.QMIN_OFFSET)
        if cqmax is None:
            cqmax = str(int(cq) + EncodingDefaults.QMAX_OFFSET)

        # Prepare subtitle and logo paths (without os.chdir)
        if sub_path and os.path.exists(sub_path):
            self.sub_escaper(sub_path)
        self.logo_escaper()

        args = []

        # Basic options
        args.extend(['-y'])  # Override output

        # Input files
        args.extend(['-i', raw_path])
        args.extend(['-i', sound_path])
        if self.sub.exists:
            args.extend(['-i', sub_path])

        # Stream mapping
        args.extend(['-map', '0:v:0'])
        args.extend(['-map', '1:a'])
        if self.sub.exists:
            args.extend(['-map', '2:s'])

        # Metadata
        args.extend(['-dn'])  # Garbage deleter
        args.extend(['-metadata:s:v:0', 'title=Original', '-metadata:s:v:0', 'language=jap'])
        args.extend(['-metadata:s:a:0', 'title=AniBaza', '-metadata:s:a:0', 'language=rus'])
        if self.sub.exists:
            args.extend(['-metadata:s:s:0', 'title=Caption', '-metadata:s:s:0', 'language=rus'])

        # Logo burning filter
        if include_logo:
            args.extend(['-vf', f"subtitles='{self.escaped_logo_path}'"])

        # Video codec
        codec = 'h264_nvenc' if nvenc else 'libx264'
        args.extend(['-c:v', codec])

        # Rate control
        if nvenc:
            args.extend(['-cq', cq, '-qmin', cqmin, '-qmax', cqmax])
        else:
            args.extend(['-crf', crf_rate])

        args.extend(['-b:v', EncodingDefaults.VIDEO_BITRATE])
        args.extend(['-maxrate', max_bitrate])
        args.extend(['-bufsize', max_buffer])
        args.extend(['-preset', preset])

        if not potato_mode:
            args.extend(['-tune', tune])

        args.extend(['-profile:v', video_profile])
        args.extend(['-pix_fmt', pixel_format])

        # Audio settings
        args.extend(['-c:a', EncodingDefaults.AUDIO_CODEC])
        args.extend(['-b:a', EncodingDefaults.AUDIO_BITRATE])
        args.extend(['-ar', str(EncodingDefaults.AUDIO_SAMPLE_RATE)])

        # Subtitle codec
        if self.sub.exists:
            args.extend(['-c:s', 'copy'])

        # Output file
        args.append(output_path)

        return args

    def build_hard_args(self, raw_path='', sound_path='', sub_path=None,
                        output_path='', nvenc=False, crf_rate=None, cqmin=None,
                        cq=None, cqmax=None, max_bitrate='', max_buffer='', preset='faster',
                        tune='animation', video_profile='main', profile_level='4.2',
                        pixel_format='yuv420p', include_logo=True, potato_mode=False):
        """Build hardsub ffmpeg arguments as a list (no shell=True needed).

        Returns a list of arguments for hardsub encoding.
        """
        if crf_rate is None:
            crf_rate = str(EncodingDefaults.CRF_1080P)
        if cq is None:
            cq = str(EncodingDefaults.CRF_1080P + EncodingDefaults.CQ_OFFSET)
        if cqmin is None:
            cqmin = str(int(cq) - EncodingDefaults.QMIN_OFFSET)
        if cqmax is None:
            cqmax = str(int(cq) + EncodingDefaults.QMAX_OFFSET)

        # Prepare subtitle and logo paths
        if sub_path and os.path.exists(sub_path):
            self.sub_escaper(sub_path)
        self.logo_escaper()

        args = []

        # Basic options
        args.extend(['-y'])  # Override output

        # Input files
        args.extend(['-i', raw_path])
        if sound_path:
            args.extend(['-i', sound_path])

        # Stream mapping
        args.extend(['-map', '0:v:0'])
        if sound_path:
            args.extend(['-map', '1:a'])

        args.extend(['-dn'])  # Garbage deleter

        # Burning filters (logo and/or subtitle)
        if include_logo and self.sub.exists:
            # Both logo and subtitle (2burning)
            args.extend(['-vf', f"subtitles='{self.escaped_logo_path}', subtitles='{self.sub.escaped_path}'"])
        elif include_logo or self.sub.exists:
            # Just one (1burning)
            path_to_burn = self.escaped_logo_path if include_logo else self.sub.escaped_path
            args.extend(['-vf', f"subtitles='{path_to_burn}'"])

        # Video codec
        codec = 'hevc_nvenc' if nvenc else 'hevc'
        args.extend(['-c:v', codec])

        # Rate control
        if nvenc:
            args.extend(['-cq', cq, '-qmin', cqmin, '-qmax', cqmax])
        else:
            args.extend(['-crf', crf_rate])

        args.extend(['-b:v', EncodingDefaults.VIDEO_BITRATE])
        args.extend(['-maxrate', max_bitrate])
        args.extend(['-bufsize', max_buffer])
        args.extend(['-preset', preset])

        if not potato_mode:
            args.extend(['-tune', tune])

        args.extend(['-profile:v', video_profile])
        args.extend(['-pix_fmt', pixel_format])

        # Audio settings (only if sound_path provided)
        if sound_path:
            args.extend(['-c:a', EncodingDefaults.AUDIO_CODEC])
            args.extend(['-b:a', EncodingDefaults.AUDIO_BITRATE])
            args.extend(['-ar', str(EncodingDefaults.AUDIO_SAMPLE_RATE)])

        # Output file
        args.append(output_path)

        return args

    def build_soft_command(self, raw_path='', sound_path='', sub_path=None,
                            output_path='', nvenc=False, crf_rate='18', cqmin='17',
                            cq='18', cqmax='25', max_bitrate='', max_buffer='', video_profile='main',
                            profile_level='4.2', pixel_format='yuv420p', preset='faster', tune='animation',
                            include_logo=True, potato_mode=False):

        os.chdir(self.config.main_paths.cwd)

        if sub_path and os.path.exists(sub_path):
            self.sub_escaper(sub_path)
        self.logo_escaper()
        command_parts = [self.softsub_ffmpeg_commands['init']]

        cmds = ['override output',
                'video input',
                'audio input',
                'subtitle input' if self.sub.exists else '',
                'video map',
                'audio map',
                'subtitle map' if self.sub.exists else '',
                'garbage deleter',
                'video metadata',
                'audio metadata',
                'subtitle metadata' if self.sub.exists else '',
                'logo burning' if include_logo else '',
                'video codec',
                'video CQ' if nvenc else 'video CRF',
                'video max bitrate' ,
                'video max bufsize' ,
                'render preset' ,
                'video tune' if not potato_mode else '',
                'video profile',
                'video pixel format',
                'audio codec',
                'audio bitrate',
                'audio discretization',
                'subtitle codec' if self.sub.exists else '',
                'video output'
            ]#'profile level',

        for command in cmds:
            if command:
                command_parts.append(self.softsub_ffmpeg_commands[command])

        command = " ".join(command_parts)
        str_out = command.format(
            RAW_PATH_INPUT    = raw_path,
            SOUND_PATH_INPUT  = sound_path,
            ESCAPED_LOGO_PATH = self.escaped_logo_path,
            CODEC             = 'libx264' if not nvenc else 'h264_nvenc',
            BITRATE           = '3500k',
            CRF_RATE          = crf_rate,
            QMIN              = cqmin,
            CQ                = cq,
            QMAX              = cqmax,
            MAX               = max_bitrate,
            BUFFER            = max_buffer,
            RENDER_PRESET     = preset,
            TUNE              = tune,
            VIDEO_PROFILE     = video_profile,
            PROFILE_LEVEL     = profile_level,
            PIXEL_FORMAT      = pixel_format,
            SUB_PATH_INPUT    = sub_path,
            OUTPUT_FILE_PATH  = output_path
        )
        self.config.logging_module.write_to_log('FFmpegConstructor', 'build_soft_command', f'FFmpeg constructor softsub: {str_out}')
        return str_out

    def build_hard_command(self, raw_path='', sound_path='', sub_path=None,
                            output_path='', nvenc=False, crf_rate='18', cqmin='17',
                            cq='18', cqmax='25', max_bitrate='', max_buffer='', preset='faster', tune='animation', video_profile='main',
                            profile_level='4.2', pixel_format='yuv420p',
                            include_logo=True, potato_mode=False):

        os.chdir(self.config.main_paths.cwd)

        if sub_path and os.path.exists(sub_path):
            self.sub_escaper(sub_path)
        self.logo_escaper()
        command_parts = [self.hardsub_ffmpeg_commands['init']]
        burning = ''
        if include_logo and self.sub.exists:
            burning = '2burning'
        elif include_logo or self.sub.exists:
            burning = '1burning'
        else:
            burning = ''
        cmds = ['override output',
                'video input',
                'audio input' if sound_path else '',
                'video map',
                'audio map' if sound_path else '',
                'garbage deleter',
                f"{burning}",
                'video codec',
                'video CQ' if nvenc else 'video CRF',
                'video max bitrate',
                'video max bufsize',
                'render preset',
                'video tune' if not potato_mode else '',
                'video profile',
                'video pixel format',
                'audio codec' if sound_path else '',
                'audio bitrate' if sound_path else '',
                'audio discretization' if sound_path else '',
                'video output'
            ]#'profile level',

        for command in cmds:
            if command:
                command_parts.append(self.hardsub_ffmpeg_commands[command])

        command = " ".join(command_parts)
        str_out = command.format(
            RAW_PATH_INPUT    = raw_path,
            SOUND_PATH_INPUT  = sound_path,
            ESCAPED_LOGO_PATH = self.escaped_logo_path,
            ESCAPED_SUB_PATH  = self.sub.escaped_path,
            LOGO_OR_SUB_PATH  = self.escaped_logo_path if include_logo else self.sub.escaped_path,
            NVENC             = '_nvenc' if nvenc else '',
            BITRATE           = '3500k',
            CRF_RATE          = crf_rate,
            QMIN              = cqmin,
            CQ                = cq,
            QMAX              = cqmax,
            MAX               = max_bitrate,
            BUFFER            = max_buffer,
            RENDER_PRESET     = preset,
            TUNE              = tune,
            VIDEO_PROFILE     = video_profile,
            PROFILE_LEVEL     = profile_level,
            PIXEL_FORMAT      = pixel_format,
            OUTPUT_FILE_PATH  = output_path
        )
        self.config.logging_module.write_to_log('FFmpegConstructor', 'build_hard_command', f'FFmpeg constructor hardsub: {str_out}')
        return str_out

    def remove_temp_sub(self):
        if os.path.exists(self.sub.temp_path):
            os.remove(self.sub.temp_path)
            self.sub = SubtitleInfo()  # Reset to empty instance
