import sys
import traceback
import requests
import configs.config as config
from PyQt5.QtCore import pyqtSignal, QThread

class UpdaterThread(QThread):
    progress_signal = pyqtSignal(str, str, str)
    download_signal = pyqtSignal(str, str, str)
    error_signal    = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()
        sys.excepthook = self.handle_exception
    
    def run(self):
        try:
            config.logging_module.write_to_log('AppUpdater', "Running updater...")
            latest_version, download_url, name = self.check_for_updates()
            if latest_version:
                self.progress_signal.emit(latest_version, download_url, name)
        except Exception as e:
            self.handle_exception(e)

    def check_for_updates(self):
        try:
            config.logging_module.write_to_log('AppUpdater', "Checking for updates...")
            response = requests.get(config.app_info['update_link'], timeout=5)
            response.raise_for_status()
            data = response.json()
            config.logging_module.write_to_log('AppUpdater', f"Data found: {data}")
            latest_version = data.get("version")
            download_url = data.get("url")
            name = data.get("name")

            if latest_version and download_url and name and latest_version > config.app_info['version_number']:
                return latest_version, download_url, name
        except Exception as e:
            self.handle_exception(e)
        return None, None, None

    def handle_exception(self, e):
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        config.logging_module.write_to_log('AppUpdater', f"UpdaterThread Exception: {error_message}")
        self.error_signal.emit(e)
