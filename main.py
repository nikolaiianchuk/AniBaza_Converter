# Lib import
import os
import sys
import ctypes
import modules.ConfigModule as ConfigModule
import traceback

from configs.config import Config, PCInfo, Paths
from modules.GlobalExceptionHandler import get_global_handler
from modules.process_runner import SubprocessRunner
from PyQt5 import QtWidgets
from windows.mainWindow import MainWindow

# Admin check (Windows-only)
def is_admin():
    # Проверяет, запущен ли скрипт с правами администратора
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False

def restore_config(config: Config):
    if os.path.exists(config.main_paths.config):
        return

    config.log('App System', 'restore_config', "Config file not found.")
    config.log('App System', 'restore_config', "Creating new config file.")
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
    with open(config.main_paths.config, 'w', encoding='utf-8') as config_file:
        config_file.write(default_config)
    config.log('App System', 'restore_config', "Config file restored.")

# Main function
def main():
    pc_info = PCInfo()

    if pc_info.is_windows() and not is_admin():
        # Перезапускаем скрипт с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return

    cwd = ''
    # determine if application is a script file or frozen exe, from the PyInstaller doc
    if getattr(sys, 'frozen', False):
        cwd = os.path.dirname(sys.executable)
    elif __file__:
        cwd = os.path.dirname(__file__)

    config = Config(Paths(cwd), pc_info)

    try:
        config.start_log()

        # Phase 5: Install global exception handler
        exception_handler = get_global_handler()
        exception_handler.install()

        # Register callback to log exceptions
        def log_exception(exc_type, exc_value, exc_traceback):
            if exc_type != KeyboardInterrupt:
                error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                config.log('App System', 'exception_handler', f"Uncaught exception: {error_message}")

        exception_handler.register_callback(log_exception)

        config.log('App System', 'main', f"CWD: {cwd}")
        config.log('App System', 'main', 'Starting application')
        config.log('App System', 'get_PC_info', f"PC info: {pc_info}")
        config.log('App System', 'ffmpeg', f"Version: {config.ffmpeg.version}, Supports NVENC: {config.ffmpeg.nvenc}")

        # Create ProcessRunner for safe subprocess execution
        runner = None
        if config.ffmpeg.installed and config.ffmpeg.path:
            runner = SubprocessRunner(
                ffmpeg_path=config.ffmpeg.path,
                ffprobe_path=config.ffmpeg.path.parent / 'ffprobe' if config.ffmpeg.path else None,
                cwd=config.main_paths.cwd
            )
            config.log('App System', 'main', f'ProcessRunner initialized with ffmpeg: {config.ffmpeg.path}')
        else:
            config.log('App System', 'main', 'ProcessRunner not available (ffmpeg not found)')

        restore_config(config)
        ConfigModule.load_configs(config)
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        mainWindow = MainWindow(config, runner=runner)
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
    main()
