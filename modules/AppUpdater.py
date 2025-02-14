import sys
import traceback
import requests
import configs.config as config
from PyQt5.QtCore import pyqtSignal, QThread

class UpdaterThread(QThread):
    progress_signal = pyqtSignal(str, str, str)
    download_signal = pyqtSignal(str, str, str)
    error_signal    = pyqtSignal(Exception)

    def __init__(self, config):
        super().__init__()
        sys.excepthook = self.handle_exception
        self.config = config
    
    def run(self):
        try:
            self.config.log('AppUpdater', "Running updater...")
            latest_version, download_url, name = self.check_for_updates()
            if latest_version:
                self.progress_signal.emit(latest_version, download_url, name)
        except Exception as e:
            self.handle_exception(e)

    def check_for_updates(self):
        try:
            self.config.log('AppUpdater', "Checking for updates...")
            response = requests.get(self.config.app_info['update_link'], timeout=5)
            response.raise_for_status()
            data = response.json()
            self.config.log('AppUpdater', f"Data found: {data}")
            latest_version = data.get("version")
            download_url = data.get("url")
            name = data.get("name")

            if latest_version and download_url and name and latest_version > self.config.app_info['version_number']:
                return latest_version, download_url, name
        except Exception as e:
            self.handle_exception(e)
        return None, None, None

    def handle_exception(self, e):
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        self.config.log('AppUpdater', f"UpdaterThread Exception: {error_message}")
        self.error_signal.emit(e)
