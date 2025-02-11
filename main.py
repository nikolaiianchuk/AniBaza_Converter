# Lib import
import os
import sys
import ctypes
import modules.ConfigModule as ConfigModule
import traceback
import configs.config as config 
import wmi

from PyQt5 import QtWidgets
from windows.mainWindow import MainWindow
from modules.LoggingModule import LoggingModule

# Admin check
def is_admin():
    # Проверяет, запущен ли скрипт с правами администратора
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False
    
def restore_config(config_path):
    if not os.path.exists(config.main_paths['config']):
        config.logging_module.write_to_log('App System', "Config file not found.")
        config.logging_module.write_to_log('App System', "Creating new config file.")
        default_config = """
                            [dev settings]
                            enabledevmode = True
                            enablelogging = True

                            [log settings]
                            max_logs = 10

                            [main settings]
                            logo = True
                            nvenc = False
                            hevc = True
                            build_state = 0
                            update_search = True
                        """
        with open(config_path, 'w', encoding='utf-8') as config_file:
            config_file.write(default_config)
        config.logging_module.write_to_log('App System', "Config file restored.")

def get_PC_info():
    config.computer = wmi.WMI()
    hardware = config.computer
    config.PC_info.update({
        'System': hardware.Win32_ComputerSystem()[0],
        'OS'    : hardware.Win32_OperatingSystem()[0],
        'CPU'   : hardware.Win32_Processor()[0],
        'GPU'   : hardware.Win32_VideoController()[0]
    })
    #config.logging_module.write_to_log('AppSystem', f"PC info: {config.PC_info}")

def start_logging():
    config.logging_module.start_logging(
        config.dev_settings['logging']['state'], 
        config.main_paths['logs'], 
        config.dev_settings['logging']['max_logs']
    )
    config.logging_module.write_to_log('App System', 'Starting application')
    
# Main function
def main():
    try:
        start_logging()
        get_PC_info()
        restore_config(config.main_paths['config'])
        ConfigModule.load_configs()
    
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        mainWindow = MainWindow()
        mainWindow.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        # Обработка стандартных ошибок
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        config.logging_module.write_to_log('App System', f"Handled exception: {error_message}")
    except BaseException as e:
        # Обработка критических ошибок (например, Ctrl+C)
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        if type(e) != SystemExit:
            config.logging_module.write_to_log('App System', f"Critical exception: {error_message}")
    finally:
        config.logging_module.write_to_log('App System', "Closing application.")
        config.logging_module.stop_logging()

# Standard code
if __name__ == "__main__":
    if not is_admin():
        # Перезапускаем скрипт с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()
