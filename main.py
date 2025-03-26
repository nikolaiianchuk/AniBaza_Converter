# Lib import
import os
import sys
import ctypes
import modules.ConfigModule as ConfigModule
import traceback

from configs.config import Config
from PyQt5 import QtWidgets
from windows.mainWindow import MainWindow

# Admin check
def is_admin():
    # Проверяет, запущен ли скрипт с правами администратора
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False
    
def get_PC_info(config):
    hardware = config.computer
    #computer_info = hardware.Win32_ComputerSystem()[0]
    os_info = hardware.Win32_OperatingSystem()[0]
    proc_info = hardware.Win32_Processor()[0]
    gpu_info = hardware.Win32_VideoController()[0]

    os_name = os_info.Name.encode('utf-8').split(b'|')[0].decode('utf-8')
    os_version = ' '.join([os_info.Version, os_info.BuildNumber])
    system_ram = int(float(os_info.TotalVisibleMemorySize) // (1024 * 1024)) + 1  # KB to GB
    
    config.PC_info.update({
        'OS Name'    : f"{os_name}",
        'OS Version' : f"{os_version}",
        'CPU'        : f"{proc_info.Name}",
        'RAM'        : f"{system_ram}",
        'GPU'        : f"{gpu_info.Name}"
    })
    config.log('AppSystem', 'get_PC_info', f"PC info: {config.PC_info}")
    
def restore_config(config, config_path):
    if not os.path.exists(config.main_paths['config']):
        config.log('App System', "Config file not found.")
        config.log('App System', "Creating new config file.")
        default_config = """
                            [dev settings]
                            enabledevmode = True
                            enablelogging = True

                            [log settings]
                            max_logs = 10

                            [main settings]
                            logo_state = 0
                            nvenc_state = 0
                            build_state = 0
                            potato_PC = False
                            update_search = True
                        """
        with open(config_path, 'w', encoding='utf-8') as config_file:
            config_file.write(default_config)
        config.log('App System', "Config file restored.")

# Main function
def main():
    try:
        config = Config()
        config.start_log()
        config.log('App System', 'main', 'Starting application')
        get_PC_info(config)
        restore_config(config, config.main_paths['config'])
        ConfigModule.load_configs(config)
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        mainWindow = MainWindow(config)
        mainWindow.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        # Обработка стандартных ошибок
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        config.log('App System', 'main', f"Handled exception: {error_message}")
    except BaseException as e:
        # Обработка критических ошибок (например, Ctrl+C)
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        if type(e) != SystemExit:
            config.log('App System', 'main', f"Critical exception: {error_message}")
    finally:
        config.log('App System', 'main', "Closing application.")
        config.stop_log()

# Standard code
if __name__ == "__main__":
    if not is_admin():
        # Перезапускаем скрипт с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()
