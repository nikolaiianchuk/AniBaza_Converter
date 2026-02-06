import os
import shutil

from pathlib import Path
from models.encoding import SubtitleInfo, EncodingDefaults

class FFmpegConstructor:
    def __init__(self, config):
        self.config = config
        # Mutable state for subtitle processing (used by build_*_args methods)
        # TODO: Phase 5 - remove when deleting build_*_args methods
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


    def remove_temp_sub(self):
        if os.path.exists(self.sub.temp_path):
            os.remove(self.sub.temp_path)
            self.sub = SubtitleInfo()  # Reset to empty instance
