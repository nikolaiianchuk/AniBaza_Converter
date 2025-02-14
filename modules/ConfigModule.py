import configparser
import os

def load_parser(config, path):
    if os.path.exists(path):
        parser = configparser.ConfigParser()
        parser.read(path)
        config.log('ConfigModule', f"Successfully loaded {path}")
        return parser
    else:
        config.log('ConfigModule', f"Unable to load {path}")
        return None

def get_config_value(config, parser, section, option, conv):
    if conv == bool:
        config.log('ConfigModule', f"Loaded value {parser.getboolean(section, option)}")
        return parser.getboolean(section, option) if parser.has_option(section, option) else None
    elif conv == int:
        config.log('ConfigModule', f"Loaded value {parser.getint(section, option)}")
        return parser.getint(section, option) if parser.has_option(section, option) else None
    elif conv == str:
        config.log('ConfigModule', f"Loaded value {parser.get(section, option)}")
        return str(parser.get(section, option)) if parser.has_option(section, option) else None
    return None

def load_configs(config):
    parser = load_parser(config, config.main_paths['config'])
    if parser:
        config.dev_settings['dev_mode'] = get_config_value(config, parser, 'dev settings', 'enableDevMode', bool)
        config.dev_settings['logging'].update({
            'state': get_config_value(config, parser, 'dev settings', 'enableLogging', bool),
            'max_logs': get_config_value(config, parser, 'log settings', 'max_logs', int),
        })
        config.build_settings['logo'] = get_config_value(config, parser, 'main settings', 'logo', bool)
        config.build_settings['hardsub_settings'].update({
            'nvenc' : get_config_value(config, parser, 'main settings', 'hard_nvenc', bool),
        })
        config.build_settings['softsub_settings'].update({
            'nvenc' : get_config_value(config, parser, 'main settings', 'soft_nvenc', bool),
        })
        config.build_settings['build_state'] = get_config_value(config, parser, 'main settings', 'build_state', int)
        config.update_search = get_config_value(config, parser, 'main settings', 'update_search', bool)
        config.log('ConfigModule', f"Settings loaded from file {config.main_paths['config']}")
        
    parser = load_parser(config, config.main_paths['version'])
    if parser:
        app_info_keys = {
            'title'          : ('app data', 'title', str),
            'version_number' : ('app data', 'version', str),
            'version_name'   : ('app data', 'versionname', str),
            'author'         : ('app data', 'author', str),
            'update_link'    : ('app data', 'update_url', str)
        }
        
        for key, (section, option, conv) in app_info_keys.items():
            config.app_info[key] = get_config_value(config, parser, section, option, conv)
        config.log('ConfigModule', f"Settings loaded from file {config.main_paths['version']}")
    
def save_config(config):
    parser = load_parser(config, config.main_paths['config'])
    if parser:
        parser.set('main settings', 'logo', str(config.build_settings['logo']))
        parser.set('main settings', 'build_state', str(config.build_settings['build_state']))
        parser.set('main settings', 'nvenc', str(config.build_settings['hardsub_settings']['nvenc']))
        parser.set('main settings', 'hevc', str(config.build_settings['hardsub_settings']['hevc']))
        parser.set('main settings', 'update_search', str(config.update_search))
        with open(config.main_paths['config'], 'w') as config_file:
            parser.write(config_file)
        config_file.close()
        config.log('ConfigModule', "Config saved.")
    else:
        config.log('ConfigModule', "Config file not found.")
    