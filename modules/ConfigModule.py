import configparser
import os

def load_parser(config, path):
    if os.path.exists(path):
        parser = configparser.ConfigParser()
        parser.read(path)
        config.log('ConfigModule', 'load_parser', f"Successfully loaded {path}")
        return parser
    else:
        config.log('ConfigModule', 'load_parser', f"Unable to load {path}")
        return None

def get_config_value(config, parser, section, option, conv):
    if conv == bool:
        config.log('ConfigModule', 'get_config_value', f"Loaded value: |{section}({option})|: {parser.getboolean(section, option)}")
        return parser.getboolean(section, option) if parser.has_option(section, option) else None
    elif conv == int:
        config.log('ConfigModule', 'get_config_value', f"Loaded value: |{section}({option})|: {parser.getint(section, option)}")
        return parser.getint(section, option) if parser.has_option(section, option) else None
    elif conv == str:
        config.log('ConfigModule', 'get_config_value', f"Loaded value: |{section}({option})|: {parser.get(section, option)}")
        return str(parser.get(section, option)) if parser.has_option(section, option) else None
    return None

def load_configs(config):
    from configs.config import DevSettings, BuildSettings, AppInfo
    from models.enums import BuildState, LogoState, NvencState

    parser = load_parser(config, config.main_paths.config)
    if parser:
        dev_mode = get_config_value(config, parser, 'dev settings', 'enableDevMode', bool)
        logging_enabled = get_config_value(config, parser, 'dev settings', 'enableLogging', bool)
        max_logs = get_config_value(config, parser, 'log settings', 'max_logs', int)
        config.dev_settings = DevSettings(
            dev_mode=dev_mode if dev_mode is not None else True,
            logging_enabled=logging_enabled if logging_enabled is not None else True,
            max_logs=max_logs if max_logs is not None else 10
        )

        logo_state = get_config_value(config, parser, 'main settings', 'logo_state', int)
        nvenc_state = get_config_value(config, parser, 'main settings', 'nvenc_state', int)
        build_state = get_config_value(config, parser, 'main settings', 'build_state', int)
        config.build_settings = BuildSettings(
            episode_name='',
            logo_state=LogoState(logo_state) if logo_state is not None else LogoState.LOGO_BOTH,
            nvenc_state=NvencState(nvenc_state) if nvenc_state is not None else NvencState.NVENC_BOTH,
            build_state=BuildState(build_state) if build_state is not None else BuildState.SOFT_AND_HARD,
            softsub_settings=config.build_settings.softsub_settings,
            hardsub_settings=config.build_settings.hardsub_settings
        )

        config.update_search = get_config_value(config, parser, 'main settings', 'update_search', bool)
        config.potato_PC = get_config_value(config, parser, 'main settings', 'potato_PC', bool)
        config.log('ConfigModule', 'load_configs', f"Settings loaded from file {config.main_paths.config}")

    parser = load_parser(config, config.main_paths.version)
    if parser:
        app_info_keys = {
            'title'          : ('app data', 'title', str),
            'version_number' : ('app data', 'version', str),
            'version_name'   : ('app data', 'versionname', str),
            'author'         : ('app data', 'author', str),
            'update_link'    : ('app data', 'update_url', str)
        }

        app_info_values = {}
        for key, (section, option, conv) in app_info_keys.items():
            value = get_config_value(config, parser, section, option, conv)
            if value is not None:
                app_info_values[key] = value
        config.app_info = AppInfo(**app_info_values)
        config.log('ConfigModule', 'load_configs', f"Settings loaded from file {config.main_paths.version}")

def save_config(config):
    parser = load_parser(config, config.main_paths.config)
    if parser:
        parser.set('main settings', 'logo_state', str(int(config.build_settings.logo_state)))
        parser.set('main settings', 'build_state', str(int(config.build_settings.build_state)))
        parser.set('main settings', 'nvenc_state', str(int(config.build_settings.nvenc_state)))
        parser.set('main settings', 'update_search', str(config.update_search))
        parser.set('main settings', 'potato_PC', str(config.potato_PC))

        with open(config.main_paths.config, 'w') as config_file:
            parser.write(config_file)
        # File automatically closed by 'with' statement
        config.log('ConfigModule', 'save_config', "Config saved.")
    else:
        config.log('ConfigModule', 'save_config', "Config file not found.")
