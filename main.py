# Lib import
import os
import pathlib
import sys
import ctypes
import configparser
import traceback
import config
import loggingModule

from pathlib import Path
from PyQt5 import QtWidgets
from mainWindow import MainWindow

# Admin check
def is_admin():
    # Проверяет, запущен ли скрипт с правами администратора
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False
    

# Main function
def main():
    try:
        if os.path.exists('config.ini'):
            config.configSettings = configparser.ConfigParser()
            config.configSettings.read('config.ini')
            config.enableDevMode = config.configSettings.getboolean('dev settings', 'enableDevMode')
            config.enableLogging = config.configSettings.getboolean('dev settings', 'enableLogging')
            config.max_logs = config.configSettings.getint('log settings', 'max_logs')
            
        loggingModule.start_logging(config.enableLogging)
        loggingModule.write_to_log('Starting application')
    
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        # Обработка стандартных ошибок
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        loggingModule.write_to_log(f"Handled exception: {error_message}")

    except BaseException as e:
        # Обработка критических ошибок (например, Ctrl+C)
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        if type(e) != SystemExit:
            loggingModule.write_to_log(f"Critical exception: {error_message}")
    
    finally:
        loggingModule.write_to_log("Closing application.")
        loggingModule.stop_logging()

# Standard code
if __name__ == "__main__":
    if not is_admin():
        # Перезапускаем скрипт с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()
