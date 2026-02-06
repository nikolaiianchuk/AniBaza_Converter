"""Pure functional FFmpeg command builder.

Single responsibility: Convert FFmpegOptions → list[str] (ffmpeg arguments)
No state, no side effects, no file I/O.

All functions are pure: same input always produces same output.
"""

from models.ffmpeg_options import FFmpegOptions, FilterOptions
from models.encoding import EncodingDefaults


def build_ffmpeg_args(options: FFmpegOptions) -> list[str]:
    """Build complete FFmpeg argument list.

    Pure function: same input always produces same output.
    No side effects, no state, no I/O.

    Args:
        options: Complete encoding options

    Returns:
        List of ffmpeg arguments (safe for subprocess.Popen without shell=True)
    """
    args = []

    # Basic flags
    args.extend(['-y'])  # Override output

    # Inputs
    _add_inputs(args, options)

    # Stream mapping
    _add_stream_mapping(args, options)

    # Metadata
    _add_metadata(args, options)

    # Video filters (logo/subtitle burning)
    _add_filters(args, options.filters)

    # Video encoding
    _add_video_encoding(args, options)

    # Audio encoding
    if options.include_audio:
        _add_audio_encoding(args)

    # Subtitle handling (for softsub - copy subtitle stream)
    if options.include_subtitles and options.paths.sub:
        args.extend(['-c:s', options.codecs.subtitle_codec])

    # Output file
    output_path = options.paths.softsub if options.include_subtitles else options.paths.hardsub
    args.append(str(output_path))

    return args


def _add_inputs(args: list[str], options: FFmpegOptions) -> None:
    """Add input file arguments."""
    args.extend(['-i', str(options.paths.raw)])

    if options.include_audio and options.paths.audio:
        args.extend(['-i', str(options.paths.audio)])

    if options.include_subtitles and options.paths.sub:
        args.extend(['-i', str(options.paths.sub)])


def _add_stream_mapping(args: list[str], options: FFmpegOptions) -> None:
    """Add stream mapping arguments."""
    args.extend(['-map', f'{options.streams.video_input_index}:v:0'])

    if options.include_audio and options.streams.audio_input_index is not None:
        args.extend(['-map', f'{options.streams.audio_input_index}:a'])

    if options.include_subtitles and options.streams.subtitle_input_index is not None:
        args.extend(['-map', f'{options.streams.subtitle_input_index}:s'])

    args.extend(['-dn'])  # Discard data streams


def _add_metadata(args: list[str], options: FFmpegOptions) -> None:
    """Add metadata arguments."""
    args.extend([
        '-metadata:s:v:0', 'title=Original',
        '-metadata:s:v:0', 'language=jap'
    ])

    if options.include_audio:
        args.extend([
            '-metadata:s:a:0', 'title=AniBaza',
            '-metadata:s:a:0', 'language=rus'
        ])

    if options.include_subtitles and options.paths.sub:
        args.extend([
            '-metadata:s:s:0', 'title=Caption',
            '-metadata:s:s:0', 'language=rus'
        ])


def _add_filters(args: list[str], filters: FilterOptions) -> None:
    """Add video filter arguments."""
    filter_str = filters.to_filter_string()
    if filter_str:
        args.extend(['-vf', filter_str])


def _add_video_encoding(args: list[str], options: FFmpegOptions) -> None:
    """Add video encoding arguments."""
    # Codec
    args.extend(['-c:v', options.codecs.video_codec])

    # Rate control
    if options.use_nvenc:
        args.extend([
            '-cq', str(options.encoding.cq),
            '-qmin', str(options.encoding.qmin),
            '-qmax', str(options.encoding.qmax)
        ])
    else:
        args.extend(['-crf', str(options.encoding.crf)])

    # Bitrate
    args.extend(['-b:v', options.encoding.avg_bitrate])
    args.extend(['-maxrate', options.encoding.max_bitrate])
    args.extend(['-bufsize', options.encoding.buffer_size])

    # Preset
    args.extend(['-preset', options.preset])

    # Tune (skip if empty or using NVENC)
    if options.video.video_tune and not options.use_nvenc:
        args.extend(['-tune', options.video.video_tune])

    # Profile and format
    args.extend(['-profile:v', options.video.video_profile])
    args.extend(['-pix_fmt', options.video.pixel_format])


def _add_audio_encoding(args: list[str]) -> None:
    """Add audio encoding arguments."""
    args.extend(['-c:a', EncodingDefaults.AUDIO_CODEC])
    args.extend(['-b:a', EncodingDefaults.AUDIO_BITRATE])
    args.extend(['-ar', str(EncodingDefaults.AUDIO_SAMPLE_RATE)])
