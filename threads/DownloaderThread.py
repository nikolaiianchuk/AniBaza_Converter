import os
import requests
import traceback
import configs.config as config
from PyQt5.QtCore import pyqtSignal, QThread

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal    = pyqtSignal(Exception)

    def __init__(self, config, url, installer_path):
        super().__init__()
        self.config = config
        self.url = url
        self.installer_path = installer_path
        self.cancel_download = False

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(self.installer_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    if self.cancel_download:  # Проверка флага отмены
                        break  # Прерываем скачивание, но не передаем "canceled" в CMD
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        self.progress_signal.emit(int(downloaded_size / total_size * 100))

            if not self.cancel_download:  # Если скачивание не отменено
                self.finished_signal.emit(self.installer_path)
            else:
                self.finished_signal.emit('')  # Пустой сигнал, указывающий на остановку без ошибок

        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e):
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        self.config.log('DownloaderThread', 'handle_exception', f"DownloadThread Error: {error_message}")
        self.error_signal.emit(e)

    def cancel(self):
        self.cancel_download = True  # Устанавливаем флаг отмены
        self.config.log('DownloaderThread', 'cancel', "DownloadThread: Download canceled.")
