import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import traceback
import webbrowser
import requests
import modules.ConfigModule as ConfigModule

from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow, QProgressDialog, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from UI.normUI2 import Ui_MainWindow
from windows.FAQWindow import FAQWindow
from threads.RenderThread import ThreadClassRender
from modules.AppUpdater import UpdaterThread
from threads.DownloaderThread import DownloadThread

# Main window class
class MainWindow(QMainWindow):
    close_progress_signal = pyqtSignal()
    # Main window init
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.finish_message = False
        self.threadMain = None
        self.faqWindow = None
        self.first_show = True
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  
        sys.excepthook = self.handle_exception
        self.set_buttons()
        self.set_checkboxes()
        self.set_textboxes()
        self.set_comboboxes()
        self.base = [
            self.ui.render_start_button,
            self.ui.render_mode_box,
            self.ui.soft_nvenc_check,
            self.ui.hard_nvenc_check,
            self.ui.logo_check,
            self.ui.app_ffmpeg_update_check,
            self.ui.raw_path_open_button,
            self.ui.softsub_path_open_button,
            self.ui.audio_path_open_button,
            self.ui.subtitle_path_open_button,
            self.ui.episode_line,
            self.ui.raw_path_editline,
            self.ui.audio_path_editline,
            self.ui.subtitle_path_editline,
            self.ui.softsub_path_editline,
            self.ui.config_save_button
        ]
        self.ui.render_stop_button.hide()
        self.ui.app_version_label.setText(f"Version {self.config.app_info['version_number']} ({self.config.app_info['version_name']}) by {self.config.app_info['author']}")
        self.setWindowTitle(self.config.app_info['title'])
    
    def showEvent(self, event):
        super().showEvent(event)
        if self.first_show:  # Проверяем, был ли уже вызван showEvent
            self.first_show = False  # Сбрасываем флаг, чтобы не выполнять повторно
            if self.config.update_search:
                self.update_ffmpeg()
                self.start_updater()
            else:
                self.config.log('mainWindow', "Updater disabled.")
    
    def get_installed_ffmpeg_version(self):
        try:
            process = subprocess.Popen(
                "ffmpeg -version", 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True, 
                encoding='utf-8', 
                errors='replace'
            )
            output, _ = process.communicate()
            match = re.search(r'ffmpeg\s+version\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)', output)
            self.config.log('mainWindow', f"Installed FFmpeg version: {match.group(1) if match else None}")
            return match.group(1) if match else None
        except Exception as e:
            self.config.log('mainWindow', f"Ошибка при получении версии FFmpeg: {e}")
            return None
    
    def get_latest_ffmpeg_version(self):
        try:
            url = "https://www.ffmpeg.org/download.html"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            match = re.search(r'([0-9]+\.[0-9]+(?:\.[0-9]+)?) was released', response.text)
            self.config.log('mainWindow', f"Latest FFmpeg version: {match.group(1) if match else None}")
            return match.group(1) if match else None
        except Exception as e:
            self.config.log('mainWindow', f"Ошибка при получении последней версии FFmpeg: {e}")
            return None
    
    def remove_old_ffmpeg_and_install(self):
        ffmpeg_path = "C:\\ffmpeg"
        if os.path.exists(ffmpeg_path):
            self.config.log('mainWindow', "Удаляю старую версию FFmpeg...")
            try:
                shutil.rmtree(ffmpeg_path)
                self.config.log('mainWindow', "Старая версия FFmpeg удалена.")
            except Exception as e:
                self.config.log('mainWindow', f"Ошибка при удалении папки: {e}")
        else:
            self.config.log('mainWindow', "Папка FFmpeg не найдена, установка новой версии...")
        
        os.system(Path(pathlib.Path.cwd(), "ffmpeginstall.bat"))
    
    def update_ffmpeg(self):
        installed_version = self.get_installed_ffmpeg_version()
        latest_version = self.get_latest_ffmpeg_version()
        
        if installed_version and latest_version:
            if installed_version == latest_version:
                self.config.log('mainWindow', "У вас установлена актуальная версия FFmpeg.")
            else:
                self.config.log('mainWindow', "Необходимо обновление FFmpeg!")
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("FFmpegUpdater")
                msg_box.setText(f"Доступна новая версия FFmpeg: {installed_version} -> {latest_version}!")
                msg_box.setInformativeText("Вы хотите скачать и установить новую версию?")
                msg_box.setStandardButtons(
                    QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes) | 
                    QMessageBox.StandardButtons(QMessageBox.StandardButton.No)
                )
                result = msg_box.exec()
                self.config.log('mainWindow', f"User chose to update: {result == QMessageBox.StandardButton.Yes}")
                if result == QMessageBox.StandardButton.Yes:
                    self.remove_old_ffmpeg_and_install()
                else:
                    self.config.log('mainWindow', "Обновление FFmpeg было отложено!")
        else:
            self.config.log('mainWindow', "Не удалось определить версии FFmpeg.")

    def start_updater(self):
        self.config.log('mainWindow', "Starting updater...")
        self.config.updater_thread = UpdaterThread(self.config)
        self.config.updater_thread.progress_signal.connect(self.show_update_dialog)
        self.config.updater_thread.error_signal.connect(self.show_error_dialog)
        self.config.updater_thread.start()
    
    def show_error_dialog(self, ex):
        self.config.log('mainWindow', 'Showing error dialog...')
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("ABCUpdater Error")
        msg_box.setText("Произошла ошибка поиска или установки обновления! Повторите попытку обновления позже.")
        msg_box.setInformativeText(f"ERROR: [{ex}]")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        msg_box.exec()

    def show_update_dialog(self, latest_version, download_url, name):
        self.config.log('mainWindow', 'Showing App update dialog...')
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("ABCUpdater")
        msg_box.setText(f"Доступна новая версия AniBaza Converter: {self.config.app_info['version_number']} -> {latest_version}!")
        msg_box.setInformativeText("Вы хотите скачать и установить новую версию?")
        msg_box.setStandardButtons(
            QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes) | 
            QMessageBox.StandardButtons(QMessageBox.StandardButton.No)
        )
        result = msg_box.exec()
        
        self.config.log('mainWindow', f"User chose to update: {result == QMessageBox.StandardButton.Yes}")
        if result == QMessageBox.StandardButton.Yes:
            self.start_download(download_url, latest_version)

    def start_download(self, url, version):
        self.config.log('mainWindow', 'Starting download...')
        self.progress = QProgressDialog(f"Скачиваю обновление...\n{self.config.app_info['version_number']} -> {version}", "Отмена", 0, 100, self)
        self.progress.setWindowTitle("ABCUpdater")
        self.progress.setWindowFlags(self.progress.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint) # type: ignore
        self.progress.setMinimumWidth(350)
        self.progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.cancel_button = QPushButton('Cancel', self.progress)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.progress.setCancelButton(self.cancel_button)
        self.progress.show()
        self.close_progress_signal.connect(self.progress.close) # type: ignore
        temp_dir = os.getenv("TEMP")
        if temp_dir is None:
            raise EnvironmentError("TEMP environment variable is not set")
        installer_path = os.path.join(temp_dir, "update_installer.exe")

        def update_progress(value):
            self.progress.setValue(value)
            if self.progress.wasCanceled():  # Проверка на отмену скачивания
                self.config.log('mainWindow', "Download canceled.")
                self.cancel_download()  # Останавливаем скачивание, без передачи 'canceled'

        def download_finished(path):
            self.config.log('mainWindow', f"Download complete: {path}")
            if path:  # Если путь не пустой
                self.close_progress_signal.emit()  # Закрываем прогресс-диалог
                self.config.log('mainWindow', "Starting installer...")
                subprocess.Popen([path], shell=True)
                self.close()

        self.config.download_thread = DownloadThread(self.config, url, installer_path)
        self.config.download_thread.progress_signal.connect(update_progress)
        self.config.download_thread.finished_signal.connect(download_finished)
        self.config.download_thread.error_signal.connect(self.show_error_dialog)
        self.config.download_thread.start()

    def cancel_download(self):
        if hasattr(self.config, 'download_thread'):
            self.config.log('mainWindow', "Download canceled.")
            self.config.download_thread.cancel()  # type: ignore # Останавливаем скачивание
            self.close_progress_signal.emit()  # Закрываем прогресс-диалог

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.config.log('mainWindow', f"Handled exception: {error_message}")
        self.ui.app_state_label.setText("ОШИБКА! См. лог файлы.")

    def universal_update(self, setting_path, value, log_message, type):
        keys = setting_path.split('.')
        setting = self.config
        for key in keys[:-1]:
            if isinstance(setting, dict):
                setting = setting.setdefault(key, {})  
            else:
                setting = getattr(setting, key, None)
        last_key = keys[-1]
        if isinstance(setting, dict):
            setting[last_key] = value
        else:
            setattr(setting, last_key, value)
            
        if type == "checkbox":
            self.config.log('mainWindow', log_message.format(VALUE="enabled" if value else "disabled"))
        elif type == "textbox":
            self.config.log('mainWindow', log_message.format(VALUE=value))


    # Softsub path updater
    def update_soft_path(self):
        self.config.main_paths['softsub'] = self.ui.softsub_path_editline.text()
        if '[AniBaza]' in self.config.main_paths['softsub']:
            self.config.build_settings['episode_name'] = self.config.main_paths['softsub'].split('/')[-1]
            self.config.build_settings['episode_name'] = self.config.build_settings['episode_name'].replace(
                self.config.build_settings['episode_name'][self.config.build_settings['episode_name'].rfind('[')+1 : 
                self.config.build_settings['episode_name'].rfind(']')],''
            ) if '[' in self.config.build_settings['episode_name'] else self.config.build_settings['episode_name']
            self.ui.episode_line.setText(self.config.build_settings['episode_name'])
        else:
            self.config.log('mainWindow', f"Softsub base path updated to: {self.config.main_paths['softsub']}")
        self.update_render_paths()

    # Episode name updater
    def update_episode(self):
        self.config.build_settings['episode_name'] = self.ui.episode_line.text()
        self.config.log('mainWindow', f"Episode name updated to: {self.config.build_settings['episode_name']}")
        self.update_render_paths()
        
    def update_render_paths(self):
        self.config.rendering_paths['softsub'] = f"{self.config.main_paths['softsub']}/{self.config.build_settings['episode_name']}.mkv"
        self.config.log('mainWindow', f"Softsub render path updated to: {self.config.rendering_paths['softsub']}")
        self.config.rendering_paths['hardsub'] = f"{self.config.main_paths['hardsub']}/{self.config.build_settings['episode_name']}.mp4"
        self.config.log('mainWindow', f"Hardsub render path updated to: {self.config.rendering_paths['hardsub']}")
        self.config.log('mainWindow', 'Render paths updated!')

    def lock_mode(self):
        ui_for_disable = (self.ui.audio_path_editline, self.ui.audio_path_open_button, self.ui.softsub_path_editline, self.ui.softsub_path_open_button)
        for ui in ui_for_disable:
            ui.setDisabled(self.config.build_settings['build_state'] == 3)

    # Mode updater
    def update_mode(self):
        self.config.build_settings['build_state'] = self.config.build_states.get(self.ui.render_mode_box.currentText())
        self.lock_mode()
        self.config.log('mainWindow', f"Mode updated to: {self.config.build_settings['build_state']}")

    # FAQ window opener
    def open_faq(self):
        if self.faqWindow is None:
            self.faqWindow = FAQWindow(self.config)
        self.faqWindow.show()
        self.config.log('mainWindow', "FAQ window opened.")

    # Buttons definition
    def set_buttons(self):
        buttons = {
            self.ui.hardsub_folder_open_button: self.open_hardsub,
            self.ui.render_stop_button: self.proc_kill,
            self.ui.render_start_button: self.ffmpeg_thread,
            self.ui.softsub_path_open_button: self.soft_folder_path,
            self.ui.audio_path_open_button: self.sound_folder_path,
            self.ui.raw_path_open_button: self.raw_folder_path,
            self.ui.subtitle_path_open_button: self.sub_folder_path,
            self.ui.anibaza_site_open_button: lambda: webbrowser.open('https://www.youtube.com/watch?v=jQ6gPyYNgPo'),
            self.ui.rickroll_button: lambda: webbrowser.open('https://www.youtube.com/watch?v=o-YBDTqX_ZU'),
            self.ui.FAQ_open_button: self.open_faq,
            self.ui.config_save_button: lambda: ConfigModule.save_config(self.config)
        }

        for button, handler in buttons.items():
            button.clicked.connect(handler)
        
        self.config.log('mainWindow', "Buttons set.")

    # Checkboxes definition
    def set_checkboxes(self):
        #self.ui.log_mode_enable.setEnabled(self.config.dev_settings['dev_mode'])
        
        checkboxes = {
            self.ui.dev_mode_enable: (lambda: self.universal_update(
                'dev_settings.dev_mode', 
                self.ui.dev_mode_enable.isChecked(), 
                "Dev mode {VALUE}.",
                "checkbox"
            )),
            self.ui.logo_check: (lambda: self.universal_update(
                'build_settings.logo', 
                self.ui.logo_check.isChecked(), 
                "Logo {VALUE}.",
                "checkbox"
            )),
            self.ui.app_ffmpeg_update_check: (lambda: self.universal_update(
                'update_search', 
                self.ui.app_ffmpeg_update_check.isChecked(),
                "Update search {VALUE}.",
                "checkbox"
            )),
            self.ui.soft_nvenc_check: (lambda: self.universal_update(
                'build_settings.softsub_settings.nvenc', 
                self.ui.soft_nvenc_check.isChecked(),
                "Softsub NVENC {VALUE}.",
                "checkbox"
            )),
            self.ui.hard_nvenc_check: (lambda: self.universal_update(
                'build_settings.hardsub_settings.nvenc', 
                self.ui.hard_nvenc_check.isChecked(),
                "Hardsub NVENC {VALUE}.",
                "checkbox"
            ))
        }

        for checkbox, handler in checkboxes.items():
            checkbox.stateChanged.connect(handler)
            
        self.ui.log_mode_enable.setChecked(self.config.dev_settings['logging']['state'])
        self.ui.logo_check.setChecked(self.config.build_settings['logo'])
        self.ui.soft_nvenc_check.setChecked(self.config.build_settings['hardsub_settings']['nvenc'])
        self.ui.hard_nvenc_check.setChecked(self.config.build_settings['softsub_settings']['nvenc'])
        self.ui.app_ffmpeg_update_check.setChecked(self.config.update_search)

        self.config.log('mainWindow', "Checkboxes set.")

    # Textboxes definition
    def set_textboxes(self):
        paths = {
            self.ui.audio_path_editline: (lambda: self.universal_update(
                'rendering_paths.audio', 
                self.ui.audio_path_editline.text(),
                "Audio path updated to: {VALUE}.",
                "textbox"
            )),
            self.ui.raw_path_editline: (lambda: self.universal_update(
                'rendering_paths.raw', 
                self.ui.raw_path_editline.text(),
                "Raw path updated to: {VALUE}.",
                "textbox"
            )),
            self.ui.softsub_path_editline: self.update_soft_path,
            self.ui.subtitle_path_editline: (lambda: self.universal_update(
                'rendering_paths.sub', 
                self.ui.subtitle_path_editline.text(),
                "Subtitle path updated to: {VALUE}.",
                "textbox"
            )),
            self.ui.episode_line: self.update_episode,
        }

        for textbox, handler in paths.items():
            textbox.textChanged.connect(handler)

        self.config.log('mainWindow', "Textboxes set.")

    # Comboboxes definition
    def set_comboboxes(self):
        comboboxes = {
            self.ui.render_mode_box: self.update_mode,
        }

        for combobox, handler in comboboxes.items():
            combobox.currentIndexChanged.connect(handler)

        self.ui.render_mode_box.setCurrentIndex(self.config.build_settings['build_state'])
        self.config.log('mainWindow', "Comboboxes set.")

    # Open hardsub directory
    def open_hardsub(self):
        if os.path.exists(self.config.main_paths['hardsub']):
            os.startfile(self.config.main_paths['hardsub'])
        else:
            self.coding_error('hardsub_folder')
        self.config.log('mainWindow', "Hardsub folder opened.")

    # Softsub saving path
    def soft_folder_path(self):
        self.config.main_paths['softsub'] = QtWidgets.QFileDialog.getExistingDirectory(self, 'Куда пихать софт?')
        self.ui.softsub_path_editline.setText(self.config.main_paths['softsub'])
        self.config.log('mainWindow', f"Softsub path updated to: {self.config.main_paths['softsub']}")

    # Raw video choose
    def raw_folder_path(self):
        self.config.main_paths['raw'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать равку?", "",
                                                            "ALL (*.mkv *.mp4 *.avi)")
        self.ui.raw_path_editline.setText(self.config.main_paths['raw'])
        self.config.log('mainWindow', f"Raw path updated to: {self.config.main_paths['raw']}")

    # Sound file choose
    def sound_folder_path(self):
        self.config.main_paths['audio'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать звук?", "",
                                                            "All(*.wav *.flac *.aac *.m4a *.mka)")
        self.ui.audio_path_editline.setText(self.config.main_paths['audio'])
        self.config.log('mainWindow', f"Sound path updated to: {self.config.main_paths['audio']}")

    # Subtitle choose
    def sub_folder_path(self):
        self.config.rendering_paths['sub'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать надписи?", "",
                                                            "Хуй (*.ass *.srt)")
        self.ui.subtitle_path_editline.setText(self.config.rendering_paths['sub'])
        self.config.log('mainWindow', f"Subtitle path updated to: {self.config.rendering_paths['sub']}")

    # Coding Errors
    def coding_error(self, error_type):
        error_messages = {
            'softsub': ("Выбери правильно куда сохранять софтсаб!", self.soft_folder_path),
            'subtitle': ("Выбери существующий путь к файлу субтитров!", self.sub_folder_path),
            'raw': ("Выбери существующий путь к равке!", self.raw_folder_path),
            'sound': ("Выбери существующий путь к дорожке звука!", self.sound_folder_path),
            'name': ("Напиши корректное имя релиза!", None),
            'hardsub_folder': ("НАХУЯ ТЫ ПАПКИ УДАЛЯЕШЬ?!", None),
            'stop': ("Зачем остановил?!", None)
        }

        self.ui.app_state_label.setText("МЕГАПЛОХ!")
        msg = QMessageBox()
        msg.setWindowTitle("Чел ты...")
        msg.setIcon(QMessageBox.Warning)

        if error_type in error_messages:
            message, action = error_messages[error_type]
            msg.setText(message)
            if action:
                msg.setStandardButtons(QMessageBox.Open)
                msg.buttonClicked.connect(action)
            else:
                msg.setStandardButtons(QMessageBox.Ok)
            if error_type == 'hardsub_folder':
                os.mkdir('HARDSUB')

        msg.exec_()
        self.config.log('mainWindow', f"Coding error: {error_type}")

    # Progress updater
    def frame_update(self, frame):
        self.config.log('mainWindow', f"Frame updated: {frame}")
        self.ui.render_progress_bar.setValue(int(frame))

    # Set progressbar maximum
    def time_update(self, time):
        self.config.log('mainWindow', f"Time updated: {time}")
        self.ui.render_progress_bar.setMaximum(math.ceil(time))

    # State updater
    def state_update(self, state):
        self.config.log('mainWindow', f"State updated: {state}")
        self.ui.app_state_label.setText(state)
        
    def elapsed_time_update(self, time):
        self.config.log('mainWindow', f"Elapsed time updated: {time}")
        self.ui.elapsed_time_label.setText(time)

    # Thread start with ffmpeg
    def ffmpeg_thread(self):
        if not os.path.exists(self.config.main_paths['hardsub']):
            self.coding_error('hardsub_folder')
            return

        self.ui.app_state_label.setText("Работаю....(наверное)")
        self.ui.render_progress_bar.setValue(0)

        if not os.path.exists(self.config.rendering_paths['raw']):
            self.coding_error('raw')
            return

        if not os.path.exists(self.config.rendering_paths['audio']) and self.config.build_settings['build_state'] in [0, 1, 2]:
            self.coding_error('sound')
            return

        if not os.path.exists(self.config.rendering_paths['sub']) and self.config.rendering_paths['sub'].replace(' ', '') != '' and self.config.rendering_paths['sub'] != None:
            self.coding_error('subtitle')
            return

        if not os.path.exists(self.config.main_paths['softsub']) and self.config.build_settings['build_state'] in [0, 1, 4]:
            self.coding_error('softsub')
            return

        if not re.match(r'^[a-zA-Z0-9 _.\-\[\]]+$', self.config.build_settings['episode_name']):
            self.coding_error('name')
            return

        self.config.log('mainWindow', "Starting ffmpeg...")
        self.threadMain = ThreadClassRender(self.config)
        self.threadMain.finished.connect(self.finished)
        self.threadMain.frame_upd.connect(self.frame_update)
        self.threadMain.time_upd.connect(self.time_update)
        self.threadMain.state_upd.connect(self.state_update)
        self.threadMain.elapsed_time_upd.connect(self.elapsed_time_update)
        self.locker(True)
        self.ui.render_start_button.hide()
        self.ui.render_stop_button.show()
        self.threadMain.start()

    # Kill ffmpeg process
    def proc_kill(self):
        os.chdir(self.config.main_paths['CWD'])
        self.finish_message = True
        subprocess.run('taskkill /f /im ffmpeg.exe', shell=True)
        self.config.log('mainWindow', "Killed ffmpeg process")

    # After coding
    def finished(self):
        os.chdir(self.config.main_paths['CWD'])
        self.ui.render_start_button.show()
        self.ui.render_stop_button.hide()

        if self.finish_message:
            self.coding_error('stop')
            self.finish_message = False
        else:
            self.config.current_state = "Все готово!"
            self.state_update(self.config.current_state)
            self.elapsed_time_update('')
            QApplication.beep()
        self.ui.elapsed_time_label.setText('')
        self.ui.render_progress_bar.setValue(0)
        self.locker(False)
        self.config.log('mainWindow', "Coding finished")

    # Blocking strings and buttons while coding
    def locker(self, lock_value):
        for item in self.base:
            item.setDisabled(lock_value)
        
        tabs = [self.ui.folder_tab, self.ui.settings_tab, self.ui.whats_new_tab, self.ui.dev_tab]
        for tab in tabs:
            tab.setDisabled(lock_value)

        self.ui.render_stop_button.setDisabled(not lock_value)
        self.lock_mode()
        self.config.log('mainWindow', "UI locked")
