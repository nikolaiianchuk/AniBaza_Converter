import math
import os
import re
import subprocess
import sys
import traceback
import webbrowser
import config
import loggingModule

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow
from UI.normUI2 import Ui_MainWindow
from faqWindow import FAQWindow
from renderThread import ThreadClassSoft

# Main window class
class MainWindow(QMainWindow):
    # Main window init
    def __init__(self):
        super().__init__()
        self.finish_message = False
        self.threadMain = None
        self.faqWindow = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  
        sys.excepthook = self.handle_exception
        self.set_buttons()
        self.set_checkboxes()
        self.set_textboxes()
        self.set_comboboxes()
        self.set_config_init()
        self.base = [
            self.ui.startButton,
            self.ui.bitrateBox,
            self.ui.modeBox,
            self.ui.hardCheck,
            self.ui.nvencCheck,
            self.ui.codec,
            self.ui.logo_check,
            self.ui.rawButton,
            self.ui.softButton,
            self.ui.soundButton,
            self.ui.subButton,
            self.ui.episodeLine,
            self.ui.rawPath,
            self.ui.soundPath,
            #self.ui.subPath,
            self.ui.softPath,
            self.ui.settingsSaving
        ]
        self.ui.stopButton.hide()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Для прерываний типа Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        loggingModule.write_to_log(f"Handled exception: {error_message}")

    def set_config_init(self):
        if os.path.exists('config.ini'):
            config.logo = config.configSettings.getboolean('main settings', 'logo')
            config.nvencFlag = config.configSettings.getboolean('main settings', 'nvenc')
            config.hevcFlag = config.configSettings.getboolean('main settings', 'hevc')
            config.sub = config.configSettings.getboolean('main settings', 'sub')
            config.build_state = config.configSettings.getint('main settings', 'build_state')
            self.ui.logo_check.setChecked(config.logo)
            self.ui.nvencCheck.setChecked(config.nvencFlag)
            self.ui.codec.setChecked(config.hevcFlag)
            self.ui.hardCheck.setChecked(config.sub)
            self.ui.modeBox.setCurrentIndex(config.build_state)
            loggingModule.write_to_log(f"Settings initialized from config.")

    # Dev mode updater
    def update_dev_mode(self):
        config.enableDevMode = self.ui.enableDevMode.isChecked()
        self.ui.enableLogging.setEnabled(config.enableDevMode)
        if not config.enableDevMode:
            self.ui.enableLogging.setChecked(False)
        loggingModule.write_to_log(f"Dev mode {'enabled' if config.enableDevMode else 'disabled'}.")

    # Subtitle updater
    def update_sub(self):
        config.sub = self.ui.hardCheck.isChecked()
        self.ui.subPath.setEnabled(config.sub)
        self.ui.subButton.setEnabled(config.sub)
        loggingModule.write_to_log(f"Subtitles {'enabled' if config.sub else 'disabled'}.")

    # Logo updater
    def update_logo(self):
        config.logo = self.ui.logo_check.isChecked()
        loggingModule.write_to_log(f"Logo {'enabled' if config.logo else 'disabled'}.")

    # NVENC updater
    def update_nvenc(self):
        config.nvencFlag = self.ui.nvencCheck.isChecked()
        config.nvenc = '_nvenc' if config.nvencFlag else ''
        config.codec = f"{config.hevc}{config.nvenc}"
        loggingModule.write_to_log(f"NVENC {'enabled' if config.nvencFlag else 'disabled'}.")
        
    # Codec updater
    def update_codec(self):
        config.hevcFlag = self.ui.codec.isChecked()
        config.hevc = 'h265' if config.hevcFlag else 'h264'
        config.codec = f"{config.hevc}{config.nvenc}"
        loggingModule.write_to_log(f"H265 {'enabled' if config.hevc == 'h265' else 'disabled'}.")

    # Sound path updater
    def update_sound_path(self):
        config.sound_path = self.ui.soundPath.text()
        config.audio_input_cmd = f'-i "{config.sound_path}" '
        loggingModule.write_to_log(f"Sound path updated to: {config.sound_path}")

    # Raw path updater
    def update_raw_path(self):
        config.raw_path = self.ui.rawPath.text()
        config.video_input_cmd = f'-i "{config.raw_path}" '
        loggingModule.write_to_log(f"Raw path updated to: {config.raw_path}")

    # Softsub path updater
    def update_soft_path(self):
        config.soft_path = self.ui.softPath.text()
        config.episode_line = self.ui.episodeLine.text() if '[AniBaza]' not in config.soft_path else config.soft_path.split('/')[-1]
        config.episode_line = config.episode_line.replace(config.episode_line[config.episode_line.rfind('[')+1:config.episode_line.rfind(']')],'') if '[' in config.episode_line else config.episode_line
        self.ui.episodeLine.setText(config.episode_line)
        loggingModule.write_to_log(f"Softsub path updated to: {config.soft_path}")

    # Subtitle path updater
    def update_sub_path(self):
        config.sub_path = self.ui.subPath.text()
        config.subtitle_input_cmd = f'-i "{config.sub_path}" '
        loggingModule.write_to_log(f"Subtitle path updated to: {config.sub_path}")

    # Episode name updater
    def update_episode(self):
        config.episode_line = self.ui.episodeLine.text()
        config.output_title_metadata_cmd = f'-metadata title="{config.episode_line}" '
        loggingModule.write_to_log(f"Episode name updated to: {config.episode_line}")

    # Bitrate updater
    def update_bitrate(self):
        config.video_bitrate = self.ui.bitrateBox.currentText()
        config.video_bitrate_cmd = f'-b:v {config.video_bitrate}K '
        loggingModule.write_to_log(f"Bitrate updated to: {config.video_bitrate}Kbps")

    # Mode updater
    def update_mode(self):
        config.build_state = config.build_states.get(self.ui.modeBox.currentText())
        loggingModule.write_to_log(f"Mode updated to: {self.ui.modeBox.currentText()}")

    # FAQ window opener
    def open_faq(self):
        if self.faqWindow is None:
            self.faqWindow = FAQWindow()
        self.faqWindow.show()
        loggingModule.write_to_log("FAQ window opened.")
    
    # Config saving
    def save_config(self):
        config.configSettings.set('main settings', 'logo', str(config.logo))
        config.configSettings.set('main settings', 'nvenc', str(config.nvencFlag))
        config.configSettings.set('main settings', 'hevc', str(config.hevcFlag))
        config.configSettings.set('main settings', 'sub', str(config.sub))
        config.configSettings.set('main settings', 'build_state', str(config.build_state))
        with open('config.ini', 'w') as configfile:
            config.configSettings.write(configfile)
        loggingModule.write_to_log("Config saved.")

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
            self.ui.settingsSaving: self.save_config
        }

        for button, handler in buttons.items():
            button.clicked.connect(handler)
        
        loggingModule.write_to_log("Buttons set.")

    # Checkboxes definition
    def set_checkboxes(self):
        checkboxes = {
            self.ui.enableDevMode: self.update_dev_mode,
            self.ui.hardCheck: self.update_sub,
            self.ui.logo_check: self.update_logo,
            self.ui.nvencCheck: self.update_nvenc,
            self.ui.codec: self.update_codec
        }

        for checkbox, handler in checkboxes.items():
            checkbox.stateChanged.connect(handler)

        loggingModule.write_to_log("Checkboxes set.")

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

        loggingModule.write_to_log("Textboxes set.")

    # Comboboxes definition
    def set_comboboxes(self):
        comboboxes = {
            self.ui.bitrateBox: self.update_bitrate,
            self.ui.modeBox: self.update_mode,
        }

        for combobox, handler in comboboxes.items():
            combobox.currentIndexChanged.connect(handler)

        loggingModule.write_to_log("Comboboxes set.")

    # Open hardsub directory
    def open_hardsub(self):
        if os.path.exists(config.hardsub_dir):
            os.startfile(config.hardsub_dir)
        else:
            self.coding_error('hardsub_folder')
        loggingModule.write_to_log("Hardsub folder opened.")

    # Softsub saving path
    def soft_folder_path(self):
        config.soft_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Куда пихать софт?')
        self.ui.softPath.setText(config.soft_path)
        loggingModule.write_to_log(f"Softsub path updated to: {config.soft_path}")

    # Sound file choose
    def sound_folder_path(self):
        config.sound_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать звук?", "",
                                                            "All(*.wav *.flac *.aac *.m4a *.mka)")
        self.ui.soundPath.setText(config.sound_path)
        loggingModule.write_to_log(f"Sound path updated to: {config.sound_path}")

    # Raw video choose
    def raw_folder_path(self):
        config.raw_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать равку?", "",
                                                            "ALL (*.mkv *.mp4 *.avi)")
        self.ui.rawPath.setText(config.raw_path)
        loggingModule.write_to_log(f"Raw path updated to: {config.raw_path}")

    # Subtitle choose
    def sub_folder_path(self):
        config.sub_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Где брать надписи?", "",
                                                            "Хуй (*.ass *.srt)")
        self.ui.subPath.setText(config.sub_path)
        loggingModule.write_to_log(f"Subtitle path updated to: {config.sub_path}")

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
        loggingModule.write_to_log(f"Coding error: {error_type}")

    # Progress updater
    def frame_update(self, frame):
        loggingModule.write_to_log(f"Frame updated: {frame}")
        self.ui.progressBar.setValue(int(frame))

    # Set progressbar maximum
    def time_update(self, time):
        loggingModule.write_to_log(f"Time updated: {time}")
        self.ui.progressBar.setMaximum(math.ceil(time))

    # State updater
    def state_update(self, state):
        self.ui.stateLabel.setText(state)

    # Thread start with ffmpeg
    def ffmpeg_thread(self):
        if not os.path.exists(config.hardsub_dir):
            self.coding_error('hardsub_folder')
            return

        self.ui.stateLabel.setText("Работаю....(наверное)")
        self.ui.progressBar.setValue(0)

        config.softsub_output_cmd = f'"{config.soft_path}/{config.episode_line}.mkv"'
        config.hardsub_output_cmd = f'"{config.hardsub_dir}/{config.episode_line}.mp4"'

        if not os.path.exists(config.raw_path):
            self.coding_error('raw')
            return

        if not os.path.exists(config.sound_path) and config.build_state != 3:
            self.coding_error('sound')
            return

        if not os.path.exists(config.sub_path) and config.sub:
            self.coding_error('subtitle')
            return

        if not (os.path.exists(config.soft_path) and config.build_state in [0, 1]) and config.build_state not in [2, 3]:
            self.coding_error('softsub')
            return

        if not re.match(r'^[a-zA-Z0-9 _.\-\[\]]+$', config.episode_line):
            self.coding_error('name')
            return

        loggingModule.write_to_log("Starting ffmpeg...")
        self.threadMain = ThreadClassSoft()
        self.threadMain.finished.connect(self.finished)
        self.threadMain.frame_upd.connect(self.frame_update)
        self.threadMain.time_upd.connect(self.time_update)
        self.threadMain.state_upd.connect(self.state_update)
        self.locker(True)
        self.ui.startButton.hide()
        self.ui.stopButton.show()
        self.threadMain.start()

    # Kill ffmpeg process
    def proc_kill(self):
        os.chdir(config.main_dir)
        self.finish_message = True
        subprocess.run('taskkill /f /im ffmpeg.exe', shell=True)
        loggingModule.write_to_log("Killed ffmpeg process")

    # After coding
    def finished(self):
        os.chdir(config.main_dir)
        self.ui.startButton.show()
        self.ui.stopButton.hide()

        if self.finish_message:
            self.coding_error('stop')
            self.finish_message = False
        else:
            config.current_state = "Все готово!"
            self.state_update(config.current_state)
            QApplication.beep()

        self.ui.progressBar.setValue(0)
        self.locker(False)
        loggingModule.write_to_log("Coding finished")

    # Blocking strings and buttons while coding
    def locker(self, lock_value):
        for item in self.base:
            item.setDisabled(lock_value)
        
        tabs = [self.ui.folder_tab, self.ui.settings_tab, self.ui.whatsnew_tab, self.ui.dev_tab]
        for tab in tabs:
            tab.setDisabled(lock_value)

        self.ui.stopButton.setDisabled(not lock_value)
        loggingModule.write_to_log("UI locked")
