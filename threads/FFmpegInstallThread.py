import os
import shutil
import subprocess
import traceback
from PyQt5.QtCore import pyqtSignal, QThread

class FFmpegInstallThread(QThread):
    progress_signal = pyqtSignal(str)  # Обновление статуса
    finished_signal = pyqtSignal(bool)  # Завершение (успех/отмена)
    error_signal    = pyqtSignal(Exception)  # Ошибки

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.cancel_install = False
        self.ffmpeg_path = "C:\\ffmpeg"

    def run(self):
        try:
            # Удаление старой версии FFmpeg
            if os.path.exists(self.ffmpeg_path):
                self.progress_signal.emit("Удаление старой версии FFmpeg...")
                try:
                    shutil.rmtree(self.ffmpeg_path)
                except Exception as e:
                    raise RuntimeError(f"Ошибка при удалении FFmpeg: {e}")

            self.progress_signal.emit("Установка новой версии FFmpeg...")

            # Запуск установки через батник
            self.process = subprocess.Popen(
                ["ffmpeginstall.bat"],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Чтение вывода процесса
            while self.process.poll() is None:
                if self.cancel_install:
                    self.process.terminate()
                    self.progress_signal.emit("Установка отменена.")
                    self.finished_signal.emit(False)
                    return

            self.progress_signal.emit("Установка завершена!")
            self.finished_signal.emit(True)

        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e):
        error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        self.config.log('FFmpegInstallThread', f"Error: {error_message}")
        self.error_signal.emit(e)

    def cancel(self):
        self.cancel_install = True
        if hasattr(self, "process") and self.process:
            self.process.terminate()
