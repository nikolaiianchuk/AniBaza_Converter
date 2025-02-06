import math
import os
import re
import subprocess
import sys
import traceback
import webbrowser
import modules.ConfigModule as ConfigModule
import configs.config as config

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
    def __init__(self):
        super().__init__()
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
            self.ui.startButton,
            self.ui.modeBox,
            self.ui.nvencCheck,
            self.ui.codec,
            self.ui.logo_check,
            self.ui.update_check,
            self.ui.rawButton,
            self.ui.softButton,
            self.ui.soundButton,
            self.ui.subButton,
            self.ui.episodeLine,
            self.ui.rawPath,
            self.ui.soundPath,
            self.ui.subPath,
            self.ui.softPath,
            self.ui.settingsSaving
        ]
        self.ui.stopButton.hide()
        self.ui.versionLabel.setText(f"Version {config.app_info['version_number']} ({config.app_info['version_name']}) by {config.app_info['author']}")
        self.setWindowTitle(config.app_info['title'])
        
    
    def showEvent(self, event):
        super().showEvent(event)
        if self.first_show:  # Проверяем, был ли уже вызван showEvent
            self.first_show = False  # Сбрасываем флаг, чтобы не выполнять повторно
            if config.update_search:
                self.start_updater()
            else:
                config.logging_module.write_to_log('mainWindow', "Updater disabled.")

    def start_updater(self):
        config.logging_module.write_to_log('mainWindow', "Starting updater...")
        config.updater_thread = UpdaterThread()
        config.updater_thread.progress_signal.connect(self.show_update_dialog)
        config.updater_thread.error_signal.connect(self.show_error_dialog)
        config.updater_thread.start()
        
    def show_error_dialog(self, ex):
        config.logging_module.write_to_log('mainWindow', 'Showing error dialog...')
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("ABCUpdater Error")
        msg_box.setText("Произошла ошибка поиска или установки обновления! Повторите попытку обновления позже.")
        msg_box.setInformativeText(f"ERROR: [{ex}]")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        msg_box.exec()

    def show_update_dialog(self, latest_version, download_url, name):
        config.logging_module.write_to_log('mainWindow', 'Showing update dialog...')
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("ABCUpdater")
        msg_box.setText(f"Доступна новая версия: {config.app_info['version_number']} -> {latest_version}!")
        msg_box.setInformativeText("Вы хотите скачать и установить новую версию?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg_box.exec()
        
        config.logging_module.write_to_log('mainWindow', f"User chose to update: {result == QMessageBox.StandardButton.Yes}")
        if result == QMessageBox.StandardButton.Yes:
            self.start_download(download_url, latest_version)

    def start_download(self, url, version):
        config.logging_module.write_to_log('mainWindow', 'Starting download...')
        self.progress = QProgressDialog(f"Скачиваю обновление...\n{config.app_info['version_number']} -> {version}", "Отмена", 0, 100, self)
        self.progress.setWindowTitle("ABCUpdater")
        self.progress.setWindowFlags(self.progress.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.progress.setMinimumWidth(350)
        self.progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.cancel_button = QPushButton('Cancel', self.progress)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.progress.setCancelButton(self.cancel_button)
        self.progress.show()
        self.close_progress_signal.connect(self.progress.close)
        installer_path = os.path.join(os.getenv("TEMP"), "update_installer.exe")

        def update_progress(value):
            self.progress.setValue(value)
            if self.progress.wasCanceled():  # Проверка на отмену скачивания
                config.logging_module.write_to_log('mainWindow', "Download canceled.")
                self.cancel_download()  # Останавливаем скачивание, без передачи 'canceled'

        def download_finished(path):
            config.logging_module.write_to_log('mainWindow', f"Download complete: {path}")
            if path:  # Если путь не пустой
                self.close_progress_signal.emit()  # Закрываем прогресс-диалог
                config.logging_module.write_to_log('mainWindow', "Starting installer...")
                subprocess.Popen([path], shell=True)
                self.close()

        config.download_thread = DownloadThread(url, installer_path)
        config.download_thread.progress_signal.connect(update_progress)
        config.download_thread.finished_signal.connect(download_finished)
        config.download_thread.error_signal.connect(self.show_error_dialog)
        config.download_thread.start()

    def cancel_download(self):
        if hasattr(config, 'download_thread'):
            config.logging_module.write_to_log('mainWindow', "Download canceled.")
            config.download_thread.cancel()  # Останавливаем скачивание
            self.close_progress_signal.emit()  # Закрываем прогресс-диалог

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        config.logging_module.write_to_log('mainWindow', f"Handled exception: {error_message}")
        self.ui.stateLabel.setText("ОШИБКА! См. лог файлы.")

    # Dev mode updater
    def update_dev_mode(self):
        config.dev_settings['dev_mode'] = self.ui.enableDevMode.isChecked()
        self.ui.enableLogging.setEnabled(config.dev_settings['dev_mode'])
        config.logging_module.write_to_log('mainWindow', f"Dev mode {'enabled' if config.dev_settings['dev_mode'] else 'disabled'}.")

    # Logo updater
    def update_logo(self):
        config.build_settings['logo'] = self.ui.logo_check.isChecked()
        config.logging_module.write_to_log('mainWindow', f"Logo {'enabled' if config.build_settings['logo'] else 'disabled'}.")

    # NVENC updater
    def update_nvenc(self):
        config.build_settings['hardsub_settings']['nvenc'] = self.ui.nvencCheck.isChecked()
        config.logging_module.write_to_log('mainWindow', f"NVENC {'enabled' if config.build_settings['hardsub_settings']['nvenc'] else 'disabled'}.")
        
    # Codec updater
    def update_codec(self):
        config.build_settings['hardsub_settings']['hevc'] = self.ui.codec.isChecked()
        config.logging_module.write_to_log('mainWindow', f"H265 {'enabled' if config.build_settings['hardsub_settings']['hevc'] else 'disabled'}.")

    def update_check(self):
        config.update_search = self.ui.update_check.isChecked()
        config.logging_module.write_to_log('mainWindow', f"Update search {'enabled' if config.update_search else 'disabled'}.")

    # Raw path updater
    def update_raw_path(self):
        config.rendering_paths['raw'] = self.ui.rawPath.text()
        config.logging_module.write_to_log('mainWindow', f"Raw path updated to: {config.rendering_paths['raw']}")

    # Sound path updater
    def update_sound_path(self):
        config.rendering_paths['audio'] = self.ui.soundPath.text()
        config.logging_module.write_to_log('mainWindow', f"Sound path updated to: {config.rendering_paths['audio']}")

    # Subtitle path updater
    def update_sub_path(self):
        config.rendering_paths['sub'] = self.ui.subPath.text()
        config.logging_module.write_to_log('mainWindow', f"Subtitle path updated to: {config.rendering_paths['sub']}")

    # Softsub path updater
    def update_soft_path(self):
        config.main_paths['softsub'] = self.ui.softPath.text()
        if '[AniBaza]' in config.main_paths['softsub']:
            config.build_settings['episode_name'] = config.main_paths['softsub'].split('/')[-1]
            config.build_settings['episode_name'] = config.build_settings['episode_name'].replace(
                config.build_settings['episode_name'][config.build_settings['episode_name'].rfind('[')+1 : 
                config.build_settings['episode_name'].rfind(']')],''
            ) if '[' in config.build_settings['episode_name'] else config.build_settings['episode_name']
            self.ui.episodeLine.setText(config.build_settings['episode_name'])
            self.update_render_paths()
        else:
            config.logging_module.write_to_log('mainWindow', f"Softsub base path updated to: {config.main_paths['softsub']}")

    # Episode name updater
    def update_episode(self):
        config.build_settings['episode_name'] = self.ui.episodeLine.text()
        config.logging_module.write_to_log('mainWindow', f"Episode name updated to: {config.build_settings['episode_name']}")
        self.update_render_paths()
        
    def update_render_paths(self):
        config.rendering_paths['softsub'] = f"{config.main_paths['softsub']}/{config.build_settings['episode_name']}.mkv"
        config.logging_module.write_to_log('mainWindow', f"Softsub render path updated to: {config.rendering_paths['softsub']}")
        config.rendering_paths['hardsub'] = f"{config.main_paths['hardsub']}/{config.build_settings['episode_name']}.mp4"
        config.logging_module.write_to_log('mainWindow', f"Hardsub render path updated to: {config.rendering_paths['hardsub']}")
        config.logging_module.write_to_log('mainWindow', 'Render paths updated!')

    # Mode updater
    def update_mode(self):
        config.build_settings['build_state'] = config.build_states.get(self.ui.modeBox.currentText())
        config.logging_module.write_to_log('mainWindow', f"Mode updated to: {config.build_settings['build_state']}")

    # FAQ window opener
    def open_faq(self):
        if self.faqWindow is None:
            self.faqWindow = FAQWindow()
        self.faqWindow.show()
        config.logging_module.write_to_log('mainWindow', "FAQ window opened.")

    # Buttons definition
    def set_buttons(self):
        buttons = {
            self.ui.hardfolderButton: self.open_hardsub,
            self.ui.stopButton: self.proc_kill,
            self.ui.startButton: self.ffmpeg_thread,
            self.ui.softButton: self.soft_folder_path,
            self.ui.soundButton: self.sound_folder_path,
            self.ui.rawButton: self.raw_folder_path,
            self.ui.subButton: self.sub_folder_path,
            self.ui.siteButton: lambda: webbrowser.open('https://www.youtube.com/watch?v=jQ6gPyYNgPo'),
            self.ui.pushButton_rick: lambda: webbrowser.open('https://www.youtube.com/watch?v=o-YBDTqX_ZU'),
            self.ui.faqButton: self.open_faq,
            self.ui.settingsSaving: lambda: ConfigModule.save_config()
        }

        for button, handler in buttons.items():
            button.clicked.connect(handler)
        
        config.logging_module.write_to_log('mainWindow', "Buttons set.")

    # Checkboxes definition
    def set_checkboxes(self):
        checkboxes = {
            self.ui.enableDevMode: self.update_dev_mode,
            self.ui.logo_check: self.update_logo,
            self.ui.nvencCheck: self.update_nvenc,
            self.ui.codec: self.update_codec,
            self.ui.update_check: self.update_check
        }

        for checkbox, handler in checkboxes.items():
            checkbox.stateChanged.connect(handler)
            
        self.ui.enableLogging.setChecked(config.dev_settings['logging']['state'])
        self.ui.logo_check.setChecked(config.build_settings['logo'])
        self.ui.nvencCheck.setChecked(config.build_settings['hardsub_settings']['nvenc'])
        self.ui.codec.setChecked(config.build_settings['hardsub_settings']['hevc'])
        self.ui.update_check.setChecked(config.update_search)

        config.logging_module.write_to_log('mainWindow', "Checkboxes set.")

    # Textboxes definition
    def set_textboxes(self):
        paths = {
            self.ui.soundPath: self.update_sound_path,
            self.ui.rawPath: self.update_raw_path,
            self.ui.softPath: self.update_soft_path,
            self.ui.subPath: self.update_sub_path,
            self.ui.episodeLine: self.update_episode,
        }

        for textbox, handler in paths.items():
            textbox.textChanged.connect(handler)

        config.logging_module.write_to_log('mainWindow', "Textboxes set.")

    # Comboboxes definition
    def set_comboboxes(self):
        comboboxes = {
            self.ui.modeBox: self.update_mode,
        }

        for combobox, handler in comboboxes.items():
            combobox.currentIndexChanged.connect(handler)

        self.ui.modeBox.setCurrentIndex(config.build_settings['build_state'])
        config.logging_module.write_to_log('mainWindow', "Comboboxes set.")

    # Open hardsub directory
    def open_hardsub(self):
        if os.path.exists(config.main_paths['hardsub']):
            os.startfile(config.main_paths['hardsub'])
        else:
            self.coding_error('hardsub_folder')
        config.logging_module.write_to_log('mainWindow', "Hardsub folder opened.")

    # Softsub saving path
    def soft_folder_path(self):
        config.main_paths['softsub'] = QtWidgets.QFileDialog.getExistingDirectory(self, 'Куда пихать софт?')
        self.ui.softPath.setText(config.main_paths['softsub'])
        config.logging_module.write_to_log('mainWindow', f"Softsub path updated to: {config.main_paths['softsub']}")

    # Raw video choose
    def raw_folder_path(self):
        config.main_paths['raw'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать равку?", "",
                                                            "ALL (*.mkv *.mp4 *.avi)")
        self.ui.rawPath.setText(config.main_paths['raw'])
        config.logging_module.write_to_log('mainWindow', f"Raw path updated to: {config.main_paths['raw']}")

    # Sound file choose
    def sound_folder_path(self):
        config.main_paths['audio'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать звук?", "",
                                                            "All(*.wav *.flac *.aac *.m4a *.mka)")
        self.ui.soundPath.setText(config.main_paths['audio'])
        config.logging_module.write_to_log('mainWindow', f"Sound path updated to: {config.main_paths['audio']}")

    # Subtitle choose
    def sub_folder_path(self):
        config.rendering_paths['sub'], _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать надписи?", "",
                                                            "Хуй (*.ass *.srt)")
        self.ui.subPath.setText(config.rendering_paths['sub'])
        config.logging_module.write_to_log('mainWindow', f"Subtitle path updated to: {config.rendering_paths['sub']}")

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

        self.ui.stateLabel.setText("МЕГАПЛОХ!")
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
        config.logging_module.write_to_log('mainWindow', f"Coding error: {error_type}")

    # Progress updater
    def frame_update(self, frame):
        config.logging_module.write_to_log('mainWindow', f"Frame updated: {frame}")
        self.ui.progressBar.setValue(int(frame))

    # Set progressbar maximum
    def time_update(self, time):
        config.logging_module.write_to_log('mainWindow', f"Time updated: {time}")
        self.ui.progressBar.setMaximum(math.ceil(time))

    # State updater
    def state_update(self, state):
        config.logging_module.write_to_log('mainWindow', f"State updated: {state}")
        self.ui.stateLabel.setText(state)
        
    def elapsed_time_update(self, time):
        config.logging_module.write_to_log('mainWindow', f"Elapsed time updated: {time}")
        self.ui.elapsed_time.setText(time)

    # Thread start with ffmpeg
    def ffmpeg_thread(self):
        if not os.path.exists(config.main_paths['hardsub']):
            self.coding_error('hardsub_folder')
            return

        self.ui.stateLabel.setText("Работаю....(наверное)")
        self.ui.progressBar.setValue(0)

        if not os.path.exists(config.rendering_paths['raw']):
            self.coding_error('raw')
            return

        if not os.path.exists(config.rendering_paths['audio']) and config.build_settings['build_state'] != 3:
            self.coding_error('sound')
            return

        if not os.path.exists(config.rendering_paths['sub']) and (config.rendering_paths['sub'].replace(' ', '') != '' and config.rendering_paths['sub'] != None):
            self.coding_error('subtitle')
            return

        if not (os.path.exists(config.main_paths['softsub']) and config.build_settings['build_state'] in [0, 1]) and config.build_settings['build_state'] not in [2, 3]:
            self.coding_error('softsub')
            return

        if not re.match(r'^[a-zA-Z0-9 _.\-\[\]]+$', config.build_settings['episode_name']):
            self.coding_error('name')
            return

        config.logging_module.write_to_log('mainWindow', "Starting ffmpeg...")
        self.threadMain = ThreadClassRender()
        self.threadMain.finished.connect(self.finished)
        self.threadMain.frame_upd.connect(self.frame_update)
        self.threadMain.time_upd.connect(self.time_update)
        self.threadMain.state_upd.connect(self.state_update)
        self.threadMain.elapsed_time_upd.connect(self.elapsed_time_update)
        self.locker(True)
        self.ui.startButton.hide()
        self.ui.stopButton.show()
        self.threadMain.start()

    # Kill ffmpeg process
    def proc_kill(self):
        os.chdir(config.main_paths['CWD'])
        self.finish_message = True
        subprocess.run('taskkill /f /im ffmpeg.exe', shell=True)
        config.logging_module.write_to_log('mainWindow', "Killed ffmpeg process")

    # After coding
    def finished(self):
        os.chdir(config.main_paths['CWD'])
        self.ui.startButton.show()
        self.ui.stopButton.hide()

        if self.finish_message:
            self.coding_error('stop')
            self.finish_message = False
        else:
            config.current_state = "Все готово!"
            self.state_update(config.current_state)
            self.elapsed_time_update('')
            QApplication.beep()

        self.ui.progressBar.setValue(0)
        self.locker(False)
        config.logging_module.write_to_log('mainWindow', "Coding finished")

    # Blocking strings and buttons while coding
    def locker(self, lock_value):
        for item in self.base:
            item.setDisabled(lock_value)
        
        tabs = [self.ui.folder_tab, self.ui.settings_tab, self.ui.whatsnew_tab, self.ui.dev_tab]
        for tab in tabs:
            tab.setDisabled(lock_value)

        self.ui.stopButton.setDisabled(not lock_value)
        config.logging_module.write_to_log('mainWindow', "UI locked")
